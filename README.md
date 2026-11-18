epu-accounting
==============
FREIHEIT * TRANSPARENZ * GELASSENHEIT

## requirements
- python 3 (up to 3.9, due to PyInquirer error. Run using `python3.9 epu_accounting.py`)

## install
- poppler, see [pdf2image Installation](https://github.com/Belval/pdf2image#how-to-install)
- `pip3 install -r requirements.txt`
- tkinter
 - linux: `[sudo] apt-get install python3-tk`
 - macOS: `brew install python-tk`
- Make sure the `de_DE` locale is available on your OS

## bookamat workflow
- download your bank/credit card/PayPal statements as CSV files
  - for PayPal, go to Reports > Activity download > and choose Transaction type: Balance affecting
- create denylist with one column "contra_iban", listing your own IBANs
- `python3.9 apply_denylist.py [input_file] [denylist_file] [output_file] --preset [preset] --drop_empty --allowlist_text "rückzahlung,zinsen"` (presets: see `presets.py`)

## workflow
- remove your old *.db file!
- download your bank/credit card/PayPal statements as CSV files
  - for PayPal, go to Reports > Activity download > and choose Transaction type: Balance affecting
- create a folder named input with your CSV files.
- `python3 epu_accounting.py` and follow instructions.
- (optional) open SQlite database and remove unneeded transactions.
- (optional) create a folder named pdf with your invoices.
- (optional) `python3 match_pdf.py --gui [db_file] [pdf_directory]`
- `python3 number_db.py [db_file] [year]`
- create a folder named output.
- (optional) `python3 number_pdf.py [db_file] [output_directory]`
- `python3 db_to_csv.py [db_file] [output_file]`
- open output CSV, remove any columns you don't need.

## old csv only workflow
- clean
- sort
- contra_histogram
- apply_denylist
- text_histogram
- apply_denylist_text
- timesplit

## known issues
### match_pdf `locale.Error: unsupported locale setting`
The `de_DE` locale is not available on your OS.
- Check using `locale -a | grep de` or `locale -a` (Mac/Linux) which locales are installed.
- Add `de_DE` to your operating system or
- copy `.env.example` to `.env` and set `LOCALE` to a locale that is available on your OS
