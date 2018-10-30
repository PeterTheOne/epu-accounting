import argparse
import os.path
import pandas as pd


def extract_csv(input_file, output_file, csv_date_format='%d.%m.%Y', csv_delimiter=',', csv_quotechar='"', csv_encoding='utf-8'):
    if not os.path.isfile(input_file):
        print('Error: File "{0}" don\'t exist.'.format(input_file))
        return
    date_parser = lambda x: pd.datetime.strptime(x, csv_date_format)
    data = pd.read_csv(filepath_or_buffer=input_file, delimiter=csv_delimiter, quotechar=csv_quotechar, encoding=csv_encoding,
                       parse_dates=['value_date', 'posting_date'], date_parser=date_parser)

    line_id_regex = '([A-Z]{2}/\d{9})'
    iban_regex = '([A-Z]{2}[A-Z\d]{14,20})'
    first_two_words_regex = '([\w\.]+ [\w\.]+)'

    data['line_id'] = data['text'].str.extract('(.*) ' + line_id_regex, expand=True)[1]
    data['comment'] = data['text'].str.extract('(.*) ' + line_id_regex, expand=True)[0].str.strip()
    data['contra_iban'] = data['text'].str.extract(iban_regex + ' (.*)', expand=True)[0]
    data['contra_bic'] = data['text'].str.extract(line_id_regex + ' (.*) ' + iban_regex, expand=True)[1]
    data['contra_name'] = data['text'].str.extract(iban_regex + ' (.*)', expand=True)[1]
    # if nothing matched (no IBAN), try alternative pattern
    data.loc[data['contra_name'].isnull(),'contra_name'] = data['text'].str.extract(first_two_words_regex + ' (.*) ' + line_id_regex, expand=True)[0]
    data.to_csv(path_or_buf=output_file, index=False,
                sep=csv_delimiter, quotechar=csv_quotechar, encoding=csv_encoding,
                date_format=csv_date_format)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file')
    parser.add_argument('output_file')
    args = parser.parse_args()
    extract_csv(args.input_file, args.output_file)


if __name__ == '__main__':
    main()
