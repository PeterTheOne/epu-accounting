epu-accounting
==============
FREIHEIT * TRANSPARENZ * GELASSENHEIT

requirements:
- python 3

install:
- poppler, see [pdf2image Installation](https://github.com/Belval/pdf2image#how-to-install)
- `pip install -r requirements.txt`

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
