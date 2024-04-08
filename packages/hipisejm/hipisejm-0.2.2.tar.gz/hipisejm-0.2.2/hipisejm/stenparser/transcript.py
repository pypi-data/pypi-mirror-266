from collections import defaultdict
import xml.etree.ElementTree as ET
from xml.dom import minidom


class SessionOfficials:
    """
    This class represents officials of the sessions like Marszałek, Marszałek senior and Wicemarszałek
    """
    def __init__(self):
        self.officials_list = []
        self.role_to_officials = defaultdict(list)

    def add_new(self, role_name, person_name):
        new_entry = (role_name, person_name)
        self.role_to_officials[role_name].append(new_entry)
        self.officials_list.append(new_entry)

    def __str__(self):
        chunks = ["Session officials:"]
        for entry in self.officials_list:
            chunks.append(f"  {entry[0]}: {entry[1]}")
        return "\n".join(chunks)

    def to_xml(self, parent_tag):
        for official in self.officials_list:
            ET.SubElement(parent_tag, "official", title=official[0], name=official[1])

    def get_by_role(self, role_name: str):
        """
        Returns list of entries for persons with given role on the session.
        If there is no such role during the session then returns empty list.
        """
        return self.role_to_officials.get(role_name, [])


class SpeechReaction:
    """
    Reactions are spontanous interruptions of the speech without particular speaker
    Can be something like appluase, noise, laugh, etc...
    """
    def __init__(self, reaction_text: str):
        self.reaction_text = reaction_text

    def to_xml(self, parent_tag):
        ET.SubElement(parent_tag, "utt", t="reaction").text = self.reaction_text


class SpeechInterruption:
    """
    Interruptions are from the audience and particular speaker
    Sometimes the speaker is unknown ("Głos z sali") or refers to multiple persons speaking
    """
    def __init__(self, interrupted_by_speaker: str, text: str):
        self.interrupted_by_speaker = interrupted_by_speaker
        self.text = text

    def to_xml(self, parent_tag):
        ET.SubElement(parent_tag, "utt", t="interrupt", by=self.interrupted_by_speaker).text = self.text


class SessionSpeech:
    """
    Speech is the one uninterrupted sequence of utterance of the given person.
    Speech consists of:
    - utterances of the speaker
    - intteruptions from the audience
    - reactions
    """
    def __init__(self, speaker: str):
        self.speaker = speaker
        self.content = []
        # memoization of the bare speech without interruptions
        self.bare_content = None

    def add_speech_text(self, text: str):
        self.bare_content = None
        self.content.append(text)

    def get_bare_content(self):
        if self.bare_content is None:
            chunks = []
            for cont in self.content:
                if isinstance(cont, str):
                    chunks.append(cont)
            self.bare_content = "".join(chunks)
        return self.bare_content

    def add_interruption(self, interruption: SpeechInterruption):
        self.content.append(interruption)

    def add_reaction(self, reaction: SpeechReaction):
        self.content.append(reaction)

    def to_xml(self, parent_tag):

        speech_tag = ET.SubElement(parent_tag, "speech", speaker=self.speaker)
        for entry in self.content:
            if isinstance(entry, str):
                ET.SubElement(speech_tag, "utt", t="norm").text = entry
            else:
                entry.to_xml(speech_tag)


class SessionTranscript:
    """
    Session Transcript stores all speeches from the given session.
    """
    def __init__(self):
        self.session_officials = SessionOfficials()
        self.session_content = []
        self.session_no = None
        self.term_no = None
        self.session_date = None
        self.source_filename = None

    def dump_to_xml(self, filepath: str= None):
        session_tag = ET.Element("session", source=self.source_filename)

        meta_tag = ET.SubElement(session_tag, "meta")

        ET.SubElement(meta_tag, "session_no").text = str(self.session_no)
        ET.SubElement(meta_tag, "term_no").text = str(self.term_no)
        ET.SubElement(meta_tag, "session_date").text = self.session_date

        session_officials_tag = ET.SubElement(session_tag, "session_officials")
        self.session_officials.to_xml(session_officials_tag)

        content_tag = ET.SubElement(session_tag, "content")
        for speech in self.session_content:
            speech.to_xml(content_tag)

        tree_str = ET.tostring(session_tag, 'utf-8')
        pretty_xml = minidom.parseString(tree_str).toprettyxml(indent="  ")

        with open(filepath, "w") as f:
            f.write(pretty_xml)
            f.write("\n")
        return

    def load_from_xml(self, filepath: str):
        xml_tree = ET.parse(filepath)

        session_tag = xml_tree.getroot()

        self.source_filename = session_tag.get("source")

        self._load_xml_meta_tag(session_tag.find("meta"))
        self._load_xml_session_officials_tag(session_tag.find("session_officials"))
        self._load_xml_content_tag(session_tag.find("content"))

    def set_source_filename(self, source_filename: str):
        self.source_filename = source_filename

    def __str__(self):
        chunks = []
        chunks.append(str(self.session_officials))
        return "\n".join(chunks)

    def add_speech(self, speech: SessionSpeech):
        self.session_content.append(speech)

    def _load_xml_meta_tag(self, meta_tag):
        session_no_tag = meta_tag.find("session_no")
        if session_no_tag is not None:
            self.session_no = int(session_no_tag.text)
        session_date_tag = meta_tag.find("session_date")
        if session_date_tag is not None:
            self.session_date = session_date_tag.text
        term_no_tag = meta_tag.find("term_no")
        if term_no_tag is not None:
            self.term_no = int(term_no_tag.text)

    def _load_xml_session_officials_tag(self, session_officials_tag):
        for official_tag in session_officials_tag.findall("official"):
            self.session_officials.add_new(official_tag.get("title"), official_tag.get("name"))

    def _load_xml_content_tag(self, content_tag):
        for speech_tag in content_tag.findall("speech"):
            speech = SessionSpeech(speech_tag.get("speaker"))
            for utt_tag in speech_tag.findall("utt"):
                if utt_tag.get("t") == "norm":
                    speech.add_speech_text(utt_tag.text)
                elif utt_tag.get("t") == "reaction":
                    speech.add_reaction(SpeechReaction(utt_tag.text))
                elif utt_tag.get("t") == "interrupt":
                    speech.add_interruption(SpeechInterruption(utt_tag.get("by"), utt_tag.text))
            self.add_speech(speech)
