import argparse
import os.path
import pandas as pd


def negative_rolling_sum(input_file, output_file, whitelist_column='contra_iban', csv_date_format='%d.%m.%Y', csv_delimiter=',', csv_quotechar='"', csv_encoding='utf-8'):
    if not os.path.isfile(input_file):
        print('Error: File "{0}" don\'t exist.'.format(input_file))
        return
    date_parser = lambda x: pd.datetime.strptime(x, csv_date_format)
    data = pd.read_csv(filepath_or_buffer=input_file, delimiter=csv_delimiter, quotechar=csv_quotechar, encoding=csv_encoding,
                       parse_dates=['value_date', 'posting_date'], date_parser=date_parser)



    data = data[['posting_date', 'amount']].set_index('posting_date')
    data = data[data['amount'] < 0]
    data = data.resample("1d").sum().fillna(0)
    data = data.rolling(center=False, window=30).sum()
    #print(data)

    data.to_csv(path_or_buf=output_file, index=True,
                sep=csv_delimiter, quotechar=csv_quotechar, encoding=csv_encoding,
                date_format=csv_date_format)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file')
    parser.add_argument('output_file')
    #parser.add_argument('--whitelist_column')
    args = parser.parse_args()
    negative_rolling_sum(args.input_file, args.output_file)


if __name__ == '__main__':
    main()
