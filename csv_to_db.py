import argparse
import os.path
import pandas as pd
import sqlite3
from sqlite3 import Error

import constants
from functions_data import *
from functions_db import *


def import_records(input_file, db_file, account_name, csv_date_format='%d.%m.%Y', csv_delimiter=',', csv_quotechar='"', csv_encoding='utf-8'):
    if not os.path.isfile(input_file):
        print('Error: File "{0}" doesn\'t exist.'.format(input_file))
        return

    # find account id
    account_id = 0
    conn = create_connection(db_file)
    with conn:
        sql = ''' SELECT id FROM accounts WHERE name = ? LIMIT 1 '''
        cur = conn.cursor()
        cur.execute(sql, (account_name,))

        rows = cur.fetchall()

        for row in rows:
            account_id = row[0]

    if account_id == 0:
        print('Error: Account "{0}" doesn\'t exist.'.format(account_name))
        return

    date_parser = lambda x: pd.to_datetime(x, format=csv_date_format, errors='coerce')
    data = pd.read_csv(filepath_or_buffer=input_file, delimiter=csv_delimiter, quotechar=csv_quotechar, encoding=csv_encoding,
                       parse_dates=get_date_cols(), date_parser=date_parser)

    # create a database connection
    conn = create_connection(db_file)
    with conn:
        data['account_id'] = account_id
        # set defaults
        data['accounting_no'] = 0
        data['status'] = constants.STATUS_NONE
        # todo: save in account table
        if 'iban' in data.columns:
            data = data.drop(columns=['iban'])
        if 'account' in data.columns:
            data = data.drop(columns=['account'])

        data.to_sql('records', conn, if_exists='append', index=False)

    conn.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file')
    parser.add_argument('db_file')
    parser.add_argument('account_name')
    args = parser.parse_args()
    import_records(args.input_file, args.db_file, args.account_name)


if __name__ == '__main__':
    main()
