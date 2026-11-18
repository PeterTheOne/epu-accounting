epu-accounting
==============
FREIHEIT * TRANSPARENZ * GELASSENHEIT

## requirements
- python 3.9 (the pinned dependency versions are the last ones that support 3.9; moving to a newer Python is planned)

## install
- poppler, see [pdf2image Installation](https://github.com/Belval/pdf2image#how-to-install)
- tkinter
 - linux: `[sudo] apt-get install python3-tk`
 - macOS: `brew install python-tk@3.9`
- Make sure the `de_DE` locale is available on your OS
- Python dependencies are installed into a virtual environment, see below

### virtual environment
Create the venv once (the `venv/` folder is ignored by git):

```
python3.9 -m venv venv
venv/bin/pip install --upgrade pip
```

Then install the dependencies:

```
venv/bin/pip install -r requirements.txt
```

### running
Activate the venv in each new terminal session:

```
source venv/bin/activate
```

While it is active, `python` points to the venv's Python 3.9, so use `python` wherever this README says `python3.9` or `python3`, e.g. `python epu_accounting.py`. Run `deactivate` to leave the venv.

Without activating, call the venv's Python directly: `venv/bin/python epu_accounting.py`.

### testing
`tests/run_fixtures.py` runs the whole pipeline (clean, histograms/classification, database import, record matching, numbering, export and the legacy CSV scripts) on the fixtures in `examples/`, answering the interactive prompts automatically. Run it before and after a change and compare the results:

```
venv/bin/python tests/run_fixtures.py examples/out/before
# ... make changes ...
venv/bin/python tests/run_fixtures.py examples/out/after
diff -r examples/out/before examples/out/after
```

Failing steps are listed at the end and written to `failures.txt` in the output folder. PDF matching (`match_pdf.py`) is not covered, since there are no example PDFs.

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
