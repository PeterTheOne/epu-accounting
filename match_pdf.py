import argparse
import os.path
from pathlib import Path
import pandas as pd
import sqlite3
from sqlite3 import Error

import ntpath

import PyPDF2 
#import textract

import re
from collections import Counter

import datetime
import locale

import unicodedata

#from nltk.tokenize import word_tokenize
#from nltk.corpus import stopwords

import constants
from functions_data import *
from functions_db import *
from functions_match import *


def convert_strings_to_dates(value, format):
    locale.setlocale(locale.LC_ALL, 'de_DE.utf8')
    try:
        return pd.datetime.strptime(value, format)
    except ValueError:
        return False


def read_pdf(data, invoice_file):
    if not os.path.isfile(invoice_file):
        print('Error: File "{0}" doesn\'t exist.'.format(invoice_file))
        return

    #open allows you to read the file
    pdfFileObj = open(invoice_file,'rb')
    #The pdfReader variable is a readable object that will be parsed
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    #discerning the number of pages will allow us to parse through all #the pages
    num_pages = pdfReader.numPages
    count = 0
    text = ""
    #The while loop will read each page
    while count < num_pages:
        pageObj = pdfReader.getPage(count)
        count +=1
        text += pageObj.extractText()
    #This if statement exists to check if the above library returned #words. It's done because PyPDF2 cannot read scanned files.
    if text != "":
       text = text
    #If the above returns as False, we run the OCR library textract to #convert scanned/image based PDF files into text
    #else:
       #text = textract.process(fileurl, method='tesseract', language='eng')
    # Now we have a text variable which contains all the text derived #from our PDF file. Type print(text) to see what it contains. It #likely contains a lot of spaces, possibly junk such as '\n' etc.
    # Now, we will clean our text variable, and return it as a list of keywords.

    #with open('work/output.txt', 'w') as out:
        #out.write(text)

    # extract important info
    filename_keywords = os.path.splitext(ntpath.basename(invoice_file))[0]
    filename_keywords = re.split('\W+|_', filename_keywords)
    ibans = re.findall('([A-Z]{2}\d{2}(?:\s?\d{4}){4,8})', text, re.MULTILINE)
    amounts = re.findall('(\d{1,3},\d{2})', text, re.MULTILINE)
    emails = re.findall('\@(\w+)\..+', text, re.MULTILINE)
    invoice_no = re.findall('(\d{5,20})', text, re.MULTILINE)

    # extract dates
    # TODO: support for other locales
    date_regex_format = [
        {'regex': '(\d{1,2}\.\d{1,2}\.\d{4})', 'format': '%d.%m.%Y'},
        {'regex': '(\d{1,2}\.\s+(?:Januar|Jänner|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|September|Oktober|November|Dezember)\s+\d{4})', 'format': '%d. %B %Y'},
    ]
    dates = []
    for regex_format in date_regex_format:
        dates_set = re.findall(regex_format['regex'], text, re.MULTILINE)
        dates_set = list(filter(lambda y: y != False, map(lambda x: convert_strings_to_dates(x, regex_format['format']), dates_set)))
        dates.extend(dates_set)

    # format for csv matching
    ibans = list(map(lambda iban: ''.join(iban.split()), ibans))
    amounts = list(map(lambda amount: amount.replace(',', '.'), amounts))

    # find date by last
    if len(dates) > 0:
        date = dates[len(dates) - 1]
    else:
        date = False

    # find amount by most common
    amounts.sort(key=Counter(amounts).get, reverse=True) # sort by most common
    amounts = list(filter(lambda amount: amount != '0.00', amounts)) # filter zeros
    if len(amounts) > 0:
        amount = float(amounts[0])
    else:
        amount = False

    # filter filename keywords
    filename_keywords = list(filter(lambda keyword: len(keyword) > 4, filename_keywords)) # filter short

    # filter keywords in text
    invoice_no.sort(key=Counter(invoice_no).get, reverse=True) # sort by most common
    invoice_no = list(set(invoice_no)) # remove duplicates
    invoice_no = invoice_no[:4] # limit to 4 keywords

    # weights
    filename_weights = match_keywords(data['comment'], filename_keywords)
    iban_weights = match_exact(data['contra_iban'], ibans)
    numbers_weights = match_keywords(data['comment'], invoice_no)
    amount_weights = match_amount(data['amount'], amount, absolute=True)
    date_weights = match_date(data['posting_date'], date)
    emails_weights = match_keywords(data['contra_name'], emails)

    weights = (filename_weights*0.25 + iban_weights*0.1 + numbers_weights*0.2 + date_weights*0.1 + amount_weights*0.15 + emails_weights*0.2)

    print('Date: ' + str(date))
    print('Filename: ' + str(filename_keywords))
    print('IBAN: ' + str(ibans))
    print('Numbers: ' + str(invoice_no))
    print('Amount: ' + str(amount))
    print('E-Mails: ' + str(emails))
    result = pd.concat([
        data,
        weights.rename('w'),
        filename_weights.rename('filename_w'),
        iban_weights.rename('iban_w'),
        numbers_weights.rename('numbers_w'),
        date_weights.rename('date_w'),
        amount_weights.rename('amount_w'),
        emails_weights.rename('emails_w')
    ], axis=1, sort=False)
    result = result.sort_values(by=['w'], ascending=False) # sort by closest matches
    result = result.iloc[:10] # keep only top 10
    #print(result[['line_id', 'posting_date', 'amount', 'w', 'filename_w', 'iban_w', 'numbers_w', 'date_w', 'amount_w', 'emails_w']])

    return result


