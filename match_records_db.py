import argparse
import os.path
import pandas as pd
import sqlite3
from sqlite3 import Error
from functions_db import *


def match_records(db_file, csv_date_format='%d.%m.%Y', csv_delimiter=',', csv_quotechar='"', csv_encoding='utf-8'):
    # create a database connection
    conn = create_connection(db_file)
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM accounts WHERE parent_id != 0")

        accounts = cur.fetchall()

        for account in accounts:
            sql = ''' SELECT * FROM records_temp WHERE account_id = ? ORDER BY value_date DESC '''
            cur = conn.cursor()
            cur.execute(sql, account)

            rows = cur.fetchall()

            for row in rows:
                ignore = row[3]
                text = row[4]
                value_date = row[5]
                print(text + '' + value_date)

    conn.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('db_file')
    args = parser.parse_args()
    match_records(args.db_file)


if __name__ == '__main__':
    main()
