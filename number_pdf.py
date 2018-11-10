import argparse
import os.path
import pandas as pd
import sqlite3
from sqlite3 import Error
import ntpath
from shutil import copyfile

from functions_db import *


def number_invoices(db_file, output_path='.'):
    if not os.path.exists(output_path):
        print('Error: No such directory "{0}".'.format(output_path))
        return

    # create a database connection
    conn = create_connection(db_file)
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT accounting_no,path FROM files INNER JOIN records ON files.record_id = records.id ORDER BY records.accounting_no")

        rows = cur.fetchall()

        for row in rows:
            no = row[0]
            path = row[1]
            filename = ntpath.basename(path)
            filename_new = '{0:05d}_'.format(no) + filename
            path_new = os.path.join(output_path, filename_new)
            copyfile(path, path_new)
            print(path_new)

    conn.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('db_file')
    parser.add_argument('output_path', nargs='?', default=os.getcwd())
    args = parser.parse_args()
    number_invoices(args.db_file, args.output_path)


if __name__ == '__main__':
    main()
