import argparse
import os.path
import pandas as pd


def timesplit_csv(input, output='.'):
    if not os.path.isfile(input):
        print('Error: File "{0}" don\'t exist.'.format(input))
        return
    if not os.path.exists(output):
        print('Error: No such directory "{0}".'.format(output))
        return
    csv_date_format = '%d.%m.%Y'
    csv_delimiter = ';'
    csv_quotechar = '"'
    csv_encoding = 'ISO/-8859-1'
    date_parser = lambda x: pd.datetime.strptime(x, csv_date_format)
    amount_parser = lambda x: float(x.replace('.', '').replace(',', '.'))
    data = pd.read_csv(filepath_or_buffer=input, delimiter=csv_delimiter, quotechar=csv_quotechar, encoding=csv_encoding, header=None,
                       names=['iban', 'text', 'value_date', 'posting_date', 'amount', 'currency'],
                       parse_dates=['value_date', 'posting_date'], date_parser=date_parser,
                       converters={'amount': amount_parser})
    #todo: split by value_date or posting_date?
    date_column = 'value_date'
    data['year'] = data[date_column].dt.year
    data['quarter'] = data[date_column].dt.quarter

    for year in data['year'].unique():
        data_year = data.loc[data['year'] == year]
        for quarter in data_year['quarter'].unique():
            data_quarter = data_year.loc[data['quarter'] == quarter].drop(['year', 'quarter'], axis=1)
            data_quarter.to_csv(path_or_buf='{0}/{1}-{2}.csv'.format(output, year, quarter), index=False,
                                sep=csv_delimiter, quotechar=csv_quotechar, encoding=csv_encoding,
                                date_format=csv_date_format)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input')
    parser.add_argument('output', nargs='?', default=os.getcwd())
    #todo:
    #csv_delimiter
    #csv_quotechar
    #csv_encoding
    #timeframe
    args = parser.parse_args()
    timesplit_csv(args.input, args.output)


if __name__ == '__main__':
    main()
