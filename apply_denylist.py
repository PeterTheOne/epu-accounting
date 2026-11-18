import argparse
import os.path
import re
import pandas as pd

import clean_csv
import presets
from functions_data import get_date_cols, get_record_subject


def print_records(title, records):
    if records.empty:
        return
    print('{} ({}):'.format(title, len(records.index)))
    for _, row in records.iterrows():
        print('  {:>8}  {:10.10}  {:18.18}  {:28.28}'.format(row['amount'], str(row['value_date']), str(row['contra_name']), get_record_subject(row)))
    print()


def apply_denylist(input_file, denylist_file, output_file, preset_key=None, drop_empty=False, allowlist_text=None, denylist_column='contra_iban', csv_date_format='%d.%m.%Y', csv_delimiter=',', csv_quotechar='"', csv_encoding='utf-8'):
    if not os.path.isfile(input_file):
        print('Error: File "{0}" doesn\'t exist.'.format(input_file))
        return
    if not os.path.isfile(denylist_file):
        print('Error: File "{0}" doesn\'t exist.'.format(denylist_file))
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

    denylist = pd.read_csv(filepath_or_buffer=denylist_file, delimiter=csv_delimiter, quotechar=csv_quotechar, encoding=csv_encoding)

    # lines whose subject contains a allowlisted keyword are always kept
    keywords = [k.strip() for k in (allowlist_text or '').split(',') if k.strip()]
    if keywords:
        pattern = '|'.join(re.escape(k) for k in keywords)
        allowlisted = data['subject'].astype(str).str.contains(pattern, case=False, regex=True, na=False)
    else:
        allowlisted = pd.Series(False, index=data.index)

    denylisted = data[denylist_column].isin(denylist[denylist_column])

    if drop_empty:
        empty = data['contra_iban'].isnull() | (data['contra_iban'].astype(str).str.strip() == '')
    else:
        empty = pd.Series(False, index=data.index)

    drop = denylisted | empty

    # log removed records grouped by reason (denylist takes precedence over empty contra_iban)
    print_records('Removed: {} in denylist'.format(denylist_column), data[denylisted & ~allowlisted])
    print_records('Removed: empty contra_iban', data[empty & ~denylisted & ~allowlisted])
    print_records('Kept: allowlisted', data[drop & allowlisted])

    data = data[~drop | allowlisted]

    data.to_csv(path_or_buf=output_file, index=False,
                sep=csv_delimiter, quotechar=csv_quotechar, encoding=csv_encoding,
                date_format=csv_date_format)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file')
    parser.add_argument('denylist_file')
    parser.add_argument('output_file')
    parser.add_argument('--preset', choices=list(presets.PRESETS.keys()),
                        help='parse input_file as a raw statement using this preset (otherwise input_file must already be cleaned)')
    parser.add_argument('--drop_empty', action='store_true',
                        help='also filter out lines with an empty contra_iban')
    parser.add_argument('--allowlist_text',
                        help='comma separated keywords; lines whose subject contains any of them (case-insensitive) are always kept')
    #parser.add_argument('--denylist_column')
    args = parser.parse_args()
    apply_denylist(args.input_file, args.denylist_file, args.output_file, args.preset, args.drop_empty, args.allowlist_text)


if __name__ == '__main__':
    main()
