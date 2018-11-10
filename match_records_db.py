import argparse
import os.path
import pandas as pd
import sqlite3
from sqlite3 import Error

import constants
from functions_data import *
from functions_db import *
from functions_match import *


def match_records(db_file, account_name, csv_date_format='%d.%m.%Y', csv_delimiter=',', csv_quotechar='"', csv_encoding='utf-8'):
    # create a database connection
    conn = create_connection(db_file)
    with conn:
        # get secondary account
        sec_account_id = 0
        parent_account_id = 0
        cur = conn.cursor()
        cur.execute("SELECT id,parent_id FROM accounts WHERE name = ?", (account_name,))
        sec_account = cur.fetchone()
        sec_account_id = sec_account[0]
        parent_account_id = sec_account[1]

        if sec_account_id == 0:
            print('Error: Account "{0}" doesn\'t exist.'.format(account_name))
            return

        # get all records
        sql = ''' SELECT * FROM records WHERE status = ? ORDER BY posting_date DESC '''
        data = pd.read_sql(sql, conn, params=[constants.STATUS_NONE], parse_dates=get_date_cols())

        main = data[data.account_id == parent_account_id]
        orphans = data[data.account_id == sec_account_id]

        #orphans = orphans.iloc[:10] # debug

        log_matches = 0
        log_orphans = len(orphans.index)
        log_updated = 0

        for index, row in orphans.iterrows():
            # get preset
            preset = row['import_preset']
            if preset not in presets:
                print( 'Preset {} not found, skipping...'.format( preset ) )
                continue

            current_preset = presets[preset]

            # weight fields
            amount_source_field = current_preset.get('match_weights', {}).get('amount', {}).get('source_field', 'amount')
            amount_target_field = current_preset.get('match_weights', {}).get('amount', {}).get('target_field', 'amount')
            date_source_field = current_preset.get('match_weights', {}).get('date', {}).get('source_field', 'posting_date')
            date_target_field = current_preset.get('match_weights', {}).get('date', {}).get('target_field', 'posting_date')

            # weight factors
            amount_w_factor = current_preset.get('match_weights', {}).get('amount', {}).get('weight', 0)
            date_w_factor = current_preset.get('match_weights', {}).get('date', {}).get('weight', 0)

            # orphan values to match
            amount = row[amount_source_field]
            date = row[date_source_field]

            #print('Searching for record matching: ')
            #print(row[[date_source_field, amount_source_field]])

            # filter main (target) records
            for key, value in current_preset['match_filter'].items():
                main = main.loc[main[key].str.contains(r'(?:' + value + ')(?i)')]

            # weights
            amount_weights = match_amount(main[amount_target_field], amount)
            date_weights = match_date(main[date_target_field], date) # todo: results should always be *after* supplied date

            weights = (date_weights*date_w_factor + amount_weights*amount_w_factor)

            # list most likely records
            result = pd.concat([
                main,
                weights.rename('w'),
                date_weights.rename('date_w'),
                amount_weights.rename('amount_w')
            ], axis=1, sort=False)
            result = result.sort_values(by=['w'], ascending=False) # sort by closest matches
            result = result.iloc[:1]

            # is the match good enough?
            if any(result.w > 0.75):
                log_matches += 1

                #print(result[['text', date_target_field, amount_target_field, 'w', 'date_w', 'amount_w']])

                # update record
                sql_date_format = '%Y-%m-%d %H:%M:%S'
                params = [
                    result.iloc[0].at[date_target_field].strftime(sql_date_format), # use date from result
                    constants.STATUS_DONE,
                    row.id
                ]
                cur.execute("UPDATE records SET accounting_date = ?, status = ? WHERE id = ?", params)
                log_updated += cur.rowcount

                # update main record
                # todo: when to mark credit card billing record as done?
                params = [
                    constants.STATUS_IGNORE,
                    int(result.iloc[0].at['id'])
                ]
                cur.execute("UPDATE records SET status = ? WHERE id = ?", params)
                log_updated += cur.rowcount

            #else:
                #print('NO match!')

        log_notfound = log_orphans - log_matches
        print('Found {0} matches for {1} records, {2} updated, {3} could not be matched.'.format(log_matches, log_orphans, log_updated, log_notfound))

    conn.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('db_file')
    parser.add_argument('account_name')
    args = parser.parse_args()
    match_records(args.db_file, args.account_name)


if __name__ == '__main__':
    main()
