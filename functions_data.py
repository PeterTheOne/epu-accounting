presets = {
    'psk': {
        'preset_name': 'BAWAG P.S.K.',
        'encoding':    'ISO/-8859-1',
        'date_format': '%d.%m.%Y',
        'delimiter':   ';',
        'quotechar':   '"',
        'decimal':     ',',
        'thousands':   '.',
        'col_names':   ['iban', 'text', 'value_date', 'posting_date', 'amount', 'currency'], # add missing column names
        'usecols':     None,
        'col_map':     [],
        'date_cols':   ['value_date', 'posting_date']
    },
    'paylife': {
        # todo: select correct 'Währung' column
        'preset_name': 'PayLife',
        'encoding':    'utf-8',
        'date_format': '%d.%m.%Y',
        'delimiter':   ';',
        'quotechar':   '"',
        'decimal':     ',',
        'thousands':   '.',
        'col_names':   None, # column names already present
        'usecols':     ['Buchungsdatum', 'Transaktionsdatum', 'Abrechnungsdatum', 'Rechnungstext', 'Währung', 'Betrag'], #include from source
        'col_map':     {
            'Rechnungstext':     'text',
            'Buchungsdatum':     'value_date',
            'Transaktionsdatum': 'posting_date',
            'Abrechnungsdatum':  'billing_date',
            'Betrag':            'amount',
            'Währung':           'currency'
        },
        'date_cols':   ['Buchungsdatum', 'Transaktionsdatum', 'Abrechnungsdatum'],
        'match_filter': {
            'text': 'paylife abrechnung'
        },
        'match_weights': {
            'date': {
                'source_field': 'billing_date',
                'target_field': 'posting_date',
                'weight': 1
            }
        }
    },
    'paypal': {
        'preset_name': 'PayPal',
        'encoding':    'utf-8',
        'date_format': '%d.%m.%Y',
        'delimiter':   ',',
        'quotechar':   '"',
        'decimal':     ',',
        'thousands':   '.',
        'col_names':   None, # column names already present
        'usecols':     ['Datum', 'Name', 'Betreff', 'Brutto', 'Währung'], # include from source
        'col_map':     {
            'Name':    'contra_name',
            'Betreff': 'subject',
            'Datum':   'value_date',
            'Brutto':  'amount',
            'Währung': 'currency'
        },
        'date_cols':   ['Datum'],
        'match_filter': {
            'text': 'paypal'
        },
        'match_weights': {
            'date': {
                'source_field': 'value_date',
                'target_field': 'posting_date',
                'weight': 0.4
            },
            'amount': {
                'source_field': 'amount',
                'target_field': 'amount',
                'weight': 0.6
            }
        }
    }
}


def get_date_cols():
    return ['value_date', 'posting_date', 'billing_date', 'accounting_date']
