PRESETS = {
    'n26': {
        'preset_name': 'N26 DE',
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
    'n26-en': {
        'preset_name': 'N26 EN',
        'encoding':    'utf-8',
        'date_format': '%Y-%m-%d',
        'delimiter':   ',',
        'quotechar':   '"',
        'decimal':     '.',
        'thousands':   None,
        'col_names':   None, # column names already present
        'usecols':     ['Value Date', 'Partner Name', 'Partner Iban', 'Type', 'Payment Reference', 'Amount (EUR)'], #include from source
        'col_map':     {
            'Value Date':        'value_date',
            'Partner Name':      'contra_name',
            'Partner Iban':      'contra_iban',
            'Payment Reference': 'subject',
            'Amount (EUR)':      'amount'
        },
        'date_cols':   ['Value Date']
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
        'header':      None, # source has no header row, first line is data
        'usecols':     None,
        'col_map':     [],
        'date_cols':   ['value_date', 'posting_date']
    },
    'paylife': {
        # todo: select correct 'Währung' column
        'preset_name': 'PayLife',
        'encoding':    'utf-8',
        'date_format': '%Y-%m-%d',
        'delimiter':   ';',
        'quotechar':   '"',
        'decimal':     ',',
        'thousands':   '.',
        'col_names':   None, # column names already present
        'usecols':     ['Buchungsdatum', 'Umsatzdatum', 'Abrechnungsdatum', 'Buchungstext', 'Währung', 'Betrag in EUR'], #include from source
        'col_map':     {
            'Buchungstext':      'text',
            'Buchungsdatum':     'value_date',
            'Umsatzdatum':       'posting_date',
            'Abrechnungsdatum':  'billing_date',
            'Betrag in EUR':     'amount',
            'Währung':           'currency'
        },
        'date_cols':   ['Buchungsdatum', 'Umsatzdatum', 'Abrechnungsdatum']
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
