import argparse
import os.path
import pandas as pd
import sqlite3
from sqlite3 import Error
from functions_db import *


def export_records(db_file, output_file, csv_date_format='%d.%m.%Y', csv_delimiter=',', csv_quotechar='"', csv_encoding='utf-8'):
    # create a database connection
    conn = create_connection(db_file)
    with conn:
        data = pd.read_sql('SELECT * FROM records', conn, parse_dates=['value_date', 'posting_date'])
        data = data.drop(['index'], axis=1)
        data.to_csv(path_or_buf=output_file, index=False,
                sep=csv_delimiter, quotechar=csv_quotechar, encoding=csv_encoding,
                date_format=csv_date_format)
    conn.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('db_file')
    parser.add_argument('output_file')
    args = parser.parse_args()
    export_records(args.db_file, args.output_file)


if __name__ == '__main__':
    main()
