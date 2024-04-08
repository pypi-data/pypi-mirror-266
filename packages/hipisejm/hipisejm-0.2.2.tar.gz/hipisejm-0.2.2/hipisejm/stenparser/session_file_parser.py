import math
import re
from hipisejm.stenparser.transcript import SessionTranscript
from hipisejm.stenparser.raw_speech_parser import RawSpeechParser
from hipisejm.utils.pdfminer_wrapper import PDFText, PDFLineBreak, PDFTextBoxBreak, PDFPageBreak
from hipisejm.utils.pdfminer_wrapper_helper import get_first_text_box_from_index, get_first_page_from_index, extract_text_from_parsed_list, remove_all_tags
from hipisejm.utils.roman_numbers import roman_to_arabic
from hipisejm.utils.polish_dates import convert_polish_date_to_iso, find_polish_dates_in_text


class SejmParseError(Exception):
    """Raised when parse is not possible"""
    def __init__(self, message="Sejm Parsing error"):
        self.message = message
        super().__init__(self.message)


class SessionFileParser:
    SPEAKER_NAME_FONT_HEIGHT = 12.0
    FONT_HEIGHT_TOLLERANCE = 0.01
    MAX_TEXT_BOX_Y_COORD = 784.0

    def __init__(self):
        self.parse_cache = dict()
        self.raw_speech_parser = RawSpeechParser()
        self._clear_parse_cache()

    def run_parse(self, raw_data) -> SessionTranscript:
        self._get_transcript_metadata_from_first_page(raw_data)
        current_data = self._leave_only_transcript_data(raw_data)
        current_data = self._extract_initial_who_leads(current_data)

        page_no = 0
        while(len(current_data) > 0):
            page_no += 1

            current_page = get_first_page_from_index(current_data, 0, with_breaking_box=False)
            list_of_boxes = self._fix_page(current_page, page_no)

            for text_boxes in list_of_boxes:
                self._process_transcript_parse_on_page(text_boxes)
                # need to add artificial page break to current speech entries if non empty
                if len(self.parse_cache['current_speech_entries']) > 0:
                    self.parse_cache['current_speech_entries'].append(PDFPageBreak())

            current_data = current_data[len(current_page) + 1:]

        # need to save last speech
        self._save_current_speech()

        result_transcript = self.parse_cache['transcript']
        self._clear_parse_cache()
        return result_transcript

    def _get_transcript_metadata_from_first_page(self, raw_data):
        first_page = get_first_page_from_index(raw_data, 0, with_breaking_box=True)
        first_page_text = extract_text_from_parsed_list(first_page, with_font_styles_tags=True)

        transcript = self.parse_cache['transcript']
        for line in first_page_text.split("\n"):
            match_term = re.search(r"kadencja\s+([XIV]+)\b", line, re.IGNORECASE)
            if match_term:
                term_roman = match_term.group(1)
                term_no = roman_to_arabic(term_roman)
                transcript.term_no = term_no
            else:
                match_session_no = re.search(r"\b(\d+)[.]\s*posiedze", line, re.IGNORECASE)
                if match_session_no:
                    session_no = int(match_session_no.group(1))
                    transcript.session_no = session_no

                all_dates_str = find_polish_dates_in_text(line)
                if len(all_dates_str) > 0:
                    session_date = convert_polish_date_to_iso(all_dates_str[0])
                    transcript.session_date = session_date

            if transcript.term_no is not None and transcript.session_no is not None and transcript.session_date is not None:
                return

    def _fix_page(self, current_page, page_no):
        """
        Removes headers. Fixes text box order.
        Returns ordered text boxes to parse.
        """
        text_boxes = self._convert_raw_parse_to_list_of_text_box_entries(current_page)
        text_boxes = self._remove_header_text_boxes(text_boxes)
        left_text_boxes, right_text_boxes = self._order_text_boxes_in_two_columns(text_boxes)

        list_of_boxes = [left_text_boxes, right_text_boxes]
        return list_of_boxes

    def _convert_raw_parse_to_list_of_text_box_entries(self, entries):
        text_boxes = []
        while len(entries) > 0:
            current_text_box = get_first_text_box_from_index(entries, 0, with_breaking_box=True)

            if isinstance(current_text_box[-1], PDFTextBoxBreak):
                text_box_entry = (current_text_box, current_text_box[-1])
                text_boxes.append(text_box_entry)
            else:
                # sometimes some orphaned entries are left in the back, let's ignore them
                pass

            entries = entries[len(current_text_box):]
        return text_boxes

    def _remove_header_text_boxes(self, text_boxes):
        nonheader_text_boxes = []
        for text_box_entry in text_boxes:
            text_box = text_box_entry[1]
            if text_box.y0 > self.MAX_TEXT_BOX_Y_COORD:
                continue
            nonheader_text_boxes.append(text_box_entry)
        return nonheader_text_boxes

    def _order_text_boxes_in_two_columns(self, text_boxes):
        left_column = []
        right_column = []
        ordered_left_column = []
        ordered_right_column = []
        for e in text_boxes:
            if e[1].x0 > 200.0:
                right_column.append(e)
            else:
                left_column.append(e)

        for e in sorted(left_column, key=lambda x: -int(x[1].y0)):
            ordered_left_column.append(e)

        for e in sorted(right_column, key=lambda x: -int(x[1].y0)):
            ordered_right_column.append(e)

        return ordered_left_column, ordered_right_column

    def _process_transcript_parse_on_page(self, text_boxes):
        for text_box_entry in text_boxes:
            current_text_box = text_box_entry[0]
            self._parse_next_transcript_text_box(current_text_box)

    def _clear_parse_cache(self):
        self.parse_cache = dict()
        self.parse_cache['in_general_transcript'] = False
        self.parse_cache['transcript'] = SessionTranscript()
        self._clear_current_speech()

    def _clear_current_speech(self):
        self.parse_cache['current_speaker_entries'] = []
        self.parse_cache['new_speaker_entries'] = []
        self.parse_cache['current_speech_entries'] = []

    def _leave_only_transcript_data(self, raw_data):
        start_index = -1
        end_index = -1

        for i, entry in enumerate(raw_data):
            if isinstance(entry, PDFText):
                if start_index < 0:
                    match_poczatek = re.search(r"(?:Początek|Wznowienie)\s+posiedzenia\s+o\s+godz.(.*)", entry.text)
                    if match_poczatek:
                        # TODO wczytać początek posiedzenia
                        start_index = i
                elif end_index < 0:
                    match_koniec = re.search(r"(?:Przerwa\s+w\s+posiedzeniu|Koniec\s+posiedzenia)\s+o\s+godz.(.*)", entry.text)
                    if match_koniec:
                        # TODO wczytać koniec posiedzenia
                        end_index = i
                        # don't need to parse rest
                        break

        if start_index < 0 or end_index < 0:
            raise SejmParseError
        return raw_data[start_index:end_index]

    def _extract_initial_who_leads(self, current_data):
        first_box = get_first_text_box_from_index(current_data, 0, with_breaking_box=True)
        # first box is information about start time so we can skip it
        # let's extract next one which should contain information about who leads
        who_leads_box = get_first_text_box_from_index(current_data[len(first_box):], 0, with_breaking_box=True)

        who_leads_box_text = extract_text_from_parsed_list(who_leads_box)

        if re.search(r"Na posiedzeniu przewodnicz[ąy]", who_leads_box_text, re.IGNORECASE):
            match_speaker = re.search(
                r"[Mm](?:arszałek|arszałkini) [Ss]ejmu ((?:[A-ZĄŻŚŹĘĆÓŁŃ][a-zążśźęćółń]+[ -]?)+)",
                who_leads_box_text)
            if match_speaker:
                self._add_parsed_official("speaker", match_speaker.group(1))

            match_vice = re.search(
                r"[wW](?:icemarszałek|icemarszałkini|icemarszałkowie)\s+(?:Sejmu?\s*)?([A-ZĄŻŚŹĘĆÓŁŃa-zążśźęćółń, -]+)[)]",
                who_leads_box_text)
            if match_vice:
                self._add_parsed_official_list("vice_speaker", match_vice.group(1))
        else:
            raise SejmParseError(message=f"Unexpected form of introduction of leaders of the session: {who_leads_box_text}")

        index_to_cut = len(who_leads_box_text)
        for i, entry in enumerate(who_leads_box):
            if isinstance(entry, PDFText):
                if entry.text.startswith(')'):
                    index_to_cut = i + 1
                    break

        rest_to_parse = current_data[len(first_box) + index_to_cut:]
        return rest_to_parse

    def _normalize_text(self, text):
        text = re.sub(r"^\s+", "", text)
        text = re.sub(r"\s+$", "", text)
        text = re.sub(r"\s+", " ", text)
        return text

    def _is_text_matches_person_name(self, text):
        return re.match(r"(?:[A-ZĄŻŚŹĘĆÓŁŃ][a-zążśźęćółń]+[ -]?)+", text)

    def _add_parsed_official(self, role_name, raw_name_txt):
        person_name = self._normalize_text(raw_name_txt)
        if self._is_text_matches_person_name(person_name):
            self.parse_cache['transcript'].session_officials.add_new(role_name, person_name)

    def _add_parsed_official_list(self, role_name, raw_name_txt):
        for chunk in re.split(r"(?:, | i )", raw_name_txt):
            self._add_parsed_official(role_name, chunk)

    def _parse_next_transcript_text_box(self, text_box_list):
        prev_entry = None
        in_new_speaker_part = False
        for entry, next_entry in zip(text_box_list, text_box_list[1:] + [None]):
            if in_new_speaker_part:
                # all non text entries are automatically added to new speaker entries
                # if we found first text which marks beginning of the new speaker name
                if not isinstance(entry, PDFText):
                    self.parse_cache['new_speaker_entries'].append(entry)
                    continue

            if self._is_new_speaker_mark(prev_entry, entry, next_entry):
                in_new_speaker_part = True
                self.parse_cache['new_speaker_entries'].append(entry)
            else:
                if in_new_speaker_part:
                    in_new_speaker_part = False
                    self._save_current_speech()
                    self._start_new_speech()
                self._add_entry_to_current_speech(entry)

            # for next iteration:
            prev_entry = entry

        if in_new_speaker_part:
            in_new_speaker_part = False
            self._save_current_speech()
            self._start_new_speech()

    def _is_new_speaker_mark(self, prev_entry, entry, next_entry):
        """
        Speaker in PDF is marked with full bold text.
        """
        if isinstance(entry, PDFText):
            if entry.bold and math.isclose(entry.height, self.SPEAKER_NAME_FONT_HEIGHT, rel_tol=self.FONT_HEIGHT_TOLLERANCE):
                if next_entry is None or isinstance(next_entry, PDFLineBreak):
                    if prev_entry is None \
                        or isinstance(next_entry, PDFLineBreak) \
                        or isinstance(next_entry, PDFPageBreak):
                        return True

        return False

    def _save_current_speech(self):
        speaker_raw_name = extract_text_from_parsed_list(self.parse_cache['current_speaker_entries'])

        speech_txt = self._convert_speech_entries_to_raw_speech()
        self.parse_cache['current_speaker_entries'] = self.parse_cache['new_speaker_entries']

        if re.match(r"^\s*$", speaker_raw_name):
            if not re.match(r"^\s*(?:<[ib]>)*\s*(?:</[ib]>)*\s*$", speech_txt):

                # special case if there is empty speaker but there are no speeches yet
                # and the speech txt is in parens then maybe there are some additional reactions in the initial part of the file
                # we can omit them
                if len(self.parse_cache['transcript'].session_content) == 0 and re.match(r"^\s*[(].*[)]\s*$", speech_txt):
                    return
                else:
                    raise SejmParseError(message=f"Non empty speech for empty speaker: {speech_txt}")

            return

        speaker_clear_name = self._fix_speaker_name(speaker_raw_name)
        parsed_speech = self.raw_speech_parser.parse_raw_speech(speaker_clear_name, speech_txt)

        self.parse_cache['transcript'].add_speech(parsed_speech)

    def _convert_speech_entries_to_raw_speech(self):
        speech_entries = []

        new_page = False
        for entry in self.parse_cache['current_speech_entries']:
            if isinstance(entry, PDFPageBreak):
                new_page = True
                continue

            if new_page:
                # need to fix begining of the speech after new page
                # remove of page no entries
                # remove repetition of the speaker name
                if isinstance(entry, PDFText):
                    if re.match(r"^\d\d?\d?\d?$", entry.text):
                        # page no! keep removal
                        pass
                    elif entry.bold and not math.isclose(entry.height, self.SPEAKER_NAME_FONT_HEIGHT, rel_tol=self.FONT_HEIGHT_TOLLERANCE):
                        # speaker repetition - keep removing!
                        pass
                    else:
                        new_page = False

                if new_page:
                    continue

            speech_entries.append(entry)

        raw_speech = extract_text_from_parsed_list(speech_entries, with_font_styles_tags=True)
        return raw_speech

    def _fix_speaker_name(self, raw_name):
        raw_name = re.sub(r"^\s+", "", raw_name)
        raw_name = re.sub(r"\s+$", "", raw_name)
        raw_name = re.sub(r"[:]+", "", raw_name)
        raw_name = re.sub(r"\s+", " ", raw_name)

        if raw_name == 'Marszałek':
            sejm_speaker_names = self.parse_cache['transcript'].session_officials.get_by_role('speaker')
            if len(sejm_speaker_names) > 0:
                raw_name = 'Marszałek ' + sejm_speaker_names[0][1]

        # remove tags if any are left
        raw_name = remove_all_tags(raw_name)
        return raw_name

    def _start_new_speech(self):
        self.parse_cache['new_speaker_entries'] = []
        self.parse_cache['current_speech_entries'] = []

    def _add_entry_to_current_speech(self, entry):
        self.parse_cache['current_speech_entries'].append(entry)
