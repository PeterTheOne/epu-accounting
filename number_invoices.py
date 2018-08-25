import argparse
import os.path
import pandas as pd
import sqlite3
from sqlite3 import Error
import ntpath
from shutil import copyfile


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
 
    return None


def export_records(db_file, output_path='.', csv_date_format='%d.%m.%Y', csv_delimiter=',', csv_quotechar='"', csv_encoding='utf-8'):
    if not os.path.exists(output_path):
        print('Error: No such directory "{0}".'.format(output_path))
        return

    # create a database connection
    conn = create_connection(db_file)
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT no,path FROM files INNER JOIN records_temp ON files.record_id = records_temp.id ORDER BY records_temp.no")

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
    export_records(args.db_file, args.output_path)


if __name__ == '__main__':
    main()
