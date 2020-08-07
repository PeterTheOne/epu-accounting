PRESETS_MATCHING = {
    'psk': {
        'match_fields': {
            'date':   'value_date',
            'amount': 'amount'
        }#,
        #'match_weights': {
        #    'date':   0.4,
        #    'amount': 0.6
        #}
    },
    'paylife': {
        'match_filter': {
            'text': 'paylife abrechnung'
        },
        'match_fields': {
            'date': 'billing_date'
        },
        'match_weights': {
            'date': 1
        }
    },
    'paypal-de': {
        'match_filter': {
            'text': 'paypal'
        },
        'match_fields': {
            'date':   'value_date',
            'amount': 'amount'
        },
        'match_weights': {
            'date':   0.4,
            'amount': 0.6
        }
    },
    'paypal-en': {
        'match_filter': {
            'text': 'paypal'
        },
        'match_fields': {
            'date':   'value_date',
            'amount': 'amount'
        },
        'match_weights': {
            'date':   0.4,
            'amount': 0.6
        }
    }
}
