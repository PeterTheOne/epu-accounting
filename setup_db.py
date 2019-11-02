import argparse
#import os.path
#import sqlite3
#from sqlite3 import Error
from functions_db import create_connection, create_table, create_account


def setup_db(db_file, account_names):
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
                                        parent_id integer DEFAULT 0,
                                        account_id integer NOT NULL,    /* foreign key */
                                        /* accounting */
                                        accounting_no integer,
                                        accounting_date timestamp,      /* date to be used in accounting */
                                        status integer DEFAULT 0,
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
                                        FOREIGN KEY (parent_id) REFERENCES records (id),
                                        FOREIGN KEY (account_id) REFERENCES accounts (id)
                                    ); """

    sql_create_files_table = """ CREATE TABLE IF NOT EXISTS files (
                                        id integer PRIMARY KEY,
                                        record_id integer NOT NULL,
                                        path text NOT NULL,
                                        FOREIGN KEY (record_id) REFERENCES records (id)
                                    ); """

    # create a database connection
    conn = create_connection(db_file)
    if conn is not None:
        # create accounts table
        create_table(conn, sql_create_accounts_table)

        # create records table
        create_table(conn, sql_create_records_table)

        # create files table
        create_table(conn, sql_create_files_table)

        # create accounts
        # todo: set parent/child relationships
        print('Adding accounts', account_names)
        for name in account_names:
            account_data = (0, 1, '', '', '', name)
            account_id = create_account(conn, account_data)

        conn.commit()
    else:
        print("Error! cannot create the database connection.")

    conn.close()

def main():
    # todo: args for accounts setup (config file or csv filenames?)
    # todo: ask for account parent/child relationships
    parser = argparse.ArgumentParser()
    parser.add_argument('db_file')
    args = parser.parse_args()

    account_names = ['work', 'private']
    setup_db(args.db_file, account_names)

if __name__ == '__main__':
    main()