def batch_read_pdf(db_file, input_path='.', automatic=False):
    if not os.path.exists(input_path):
        print('Error: No such directory "{0}".'.format(input_path))
        return

    # create a database connection
    conn = create_connection(db_file)

    with conn:
        cur = conn.cursor()
        sql = ''' SELECT * FROM records WHERE status != ? '''
        params = [constants.STATUS_IGNORE]
        data = pd.read_sql(sql, conn, params=params, parse_dates=get_date_cols())

        # batch process all PDFs recursively
        pathlist = Path(input_path).glob('**/*.pdf')
        log_files = 1
        log_matches = 0
        log_inserted = 0
        choices_exclude = []

        for path in pathlist:
            # because path is object not string
            path_in_str = str(path)
            print('Processing ' + path_in_str)
            matches = read_pdf(data, path_in_str)

            chosen_result = None
            if not automatic:
                # Present choices
                choices_objects = []
                for index, match in matches.iterrows():
                    if match['id'] in choices_exclude:
                        # mark as already chosen
                        record_format = '({0:.2f}: {1} at {2} from/to {3}, subject: )'
                    else:
                        record_format = '{0:.2f}: {1} at {2} from/to {3}, subject: '
                    name = record_format.format(match['w'], match['amount'], match['posting_date'], match['contra_name'])#, get_record_subject(match))
                    choices_objects.append({'value': match.at['id'], 'name': name})
                choices_objects.append({'value': 'none', 'name': 'None of the above'})
                answers = prompt([
                    {
                        'type': 'list',
                        'name': 'selected_record',
                        'message': 'Select record for PDF',
                        'choices': choices_objects
                    }
                ])
                selected_record = answers['selected_record']

                # Skip if nothing was selected
                if selected_record != 'none':
                    chosen_result = matches.loc[matches['id'] == selected_record]
                    choices_exclude.append(selected_record)

            else:
                # Choose match with highest score
                chosen_result = matches.iloc[:1]
                # is the match good enough?
                chosen_result = chosen_result.loc[matches['w'] > 0.3]

            if chosen_result is not None and not chosen_result.empty:
                chosen_result = chosen_result.iloc[0]
                log_matches += 1

                # insert file
                params = [
                    int(chosen_result.at['id']),
                    path_in_str
                ]

                cur.execute("INSERT INTO files (record_id,path) VALUES (?,?)", params)
                log_inserted += cur.rowcount

            log_files += 1

    conn.close()

    print('Found {0} matching records for {1} files, {2} inserted.'.format(log_matches, log_files, log_inserted))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('db_file')
    parser.add_argument('input_path')
    parser.add_argument('--automatic', dest='automatic', action='store_true')
    args = parser.parse_args()
    batch_read_pdf(args.db_file, args.input_path, args.automatic)


if __name__ == '__main__':
    main()
