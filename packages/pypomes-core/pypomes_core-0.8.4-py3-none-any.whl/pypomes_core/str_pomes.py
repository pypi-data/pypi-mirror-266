def str_sanitize(target_str: str) -> str:
    """
    Clean the given *target_str* string.

    The sanitization is carried out by:
        - removing backslashes
        - replacing double quotes with single quotes
        - replacing newlines and tabs with whitespace
        - replacing multiple consecutive spaces with a single space

    :param target_str: the string to be cleaned
    :return: the cleaned string
    """
    cleaned: str = target_str.replace("\\", "") \
                             .replace('"', "'") \
                             .replace("\n", " ") \
                             .replace("\t", " ")
    return " ".join(cleaned.split())


def str_split_on_mark(source: str, mark: str) -> list[str]:
    """
    Extract from *source* the text segments separated by *mark*, and return them in a *list*.

    The separator itself will not be in the returned list.

    :param source: the string to be inspected
    :param mark: the separator
    :return: the list of text segments extracted
    """
    # inicializa a variável de retorno
    result: list[str] = []

    pos: int = 0
    skip: int = len(mark)
    after: int = source.find(mark)
    while after >= 0:
        result.append(source[pos:after])
        pos = after + skip
        after = source.find(mark, pos)
    if pos < len(source):
        result.append(source[pos:])
    else:
        result.append("")

    return result


def str_find_whitespace(source: str) -> int:
    """
    Locate and return the position of the first occurence of a *whitespace* character in *source*.

    :param source: the string to be inspected
    :return: the position of the first whitespace character, or -1 if none was found
    """
    # inicializa a variável de retorno
    result: int = -1

    # busca por whitespace
    for inx, char in enumerate(source):
        if char.isspace():
            result = inx
            break

    return result


def str_get_between(source: str, from_str: str, to_str: str) -> str:
    """
    Extract and return the *substring* in *source* located between the delimiters *from_str* and *to_str*.

    :param source: the string to be inspected
    :param from_str: the initial delimiter
    :param to_str: the final delimiter
    :return: the extracted substring, or None if no substring was obtained
    """
    # inicializa a variável de retorno
    result: str | None = None

    pos1: int = source.find(from_str)
    if pos1 >= 0:
        pos1 += len(from_str)
        pos2: int = source.find(to_str, pos1)
        if pos2 >= pos1:
            result = source[pos1:pos2]

    return result


def str_get_positional(source: str, list_origin: list[str], list_dest: list[str]) -> str:
    """
    Locate the position of *source* within *list_origin*, and return the element in the same position in *list_dest*.

    :param source: the source string
    :param list_origin: the list to be inspected
    :param list_dest: the list containing the positionally corresponding values
    :return: the value positionally corresponding to the source string, or None if not found
    """
    # declare the return variable
    result: str | None

    try:
        pos: int = list_origin.index(source)
        result = list_dest[pos]
    except ValueError:
        result = None

    return result


