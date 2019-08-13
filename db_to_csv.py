import argparse
import os.path
import pandas as pd
import sqlite3
from sqlite3 import Error

import constants
from functions_data import *
from functions_db import *


def export_records(db_file, output_file, include_unfinished=False, include_ignored=False, csv_date_format='%d.%m.%Y', csv_delimiter=',', csv_quotechar='"', csv_encoding='utf-8'):
    # create a database connection
    conn = create_connection(db_file)
    with conn:
        params = [constants.STATUS_DONE]
        if include_unfinished:
            params.append(constants.STATUS_NONE)
        if include_ignored:
            params.append(constants.STATUS_IGNORE)
        sql = ''' SELECT records.id,accounting_no,accounting_date,status,text,value_date,posting_date,billing_date,amount,currency,subject,line_id,comment,contra_name,contra_iban,contra_bic,import_preset,iban,email,creditcard_no FROM records INNER JOIN accounts ON records.account_id = accounts.id WHERE status IN (%s) ''' % ','.join('?' for i in params)
        data = pd.read_sql(sql, conn, params=params, parse_dates=get_date_cols())
        data.to_csv(path_or_buf=output_file, index=False,
                sep=csv_delimiter, quotechar=csv_quotechar, encoding=csv_encoding,
                date_format=csv_date_format)
    conn.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('db_file')
    parser.add_argument('output_file')
    parser.add_argument('--include_unfinished', dest='include_unfinished', action='store_true')
    parser.add_argument('--include_ignored', dest='include_ignored', action='store_true')
    parser.set_defaults(include_unfinished=False)
    parser.set_defaults(include_ignored=False)
    args = parser.parse_args()
    export_records(args.db_file, args.output_file, args.include_unfinished, args.include_ignored)


if __name__ == '__main__':
    main()
