import argparse
import os.path

from functions_data import read_csv_dates


def sort_csv(input_file, output_file, csv_date_format='%d.%m.%Y', csv_delimiter=',', csv_quotechar='"', csv_encoding='utf-8'):
    if not os.path.isfile(input_file):
        print('Error: File "{0}" don\'t exist.'.format(input_file))
        return
    data = read_csv_dates(['value_date', 'posting_date'], csv_date_format, filepath_or_buffer=input_file, delimiter=csv_delimiter, quotechar=csv_quotechar, encoding=csv_encoding)
    data = data.sort_values(by=['value_date', 'posting_date'])
    data.to_csv(path_or_buf=output_file, index=False,
                sep=csv_delimiter, quotechar=csv_quotechar, encoding=csv_encoding,
                date_format=csv_date_format)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file')
    parser.add_argument('output_file')
    args = parser.parse_args()
    sort_csv(args.input_file, args.output_file)


if __name__ == '__main__':
    main()
