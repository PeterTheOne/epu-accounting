epu-accounting
==============
FREIHEIT * TRANSPARENZ * GELASSENHEIT

requirements:
- python 3

install:
- `pip install -r requirements.txt`

recommended order of running scripts:

csv only workflow
- clean
- extract and sort
- contra_histogram
- apply_blacklist
- text_histogram
- apply_blacklist_text
- timesplit

db workflow
- clean: provide the preset for non psk csv files
- extract
- setup_db
- csv_to_db
- match_records_db: provide the non psk account to match with
- match_pdf
- number_db
- number_pdf
- db_to_csv: maybe include unfinished?
