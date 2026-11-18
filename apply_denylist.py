import argparse
import os.path
import pandas as pd

import clean_csv
import presets
from functions_data import get_date_cols, print_records, match_list, match_text_keywords, read_csv_dates


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
        data = read_csv_dates(get_date_cols(), csv_date_format, filepath_or_buffer=input_file, delimiter=csv_delimiter, quotechar=csv_quotechar, encoding=csv_encoding)

    denylist = pd.read_csv(filepath_or_buffer=denylist_file, delimiter=csv_delimiter, quotechar=csv_quotechar, encoding=csv_encoding)

    denylisted = match_list(data, denylist, denylist_column, denylist_file)
    if denylisted is None:
        return

    # lines whose subject/comment/text contains a allowlisted keyword are always kept
    keywords = [k.strip() for k in (allowlist_text or '').split(',') if k.strip()]
    allowlisted = match_text_keywords(data, keywords)

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
                        help='comma separated keywords; lines whose subject, comment or text contains any of them (case-insensitive) are always kept')
    parser.add_argument('--denylist_column', default='contra_iban',
                        help='column to match between input_file and denylist_file (default: contra_iban)')
    args = parser.parse_args()
    apply_denylist(args.input_file, args.denylist_file, args.output_file, args.preset, args.drop_empty, args.allowlist_text, args.denylist_column)


if __name__ == '__main__':
    main()
