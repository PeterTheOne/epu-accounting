import argparse
import os.path
import pandas as pd

import clean_csv
import presets
from functions_data import get_date_cols


def apply_blacklist(input_file, blacklist_file, output_file, preset_key=None, drop_empty=False, blacklist_column='contra_iban', csv_date_format='%d.%m.%Y', csv_delimiter=',', csv_quotechar='"', csv_encoding='utf-8'):
    if not os.path.isfile(input_file):
        print('Error: File "{0}" doesn\'t exist.'.format(input_file))
        return
    if not os.path.isfile(blacklist_file):
        print('Error: File "{0}" doesn\'t exist.'.format(blacklist_file))
        return

    if preset_key:
        # raw statement: parse and normalize it with the given preset first
        if preset_key not in presets.PRESETS:
            print('Preset {} not found'.format(preset_key))
            return
        data = clean_csv.clean_from_preset(input_file, None, preset_key)
    else:
        # already cleaned CSV
        date_parser = lambda x: pd.to_datetime(x, format=csv_date_format, errors='coerce')
        data = pd.read_csv(filepath_or_buffer=input_file, delimiter=csv_delimiter, quotechar=csv_quotechar, encoding=csv_encoding,
                           parse_dates=get_date_cols(), date_parser=date_parser)

    blacklist = pd.read_csv(filepath_or_buffer=blacklist_file, delimiter=csv_delimiter, quotechar=csv_quotechar, encoding=csv_encoding)

    data = data[~data[blacklist_column].isin(blacklist[blacklist_column])]

    if drop_empty:
        empty = data['contra_iban'].isnull() | (data['contra_iban'].astype(str).str.strip() == '')
        data = data[~empty]

    data.to_csv(path_or_buf=output_file, index=False,
                sep=csv_delimiter, quotechar=csv_quotechar, encoding=csv_encoding,
                date_format=csv_date_format)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file')
    parser.add_argument('blacklist_file')
    parser.add_argument('output_file')
    parser.add_argument('--preset', choices=list(presets.PRESETS.keys()),
                        help='parse input_file as a raw statement using this preset (otherwise input_file must already be cleaned)')
    parser.add_argument('--drop_empty', action='store_true',
                        help='also filter out lines with an empty contra_iban')
    #parser.add_argument('--blacklist_column')
    args = parser.parse_args()
    apply_blacklist(args.input_file, args.blacklist_file, args.output_file, args.preset, args.drop_empty)


if __name__ == '__main__':
    main()
