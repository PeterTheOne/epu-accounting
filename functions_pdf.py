from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import PDFConverter
from pdfminer.cmapdb import CMapDB
from pdfminer.layout import LAParams, LTContainer, LTText, LTTextBox, LTImage

# todo: OCR fallback
#import textract

# todo: try TagConverter?

class TextConverter(PDFConverter):

    def __init__(self, rsrcmgr, outfp, pageno=1, laparams=None,
                 showpageno=False, imagewriter=None):
        PDFConverter.__init__(self, rsrcmgr, outfp, pageno=pageno, laparams=laparams)
        self.showpageno = showpageno
        self.imagewriter = imagewriter
        self.outtext = ''

    def write_text(self, text):
        #self.outfp.write(text)
        self.outtext += text

    def get_text(self):
        return self.outtext

    def receive_layout(self, ltpage):
        def render(item):
            if isinstance(item, LTContainer):
                for child in item:
                    render(child)
            elif isinstance(item, LTText):
                self.write_text(item.get_text())
            if isinstance(item, LTTextBox):
                self.write_text('\n')
            elif isinstance(item, LTImage):
                if self.imagewriter is not None:
                    self.imagewriter.export_image(item)
        if self.showpageno:
            self.write_text('Page %s\n' % ltpage.pageid)
        render(ltpage)
        self.write_text('\f')
        return

    # Some dummy functions to save memory/CPU when all that is wanted
    # is text.  This stops all the image and drawing output from being
    # recorded and taking up RAM.
    def render_image(self, name, stream):
        if self.imagewriter is None:
            return
        PDFConverter.render_image(self, name, stream)
        return

    def paint_path(self, gstate, stroke, fill, evenodd, path):
        return


def extract_text_pdf(filename):
    # debug option
    debug = 0
    # input option
    password = b''
    pagenos = set()
    maxpages = 1
    # output option
    imagewriter = None
    rotation = 0
    caching = True
    laparams = LAParams()
    #
    PDFDocument.debug = debug
    PDFParser.debug = debug
    CMapDB.debug = debug
    PDFPageInterpreter.debug = debug
    #
    rsrcmgr = PDFResourceManager(caching=caching)
    outfp = None
    device = TextConverter(rsrcmgr, outfp, laparams=laparams,
                           imagewriter=imagewriter)
    with open(filename, 'rb') as file:
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.get_pages(file, pagenos,
                                      maxpages=maxpages, password=password,
                                      caching=caching, check_extractable=True):
            page.rotate = (page.rotate+rotation) % 360
            interpreter.process_page(page)
    text = device.get_text()
    device.close()
    #outfp.close()

    return text
