import argparse
import os.path
import pandas as pd
import locale

import constants
import presets


def extract_psk(data):
    line_id_regex = '([A-Z]{2}/\d{9})'
    iban_regex = '([A-Z]{2}[\d]{2}[A-Z\d]{12,18})'
    first_two_words_regex = '([\w\.]+ [\w\.]+)'
    word_regex = '([a-zA-Z_]{3,})'

    data['line_id'] = data['text'].str.extract('(.*) ' + line_id_regex, expand=True)[1]
    data['comment'] = data['text'].str.extract('(.*) ' + line_id_regex, expand=True)[0].str.strip()
    data['contra_iban'] = data['text'].str.extract(iban_regex + ' (.*)', expand=True)[0]
    data['contra_bic'] = data['text'].str.extract(line_id_regex + ' (.*) ' + iban_regex, expand=True)[1]
    data['contra_name'] = data['text'].str.extract(iban_regex + ' (.*)', expand=True)[1]
    # if nothing matched (no IBAN), try alternative pattern
    data.loc[data['contra_name'].isnull(), 'contra_name'] = data['text'].str.extract(first_two_words_regex + ' (.*) ' + line_id_regex, expand=True)[0]
    # if comment is same as contra_name, get more info
    data.loc[data['comment'] == data['contra_name'], 'comment'] = data['text'].str.findall(word_regex).apply(' '.join)
    return data


def extract_paypal(data):
    # Filter redundant rows
    data.insert(0, 'status', 0)
    data.loc[data['Typ'] == 'Bankgutschrift auf PayPal-Konto', 'status'] = constants.STATUS_IGNORE
    data.loc[data['Währung'] != 'EUR', 'status'] = constants.STATUS_IGNORE

    # Find parent transaction to get missing data (Name)
    data = pd.merge(data, data[['Transaktionscode', 'Name']], how='left', left_on=['Zugehöriger Transaktionscode'], right_on=['Transaktionscode'])
    
    # Set missing data
    data['Name_x'] = data['Name_x'].fillna(data['Name_y'])
    data.rename(index=str, columns={"Name_x": "Name"}, inplace=True)
    
    # Clean up unneeded columns
    data.drop(columns=['Name_y', 'Typ', 'Zugehöriger Transaktionscode', 'Transaktionscode_x', 'Transaktionscode_y'], inplace=True)
    return data


def clean_csv(input_file, output_file, preset_key='', preset_name='', date_format='%d.%m.%Y', delimiter=';', quotechar='"', encoding='ISO/-8859-1', decimal=',', thousands='.', col_names=None, usecols=[], col_map=[], date_cols=[]):
    locale.setlocale(locale.LC_NUMERIC, '')
    date_parser = lambda x: pd.to_datetime(x, format=date_format, errors='coerce')
    data = pd.read_csv(filepath_or_buffer=input_file, delimiter=delimiter,
                       quotechar=quotechar, encoding=encoding, header=0,
                       decimal=decimal, thousands=thousands,
                       names=col_names, usecols=usecols,
                       parse_dates=date_cols, date_parser=date_parser)

    if preset_key == 'paypal':
        data = extract_paypal(data)

    # Add columns
    data['import_preset'] = preset_key # todo: default value

    # Reformat columns # todo: broken?
    if col_map:
        data = data.rename(index=str, columns=col_map)
    # Add missing columns
    header_list = ['account_id', 'accounting_no', 'status',
        'text', 'value_date', 'posting_date', 'billing_date', 'amount', 'currency',
        'subject', 'line_id', 'comment', 'accounting_date', 'contra_name', 'contra_iban', 'contra_bic', 'import_preset', 'account']
    data = data.reindex(columns=header_list)

    if preset_key == 'psk':
        data = extract_psk(data)

    if output_file:
        data.to_csv(path_or_buf=output_file, index=False, date_format='%d.%m.%Y', sep=',', decimal='.', quotechar='"', encoding='utf-8')
    return data


# todo: detect preset if not set
def clean_from_preset(input_file, output_file, preset):
    current_preset = presets.PRESETS[preset]
    print( 'Using preset {}'.format( current_preset['preset_name'] ) )
    return clean_csv(input_file, output_file, preset, **current_preset)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file')
    parser.add_argument('output_file')
    parser.add_argument('preset')
    args = parser.parse_args()
    if not os.path.isfile(args.input_file):
        print('Error: File "{0}" don\'t exist.'.format(args.input_file))
        return
    clean_from_preset(args.input_file, args.output_file, args.preset)


if __name__ == '__main__':
    main()
