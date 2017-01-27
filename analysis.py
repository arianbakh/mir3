from enum import Enum


class LanguageCode(Enum):
    PERSIAN = 'fa'
    ENGLISH = 'en'
    NUMBER = '#'
    UNKNOWN = '?'


CHARACTER_REPLACE_DICT = {
    chr(8204): chr(32),  # half-space -> space
    chr(1570): chr(1575),  # آ -> ا
    chr(1571): chr(1575),  # أ -> ا
    chr(1573): chr(1575),  # إ -> ا
    chr(1572): chr(1608),  # ؤ -> و
    chr(1577): chr(1578),  # ة -> ت
    chr(1603): chr(1705),  # ك -> ک
    chr(1609): chr(1740),  # ى -> ی
    chr(1610): chr(1740),  # ي -> ی
    chr(1574): chr(1740),  # ئ -> ی
    chr(1569): chr(1740),  # ء -> ی
    chr(1726): chr(1607),  # ھ -> ه
    chr(233): chr(101),    # e <- é
}
for i in range(1611, 1618):  # tanvins, short vowels, hamzah, sokun
    CHARACTER_REPLACE_DICT[chr(i)] = ''
for english_number, persian_number in [(x - 1728, x) for x in range(1776, 1776 + 10)]:  # persian numbers
    CHARACTER_REPLACE_DICT[chr(persian_number)] = chr(english_number)
for english_number, persian_number in [(x - 1584, x) for x in range(1632, 1632 + 10)]:  # another set of persian numbers!
    CHARACTER_REPLACE_DICT[chr(persian_number)] = chr(english_number)


PERSIAN_ALPHABET_CODES = [
    1575, 1576, 1662, 1578, 1579, 1580, 1670, 1581, 1582, 1583, 1584, 1585, 1586, 1688, 1587, 1588,
    1589, 1590, 1591, 1592, 1593, 1594, 1601, 1602, 1705, 1711, 1604, 1605, 1606, 1608, 1607, 1740
]
PERSIAN_NUMBER_CODES = list(range(1776, 1776 + 10)) + list(range(1632, 1632 + 10))


ENGLISH_SMALL_ALPHABET_CODES = list(range(65, 65 + 26))
ENGLISH_CAPITAL_ALPHABET_CODES = list(range(97, 97 + 26))
ENGLISH_ALPHABET_CODES = ENGLISH_SMALL_ALPHABET_CODES + ENGLISH_CAPITAL_ALPHABET_CODES
ENGLISH_NUMBER_CODES = list(range(48, 48 + 10))


SPACE_CODE = 32


VALID_CHARACTER_CODES = PERSIAN_ALPHABET_CODES + \
    PERSIAN_NUMBER_CODES + \
    ENGLISH_ALPHABET_CODES + \
    ENGLISH_NUMBER_CODES


def remove_inside_brackets(text):
    inside_bracket = 0
    new_text = ''
    for character in text:
        if character == '[':
            inside_bracket += 1
        elif character == ']':
            inside_bracket -= 1
        elif not inside_bracket:
            new_text += character
    return new_text


def normalize_characters(raw_string):
    normalized_string = ''
    if raw_string:
        for character in raw_string:
            if character in CHARACTER_REPLACE_DICT:
                normalized_string += CHARACTER_REPLACE_DICT[character]
            else:
                normalized_string += character
    return normalized_string


def _get_language_code(char):
    char_code = ord(char)
    if char_code in PERSIAN_ALPHABET_CODES:
        return LanguageCode.PERSIAN
    elif char_code in ENGLISH_ALPHABET_CODES:
        return LanguageCode.ENGLISH
    elif char_code in ENGLISH_NUMBER_CODES:
        return LanguageCode.NUMBER
    else:
        return LanguageCode.UNKNOWN


def _have_different_language(char_1, char_2):
    language_code_1 = _get_language_code(char_1)
    language_code_2 = _get_language_code(char_2)

    if language_code_1 == LanguageCode.UNKNOWN or language_code_2 == LanguageCode.UNKNOWN:
        return False  # if either is unknown, we assume it has the same language

    return language_code_1 != language_code_2


def add_whitespace_on_language_transition(string):
    final_string = ''
    if string:
        for i in range(len(string) - 1):
            final_string += string[i]
            if _have_different_language(string[i], string[i + 1]):
                final_string += ' '
        final_string += string[-1]
    return final_string


def replace_invalid_characters_with_whitespace(string):
    result_string = ''
    for character in string:
        if ord(character) not in VALID_CHARACTER_CODES:
            result_string += chr(SPACE_CODE)
        else:
            result_string += character
    return result_string


def normalize_whitespace(string):
        return chr(SPACE_CODE).join(string.strip().split())


def analyze(text):
    text = remove_inside_brackets(text)
    text = normalize_characters(text)
    text = add_whitespace_on_language_transition(text)
    text = replace_invalid_characters_with_whitespace(text)
    text = normalize_whitespace(text)
    return text
