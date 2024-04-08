import re
import logging
import os
from collections import Counter
from pdfminer.layout import LAParams
from hipisejm.utils.pdfminer_wrapper import PDFMinerWrapper
from hipisejm.utils.pdfminer_wrapper import PDFText, PDFLineBreak, PDFTextBoxBreak, PDFPageBreak
from hipisejm.utils.pdfminer_wrapper_helper import get_first_text_box_from_index, get_first_page_from_index
from hipisejm.stenparser.session_file_parser import SessionFileParser
from hipisejm.stenparser.transcript import SessionTranscript


class SejmParser:
    # need to force line merge due to two column layout to fix text order
    # inspired by: https://github.com/pdfminer/pdfminer.six/issues/276#issuecomment-518010761
    PDF_LINE_MARGIN = 2.0
    PDF_CHAR_MARGIN = 4.0
    PDF_BOXES_FLOW = 0.5

    """
    Parses transcripts from: https://www.sejm.gov.pl/sejm10.nsf/stenogramy.xsp
    """
    def __init__(self):
        self.number_of_pages = 0
        self.session_file_parser = SessionFileParser()

    def parse_file(self, filepath: str) -> SessionTranscript:
        """
        Parses file given from filepath.
        Returns: ???
        """
        self.number_of_pages = 0
        raw_results = self._parse_pdf_to_raw(filepath)
        if raw_results is not None:

            transcript = self.session_file_parser.run_parse(raw_results)
            transcript.set_source_filename(os.path.basename(filepath))
            return transcript

        return None

    def parse_file_to_raw(self, filepath: str):
        raw_results = self._parse_pdf_to_raw(filepath)
        return raw_results

    def _parse_pdf_to_raw(self, filepath: str):
        raw_results = []
        with open(filepath, "rb") as pdffile:
            laparams = LAParams(
                char_margin=self.PDF_CHAR_MARGIN,
                line_margin=self.PDF_LINE_MARGIN,
                boxes_flow=self.PDF_BOXES_FLOW)
            pdfminer_wrapper = PDFMinerWrapper(
                pdffile,
                laparams=laparams,
                print_parse=False)  # for DEBUG, in real life set to False!
            pdfminer_wrapper.parse()
            self.number_of_pages = pdfminer_wrapper.number_of_pages

            raw_results = pdfminer_wrapper.parsed_data
            return raw_results
        return None
