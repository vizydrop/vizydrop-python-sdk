import re

# yummy regex
camelcase_regex = re.compile(r'(?!^)([A-Z]+)')


def convert_camel_to_underscore(camelcase):
    """
    Convert CamelCase words to camel_case
    :param camelcase: CamelCase word
    :return: underscored version of camelcase
    """
    return camelcase_regex.sub(r'_\1', camelcase).lower()


links_header_regex = re.compile(r'(<(?P<link>\S+)>;\srel="(?P<rel>\w+)",?)+')


def parse_link_header(header_contents):
    """
    Parse a Link header (RFC5988 §5) to a dictionary
    :param header_contents: header contents (str)
    :return: dictionary (rel=>url)
    """
    matches = links_header_regex.findall(header_contents)
    ret = {}
    for match in matches:
        ret[match[2]] = match[1]
    return ret


identifier_construction_regex = re.compile(r'(\s|\W)')


def generate_identifier_from_string(string):
    """
    Generates an identifier string (alphanumeric with hyphens) from an input string
    :param string: Input
    :return: identifier constructed from input string
    """
    return identifier_construction_regex.sub(r'-', string).lower().rstrip('-')


def pluralize(singular):
    """
    Returns the plural representation of the singular noun provided
    :param singular: singular name
    :return: pluralized version of the singular
    """
    if not singular:
        return ''
    root = singular
    vowels = set('aeiou')
    try:
        if singular[-1] == 'y' and singular[-2] not in vowels:
            root = singular[:-1]
            suffix = 'ies'
        elif singular[-1] == 's':
            if singular[-2] in vowels:
                if singular[-3:] == 'ius':
                    root = singular[:-2]
                    suffix = 'i'
                else:
                    root = singular[:-1]
                    suffix = 'ses'
            else:
                suffix = 'es'
        elif singular[-2:] in ('ch', 'sh'):
            suffix = 'es'
        else:
            suffix = 's'
    except IndexError:
        suffix = 's'
    plural = root + suffix
    return plural
