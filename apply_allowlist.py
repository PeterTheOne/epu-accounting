import argparse
import os.path
import pandas as pd

from functions_data import match_list, read_csv_dates


def apply_allowlist(input_file, allowlist_file, output_file, allowlist_column='contra_iban', csv_date_format='%d.%m.%Y', csv_delimiter=',', csv_quotechar='"', csv_encoding='utf-8'):
    if not os.path.isfile(input_file):
        print('Error: File "{0}" don\'t exist.'.format(input_file))
        return
    if not os.path.isfile(allowlist_file):
        print('Error: File "{0}" don\'t exist.'.format(allowlist_file))
        return
    data = read_csv_dates(['value_date', 'posting_date'], csv_date_format, filepath_or_buffer=input_file, delimiter=csv_delimiter, quotechar=csv_quotechar, encoding=csv_encoding)

    allowlist = pd.read_csv(filepath_or_buffer=allowlist_file, delimiter=csv_delimiter, quotechar=csv_quotechar, encoding=csv_encoding)

    allowlisted = match_list(data, allowlist, allowlist_column, allowlist_file)
    if allowlisted is None:
        return
    data = data[allowlisted]

    data.to_csv(path_or_buf=output_file, index=False,
                sep=csv_delimiter, quotechar=csv_quotechar, encoding=csv_encoding,
                date_format=csv_date_format)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file')
    parser.add_argument('allowlist_file')
    parser.add_argument('output_file')
    parser.add_argument('--allowlist_column', default='contra_iban',
                        help='column to match between input_file and allowlist_file (default: contra_iban)')
    args = parser.parse_args()
    apply_allowlist(args.input_file, args.allowlist_file, args.output_file, args.allowlist_column)


if __name__ == '__main__':
    main()
