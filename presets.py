PRESETS = {
    'n26': {
        'preset_name': 'N26',
        'encoding':    'utf-8',
        'date_format': '%Y-%m-%d',
        'delimiter':   ',',
        'quotechar':   '"',
        'decimal':     '.',
        'thousands':   None,
        'col_names':   None, # column names already present
        'usecols':     ['Datum', 'Empfänger', 'Kontonummer', 'Transaktionstyp', 'Verwendungszweck', 'Betrag (EUR)'], #include from source
        'col_map':     {
            'Datum':            'value_date',
            'Empfänger':        'contra_name',
            'Kontonummer':      'contra_iban',
            'Verwendungszweck': 'subject',
            'Betrag (EUR)':     'amount'
        },
        'date_cols':   ['Datum']
    },
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
    'paypal-de': {
        'preset_name': 'PayPal DE',
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
    },
    'paypal-en': {
        'preset_name': 'PayPal EN',
        'encoding':    'utf-8',
        'date_format': '%d/%m/%Y',
        'delimiter':   ',',
        'quotechar':   '"',
        'decimal':     ',',
        'thousands':   '.',
        'col_names':   None, # column names already present
        'usecols':     ['Date', 'Name', 'Type', 'Subject', 'Gross', 'Currency', 'Transaction ID', 'Reference Txn ID'], # include from source
        'col_map':     {
            'Name':     'contra_name',
            'Subject':  'subject',
            'Date':     'value_date',
            'Gross':    'amount',
            'Currency': 'currency'
        },
        'date_cols':   ['Date']
    }
}
