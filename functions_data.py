from PyInquirer import prompt
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
