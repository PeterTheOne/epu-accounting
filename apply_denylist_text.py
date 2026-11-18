import argparse
import os.path
import pandas as pd
import re


def apply_denylist_text(input_file, denylist_file, output_file, denylist_column='text', csv_date_format='%d.%m.%Y', csv_delimiter=',', csv_quotechar='"', csv_encoding='utf-8'):
    if not os.path.isfile(input_file):
        print('Error: File "{0}" don\'t exist.'.format(input_file))
        return
    if not os.path.isfile(denylist_file):
        print('Error: File "{0}" don\'t exist.'.format(denylist_file))
        return
    date_parser = lambda x: pd.datetime.strptime(x, csv_date_format)
    data = pd.read_csv(filepath_or_buffer=input_file, delimiter=csv_delimiter, quotechar=csv_quotechar, encoding=csv_encoding,
                       parse_dates=['value_date', 'posting_date'], date_parser=date_parser)

    denylist = pd.read_csv(filepath_or_buffer=denylist_file, delimiter=csv_delimiter, quotechar=csv_quotechar, encoding=csv_encoding)
    denylist[denylist_column] = denylist[denylist_column].map(lambda x: re.escape(x))

    data = data[~data[denylist_column].str.contains('|'.join(denylist[denylist_column]))]

    data.to_csv(path_or_buf=output_file, index=False,
                sep=csv_delimiter, quotechar=csv_quotechar, encoding=csv_encoding,
                date_format=csv_date_format)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file')
    parser.add_argument('denylist_file')
    parser.add_argument('output_file')
    #parser.add_argument('--denylist_column')
    args = parser.parse_args()
    apply_denylist_text(args.input_file, args.denylist_file, args.output_file)


if __name__ == '__main__':
    main()
