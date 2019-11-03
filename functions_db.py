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


def create_account(conn, account):
    """
    Create a new account into the accounts table
    :param conn:
    :param account:
    :return: account id
    """
    sql = ''' INSERT INTO accounts(parent_id,main_account,iban,email,creditcard_no,name)
              VALUES((SELECT IFNULL((SELECT id FROM accounts WHERE name = :parent), 0)),
                     :main_account,:iban,:email,:creditcard_no,:name) '''
    cur = conn.cursor()
    cur.execute(sql, account)
    return cur.lastrowid


def create_record(conn, record):
    """
    Create a new record into the records table
    :param conn:
    :param record:
    :return: record id
    """
    sql = ''' INSERT INTO records(parent_id,account_id,accounting_no,accounting_date,status,
                    text,value_date,posting_date,billing_date,amount,currency,
                    subject,line_id,comment,contra_name,contra_iban,contra_bic,import_preset)
              VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) '''
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


def get_secondary_accounts(conn):
    cur = conn.cursor()
    cur.execute("SELECT name FROM accounts WHERE main_account = ?", (False,))
    return cur.fetchall()


# generator to flatten values of irregular nested sequences,
# modified from answers http://stackoverflow.com/questions/952914/making-a-flat-list-out-of-list-of-lists-in-python
def flatten(l):
    for el in l:
        try:
            yield from flatten(el)
        except TypeError:
            yield el
