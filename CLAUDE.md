# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

epu-accounting is a CLI tool for Austrian EPU (Ein-Personen-Unternehmen / sole proprietorship) bookkeeping. It ingests bank / credit card / PayPal statements as CSV, normalizes them with per-institution presets, matches secondary-account transactions (card/PayPal) against their main bank account, optionally matches invoice PDFs to records, numbers the records for accounting, and exports a final CSV.

Python 3 only — pinned to **3.9** (PyInquirer incompatibility with newer versions). Run scripts with `python3.9`. There is no test suite, no linter config, and no build step.

## Setup

- `pip3 install -r requirements.txt` (PyInquirer is installed from a pinned git commit)
- poppler (for pdf2image), tkinter (`brew install python-tk` on macOS)
- The `de_DE` locale must be available (`match_pdf.py` and `clean_csv.py` call `locale.setlocale`)

## Main workflow (end-to-end)

Scripts are run in this order; each is a standalone CLI taking positional args (see each file's `argparse` in `main()`):

1. `python3.9 epu_accounting.py` — interactive wizard (PyInquirer). Prompts for the `input/` folder of CSVs, cleans each via a chosen preset, optionally classifies records private/company (built from contra-IBAN and text histograms), asks for a db filename, sets up the schema, imports all CSVs, and then runs `match_records_db` for every secondary account.
2. (optional) `python3.9 match_pdf.py [db_file] [pdf_dir]` — match invoice PDFs to records. `--gui` shows the PDF in a tkinter viewer alongside the prompt; `--automatic` skips prompts and accepts the top match above a weight threshold (0.3).
3. `python3.9 number_db.py [db_file] [year]` — assigns sequential `accounting_no` to all STATUS_DONE records of a year (`--start N` to begin at N).
4. (optional) `python3.9 number_pdf.py [db_file] [output_dir]` — copies matched invoice PDFs into `output_dir`, prefixed with their accounting number.
5. `python3.9 db_to_csv.py [db_file] [output_file]` — final export (`--include_unfinished`, `--include_ignored`).

Delete the old *.db file before starting a fresh run — `epu_accounting.py` does not deduplicate on re-import.

### Legacy CSV-only workflow

`clean_csv.py`, `sort_csv.py`, `contra_histogram_csv.py`, `apply_blacklist.py`/`apply_blacklist_text.py`, `text_histogram_csv.py`, `apply_whitelist.py`, `timesplit_csv.py` form an older pipeline that works without the database (see README). They are mostly superseded by the DB workflow above; `contra_histogram_csv` and `text_histogram_csv` are still imported by `epu_accounting.py` for classification. Also related: `sum_by_contra_csv.py`, `negative_rolling_sum.py`.

## Architecture

Three layers, all coordinating through a SQLite database:

**Presets** (`presets.py`) — dict keyed by institution (`n26`, `n26-en`, `psk`, `paylife`, `paypal-de`, `paypal-en`). Each defines CSV reading parameters (encoding, delimiter, decimal, `usecols`, `col_map` renaming source columns to canonical names, `date_cols`). `clean_csv.py` consumes these: reads the source CSV with pandas, adds `status`/`accounting_no` defaults, applies per-preset extraction (`extract_n26` filters internal transfers, `extract_psk` regex-parses IBAN/BIC/name from the text column, `extract_paypal` filters non-EUR and bank transfers and self-joins on transaction ID to backfill names), then `reindex`es to the canonical 17-column header. To support a new institution: add an entry to `presets.PRESETS` **and** `presets_matching.PRESETS_MATCHING` (csv_to_db aborts the whole account import if the preset has no matching entry — currently true for `n26-en`), plus an `extract_*` function in `clean_csv.py` if the source needs filtering/parsing beyond the generic col_map path.

**Matching** — two independent matchers share `functions_match.py`, which computes per-row weights in [0,1]:
- `match_records_db.py` links secondary-account records (credit card/PayPal) to a parent record on the main account. Per-preset config lives in `presets_matching.py`: `match_fields` picks which date/amount columns to compare, `match_weights` sets factor weights (note: weights are taken from the *source* preset), `match_filter` pre-filters candidate main records by regex on a text column. On a match it sets the orphan's `parent_id` and `accounting_date` (from the parent record's date) and marks it STATUS_DONE, while marking the parent STATUS_IGNORE so it isn't double-counted.
- `match_pdf.py` reads each PDF via `functions_pdf.py` (pdfminer-based `TextConverter`, first page only), extracts IBANs, amounts, dates (German month names, `de_DE` locale), invoice numbers and email domains plus filename keywords, then combines six weighted signals (weights hardcoded around line 202) into a score. Interactive mode shows the top 10 as a PyInquirer list; GUI mode runs `batch_read_pdf` in a thread while a tkinter window displays the current page.

**Database** — schema created by `setup_db.py`: `accounts` (self-referencing `parent_id`, `main_account` flag — main accounts provide the accounting date, secondary accounts get matched into them), `records` (canonical columns from clean_csv plus `parent_id`, `accounting_no`, `accounting_date`, `status`), `files` (PDF ↔ record links). `functions_db.py` holds connection helpers and insert helpers. `csv_to_db.py` appends cleaned DataFrames via `to_sql`; on import, main-account records get `accounting_date` = preset date field and STATUS_DONE, secondary records keep STATUS_NONE until matched.

Record lifecycle via `constants.py`: STATUS_NONE (0, unmatched) → STATUS_DONE (1, matched/numbered, exported by default) or STATUS_IGNORE (2, filtered out; excluded from matching and from default export).

## Conventions

- All user interaction is through PyInquirer prompts inside the scripts; scripts double as importable modules (logic in functions, `main()` only parses args), so `epu_accounting.py` imports `match_records_db.match_records(...)` directly.
- Canonical record columns are the 17-entry `header_list` in `clean_csv.py`; anything reading records assumes that shape (`get_date_cols()` in `functions_data.py` lists the date columns pandas should parse).
- DB access pattern everywhere: `create_connection`, then `with conn:` blocks with raw SQL cursors, or `pd.read_sql` into a DataFrame for matching logic.
- No tests exist; to verify a change, run the relevant script against a fixture in `examples/` and inspect the resulting DB/CSV output (see below).

## Private data and test fixtures

The repo holds real financial data. Access is blocked by deny rules and a `PreToolUse` hook (`.claude/hooks/block-sensitive.sh`, configured in `.claude/settings.json`):

- **Off-limits:** everything in `input/` and `output/`, plus any `.csv`, `.pdf`, or `.db` file outside `examples/`, whether you read it, grep it or reference it in a shell command. If a command is blocked, don't try to get around it; ask the user to run it (`! <command>`).
- **Allowed for testing:** files in `examples/` (e.g. `examples/n26-en.csv`, `examples/iban_blacklist.csv`). Use these as script inputs.
- **Temp output:** write generated files (test DBs, exported CSVs, numbered PDFs) to `examples/out/`, e.g. `python3.9 db_to_csv.py examples/out/test.db examples/out/out.csv`. Don't write outputs anywhere else.
- Refer to example files by paths starting with `examples/` (relative to the repo root). After `cd examples`, a bare `n26-en.csv` would be blocked.
