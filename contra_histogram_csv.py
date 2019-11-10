import argparse
import os.path
import pandas as pd
import datetime


def calc_weight(date):
    # todo: don't use today but last data in dataset or data of interesting period
    today = datetime.datetime.today()
    diff = today - date
    period = 1095
    weight = (period - diff.days) / period
    if weight < 0:
        return 0
    return weight


def contra_histogram(data):
    data['weight'] = data['value_date'].apply(calc_weight)
    data['count'] = 1
    hist = data[['contra_iban', 'count', 'weight']].groupby(['contra_iban']).sum().sort_values(['weight', 'contra_iban'], ascending=[False, True])
    hist = pd.merge(hist, data[['contra_iban', 'contra_name']], how='inner', on=['contra_iban']).drop_duplicates(subset='contra_iban')
    return hist


def main(csv_date_format='%d.%m.%Y', csv_delimiter=',', csv_quotechar='"', csv_encoding='utf-8'):
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file')
    parser.add_argument('output_file')
    args = parser.parse_args()

    if not os.path.isfile(args.input_file):
        print('Error: File "{0}" don\'t exist.'.format(args.input_file))
        return
    date_parser = lambda x: pd.datetime.strptime(x, csv_date_format)
    data = pd.read_csv(filepath_or_buffer=args.input_file, delimiter=csv_delimiter, quotechar=csv_quotechar, encoding=csv_encoding,
                       parse_dates=['value_date', 'posting_date'], date_parser=date_parser)
    hist = contra_histogram(data)
    hist.to_csv(path_or_buf=args.output_file, index=False,
                sep=csv_delimiter, quotechar=csv_quotechar, encoding=csv_encoding,
                date_format=csv_date_format)


if __name__ == '__main__':
    main()
