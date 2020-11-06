import argparse
import os.path
import pandas as pd

from functions_data import *

import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import numpy as np


def import_records_from_file(input_file, csv_date_format='%d.%m.%Y', csv_delimiter=',', csv_quotechar='"', csv_encoding='utf-8'):
    if not os.path.isfile(input_file):
        print('Error: File "{0}" doesn\'t exist.'.format(input_file))
        return

    date_parser = lambda x: pd.to_datetime(x, format=csv_date_format, errors='coerce')
    data = pd.read_csv(filepath_or_buffer=input_file, delimiter=csv_delimiter, quotechar=csv_quotechar, encoding=csv_encoding,
                       parse_dates=['value_date'], date_parser=date_parser)

    return data


def show_plot(data):

    data = data[['value_date', 'amount']]

    # expand date range by adding add start & end dates
    # todo: does this override existing amounts?
    start_row = pd.Series(data={'value_date': pd.Timestamp('2020-09-01'), 'amount': 0}, name='x')
    end_row = pd.Series(data={'value_date': pd.Timestamp('2021-01-01'), 'amount': 0}, name='x')
    data = data.append(start_row, ignore_index=True)
    data = data.append(end_row, ignore_index=True)
    # todo: clamp dates
    data = data.set_index('value_date') # remove integer index

    print('corrected:')
    print(data)

    data = data.resample('1d').sum().fillna(0) # fill in dates

    print('resampled:')
    print(data)

    data = data.cumsum()

    # todo: add current account balance
    data['amount'] += 2000

    #print('final:')
    #print(data)

    root = tk.Tk()

    figure = plt.Figure(figsize=(5, 4), dpi=100)
    ax = figure.add_subplot(111)
    line = FigureCanvasTkAgg(figure, root)
    line.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
    data.plot(kind='line', legend=True, ax=ax, color='r', marker='o', fontsize=10)
    ax.set_title('Future balance')

    root.mainloop()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file')
    args = parser.parse_args()

    data = import_records_from_file(args.input_file)
    show_plot(data)

if __name__ == '__main__':
    main()
