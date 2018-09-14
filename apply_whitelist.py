import argparse
import os.path
import pandas as pd


def apply_whitelist(input_file, whitelist_file, output_file, whitelist_column='contra_iban', csv_date_format='%d.%m.%Y', csv_delimiter=',', csv_quotechar='"', csv_encoding='utf-8'):
    if not os.path.isfile(input_file):
        print('Error: File "{0}" don\'t exist.'.format(input_file))
        return
    if not os.path.isfile(whitelist_file):
        print('Error: File "{0}" don\'t exist.'.format(whitelist_file))
        return
    date_parser = lambda x: pd.datetime.strptime(x, csv_date_format)
    data = pd.read_csv(filepath_or_buffer=input_file, delimiter=csv_delimiter, quotechar=csv_quotechar, encoding=csv_encoding,
                       parse_dates=['value_date', 'posting_date'], date_parser=date_parser)

    whitelist = pd.read_csv(filepath_or_buffer=whitelist_file, delimiter=csv_delimiter, quotechar=csv_quotechar, encoding=csv_encoding)

    data = data[data[whitelist_column].isin(whitelist[whitelist_column])]

    data.to_csv(path_or_buf=output_file, index=False,
                sep=csv_delimiter, quotechar=csv_quotechar, encoding=csv_encoding,
                date_format=csv_date_format)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file')
    parser.add_argument('whitelist_file')
    parser.add_argument('output_file')
    #parser.add_argument('--whitelist_column')
    args = parser.parse_args()
    apply_whitelist(args.input_file, args.whitelist_file, args.output_file)


if __name__ == '__main__':
    main()
