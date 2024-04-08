import re
from hipisejm.utils.pdfminer_wrapper import PDFText, PDFLineBreak, PDFTextBoxBreak, PDFPageBreak


def get_first_text_box_from_index(raw_parsed_list, index=0, with_breaking_box=False):
    return get_first_pdf_container_from_index(PDFTextBoxBreak, raw_parsed_list, index=index, with_breaking_box=with_breaking_box)


def get_first_page_from_index(raw_parsed_list, index=0, with_breaking_box=False):
    return get_first_pdf_container_from_index(PDFPageBreak, raw_parsed_list, index=index, with_breaking_box=with_breaking_box)


def get_first_pdf_container_from_index(pdf_container_type, raw_parsed_list, index=0, with_breaking_box=False):
    """
    Extracts all entries between <ContainerBreak>
    which surrounds given index.
    If index points out to ContainerBreak
    then returns all elements in the container before it.
    Params:
       pdf_container_type - PDFTextBoxBreak, PDFLineBreak or PDFPageBreak
       raw_parsed_list - list of elements to get text box
       index - index to check for surrounding elements
       with_breaking_box - if set to True then last extracted index is breaking (closing) Element (useful to get metadata from it)
    """
    assert pdf_container_type in [PDFTextBoxBreak, PDFLineBreak, PDFPageBreak]

    result = []
    after_elements = []
    before_elements = []

    if not isinstance(raw_parsed_list[index], pdf_container_type):
        for entry in raw_parsed_list[index+1:]:
            if isinstance(entry, pdf_container_type):
                if with_breaking_box:
                    after_elements.append(entry)
                break
            else:
                after_elements.append(entry)
        result.append(raw_parsed_list[index])
    else:
        if with_breaking_box:
            result.append(raw_parsed_list[index])

    if index > 0:
        for entry in reversed(raw_parsed_list[:index]):
            if isinstance(entry, pdf_container_type):
                break
            else:
                before_elements.append(entry)

    result = list(reversed(before_elements)) + result + after_elements
    return result


def extract_text_from_parsed_list(raw_parsed_list, with_font_styles_tags: bool = False) -> str:
    """
    Extracts text from parsed list. Returns text.
    Fixes problems with line breaks like:
    - word splits
    - line breaks (if line break occurs then space is introduced) -> newline is not introduced
    - text box breaks - adds newline here
    - page breaks - adds additional newline here
    Params:
    with_font_styles_tags - if True, then surround italic and bold with <i> and <b> tags (for further extraction)
    """
    result_chunks = []
    for entry in raw_parsed_list:
        if isinstance(entry, PDFText):
            dump_text = entry.text
            if with_font_styles_tags:
                if entry.bold:
                    dump_text = f"<b>{dump_text}</b>"
                if entry.italic:
                    dump_text = f"<i>{dump_text}</i>"
            result_chunks.append(dump_text)
        else:
            if isinstance(entry, PDFLineBreak):
                # fix word splits
                was_word_split = False
                if len(result_chunks) > 0:
                    last_chunk = result_chunks[-1]
                    if len(last_chunk) > 1:    # should be something which is at least longer than one letter to avoid removing single dash
                        match = re.search("-(</i>$|</b>$|</b></i>)?$", last_chunk)
                        if match:
                            matched_part = match.group(1)
                            if matched_part is None:
                                matched_part = ''
                            fixed_last_chunk = last_chunk[:-(1+len(matched_part))]
                            if len(matched_part):
                                fixed_last_chunk += matched_part
                            fixed_last_chunk = fixed_last_chunk + '<WORD_SPLIT>'
                            was_word_split = True
                            result_chunks[-1] = fixed_last_chunk
                if not was_word_split:
                    # add space only if previous one was not ending with a space
                    if len(result_chunks) > 0 and len(result_chunks[-1]) > 0 and (not re.match(r" (?:</i>|</b>|</b></i>)?$", result_chunks[-1][-1])):
                        result_chunks.append(" ")
            elif isinstance(entry, PDFTextBoxBreak):
                result_chunks.append("\n")
            elif isinstance(entry, PDFPageBreak):
                result_chunks.append("\n")
            else:
                raise ValueError(f"unknown instance in parsed entry: {entry}")

    result = "".join(result_chunks)

    # remove word splits
    result = re.sub(r"<WORD_SPLIT>\s*", "", result)

    # remove unnecessary tags
    if with_font_styles_tags:
        result = re.sub("</b></i><i><b>", "", result)
        result = re.sub("</i><i>", "", result)
        result = re.sub("</b><b>", "", result)

    # fix spaces
    result = re.sub(r"[ ][\n]", "\n", result)
    return result


def remove_all_tags(text: str) -> str:
    text = re.sub(r"<.*?>", "", text)
    return text
