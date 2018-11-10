import argparse
import os.path
import pandas as pd
import sqlite3
from sqlite3 import Error

import constants
from functions_db import *


def number_records(db_file, year):
    # create a database connection
    conn = create_connection(db_file)
    with conn:
        sql = ''' SELECT id FROM records WHERE status = ? AND strftime('%Y', accounting_date) = ? ORDER BY accounting_date '''
        cur = conn.cursor()
        cur.execute(sql, (constants.STATUS_DONE,year))

        rows = cur.fetchall()
        log_records = len(rows)

        running_no = 1
        log_updated = 0

        for row in rows:
            id = row[0]

            params = [
                running_no,
                id
            ]
            cur.execute("UPDATE records SET accounting_no = ? WHERE id = ?", params)
            log_updated += cur.rowcount
            running_no = running_no + 1

        print('Found {0} records, {1} updated.'.format(log_records, log_updated))

    conn.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('db_file')
    parser.add_argument('year')
    args = parser.parse_args()
    number_records(args.db_file, args.year)


if __name__ == '__main__':
    main()
