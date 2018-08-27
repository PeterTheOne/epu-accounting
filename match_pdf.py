import argparse
import os.path
import pandas as pd

import PyPDF2 
#import textract

import re
from collections import Counter

import datetime
import locale

#from nltk.tokenize import word_tokenize
#from nltk.corpus import stopwords

def read_pdf(invoice_file, csv_file, csv_date_format='%d.%m.%Y', csv_delimiter=',', csv_quotechar='"', csv_encoding='utf-8'):
    if not os.path.isfile(invoice_file):
        print('Error: File "{0}" doesn\'t exist.'.format(invoice_file))
        return

    if not os.path.isfile(csv_file):
        print('Error: File "{0}" doesn\'t exist.'.format(csv_file))
        return

    # read csv
    date_parser = lambda x: pd.datetime.strptime(x, csv_date_format)
    data = pd.read_csv(filepath_or_buffer=csv_file, delimiter=csv_delimiter, quotechar=csv_quotechar, encoding=csv_encoding,
                       parse_dates=['value_date', 'posting_date'], date_parser=date_parser)

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
    ibans = re.findall('([A-Z]{2}\d{2}(?:\s?\d{4}){4,8})', text, re.MULTILINE)
    dates = re.findall('((?:\d{1,2}\.\d{1,2}\.\d{4})|(?:\d{1,2}\.\s+(?:Januar|Jänner|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|September|Oktober|November|Dezember)\s+\d{4}))', text, re.MULTILINE)
    amounts = re.findall('(\d{1,3},\d{2})', text, re.MULTILINE)
    emails = re.findall('\@(.+\..+)', text, re.MULTILINE)
    invoice_no = re.findall('(\d{5,20})', text, re.MULTILINE)

    # format for csv matching
    ibans = list(map(lambda iban: ''.join(iban.split()), ibans))
    amounts = list(map(lambda amount: amount.replace(',', '.'), amounts))

    # find date by last
    locale.setlocale(locale.LC_ALL, 'de_DE.utf8')
    dates = list(map(lambda x: pd.datetime.strptime(x, '%d. %B %Y'), dates))
    if len(dates) > 0:
        date = dates[len(dates) - 1]
    else:
        date = pd.datetime.now()

    # find amount by most common
    amounts.sort(key=Counter(amounts).get, reverse=True) # sort by most common
    amounts = list(filter(lambda amount: amount != '0.00', amounts)) # filter zeros
    if len(amounts) > 0:
        amount = float(amounts[0])
    else:
        amount = 0.0

    print('IBANs:')
    print(ibans)
    print('dates:')
    print(dates)
    print('date:')
    print(date)
    print('amounts:')
    print(amounts)
    print('amount:')
    print(amount)
    print('emails:')
    print(emails)
    print('invoice no:')
    print(invoice_no)

    #for iban in ibans:
    invoice_pattern = '|'.join(invoice_no)

    # TODO: Create list of matches, weighted by conditions

    condition_iban = (data['contra_iban'].isin(ibans))
    condition_amount = (data['amount'].abs() == amount)
    condition_invoice_no = (data['comment'].str.contains(invoice_pattern)==True)
    condition_date = abs(data['posting_date'] - date) < datetime.timedelta(days=30)
    #matches = data[condition_iban & condition_amount & condition_invoice_no]
    matches = data[condition_invoice_no & condition_date]

    print(matches[['line_id', 'posting_date']])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('invoice_file')
    parser.add_argument('csv_file')
    args = parser.parse_args()
    read_pdf(args.invoice_file, args.csv_file)


if __name__ == '__main__':
    main()
