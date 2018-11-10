import argparse
import os.path
import sqlite3
from sqlite3 import Error
from functions_db import *


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('db_file')
    args = parser.parse_args()

    sql_create_accounts_table = """ CREATE TABLE IF NOT EXISTS accounts (
                                        id integer PRIMARY KEY,
                                        parent_id integer NOT NULL,
                                        main_account integer,
                                        iban text,
                                        email text,
                                        creditcard_no text,
                                        name text NOT NULL,
                                        FOREIGN KEY (parent_id) REFERENCES accounts (id)
                                    ); """

    sql_create_records_table = """ CREATE TABLE IF NOT EXISTS records (
                                        /* only in database */
                                        id integer PRIMARY KEY,
                                        account_id integer NOT NULL,    /* foreign key */
                                        /* accounting */
                                        accounting_no integer,
                                        accounting_date timestamp,      /* date to be used in accounting */
                                        status integer,
                                        /* data source; read only */
                                        text text,
                                        value_date timestamp,
                                        posting_date timestamp,
                                        billing_date timestamp,         /* credit card bill date */
                                        amount real,
                                        currency text,
                                        /* generated fields */
                                        subject text,
                                        line_id text,
                                        comment text,
                                        contra_name text,
                                        contra_iban text,
                                        contra_bic text,
                                        import_preset text,
                                        /* export fields (in 'accounts' table) */
                                        /*
                                        'iban',
                                        'email',
                                        'creditcard_no'
                                        */
                                        FOREIGN KEY (account_id) REFERENCES accounts (id)
                                    ); """

    sql_create_files_table = """ CREATE TABLE IF NOT EXISTS files (
                                        id integer PRIMARY KEY,
                                        record_id integer NOT NULL,
                                        path text NOT NULL,
                                        FOREIGN KEY (record_id) REFERENCES records (id)
                                    ); """

    # create a database connection
    conn = create_connection(args.db_file)
    if conn is not None:
        # create accounts table
        create_table(conn, sql_create_accounts_table)

        # create records table
        create_table(conn, sql_create_records_table)

        # create files table
        create_table(conn, sql_create_files_table)

        # create accounts
        account_1 = (0, 1, '', '', '', 'PSK')
        account_1_id = create_account(conn, account_1)

        account_2 = (account_1_id, 0, '', '', '', 'Kreditkarte')
        account_2_id = create_account(conn, account_2)

        account_3 = (account_1_id, 0, '', '', '', 'PayPal')
        account_3_id = create_account(conn, account_3)

        # records
        #record_1 = (account_1_id, 6, 0, 'buchungszeile 1', '2018-03-07 20:40:39.808427')
        #record_2 = (account_1_id, 5, 0, 'buchungszeile 2', '2017-03-07 20:40:39.808427')
        #record_3 = (account_1_id, 1, 0, 'buchungszeile 3', '2012-03-07 20:40:39.808427')
        #record_4 = (account_1_id, 3, 0, 'kreditkarten rechnung', '2015-03-07 20:40:39.808427')
        #record_5 = (account_1_id, 2, 0, 'buchungszeile 5', '2014-03-07 20:40:39.808427')
        #record_6 = (account_2_id, 4, 0, 'buchung kreditkarte', '2015-03-07 20:40:39.808427')

        # create records
        #record_1_id = create_record(conn, record_1)
        #record_2_id = create_record(conn, record_2)
        #record_3_id = create_record(conn, record_3)
        #record_4_id = create_record(conn, record_4)
        #record_5_id = create_record(conn, record_5)
        #record_6_id = create_record(conn, record_6)
 
        # files
        #file_1 = (record_1_id, 'work\\files\\rechnung_18011.pdf')
        #file_2 = (record_2_id, 'work\\files\\rechnung_18012.pdf')
        #file_3 = (record_3_id, 'work\\files\\rechnung_18013.pdf')
        #file_4 = (record_4_id, 'work\\files\\rechnung_18008.pdf')
        #file_5 = (record_5_id, 'work\\files\\rechnung_18009.pdf')
        #file_6 = (record_6_id, 'work\\files\\rechnung_18010.pdf')
        #file_7 = (record_6_id, 'work\\files\\rechnung_18012.pdf')
 
        # create files
        #create_file(conn, file_1)
        #create_file(conn, file_2)
        #create_file(conn, file_3)
        #create_file(conn, file_4)
        #create_file(conn, file_5)
        #create_file(conn, file_6)
        #create_file(conn, file_7)

        conn.commit()
    else:
        print("Error! cannot create the database connection.")

    conn.close()


if __name__ == '__main__':
    main()
