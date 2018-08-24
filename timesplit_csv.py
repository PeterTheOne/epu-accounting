import argparse
import os.path
import pandas as pd


def timesplit_csv(input_file, output_path='.', csv_date_format='%d.%m.%Y', csv_delimiter=',', csv_quotechar='"', csv_encoding='utf-8'):
    if not os.path.isfile(input_file):
        print('Error: File "{0}" don\'t exist.'.format(input_file))
        return
    if not os.path.exists(output_path):
        print('Error: No such directory "{0}".'.format(output_path))
        return
    date_parser = lambda x: pd.datetime.strptime(x, csv_date_format)
    data = pd.read_csv(filepath_or_buffer=input_file, delimiter=csv_delimiter, quotechar=csv_quotechar, encoding=csv_encoding,
                       parse_dates=['value_date', 'posting_date'], date_parser=date_parser)
    #todo: split by value_date or posting_date?
    date_column = 'value_date'
    data['year'] = data[date_column].dt.year
    data['quarter'] = data[date_column].dt.quarter

    for year in data['year'].unique():
        data_year = data.loc[data['year'] == year]
        for quarter in data_year['quarter'].unique():
            data_quarter = data_year.loc[data['quarter'] == quarter].drop(['year', 'quarter'], axis=1)
            data_quarter.to_csv(path_or_buf='{0}/{1}-{2}.csv'.format(output_path, year, quarter), index=False,
                                sep=csv_delimiter, quotechar=csv_quotechar, encoding=csv_encoding,
                                date_format=csv_date_format)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file')
    parser.add_argument('output_path', nargs='?', default=os.getcwd())
    #todo:
    #csv_delimiter
    #csv_quotechar
    #csv_encoding
    #timeframe
    args = parser.parse_args()
    timesplit_csv(args.input_file, args.output_path)


if __name__ == '__main__':
    main()
