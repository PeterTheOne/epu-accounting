import argparse
import os.path
import pandas as pd


def contra_histogram(data):
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

    def ngram_string_list_combined(data, start=1, end=5):
        def ngram_string_list(data, n=2):
            def find_ngrams(input_list, n=2):
                return list(zip(*[input_list[i:] for i in range(n)]))

            text_clean = data['text_clean'].tolist()
            l = list(map(lambda x: find_ngrams(x.split(" "), n), text_clean))
            flat_l = [item for sublist in l for item in sublist]
            return list(map(lambda x: ' '.join(x), flat_l))

        strings = []
        for n in range(start, end + 1):
            for i in range(n):
                strings.extend(ngram_string_list(data, n))
                #print('n: {}, i: {}'.format(n, i))
        return strings

    ngram_strings = ngram_string_list_combined(data, 1, 5)
    #print(ngram_strings)
    hist = pd.DataFrame(data={'text': ngram_strings})
    hist = hist.groupby(['text']).size().to_frame('weight').sort_values(['weight'], ascending=[False])
    print(hist)

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
                date_format=csv_date_format, index_label=['first', 'second', 'count'])


if __name__ == '__main__':
    main()
