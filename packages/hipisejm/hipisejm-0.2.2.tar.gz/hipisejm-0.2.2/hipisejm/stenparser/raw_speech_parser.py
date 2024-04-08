import logging
import re
from hipisejm.stenparser.transcript import SessionSpeech, SpeechInterruption, SpeechReaction
from hipisejm.utils.pdfminer_wrapper_helper import remove_all_tags


class RawSpeechParser:
    """
    Helper class to parse raw text speech
    """
    def __init__(self):
        pass

    def parse_raw_speech(self, speaker_name: str, raw_speech_txt: str) -> SessionSpeech:
        speech = SessionSpeech(speaker_name)

        raw_speech_txt = self._preprocess_raw_speech(raw_speech_txt)

        speech_raw_parts = re.split(r"([(][^)]+[)])", raw_speech_txt)
        current_txt = ""

        for part in speech_raw_parts:
            if self._can_speech_part_be_interruption_or_reaction(part):
                # in such case need to save current text
                if len(current_txt) > 0:
                    self._add_speech_text_to_speech(speech, current_txt)
                    current_txt = ""

                interruption = self._convert_speech_part_to_interruption(part)
                if interruption is not None:
                    speech.add_interruption(interruption)
                else:
                    reaction = self._convert_speech_part_to_reaction(part)
                    if reaction is not None:
                        speech.add_reaction(reaction)
                    else:
                        message = f"Unable to parse reaction or interruption: {part}"
                        logging.info("Reaction or interruption parsing error near: %s", message)
                        continue
            else:
                # probably regular text
                current_txt = current_txt + part

        if len(current_txt) > 0:
            self._add_speech_text_to_speech(speech, current_txt)


        return speech

    def _preprocess_raw_speech(self, raw_speech_txt):
        raw_speech_txt = re.sub(r'<i>\s*</i>', ' ', raw_speech_txt)
        raw_speech_txt = re.sub(r'<b>\s*</b>', ' ', raw_speech_txt)

        # remove some special parts
        raw_speech_txt = re.sub(r"Teksty\s+wystąpień\s+niewygłoszonych.*", "", raw_speech_txt)
        raw_speech_txt = re.sub(r"[*][)]", " ", raw_speech_txt)

        raw_speech_txt = self._fix_spaces(raw_speech_txt)
        return raw_speech_txt

    def _add_speech_text_to_speech(self, speech, speech_txt):
        speech_txt = re.sub(r"</?[ib]>", "", speech_txt)
        speech_txt = self._fix_spaces(speech_txt)
        if len(speech_txt) > 0:
            speech.add_speech_text(speech_txt)

    def _can_speech_part_be_interruption_or_reaction(self, part: str) -> bool:
        if len(part) < 3:
            return False

        if not (part[0] == '(' and part[-1] == ')'):
            return False

        if not '<i>' in part:
            return False

        return True

    def _convert_speech_part_to_interruption(self, part):
        match = re.match(r"^[(]<i>(?P<speaker>.*?)(?:</i>\s*:\s*|:\s*</i>|(?:</i>\s*(?P<broken_font>[A-Za-zĄŻŚŹĘĆÓŁŃ][a-zążśźęćółń]+)\s*:))(?P<text>.*)[)]$", part)
        if match:
            speaker = match.group('speaker')
            broken_font = match.group('broken_font')
            if broken_font:
                speaker = speaker + ' ' + broken_font

            interrupted_by = self._fix_interruption_by(speaker)

            interruption_text = self._fix_spaces(match.group('text'))

            # other italic tags should not occur in interruption
            # if there is italic tag, then maybe something is wrong with the parse
            if '<i>' in interruption_text:
                return None
            return SpeechInterruption(interrupted_by, interruption_text)

        return None

    def _convert_speech_part_to_reaction(self, part):
        # Workaround for such case:
        # (<i>Oklaski</i>, <i>część posłów wstaje</i>)
        part = re.sub(r"</i>\s*,\s*<i>", ", ", part)
        part = re.sub(r"</i>\s*<i>", " ", part)

        match = re.match(r"^[(]<i>(.*)</i>([^<>]*)[)]$", part)
        if match:
            reaction_txt = match.group(1)

            additional_non_italic = match.group(2)

            # if there are multiple <i> tags in parens, then possibly this is something different than
            # audience reaction
            if '<i>' in reaction_txt:
                return None

            # sometimes some parts of the reaction are not in italic
            # this is workaround for such cases:
            # (<i>Wicemarszałek wyłącza mikrofon, poseł przemawia przy wyłączonym </i>mikrofonie)
            if additional_non_italic:
                if len(additional_non_italic) > len(reaction_txt):
                    return None
                reaction_txt = f"{reaction_txt} {additional_non_italic}"

            reaction_txt = self._fix_spaces(reaction_txt)
            return SpeechReaction(reaction_txt)

        return None

    def _fix_interruption_by(self, txt: str) -> str:
        txt = remove_all_tags(txt)
        txt = self._fix_spaces(txt)
        return txt

    def _fix_spaces(self, txt):
        txt = re.sub(r"^\s+", "", txt)
        txt = re.sub(r"\s+$", "", txt)
        txt = re.sub(r"\s+", " ", txt)
        return txt
