from PyInquirer import prompt
import re
import pandas as pd

import presets

def get_date_cols():
    return ['value_date', 'posting_date', 'billing_date', 'accounting_date']

def choose_preset(filename):
    choices_objects = map(lambda c: {'name': c}, presets.PRESETS.keys())
    answers = prompt([
        {
            'type': 'list',
            'name': 'preset',
            'message': 'Which preset do you want to use to parse {}?'.format(filename),
            'choices': choices_objects
        }
    ])

    return answers['preset']

def get_record_subject(row):
    record_subject = ''

    if pd.notnull(row['subject']):
        record_subject = row['subject']
    elif pd.notnull(row['comment']):
        record_subject = row['comment']
    elif pd.notnull(row['text']):
        record_subject = row['text']

    return str(record_subject)


def print_records(title, records):
    if records.empty:
        return
    print('{} ({}):'.format(title, len(records.index)))
    for _, row in records.iterrows():
        print('  {:>8}  {:10.10}  {:18.18}  {:28.28}'.format(row['amount'], str(row['value_date']), str(row['contra_name']), get_record_subject(row)))
    print()


def normalize_values(values, column):
    # Compare case-insensitively and ignore surrounding whitespace; IBAN/BIC are
    # often written in groups ("AT12 3456 ..."), so drop inner whitespace too
    values = values.astype('string').str.strip().str.upper()
    if 'iban' in column or 'bic' in column:
        values = values.str.replace(r'\s+', '', regex=True)
    return values


def match_list(data, list_data, column, list_file):
    # Boolean mask of records whose column value is in list_data (allowlist/denylist).
    # Empty list entries are ignored, so they never match records with an empty value.
    # Returns None (after printing an error) if the column is missing.
    for name, df in (('the records', data), ('list file "{}"'.format(list_file), list_data)):
        if column not in df.columns:
            print('Error: Column "{0}" not found in {1} (columns: {2}).'.format(column, name, ', '.join(df.columns)))
            return None
    list_values = normalize_values(list_data[column], column).replace('', pd.NA).dropna()
    return normalize_values(data[column], column).isin(list_values).fillna(False).astype(bool)


def match_text_keywords(data, keywords, columns=('subject', 'comment', 'text')):
    # Boolean mask of records where any of the text columns contains any keyword
    # (case-insensitive). Empty values never match.
    mask = pd.Series(False, index=data.index)
    if not keywords:
        return mask
    pattern = '|'.join(re.escape(k) for k in keywords)
    for column in columns:
        if column in data.columns:
            mask |= data[column].fillna('').astype(str).str.contains(pattern, case=False, regex=True)
    return mask
