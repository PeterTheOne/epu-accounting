import argparse
#import os.path
#import sqlite3
#from sqlite3 import Error
from PyInquirer import prompt
from functions_db import create_connection, create_table, create_account


def query_account_tree(account_names):
    if len(account_names) > 1:
        # Classify main accounts
        choices_objects = map(lambda c: {'name': c}, account_names)
        answers = prompt([
            {
                'type': 'checkbox',
                'name': 'main_accounts',
                'message': 'Which are the main accounts/sources for accounting date?',
                'choices': choices_objects
            }
        ])
        main_accounts = answers['main_accounts']
    else:
        main_accounts = account_names

    accounts = list(map(lambda a: {'name': a, 'main_account': True, 'parent': False, 'iban': '', 'email': '', 'creditcard_no': ''}, main_accounts))

    # Set parent accounts of children
    for a in account_names:
        if a not in main_accounts:
            parent_account = False
            if len(main_accounts) > 1:
                # Multiple main accounts, ask for individual parent
                choices_objects = map(lambda c: {'name': c}, main_accounts)
                answers = prompt([
                    {
                        'type': 'list',
                        'name': 'parent_account',
                        'message': 'What is {}\'s the parent account?'.format(a),
                        'choices': choices_objects
                    }
                ])
                parent_account = answers['parent_account']
            elif len(main_accounts) == 1:
                # Only 1 main account, we are done
                parent_account = main_accounts[0]

            accounts.append({'name': a, 'main_account': False, 'parent': parent_account, 'iban': '', 'email': '', 'creditcard_no': ''})

    return accounts


def setup_db(db_file, account_names):
    accounts = query_account_tree(account_names)

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
                                        accounting_no integer DEFAULT 0,
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
        print('Adding accounts', account_names)
        # Add main accounts first
        for account in accounts:
            if account['main_account']:
                create_account(conn, account)
        # Add child accounts linked to parents
        for account in accounts:
            if not account['main_account']:
                create_account(conn, account)

        conn.commit()
    else:
        print("Error! cannot create the database connection.")

    conn.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('db_file')
    parser.add_argument('account_names', help='Comma seperated list of account names')
    args = parser.parse_args()

    # Clean up account names
    account_names = args.account_names.split(',')
    account_names = map(lambda a: a.strip(), account_names)
    account_names = filter(lambda a: a != '', account_names)
    account_names = list(account_names)

    if len(account_names) > 0:
        setup_db(args.db_file, account_names)
    else:
        print('No account names provided, database not created.')

if __name__ == '__main__':
    main()
