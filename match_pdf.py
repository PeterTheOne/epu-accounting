import argparse
import os.path
from pathlib import Path
import pandas as pd

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


def convert_strings_to_dates(value, format):
    locale.setlocale(locale.LC_ALL, 'de_DE.utf8')
    try:
        return pd.datetime.strptime(value, format)
    except ValueError:
        return False


def lerp(a, b, x):
    return (x * a) + ((1-x) * b)


def clamp(num, min_value, max_value):
   return max(min(num, max_value), min_value)


def normalize_caseless(text):
    return unicodedata.normalize("NFKD", text.casefold())


def caseless_equal(left, right):
    return normalize_caseless(left) == normalize_caseless(right)


# TODO: min larger than max
def linear_conversion(old_value, old_min, old_max, new_min, new_max):
    new_value = ( (old_value - old_min) / (old_max - old_min) ) * (new_max - new_min) + new_min
    return clamp(abs(new_value), 0, 1)


def match_date(csv_dates, date):
    if date == False:
        return pd.Series([0] * len(csv_dates), index=csv_dates.index)
    weights = []
    for csv_date in csv_dates:
        weight = 1 - linear_conversion((csv_date - date).days, 0, datetime.timedelta(days=30).days, 0, 1)
        weights.append( weight )
        #print(str(csv_date - date) + ' to ' + str(weight))
    weights = pd.Series(weights, index=csv_dates.index)
    return weights


def match_exact(csv_column, values):
    values = list(map(lambda v: normalize_caseless(v), values))
    weights = []
    for csv_row in csv_column:
        if len(values) > 0:
            if normalize_caseless(str(csv_row)) in values: # TODO: str cast?
                weight = 1
            else:
                weight = 0
        else:
            weight = 0
        weights.append( weight )
    weights = pd.Series(weights, index=csv_column.index)
    return weights


def match_keywords(csv_comments, keywords):
    weights = []
    pattern = '|'.join(keywords)
    for csv_comment in csv_comments:
        if len(keywords) > 0:
            matches = re.findall(pattern, str(csv_comment), re.IGNORECASE | re.MULTILINE)
            weight = linear_conversion(len(matches), 0, len(keywords), 0, 1)
        else:
            weight = 0
        weights.append( weight )
    weights = pd.Series(weights, index=csv_comments.index)
    return weights


def match_amount(csv_amounts, amount):
    weights = []
    for csv_amount in csv_amounts:
        diff = abs(csv_amount) - abs(amount)
        if amount != False:
            weight = 1 - linear_conversion(diff, 0, 2, 0, 1)
        else:
            weight = 0
        weights.append( weight )
    weights = pd.Series(weights, index=csv_amounts.index)
    return weights


def read_pdf(data, invoice_file, csv_date_format='%d.%m.%Y', csv_delimiter=',', csv_quotechar='"', csv_encoding='utf-8'):
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
    amount_weights = match_amount(data['amount'], amount)
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
    print(result[['line_id', 'posting_date', 'amount', 'w', 'filename_w', 'iban_w', 'numbers_w', 'date_w', 'amount_w', 'emails_w']])


def batch_read_pdf(csv_file, input_path='.', csv_date_format='%d.%m.%Y', csv_delimiter=',', csv_quotechar='"', csv_encoding='utf-8'):
    if not os.path.exists(input_path):
        print('Error: No such directory "{0}".'.format(input_path))
        return

    if not os.path.isfile(csv_file):
        print('Error: File "{0}" doesn\'t exist.'.format(csv_file))
        return

    # read csv
    date_parser = lambda x: pd.datetime.strptime(x, csv_date_format)
    data = pd.read_csv(filepath_or_buffer=csv_file, delimiter=csv_delimiter, quotechar=csv_quotechar, encoding=csv_encoding,
                       parse_dates=['value_date', 'posting_date'], date_parser=date_parser)

    # batch process all PDFs recursively
    pathlist = Path(input_path).glob('**/*.pdf')
    for path in pathlist:
        # because path is object not string
        path_in_str = str(path)
        print('Processing ' + path_in_str)
        read_pdf(data, path_in_str)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('csv_file')
    parser.add_argument('input_path')
    args = parser.parse_args()
    batch_read_pdf(args.csv_file, args.input_path)


if __name__ == '__main__':
    main()
