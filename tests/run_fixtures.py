"""Regression harness: run the whole pipeline on the fixtures in examples/.

Usage (from the repo root):
    venv/bin/python tests/run_fixtures.py examples/out/<run_name>

Writes every intermediate and final output to the given folder: cleaned CSVs,
histograms, classification, database table dumps, exports and legacy-script
outputs, plus log.txt (captured stdout) and prompts.txt (every prompt the user
would have seen, with its choices). Interactive prompts are answered by a
scripted fake, and "today" is pinned, so two runs of the same code produce
identical output.

Compare two runs with:
    diff -r examples/out/<baseline> examples/out/<new>
"""
import contextlib
import datetime
import os
import re
import shutil
import sqlite3
import sys
import traceback
import types

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
os.chdir(REPO)

# Settings normally read from .env; set here so results don't depend on it
# (load_dotenv() does not override variables that are already set).
os.environ['N26_OWN_ACCOUNTS'] = 'Hauptkonto,Space1'
os.environ['LOCALE'] = 'de_DE.UTF-8'

import clean_csv  # noqa: E402
import contra_histogram_csv  # noqa: E402
import text_histogram_csv  # noqa: E402
import csv_to_db  # noqa: E402
import setup_db  # noqa: E402
import match_records_db  # noqa: E402
import number_db  # noqa: E402
import db_to_csv  # noqa: E402
import functions_data  # noqa: E402
import epu_accounting  # noqa: E402
import sort_csv  # noqa: E402
import timesplit_csv  # noqa: E402
import apply_denylist  # noqa: E402
import apply_denylist_text  # noqa: E402
import apply_allowlist  # noqa: E402
import negative_rolling_sum  # noqa: E402
import sum_by_contra_csv  # noqa: E402
import match_pdf  # noqa: E402
import number_pdf  # noqa: E402
import make_pdf_fixtures  # noqa: E402  (tests/ is on sys.path when run as a script)

FIXTURES = {
    # file in examples/: preset
    'psk_paypal_fixture.csv': 'psk',
    'paypal_de_fixture.csv': 'paypal-de',
    'n26en_fixture.csv': 'n26-en',
    'n26de_fixture.csv': 'n26',
    'psk_fixture.csv': 'psk',
}
MAIN_ACCOUNTS = ['psk_paypal_fixture', 'n26en_fixture', 'n26de_fixture', 'psk_fixture']
PARENTS = {'paypal_de_fixture': 'psk_paypal_fixture'}
YEAR = '2026'
TODAY = datetime.datetime(2026, 12, 31)


# --- determinism -----------------------------------------------------------

class FixedDatetime(datetime.datetime):
    @classmethod
    def today(cls):
        return TODAY

    @classmethod
    def now(cls, tz=None):
        return TODAY


# contra_histogram_csv.calc_weight() weights records by age relative to today
contra_histogram_csv.datetime = types.SimpleNamespace(datetime=FixedDatetime)

_real_listdir = os.listdir


def sorted_listdir(path='.'):
    return sorted(_real_listdir(path))


# --- scripted prompts ------------------------------------------------------

