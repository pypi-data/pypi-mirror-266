"""
Wraps some PDFMiner functions to simplify text extraction
"""
import re
import logging
from typing import BinaryIO, Tuple
from functools import lru_cache
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LAParams, LTTextBox, LTTextLine, LTChar
from pdfminer.pdfparser import PDFParser
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage


@lru_cache(maxsize=100)
def clean_fontname(fontname: str) -> str:
    """
    Returns fontname without hashed prefix, e.g.:
    UYJZJF+CentSchbookEU-Normal -> CentSchbookEU-Normal
    """
    fontname = re.sub(r"^[A-Z]+[+]", "", fontname)
    return fontname


@lru_cache(maxsize=100)
def get_fontname_bold_italic_flags(fontname: str) -> Tuple[bool, bool]:
    """ Returns (flag_bold, flag_italic) for given PDF fontname"""
    flag_bold = False
    flag_italic = False

    match = re.search(r"-([^-]+)$", fontname)
    if match:
        matched = match.group(1).lower()
        if "bold" in matched:
            flag_bold = True
        if "italic" in matched:
            flag_italic = True

    return (flag_bold, flag_italic)


class PDFText:
    """
    This represents continuous text fragment, with the same fontname and height.
    """
    def __init__(self, text: str, fontname: str, height: float):
        self.text = text
        self.fontname = fontname
        self.height = height
        self.bold, self.italic = get_fontname_bold_italic_flags(self.fontname)

    def __str__(self):
        return f"{self.text}|(font:{self.fontname},height:{self.height})"

    def __repr__(self):
        return str(self)


class PDFLineBreak:
    """
    Represents line break.
    """
    def __init__(self):
        pass

    def __str__(self):
        return "<PDFLineBreak>"

    def __repr__(self):
        return str(self)


class PDFTextBoxBreak:
    """
    Represents text box break.
    """
    def __init__(self, x0: float = None, y0: float = None):
        self.x0 = x0
        self.y0 = y0

    def __str__(self):
        return f"<PDFTextBoxBreak: ({self.x0}, {self.y0})>"

    def __repr__(self):
        return str(self)


class PDFPageBreak:
    """
    Represents page break.
    """
    def __init__(self):
        pass

    def __str__(self):
        return "<PDFPageBreak>"

    def __repr__(self):
        return str(self)


class PDFMinerWrapper:
    def __init__(self, file_to_parse: BinaryIO, laparams: LAParams = None, print_parse: bool = False, page_limit: int = 0):
        """
        params:
        filepath - file to be parsed
        laparams - if None, then uses PDFMiner default LAParams, otherwise uses LAParams provided here
        print_parse - if True then prints parsed entries to stdout which helps debuging
        page_limit - if set to non-zero then parses only 'page_limit' first pages of the PDF
        """
        self.parsed_data = []
        self.number_of_pages = 0
        self.print_parse = print_parse
        self.page_limit = page_limit

        self.pdf_parser = PDFParser(file_to_parse)
        self.resource_manager = PDFResourceManager()

        self.dev = PDFPageAggregator(self.resource_manager, laparams=laparams)
        self.intepreter = PDFPageInterpreter(self.resource_manager, self.dev)

    def parse(self):
        self.parsed_data = []
        self.number_of_pages = 0

        document = PDFDocument(self.pdf_parser)
        for pdf_page in PDFPage.create_pages(document):
            if self.page_limit > 0 and self.number_of_pages > self.page_limit:
                break
            self.number_of_pages += 1

            logging.debug("Parsing PDF page %i", self.number_of_pages)

            self.intepreter.process_page(pdf_page)
            layout = self.dev.get_result()

            for element in layout:
                if isinstance(element, LTTextContainer):
                    self._parse_text_container(element)

            self._add_to_parsed_data(PDFPageBreak())

    def _parse_text_container(self, text_container):
        # TODO
        # 1. zrobić test na odrzucanie containerów, linii
        # np. odrzucić nagłówki
        for text_line in text_container:
            if not isinstance(text_line, LTTextLine):
                continue

            current_fontname = None
            chunk = []
            for character in text_line:
                if not isinstance(character, LTChar):
                    continue

                character_fontname = clean_fontname(character.fontname)
                if (current_fontname is not None) and (current_fontname != character_fontname):
                    self._new_pdf_text(chunk, current_fontname, text_line)
                    current_fontname = character_fontname
                    chunk = [character.get_text()]
                else:
                    current_fontname = character_fontname
                    chunk.append(character.get_text())
            if len(chunk) > 0:
                self._new_pdf_text(chunk, current_fontname, text_line)

            self._add_to_parsed_data(PDFLineBreak())
        self._add_to_parsed_data(PDFTextBoxBreak(text_container.x0, text_container.y0))

    def _new_pdf_text(self, chunk, current_fontname, text_line):
        text = "".join(chunk)
        entry = PDFText(text, current_fontname, text_line.height)
        self._add_to_parsed_data(entry)

    def _add_to_parsed_data(self, what):
        if self.print_parse:
            print(str(what))
        self.parsed_data.append(what)
