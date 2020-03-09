epu-accounting
==============
FREIHEIT * TRANSPARENZ * GELASSENHEIT

requirements:
- python 3

install:
- poppler, see [pdf2image Installation](https://github.com/Belval/pdf2image#how-to-install)
- `pip3 install -r requirements.txt`
- tkinter (on linux): `[sudo] apt-get install python3-tk`
- Make sure the `de_DE` locale is available on your OS

new way of running scripts:

- remove your old *.db file!
- create a folder named input with your CSV files.
- `python3 epu_accounting.py` and follow instructions
- optional match_pdf
- `python3 number_db.py [db_file] [year]`
- optional number_pdf
- `python3 db_to_csv.py [db_file] [output_file]`


recommended order of running scripts:

csv only workflow
- clean
- sort
- contra_histogram
- apply_blacklist
- text_histogram
- apply_blacklist_text
- timesplit

db workflow
- clean
- setup_db
- csv_to_db
- match_records_db: provide the account to match to main account
- match_pdf
- number_db
- number_pdf
- db_to_csv: maybe include unfinished?
