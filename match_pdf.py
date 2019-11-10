import argparse

import os.path
from pathlib import Path
import ntpath

import re
from collections import Counter

import locale

import threading
import queue as Queue

import tkinter as tk
from tkinter import ttk
from PyInquirer import prompt

import pandas as pd

from PIL import ImageTk
from pdf2image import convert_from_path

import constants
from functions_data import get_date_cols
from functions_db import create_connection
from functions_match import match_date, match_keywords, match_exact, match_amount
from functions_pdf import extract_text_pdf

# constants
SINGLE_FILE = True
SIZE = (500, None)
USE_CROPBOX = True

# globals
global_image = ''
global_old_image = ''

def convert_strings_to_dates(value, format):
    locale.setlocale(locale.LC_ALL, 'de_DE.utf8')
    try:
        return pd.datetime.strptime(value, format)
    except ValueError:
        return False


class PdfGui:
    def __init__(self, master):
        self.master = master

        self.width, self.height = 700, 700
        master.minsize(width=self.width, height=self.height)
        master.maxsize(width=self.width, height=self.height)
        self.image = ''

        self.make_widgets()

    def make_widgets(self):
        frame_outer = ttk.Frame(self.master)
        canvas = tk.Canvas(frame_outer, width=self.width-20, height=self.height-50)
        frame_inner = ttk.Frame(canvas)
        scrollx = ttk.Scrollbar(frame_outer, orient='horizontal', command=canvas.xview)
        scrolly = ttk.Scrollbar(frame_outer, orient='vertical', command=canvas.yview)
        canvas.configure(xscrollcommand=scrollx.set, yscrollcommand=scrolly.set)

        frame_outer.grid()
        canvas.grid(row=1, sticky='nesw')
        scrollx.grid(row=2, sticky='ew')
        scrolly.grid(row=1, column=2, sticky='ns')
        canvas.create_window(0, 0, window=frame_inner, anchor='nw')

        self.label = ttk.Label(frame_inner)
        self.label.grid(sticky='w')

        self.prog_bar = ttk.Progressbar(
            self.master, orient="horizontal",
            length=self.width, mode="indeterminate"
            )
        self.prog_bar.grid(sticky='w')

    def update_gui(self):
        global global_image, global_old_image

        if global_image != global_old_image:
            self.set_image()
            global_old_image = global_image

    def set_image(self):
        global global_image

        self.prog_bar.start()

        # Load image
        pil_images = convert_from_path(global_image, single_file=SINGLE_FILE,
                                       size=SIZE, use_cropbox=USE_CROPBOX)
        first_page = pil_images[0]
        self.image = ImageTk.PhotoImage(first_page)
        self.label.configure(image=self.image)

        self.prog_bar.stop()

    def start_threading(self, db_file, input_path='.', automatic=False):
        self.queue = Queue.Queue()
        ThreadedTask(self.queue, db_file, input_path, automatic).start()
        self.master.after(100, self.process_queue)

    def process_queue(self):
        self.update_gui()

        try:
            msg = self.queue.get(0)
            #print(msg) # Show result of the task if needed
            self.master.destroy() # Close GUI
        except Queue.Empty:
            self.master.after(100, self.process_queue)


class ThreadedTask(threading.Thread):
    def __init__(self, queue, db_file, input_path='.', automatic=False):
        threading.Thread.__init__(self)
        self.queue = queue
        self.db_file = db_file
        self.input_path = input_path
        self.automatic = automatic
    def run(self):
        # Some long running process
        batch_read_pdf(self.db_file, self.input_path, self.automatic)
        self.queue.put("Task finished")


def read_pdf(data, invoice_file):
    if not os.path.isfile(invoice_file):
        print('Error: File "{0}" doesn\'t exist.'.format(invoice_file))
        return

    text = extract_text_pdf(invoice_file)

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
    global global_image

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
            global_image = path_in_str

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
    parser.add_argument('--gui', dest='gui', action='store_true')
    args = parser.parse_args()

    if not args.automatic and args.gui:
        root = tk.Tk()
        root.title("epu-accounting - PDF Viewer")
        main_ui = PdfGui(root)
        main_ui.start_threading(args.db_file, args.input_path, args.automatic)
        root.mainloop()
    else:
        batch_read_pdf(args.db_file, args.input_path, args.automatic)


if __name__ == '__main__':
    main()