class FakePrompt:
    """Stands in for questionary.prompt; answers by question name."""

    def __init__(self, log, out_dir):
        self.log = log
        self.out_dir = out_dir
        self.answers = {}

    def write(self, text):
        # replace the run folder so logs of different runs are comparable
        self.log.write(text.replace(self.out_dir, '<out>'))

    def __call__(self, questions, answers=None, **kwargs):
        result = {}
        for q in questions:
            choices = [c if isinstance(c, dict) else {'name': c} for c in q.get('choices', [])]
            self.write('[{}] {} {}\n'.format(q['type'], q['name'], q['message']))
            for c in choices:
                self.write('    {!r} -> {!r}\n'.format(c.get('name'), c.get('value', c.get('name'))))
            answer = self.answer(q, choices)
            validator = q.get('validate')
            if validator is not None and isinstance(validator, type):
                validator().validate(types.SimpleNamespace(text=answer))
            self.write('  answer: {!r}\n'.format(answer))
            result[q['name']] = answer
        return result

    def answer(self, q, choices):
        name = q['name']
        values = [c.get('value', c.get('name')) for c in choices]
        names = [c.get('name') for c in choices]
        if name in self.answers:
            a = self.answers[name]
            return a(q, choices) if callable(a) else a
        if name == 'preset':
            for fixture, preset in FIXTURES.items():
                if fixture in q['message']:
                    return preset
            raise ValueError('No preset for ' + q['message'])
        if name == 'parent_account':
            for child, parent in PARENTS.items():
                if "{}'s".format(child) in q['message']:
                    return parent
            raise ValueError('No parent for ' + q['message'])
        if name == 'main_accounts':
            return [n for n in names if n in MAIN_ACCOUNTS]
        if name in ('parent_record', 'selected_record'):
            return values[0]  # highest score
        if name == 'company_ibans':
            return names[:1]
        if name == 'private_texts':
            return names[:2]
        if name == 'company_texts':
            return names[:1]
        raise ValueError('Unexpected prompt ' + name)


def install_prompt(fake):
    for module in (epu_accounting, setup_db, match_records_db, functions_data, match_pdf):
        module.prompt = fake


# --- helpers ---------------------------------------------------------------

