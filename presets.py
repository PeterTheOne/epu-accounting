PRESETS = {
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
        'date_cols':   ['Buchungsdatum', 'Transaktionsdatum', 'Abrechnungsdatum']
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
        'usecols':     ['Datum', 'Name', 'Typ', 'Betreff', 'Brutto', 'Währung', 'Transaktionscode', 'Zugehöriger Transaktionscode'], # include from source
        'col_map':     {
            'Name':    'contra_name',
            'Betreff': 'subject',
            'Datum':   'value_date',
            'Brutto':  'amount',
            'Währung': 'currency'
        },
        'date_cols':   ['Datum']
    }
}
