import argparse
import os.path
import pandas as pd
import sqlite3
from sqlite3 import Error
from functions_data import *
from functions_db import *
from functions_match import *


def match_records(db_file, csv_date_format='%d.%m.%Y', csv_delimiter=',', csv_quotechar='"', csv_encoding='utf-8'):
    # create a database connection
    conn = create_connection(db_file)
    with conn:
        # get primary account
        cur = conn.cursor()
        cur.execute("SELECT id FROM accounts WHERE main_account == 1")
        main_account = cur.fetchall()

        # get all secondary accounts
        cur = conn.cursor()
        cur.execute("SELECT id FROM accounts WHERE main_account == 0")
        sec_accounts = cur.fetchall()

        # get records from secondary accounts
        # these need to be matched to records in the primary account
        #sql = ''' SELECT * FROM records WHERE account_id IN ({0}) ORDER BY posting_date DESC '''
        #sql = sql.format('?', ','.join('?' * len(sec_accounts)))
        #params = tuple(flatten((sec_accounts))) # add more params next to 'sec_accounts'
        #orphans = pd.read_sql(sql, conn, params=params, parse_dates=get_date_cols())

        # get all records
        sql = ''' SELECT * FROM records ORDER BY posting_date DESC '''
        data = pd.read_sql(sql, conn, parse_dates=get_date_cols())

        main_account = tuple(flatten((main_account)))
        main = data[data.account_id.isin(main_account)]

        sec_accounts = tuple(flatten((sec_accounts)))
        orphans = data[data.account_id.isin(sec_accounts)]

        #print('main:')
        #print(main.loc[:,['text', 'posting_date', 'amount']])
        #print('orphans:')
        #print(orphans.loc[:,['text', 'billing_date', 'amount']])

        log_matches = 0
        log_orphans = len(orphans.index)

        for index, row in orphans.iterrows():
            date = row['billing_date']
            print('Searching for record with date: ')
            print(date)

            # filter credit card billing records
            matches = main.loc[main['text'].str.contains(r'(?:paylife abrechnung)(?i)')]
            #print(matches[['text', 'posting_date', 'amount']])

            # weigh by date
            date_weights = match_date(matches['posting_date'], date)

            # list most likely records
            result = pd.concat([
                matches,
                date_weights.rename('date_w')
            ], axis=1, sort=False)
            result = result.sort_values(by=['date_w'], ascending=False) # sort by closest matches
            result = result.iloc[:1]
            #print(result[['text', 'posting_date', 'amount', 'date_w']])

            # is there a match?
            if any(result.date_w > 0.75):
                log_matches += 1

                match = result.loc[result['date_w'] > 0.75]
                print('match:')
                print(match[['text', 'posting_date', 'amount', 'date_w']])

                # update record
                row_update = row
                row_update.ignore = 1
                row_update.accounting_date = date
                #print('updated record:')
                #print(row_update[['ignore', 'text', 'accounting_date', 'amount', 'date_w']])

                # write to database
                sql_date_format = '%Y-%m-%d %H:%M:%S'
                params = [row_update.accounting_date.strftime(sql_date_format), row_update.ignore, row_update.id]

                cur = conn.cursor()
                cur.execute("UPDATE records SET accounting_date = ?, ignore = ? WHERE id = ?", params)

                # todo: when to mark credit card billing record as done?

            else:
                print('NO match!')

        log_notfound = log_orphans - log_matches
        print('Found {0} matches for {1} records, {2} could not be matched.'.format(log_matches, log_orphans, log_notfound))

    conn.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('db_file')
    args = parser.parse_args()
    match_records(args.db_file)


if __name__ == '__main__':
    main()
