import argparse
import os.path
import pandas as pd
import sqlite3
from sqlite3 import Error
from functions_db import *


def import_records(input_file, db_file, csv_date_format='%d.%m.%Y', csv_delimiter=',', csv_quotechar='"', csv_encoding='utf-8'):
    if not os.path.isfile(input_file):
        print('Error: File "{0}" don\'t exist.'.format(input_file))
        return

    date_parser = lambda x: pd.datetime.strptime(x, csv_date_format)
    data = pd.read_csv(filepath_or_buffer=input_file, delimiter=csv_delimiter, quotechar=csv_quotechar, encoding=csv_encoding,
                       parse_dates=['value_date'], date_parser=date_parser) #, 'posting_date'

    # create a database connection
    conn = create_connection(db_file)
    with conn:
        #data.to_sql('records', conn, if_exists='replace')

        for index, row in data.iterrows():
            # iban,text,subject,value_date,posting_date,amount,currency,preset,contra_name,contra_iban
            account_id = 2
            row['value_date'] = '2018-03-07 20:40:39.808427'

            record = (account_id, 0, 0, row['text'], row['value_date'])
            record_id = create_record(conn, record)

    conn.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file')
    parser.add_argument('db_file')
    args = parser.parse_args()
    import_records(args.input_file, args.db_file)


if __name__ == '__main__':
    main()
