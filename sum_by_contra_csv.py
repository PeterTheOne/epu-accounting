import argparse
import os.path
import pandas as pd


def sum_by_contra(input_file, output_file, negative, division, contra_name, csv_date_format='%d.%m.%Y', csv_delimiter=',', csv_quotechar='"', csv_encoding='utf-8'):
    if not os.path.isfile(input_file):
        print('Error: File "{0}" don\'t exist.'.format(input_file))
        return

    data = pd.read_csv(filepath_or_buffer=input_file, delimiter=csv_delimiter, quotechar=csv_quotechar, encoding=csv_encoding)
    groupby_col = 'comment' if contra_name else 'contra_name'

    if negative:
        data = data[(data['amount'] < 0)] # use negative amounts only
    else:
        data = data[(data['amount'] > 0)] # use positive amounts only

    if contra_name:
        data = data[(data['contra_name'] == contra_name)] # data subset

    hist = data.groupby([groupby_col])['amount'].agg('sum').to_frame('sum').sort_values(['sum', groupby_col], ascending=[True, True])

    if division > 0:
        hist['sum_divided'] = hist['sum'].apply(lambda x: x/division)
    
    hist = pd.merge(hist, data[['contra_iban', groupby_col, 'subject']], how='inner', on=[groupby_col]).drop_duplicates(subset=groupby_col)

    #print(hist)
    # find what amount is not included because of skipped lines (empty contra_name)?
    total = data['amount'].sum()
    totalGrouped = hist['sum'].sum()
    totalDelta = total - totalGrouped
    if abs(totalDelta) >= 1:
        print("Sum was {} lower than expected: {}, instead got: {}".format(totalDelta, total, totalGrouped))

    hist.to_csv(path_or_buf=output_file, index=False,
                sep=csv_delimiter, quotechar=csv_quotechar, encoding=csv_encoding,
                date_format=csv_date_format)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file')
    parser.add_argument('output_file')
    parser.add_argument("--negative", help="process negative amounts only", action="store_true")
    parser.add_argument("--division", help="divide sums by some value", type=int)
    parser.add_argument("--contra_name", help="search within comment of lines with specified contra_name")
    args = parser.parse_args()
    sum_by_contra(args.input_file, args.output_file, args.negative, args.division, args.contra_name)


if __name__ == '__main__':
    main()
