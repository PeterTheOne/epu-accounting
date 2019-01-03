import argparse
import os.path
import pandas as pd

from functions_data import *


def extract_csv(data):
    line_id_regex = '([A-Z]{2}/\d{9})'
    iban_regex = '([A-Z]{2}[\d]{2}[A-Z\d]{12,18})'
    first_two_words_regex = '([\w\.]+ [\w\.]+)'
    word_regex = '([a-zA-Z_]{3,})'

    data['line_id'] = data['text'].str.extract('(.*) ' + line_id_regex, expand=True)[1]
    data['comment'] = data['text'].str.extract('(.*) ' + line_id_regex, expand=True)[0].str.strip()
    data['contra_iban'] = data['text'].str.extract(iban_regex + ' (.*)', expand=True)[0]
    data['contra_bic'] = data['text'].str.extract(line_id_regex + ' (.*) ' + iban_regex, expand=True)[1]
    data['contra_name'] = data['text'].str.extract(iban_regex + ' (.*)', expand=True)[1]
    # if nothing matched (no IBAN), try alternative pattern
    data.loc[data['contra_name'].isnull(), 'contra_name'] = data['text'].str.extract(first_two_words_regex + ' (.*) ' + line_id_regex, expand=True)[0]
    # if comment is same as contra_name, get more info
    data.loc[data['comment'] == data['contra_name'], 'comment'] = data['text'].str.findall(word_regex).apply(' '.join)
    return data


def main(csv_date_format='%d.%m.%Y', csv_delimiter=',', csv_quotechar='"', csv_encoding='utf-8'):
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file')
    parser.add_argument('output_file')
    args = parser.parse_args()

    if not os.path.isfile(args.input_file):
        print('Error: File "{0}" don\'t exist.'.format(args.input_file))
        return
    date_parser = lambda x: pd.to_datetime(x, format=csv_date_format, errors='coerce')
    data = pd.read_csv(filepath_or_buffer=args.input_file, delimiter=csv_delimiter, quotechar=csv_quotechar, encoding=csv_encoding,
                       parse_dates=get_date_cols(), date_parser=date_parser)

    data = extract_csv(data, args.output_file)

    data.to_csv(path_or_buf=args.output_file, index=False,
                sep=csv_delimiter, quotechar=csv_quotechar, encoding=csv_encoding,
                date_format=csv_date_format)


if __name__ == '__main__':
    main()
