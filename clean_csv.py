import argparse
import os.path
import pandas as pd
import locale
from functions_data import *


def clean_csv(input_file, output_file, preset_name='', date_format='%d.%m.%Y', delimiter=';', quotechar='"', encoding='ISO/-8859-1', decimal=',', thousands='.', col_names=None, usecols=[], col_map=[], date_cols=[]):
    if not os.path.isfile(input_file):
        print('Error: File "{0}" don\'t exist.'.format(input_file))
        return
    locale.setlocale(locale.LC_NUMERIC, '')
    date_parser = lambda x: pd.to_datetime(x, format=date_format, errors='coerce')
    data = pd.read_csv(filepath_or_buffer=input_file, delimiter=delimiter, quotechar=quotechar, encoding=encoding, header=0,
                       decimal=decimal, thousands=thousands,
                       names=col_names, usecols=usecols,
                       parse_dates=date_cols, date_parser=date_parser)

    # Add columns
    data['import_preset'] = preset_name # todo: default value

    # Reformat columns # todo: broken?
    if col_map:
        data = data.rename(index=str, columns=col_map)
    # Add missing columns
    header_list = ['account_id', 'accounting_no', 'ignore',
        'text', 'value_date', 'posting_date', 'billing_date', 'amount', 'currency',
        'subject', 'line_id', 'comment', 'accounting_date', 'contra_name', 'contra_iban', 'contra_bic', 'import_preset']
    data = data.reindex(columns = header_list)

    data.to_csv(path_or_buf=output_file, index=False, date_format='%d.%m.%Y', sep=',', decimal='.', quotechar='"', encoding='utf-8')


def clean_from_preset(input_file, output_file, preset):
    current_preset = presets[preset]
    print( 'Using preset {}'.format( current_preset['preset_name'] ) )
    clean_csv(input_file, output_file, **current_preset)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file')
    parser.add_argument('output_file')
    parser.add_argument('--preset', default='psk')
    args = parser.parse_args()
    clean_from_preset(args.input_file, args.output_file, args.preset)


if __name__ == '__main__':
    main()
