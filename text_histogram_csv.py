import argparse
import os.path
import pandas as pd


def contra_histogram(input_file, output_file, csv_date_format='%d.%m.%Y', csv_delimiter=',', csv_quotechar='"', csv_encoding='utf-8'):
    if not os.path.isfile(input_file):
        print('Error: File "{0}" don\'t exist.'.format(input_file))
        return
    date_parser = lambda x: pd.datetime.strptime(x, csv_date_format)
    data = pd.read_csv(filepath_or_buffer=input_file, delimiter=csv_delimiter, quotechar=csv_quotechar, encoding=csv_encoding,
                       parse_dates=['value_date', 'posting_date'], date_parser=date_parser)

    pd.set_option('max_colwidth', 800)
    line_id_regex = '([A-Z]{2}/\d{9})'
    iban_regex = ' ([A-Z]{2}\d{14,20}) '
    old_account_regex = ' (\d{11})'
    bic_regex = ' (([a-zA-Z]){4}([a-zA-Z]){2}([0-9a-zA-Z]){2}([0-9a-zA-Z]{3})?)'
    blz_regex = ' (\d{5})'
    date_regex = ' (\d{2}\.\d{2}\.(\d{4})?) '

    data['text_clean'] = data['text'].str.split(iban_regex, expand=True)[0]
    data['text_clean'] = data['text_clean'].str.replace(line_id_regex, '').str.replace(iban_regex, '') \
        .str.replace(old_account_regex, '').str.replace(bic_regex, '').str.replace(blz_regex, '') \
        .str.replace(date_regex, '').replace('\s+', ' ', regex=True).str.strip()

    def find_ngrams(input_list, n=2):
        return list(zip(*[input_list[i:] for i in range(n)]))

    data['bigrams'] = data['text_clean'].map(lambda x: find_ngrams(x.split(" "), 2))
    #print(data['bigrams'])
    bigrams = pd.DataFrame(data['bigrams'].sum())
    hist = bigrams.groupby([0, 1]).size().to_frame('count').sort_values(['count'], ascending=[False])
    hist.reset_index(level=hist.index.names, inplace=True)
    hist['text'] = hist[0].astype(str) + ' ' + hist[1]
    hist = hist[['text', 'count']]
    #print(hist)

    hist.to_csv(path_or_buf=output_file, index=False,
                sep=csv_delimiter, quotechar=csv_quotechar, encoding=csv_encoding,
                date_format=csv_date_format, index_label=['first', 'second', 'count'])



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file')
    parser.add_argument('output_file')
    args = parser.parse_args()
    contra_histogram(args.input_file, args.output_file)


if __name__ == '__main__':
    main()