def dump_db(db_file, out_dir, prefix, run_dir=None):
    """Write each table to CSV with the csv module (independent of pandas)."""
    import csv

    def value(v):
        text = repr(v)  # repr keeps types visible (1 vs 1.0 vs '1')
        # file paths contain the run folder; replace it so runs are comparable
        return text.replace(run_dir, '<out>') if run_dir else text
    conn = sqlite3.connect(db_file)
    for table in ('accounts', 'records', 'files'):
        cur = conn.execute('SELECT * FROM {} ORDER BY id'.format(table))
        with open(os.path.join(out_dir, '{}_{}.csv'.format(prefix, table)), 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow([d[0] for d in cur.description])
            for row in cur:
                w.writerow([value(v) for v in row])
        cols = conn.execute('PRAGMA table_info({})'.format(table)).fetchall()
        with open(os.path.join(out_dir, '{}_{}_schema.txt'.format(prefix, table)), 'w') as f:
            f.write('\n'.join('{} {}'.format(c[1], c[2]) for c in cols) + '\n')
    conn.close()


def make_db(db_file, accounts):
    """Create schema and accounts without the interactive account-tree prompt."""
    if os.path.exists(db_file):
        os.remove(db_file)
    original = setup_db.query_account_tree
    setup_db.query_account_tree = lambda names: accounts
    try:
        setup_db.setup_db(db_file, [a['name'] for a in accounts])
    finally:
        setup_db.query_account_tree = original


def account(name, parent=False):
    return {'name': name, 'main_account': not parent, 'parent': parent,
            'iban': '', 'email': '', 'creditcard_no': ''}


class Runner:
    def __init__(self, out_dir, log):
        self.out_dir = out_dir
        self.log = log
        self.failures = []

    def path(self, *parts):
        p = os.path.join(self.out_dir, *parts)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        return p

    def step(self, name, fn, *args, **kwargs):
        self.log.write('\n===== {} =====\n'.format(name))
        try:
            return fn(*args, **kwargs)
        except Exception:
            self.failures.append(name)
            # drop line numbers so unrelated edits don't show up in diffs between runs
            tb = re.sub(r', line \d+,', ', line N,', traceback.format_exc())
            self.log.write('FAILED\n' + tb)
            with open(self.path('failures.txt'), 'a') as f:
                f.write('===== {} =====\n{}\n'.format(name, tb))
            return None


# --- pipeline --------------------------------------------------------------

def run(out_dir):
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir)
    log = open(os.path.join(out_dir, 'log.txt'), 'w')
    prompt_log = open(os.path.join(out_dir, 'prompts.txt'), 'w')
    fake = FakePrompt(prompt_log, out_dir)
    install_prompt(fake)
    r = Runner(out_dir, log)

    with contextlib.redirect_stdout(log):
        # 1. clean every fixture with its preset
        cleaned = {}
        for fixture, preset in FIXTURES.items():
            base = fixture[:-4]
            cleaned[base] = r.step('clean ' + fixture, clean_csv.clean_from_preset,
                                   'examples/' + fixture, r.path('clean', fixture), preset)
        psk_clean = r.path('clean', 'psk_paypal_fixture.csv')

        # 2. histograms and classification used by the wizard
        def histograms():
            data = clean_csv.clean_from_preset('examples/psk_paypal_fixture.csv', None, 'psk')
            contra = contra_histogram_csv.contra_histogram(data.copy())
            contra.to_csv(r.path('classify', 'contra_histogram.csv'), index=False)
            text = text_histogram_csv.contra_histogram(data.copy())
            text.to_csv(r.path('classify', 'text_histogram.csv'))
            classified = epu_accounting.classify_account(data.copy(), min_count=1, min_weight=0)
            classified.to_csv(r.path('classify', 'classified.csv'), index=False, date_format='%d.%m.%Y')
        r.step('histograms + classify_account', histograms)

        # 3. automatic matching on a DB built from the cleaned CSVs
        def build_auto_db(db):
            make_db(db, [account('psk_paypal_fixture'), account('n26en_fixture'),
                         account('paypal_de_fixture', 'psk_paypal_fixture')])
            for base in ('psk_paypal_fixture', 'n26en_fixture', 'paypal_de_fixture'):
                csv_to_db.import_records_from_file(r.path('clean', base + '.csv'), db, base)
            match_records_db.match_records(db, 'paypal_de_fixture', automatic=True)

        def auto_pipeline():
            db = r.path('auto', 'auto.db')
            build_auto_db(db)
            number_db.number_records(db, YEAR, 1)
            db_to_csv.export_records(db, r.path('auto', 'export_done.csv'))
            db_to_csv.export_records(db, r.path('auto', 'export_all.csv'), True, True)
            dump_db(db, r.path('auto', 'x')[:-2], 'db')
            os.remove(db)
        r.step('auto pipeline (csv_to_db, match --automatic, number, export)', auto_pipeline)

        # 4. the interactive wizard end to end, with scripted answers
        def wizard(classify):
            sub = 'wizard_classify' if classify else 'wizard'
            in_dir = r.path(sub, 'in', 'x')[:-2]
            for fixture in FIXTURES:
                shutil.copy('examples/' + fixture, os.path.join(in_dir, fixture))
            db = r.path(sub, 'wizard.db')
            fake.answers = {'input_path': in_dir, 'classify': classify, 'db_file': db}
            os.listdir = sorted_listdir  # deterministic account order
            try:
                epu_accounting.main()
            finally:
                os.listdir = _real_listdir
                fake.answers = {}
                shutil.rmtree(in_dir)
            number_db.number_records(db, YEAR, 1)
            db_to_csv.export_records(db, r.path(sub, 'export_done.csv'))
            db_to_csv.export_records(db, r.path(sub, 'export_all.csv'), True, True)
            dump_db(db, r.path(sub, 'x')[:-2], 'db')
            os.remove(db)
        # 5. invoice PDF matching (match_pdf), numbering (number_pdf) and the GUI's page rendering
        def pdf_matching(automatic):
            sub = 'pdf_auto' if automatic else 'pdf_interactive'
            in_dir = r.path(sub, 'in', 'x')[:-2]
            make_pdf_fixtures.write_invoices(in_dir)
            db = r.path(sub, 'pdf.db')
            try:
                build_auto_db(db)
                match_pdf.batch_read_pdf(db, in_dir, automatic)
                number_db.number_records(db, YEAR, 1)
                numbered = r.path(sub, 'numbered', 'x')[:-2]
                number_pdf.number_invoices(db, numbered)
                with open(r.path(sub, 'numbered.txt'), 'w') as f:
                    f.write('\n'.join(sorted(os.listdir(numbered))) + '\n')
                shutil.rmtree(numbered)
                dump_db(db, r.path(sub, 'x')[:-2], 'db', run_dir=out_dir)
            finally:
                shutil.rmtree(in_dir)
                if os.path.exists(db):
                    os.remove(db)
        r.step('match_pdf --automatic + number_pdf', pdf_matching, True)
        r.step('match_pdf (interactive) + number_pdf', pdf_matching, False)

        def pdf_render():
            # what PdfGui.set_image() does before handing the page to ImageTk
            in_dir = r.path('pdf_render', 'in', 'x')[:-2]
            try:
                with open(r.path('pdf_render', 'render.txt'), 'w') as f:
                    for path in make_pdf_fixtures.write_invoices(in_dir):
                        pages = match_pdf.convert_from_path(path, single_file=match_pdf.SINGLE_FILE,
                                                            size=match_pdf.SIZE, use_cropbox=match_pdf.USE_CROPBOX)
                        f.write('{}: {} page(s), {} {}\n'.format(os.path.basename(path), len(pages), pages[0].size, pages[0].mode))
            finally:
                shutil.rmtree(in_dir)
        r.step('pdf2image render', pdf_render)

        r.step('wizard (no classification)', wizard, False)
        r.step('wizard (with classification)', wizard, True)

        # 6. legacy CSV-only scripts on the cleaned PSK fixture
        r.step('sort_csv', sort_csv.sort_csv, psk_clean, r.path('legacy', 'sorted.csv'))
        r.step('timesplit_csv', timesplit_csv.timesplit_csv, psk_clean, r.path('legacy', 'timesplit', 'x')[:-2])
        r.step('apply_denylist', apply_denylist.apply_denylist, psk_clean, 'examples/iban_denylist.csv',
               r.path('legacy', 'denylist.csv'), drop_empty=True, allowlist_text='gebühr')
        r.step('apply_denylist --preset', apply_denylist.apply_denylist, 'examples/n26en_fixture.csv',
               'examples/iban_denylist.csv', r.path('legacy', 'denylist_preset.csv'), preset_key='n26-en')

        def denylist_text():
            deny = r.path('legacy', 'text_denylist.csv')
            with open(deny, 'w') as f:
                f.write('text\nPayPal Europe\nGebühr\n')
            apply_denylist_text.apply_denylist_text(psk_clean, deny, r.path('legacy', 'denylist_text.csv'))
        r.step('apply_denylist_text', denylist_text)

        def allowlist():
            allow = r.path('legacy', 'iban_allowlist.csv')
            with open(allow, 'w') as f:
                f.write('contra_iban\nAT02 2011 1000 0000 0002\n')
            apply_allowlist.apply_allowlist(psk_clean, allow, r.path('legacy', 'allowlist.csv'))
        r.step('apply_allowlist', allowlist)
        r.step('negative_rolling_sum', negative_rolling_sum.negative_rolling_sum, psk_clean,
               r.path('legacy', 'negative_rolling_sum.csv'))
        r.step('sum_by_contra (negative)', sum_by_contra_csv.sum_by_contra, psk_clean,
               r.path('legacy', 'sum_by_contra_negative.csv'), True, 0, None)
        r.step('sum_by_contra (positive, division)', sum_by_contra_csv.sum_by_contra, psk_clean,
               r.path('legacy', 'sum_by_contra_positive.csv'), False, 4, None)

    log.close()
    prompt_log.close()
    # replace the run folder in the log so logs of different runs are comparable
    log_path = os.path.join(out_dir, 'log.txt')
    with open(log_path) as f:
        text = f.read()
    with open(log_path, 'w') as f:
        f.write(text.replace(out_dir, '<out>'))
    print('Output written to {}'.format(out_dir))
    if r.failures:
        print('{} step(s) failed, see {}:'.format(len(r.failures), os.path.join(out_dir, 'failures.txt')))
        for f in r.failures:
            print('  - ' + f)
    return 1 if r.failures else 0


if __name__ == '__main__':
    if len(sys.argv) != 2 or not sys.argv[1].startswith('examples/out/'):
        print('Usage: tests/run_fixtures.py examples/out/<run_name>')
        sys.exit(2)
    sys.exit(run(sys.argv[1]))
