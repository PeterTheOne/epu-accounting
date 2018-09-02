import argparse
import os.path
import sqlite3
from sqlite3 import Error


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


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def create_record(conn, record):
    """
    Create a new record into the records table
    :param conn:
    :param record:
    :return: record id
    """
    sql = ''' INSERT INTO records_temp(no,text,value_date)
              VALUES(?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, record)
    return cur.lastrowid


def create_file(conn, file):
    """
    Create a new file into the files table
    :param conn:
    :param file:
    :return: file id
    """
    sql = ''' INSERT INTO files(record_id,path)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, file)
    return cur.lastrowid


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('db_file')
    args = parser.parse_args()

    sql_create_records_table = """ CREATE TABLE IF NOT EXISTS records_temp (
                                        id integer PRIMARY KEY,
                                        no integer,
                                        text text NOT NULL,
                                        value_date timestamp
                                    ); """

    sql_create_files_table = """ CREATE TABLE IF NOT EXISTS files (
                                        id integer PRIMARY KEY,
                                        record_id integer NOT NULL,
                                        path text NOT NULL,
                                        FOREIGN KEY (record_id) REFERENCES records_temp (id)
                                    ); """

    # create a database connection
    conn = create_connection(args.db_file)
    if conn is not None:
        # create records table
        create_table(conn, sql_create_records_table)

        # create files table
        create_table(conn, sql_create_files_table)

        # records
        record_1 = (6, 'buchungszeile 1', '2018-03-07 20:40:39.808427');
        record_2 = (5, 'buchungszeile 2', '2017-03-07 20:40:39.808427');
        record_3 = (1, 'buchungszeile 3', '2012-03-07 20:40:39.808427');
        record_4 = (3, 'buchungszeile 4', '2015-03-07 20:40:39.808427');
        record_5 = (2, 'buchungszeile 5', '2014-03-07 20:40:39.808427');
        record_6 = (4, 'buchungszeile 6', '2016-03-07 20:40:39.808427');

        # create records
        record_1_id = create_record(conn, record_1)
        record_2_id = create_record(conn, record_2)
        record_3_id = create_record(conn, record_3)
        record_4_id = create_record(conn, record_4)
        record_5_id = create_record(conn, record_5)
        record_6_id = create_record(conn, record_6)
 
        # files
        file_1 = (record_1_id, 'work\\files\\rechnung_18011.pdf')
        file_2 = (record_2_id, 'work\\files\\rechnung_18012.pdf')
        file_3 = (record_3_id, 'work\\files\\rechnung_18013.pdf')
        file_4 = (record_4_id, 'work\\files\\rechnung_18008.pdf')
        file_5 = (record_5_id, 'work\\files\\rechnung_18009.pdf')
        file_6 = (record_6_id, 'work\\files\\rechnung_18010.pdf')
        file_7 = (record_6_id, 'work\\files\\rechnung_18012.pdf')
 
        # create files
        create_file(conn, file_1)
        create_file(conn, file_2)
        create_file(conn, file_3)
        create_file(conn, file_4)
        create_file(conn, file_5)
        create_file(conn, file_6)
        create_file(conn, file_7)

        conn.commit()
    else:
        print("Error! cannot create the database connection.")

    conn.close()


if __name__ == '__main__':
    main()