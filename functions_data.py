from PyInquirer import prompt

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
