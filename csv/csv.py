"""
Ported CSV module from CPython/csv.
Provides a similar feature set as the above version
but written fully in python
"""
import io

QUOTE_MINIMAL = 0
QUOTE_ALL = 1
QUOTE_NONNUMERIC = 2
QUOTE_NONE = 3

def reader(
    csvfile, deliminter=',', lineterminator='\r\n', quotechar='"',
    escapechar=None, skipinitialspace=False, doublequote=True,
    quoting=QUOTE_MINIMAL,
):
    """
    Reader class accepts an iterable object for csvfile
    """
    try:
        csv_iterable = iter(csvfile)
    except TypeError as e:
        raise TypeError('csvfile must be of an iterable type')

    csv_row_list = []

    if hasattr(csvfile, 'read'):
        csv_rows = csvfile
    else:
        # CSV is already in an iterable format
        csv_rows = csvfile

    for string_row in _get_next_string_row(csvfile):
        yield _convert_string_to_columns(
            string_row, deliminter, quotechar, escapechar,
            skipinitialspace, doublequote, quoting,
        )


def _get_next_string_row(csvfile):
    if hasattr(csvfile, 'read'):
        csv_rows = csvfile

        char = csvfile.read(1)

        row = ''
        while char != '':
            if char == '\n' or char == '\r':
                yield row
                row = ''
            else:
                row += char
            char = csvfile.read(1)
        yield row
    else:
        for row in csvfile:
            yield row


def _convert_string_to_columns(
    string_row, deliminter, quotechar, escapechar,
    skipinitialspace, doublequote, quoting,
):
    """
    Taking a generated string row return back the formatted
    resulting CSV columns.
    """
    columns = []
    num_chars = 0

    while num_chars < len(string_row):
        current_column_value = ''
        for index, char in enumerate(string_row[num_chars:]):
            sub_string = string_row[num_chars:]
            if char == quotechar:
                # Preform look ahead for next quote char,
                # search to next quotechar if present.
                next_quote_pos = sub_string[index:].find(quotechar)
                if next_quote_pos != -1:
                    quoted_chars = sub_string[next_quote_pos:]
                    current_column_value += quoted_chars.rstrip()
                    num_chars += 1
                    break
            elif (
                quotechar == None
                and (char == deliminter and sub_string[index - 1] == escapechar)
            ):
                current_column_value = current_column_value[:-1] + char
                num_chars += 1
                continue

            elif char == deliminter:
                num_chars += (
                    2
                    if skipinitialspace and sub_string[index + 1] == ' '
                    else 1
                )
                break
            else:
                current_column_value += char

        num_chars += len(current_column_value)

        if quoting == QUOTE_NONNUMERIC:
            try:
                current_column_value = float(current_column_value)
            except ValueError as e:
                pass

        columns.append(current_column_value)
    return columns
