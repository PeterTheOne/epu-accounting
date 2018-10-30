import argparse
import os.path
import pandas as pd


def sum_by_contra(input_file, output_file, csv_date_format='%d.%m.%Y', csv_delimiter=',', csv_quotechar='"', csv_encoding='utf-8'):
    if not os.path.isfile(input_file):
        print('Error: File "{0}" don\'t exist.'.format(input_file))
        return
    date_parser = lambda x: pd.datetime.strptime(x, csv_date_format)
    data = pd.read_csv(filepath_or_buffer=input_file, delimiter=csv_delimiter, quotechar=csv_quotechar, encoding=csv_encoding,
                       parse_dates=['value_date', 'posting_date'], date_parser=date_parser)

    data = data[(data['amount'] < 0)] # use negative amounts only, todo: make it an option

    hist = data.groupby(['contra_name'])['amount'].agg('sum').to_frame('sum').sort_values(['sum', 'contra_name'], ascending=[True, True])
    hist = pd.merge(hist, data[['contra_iban', 'contra_name']], how='inner', on=['contra_name']).drop_duplicates(subset='contra_name')

    #print(hist)
    # find what amount is not included because of skipped lines (empty contra_name)?
    total = data['amount'].sum()
    totalGrouped = hist['sum'].sum()
    totalDelta = total - totalGrouped
    print("Sum was {} lower than expected: {}, instead got: {}".format(totalDelta, total, totalGrouped))

    hist.to_csv(path_or_buf=output_file, index=False,
                sep=csv_delimiter, quotechar=csv_quotechar, encoding=csv_encoding,
                date_format=csv_date_format)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file')
    parser.add_argument('output_file')
    args = parser.parse_args()
    sum_by_contra(args.input_file, args.output_file)


if __name__ == '__main__':
    main()
