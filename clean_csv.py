import argparse
import os.path
import pandas as pd
import locale

import constants
import presets


def extract_n26(data):
    # Filter redundant rows
    data.loc[data['contra_iban'].isnull(), 'status'] = constants.STATUS_IGNORE # Moving to/from Space
    return data


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


def extract_paypal(data, lang):
    # DE / EN language support
    field_name = 'Name'
    if lang == 'de':
        field_type = 'Typ'
        field_currency = 'Währung'
        field_transaction_id = 'Transaktionscode'
        field_transaction_ref = 'Zugehöriger Transaktionscode'
        value_bank_transaction = 'Bankgutschrift auf PayPal-Konto'
    else:
        field_type = 'Type'
        field_currency = 'Currency'
        field_transaction_id = 'Transaction ID'
        field_transaction_ref = 'Reference Txn ID'
        value_bank_transaction = 'Bank Deposit to PP Account '
    field_name_x = ''.join((field_name, '_x'))
    field_name_y = ''.join((field_name, '_y'))
    field_transaction_id_x = ''.join((field_transaction_id, '_y'))
    field_transaction_id_y = ''.join((field_transaction_id, '_y'))

    # Filter redundant rows
    data.loc[data[field_type] == value_bank_transaction, 'status'] = constants.STATUS_IGNORE
    data.loc[data[field_currency] != 'EUR', 'status'] = constants.STATUS_IGNORE

    # Find parent transaction to get missing data (Name)
    data = pd.merge(data, data[[field_transaction_id, field_name]], how='left', left_on=[field_transaction_ref], right_on=[field_transaction_id])

    # Set missing data
    data[field_name_x] = data[field_name_x].fillna(data[field_name_y])
    data.rename(index=str, columns={field_name_x: field_name}, inplace=True)

    # Clean up unneeded columns
    data.drop(columns=[field_name_y, field_type, field_transaction_ref, field_transaction_id_x, field_transaction_id_y], inplace=True)

    return data


def clean_csv(input_file, output_file, preset_key='', preset_name='', date_format='%d.%m.%Y', delimiter=';', quotechar='"', encoding='ISO/-8859-1', decimal=',', thousands='.', col_names=None, usecols=[], col_map=[], date_cols=[]):
    locale.setlocale(locale.LC_NUMERIC, '')
    date_parser = lambda x: pd.to_datetime(x, format=date_format, errors='coerce')
    data = pd.read_csv(filepath_or_buffer=input_file, delimiter=delimiter,
                       quotechar=quotechar, encoding=encoding, header=0,
                       decimal=decimal, thousands=thousands,
                       names=col_names, usecols=usecols,
                       parse_dates=date_cols, date_parser=date_parser)

    # Set default values for new columns
    data.insert(0, 'status', 0)
    data.insert(0, 'accounting_no', 0)

    if preset_key.startswith( 'paypal' ):
        data = extract_paypal( data, preset_key[7:9] )

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

    if preset_key == 'n26':
        data = extract_n26(data)

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
