import argparse
import os.path
import pandas as pd


def clean_csv(input_file, output_file, csv_date_format='%d.%m.%Y', csv_delimiter=';', csv_quotechar='"', csv_encoding='ISO/-8859-1'):
    if not os.path.isfile(input_file):
        print('Error: File "{0}" don\'t exist.'.format(input_file))
        return
    date_parser = lambda x: pd.datetime.strptime(x, csv_date_format)
    amount_parser = lambda x: float(x.replace('.', '').replace(',', '.'))
    data = pd.read_csv(filepath_or_buffer=input_file, delimiter=csv_delimiter, quotechar=csv_quotechar, encoding=csv_encoding, header=None,
                       names=['iban', 'text', 'value_date', 'posting_date', 'amount', 'currency'],
                       parse_dates=['value_date', 'posting_date'], date_parser=date_parser,
                       converters={'amount': amount_parser})
    data.to_csv(path_or_buf=output_file, index=False, date_format=csv_date_format, encoding='utf-8')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file')
    parser.add_argument('output_file')
    args = parser.parse_args()
    clean_csv(args.input_file, args.output_file)


if __name__ == '__main__':
    main()
