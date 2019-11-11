import argparse
import os.path
import pandas as pd
import sqlite3
from sqlite3 import Error

import constants
from functions_db import *


def check_positive(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return ivalue


def number_records(db_file, year, start_no):
    # create a database connection
    conn = create_connection(db_file)
    with conn:
        sql = ''' SELECT id FROM records WHERE status = ? AND strftime('%Y', accounting_date) = ? ORDER BY accounting_date '''
        cur = conn.cursor()
        cur.execute(sql, (constants.STATUS_DONE,year))

        rows = cur.fetchall()
        log_records = len(rows)

        log_updated = 0
        running_no = int(start_no)

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
    parser.add_argument('--start', dest='start_no', default=1, type=check_positive)
    args = parser.parse_args()
    number_records(args.db_file, args.year, args.start_no)


if __name__ == '__main__':
    main()
