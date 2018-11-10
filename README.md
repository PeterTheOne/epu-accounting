epu-accounting
==============
FREIHEIT * TRANSPARENZ * GELASSENHEIT

requirements:
- python 3

install:
- `pip install -r requirements.txt`

recommended order of running scripts:

- clean
- extract and sort
- contra_histogram
- apply_blacklist
- text_histogram
- apply_blacklist_text
- timesplit

- clean
- setup_db
- csv_to_db
- match_records_db
- match_pdf
- number_db
- number_pdf
- db_to_csv
