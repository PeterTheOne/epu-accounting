"""Synthetic invoice PDFs for tests/run_fixtures.py.

The harness generates them into its run folder on each run. To write them to
examples/invoices/ (the one PDF folder .gitignore allows), from the repo root:
    venv/bin/python tests/make_pdf_fixtures.py [folder, default examples/invoices]

Writes minimal single-page PDFs (Helvetica, WinAnsiEncoding) by hand, so no PDF
library is needed. The invoices are made up and match records in the fixtures:
- invoice_honorar_august.pdf: "Zweite Kundin", 1.200,00, German month name date
- invoice_shop_bestellung.pdf: "Shop GmbH" PayPal order, 20,00, numeric date
"""
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INVOICES = {
    'invoice_honorar_august.pdf': [
        'Zweite Kundin',
        'Musterstraße 1, 1010 Wien',
        'office@kundin.at',
        '',
        'Honorarnote Nr. 2026081',
        'Wien, 10. August 2026',
        '',
        'Beratung Juli/August',
        'Gesamtbetrag EUR',
        '1.200,00',
        '',
        'Bitte überweisen Sie an:',
        'IBAN: AT02 2011 1000 0000 0002',
    ],
    'invoice_shop_bestellung.pdf': [
        'Shop GmbH',
        'rechnung@shopgmbh.at',
        '',
        'Rechnung 4711-0815',
        'Bestelldatum: 01.07.2026',
        '',
        'Artikel 1 x Kabel',
        'Summe inkl. USt.',
        '20,00',
        'Bezahlt mit PayPal',
    ],
}


def pdf_string(text):
    raw = text.encode('cp1252')
    return b'(' + raw.replace(b'\\', b'\\\\').replace(b'(', b'\\(').replace(b')', b'\\)') + b')'


def make_pdf(lines):
    content = b'BT /F1 12 Tf 72 770 Td 16 TL\n'
    for line in lines:
        content += pdf_string(line) + b" '\n"
    content += b'ET\n'
    objects = [
        b'<< /Type /Catalog /Pages 2 0 R >>',
        b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
        b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] '
        b'/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>',
        b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>',
        b'<< /Length ' + str(len(content)).encode() + b' >>\nstream\n' + content + b'endstream',
    ]
    out = b'%PDF-1.4\n'
    offsets = []
    for i, obj in enumerate(objects, start=1):
        offsets.append(len(out))
        out += str(i).encode() + b' 0 obj\n' + obj + b'\nendobj\n'
    xref = len(out)
    out += b'xref\n0 ' + str(len(objects) + 1).encode() + b'\n0000000000 65535 f \n'
    for off in offsets:
        out += '{:010d} 00000 n \n'.format(off).encode()
    out += b'trailer\n<< /Size ' + str(len(objects) + 1).encode() + b' /Root 1 0 R >>\n'
    out += b'startxref\n' + str(xref).encode() + b'\n%%EOF\n'
    return out


def write_invoices(folder):
    """Write all invoices into folder; returns their paths."""
    os.makedirs(folder, exist_ok=True)
    paths = []
    for name, lines in INVOICES.items():
        path = os.path.join(folder, name)
        with open(path, 'wb') as f:
            f.write(make_pdf(lines))
        paths.append(path)
    return paths


if __name__ == '__main__':
    import sys
    folder = sys.argv[1] if len(sys.argv) > 1 else os.path.join('examples', 'invoices')
    for path in write_invoices(folder):
        print('wrote ' + path)
