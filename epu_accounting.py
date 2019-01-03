import os
import re
from PyInquirer import prompt
from PyInquirer import Validator, ValidationError
import clean_csv
import extract_csv
import contra_histogram_csv
import text_histogram_csv


class CsvFolderValidator(Validator):
    def validate(self, document):
        if not os.path.isdir(document.text):
            raise ValidationError(
                message='Please enter a valid folder path.',
                cursor_position=len(document.text))
        files = os.listdir(document.text)
        files = list(filter(lambda x: x.endswith('.csv'), files))
        if len(files) == 0:
            raise ValidationError(
                message='Please enter folder path with csv files.',
                cursor_position=len(document.text))


questions = [
    {
        'type': 'input',
        'name': 'input_path',
        'default': 'input',
        'message': 'Enter folder path with *.csv input files.',
        'validate': CsvFolderValidator
    }
]


def classify_account(data, min_count=5, min_weight=2.5):
    # generate histograms
    hist = contra_histogram_csv.contra_histogram(data)
    hist = hist[hist['count'] >= min_count]
    hist = hist[hist['weight'] >= min_weight]
    hist = hist[:20]
    hist['string'] = hist['contra_iban'].str.cat(hist['contra_name'], sep=' ')
    choices = hist['string'].tolist()

    text_hist = text_histogram_csv.contra_histogram(data)
    text_hist = text_hist[:20]
    text_choices = text_hist.index.values
    #print(text_choices)

    # get user input
    choices_objects = map(lambda c: {'name': c}, choices)
    answers = prompt([
        {
            'type': 'checkbox',
            'name': 'company_ibans',
            'message': 'Mark company related contra_ibans, others are marked private.',
            'choices': choices_objects
        }
    ])
    company_ibans = answers['company_ibans']


    choices_objects = map(lambda c: {'name': c}, text_choices)
    answers = prompt([
        {
            'type': 'checkbox',
            'name': 'private_texts',
            'message': 'Mark private related texts.',
            'choices': choices_objects
        }
    ])
    private_texts = answers['private_texts']

    text_choices = filter(lambda t: t not in private_texts, text_choices)
    choices_objects = map(lambda c: {'name': c}, text_choices)
    answers = prompt([
        {
            'type': 'checkbox',
            'name': 'company_texts',
            'message': 'Mark company related texts.',
            'choices': choices_objects
        }
    ])
    company_texts = answers['company_texts']

    # filter based on user input
    private_ibans = list(filter(lambda c: c not in company_ibans, choices))

    company_ibans = list(map(lambda c: c.split(' ', 1)[0], company_ibans))
    private_ibans = list(map(lambda c: c.split(' ', 1)[0], private_ibans))

    #print(list(company_ibans))
    #print(list(private_ibans))

    data.loc[data['contra_iban'].isin(company_ibans), 'account'] = 'company'
    data.loc[data['contra_iban'].isin(private_ibans), 'account'] = 'private'

    private_texts = list(map(lambda x: re.escape(x), private_texts))
    company_texts = list(map(lambda x: re.escape(x), company_texts))

    if len(private_texts) > 0:
        data.loc[data['text'].str.contains('|'.join(private_texts)), 'account'] = 'private'
    if len(company_texts) > 0:
        data.loc[data['text'].str.contains('|'.join(company_texts)), 'account'] = 'company'

    return data


def main():
    answers = prompt(questions)
    input_path = answers['input_path']
    files = os.listdir(input_path)
    files = filter(lambda f: f.endswith('.csv'), files)
    files = map(lambda f: input_path + os.sep + f, files)

    # clean
    files = map(lambda f: clean_csv.clean_from_preset(f, None, 'psk'), files)
    #print(list(files))

    # extract
    files = map(lambda f: extract_csv.extract_csv(f), files)
    #print(list(files))

    # filter private/company
    # todo: ask if one wants to even filter..
    # todo: ask how many lines the user wants to classify
    # todo: save and load user classifications
    files = map(lambda f: classify_account(f), files)
    files = list(files)
    print(files[0][['text', 'account']])
    print(files[0][:365]['account'].value_counts())

    # setup db etc.


if __name__ == '__main__':
    main()
