"""
Dummy polish dates converter to ISO format.
"""
import re


MONTH_NAMES = {
    'styczeń': 1,
    'stycznia': 1,
    'luty': 2,
    'lutego': 2,
    'marzec': 3,
    'marca': 3,
    'kwiecień': 4,
    'kwietnia': 4,
    'maj': 5,
    'maja': 5,
    'czerwiec': 6,
    'czerwca': 6,
    'lipiec': 7,
    'lipca': 7,
    'sierpień': 8,
    'sierpnia': 8,
    'wrzesień': 9,
    'września': 9,
    'październik': 10,
    'października': 10,
    'listopad': 11,
    'listopada': 11,
    'grudzień': 12,
    'grudnia': 12,
}


ALL_MONTH_NAMES_STR = "|".join(MONTH_NAMES)
DATE_REGEX = re.compile(r"\b(?P<day>[012][0-9]|3[01]|[1-9])\s*(?P<month>" + ALL_MONTH_NAMES_STR + r")\s*(?P<year>[12]\d\d\d)\b(?:\s*(?:roku|r[.]?))?", re.IGNORECASE)


def convert_polish_date_to_iso(input_string: str) -> str:
    match = DATE_REGEX.match(input_string)
    if match:
        day_str = match.group('day')
        day_out = '0' + day_str
        day_out = day_out[-2:]

        month_str = match.group('month').lower()
        month_no = MONTH_NAMES[month_str]
        month_out = '0' + str(month_no)
        month_out = month_out[-2:]

        year_str = match.group('year')
        year_out = year_str

        return f"{year_out}-{month_out}-{day_out}"

    return None


def find_polish_dates_in_text(input_text: str):
    result = []
    position = 0
    while (match := DATE_REGEX.search(input_text, position)) is not None:
        position = match.start() + 1
        result.append(match[0])
    return result
