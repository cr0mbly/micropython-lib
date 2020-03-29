"""
Ported CSV module from IPython/csv.
Provides a similar feature set as the above version
but written fully in python
"""
import io

def reader(
    csvfile, deliminter=',', newline='\n', quotechar='"'
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

    for string_row in csvfile:
        yield _convert_string_to_columns(
            string_row, newline, deliminter, quotechar,
        )


def _convert_string_to_columns(string_row, deliminter, newline, quotechar):
    """
    Taking a generated string row return back the formatted
    resulting CSV columns.
    """
    columns = []

    num_chars = 0

    while num_chars < len(string_row):
        current_column_value = ''

        for index, char in enumerate(string_row[num_chars:]):
            if char == quotechar:
                sub_string = string_row[num_chars:]

                # Preform look ahead for next quote char,
                # search to next quotechar if present.
                next_quote_pos = sub_string[index:].find(quotechar)
                if next_quote_pos != -1:
                    quoted_chars = sub_string[next_quote_pos:]
                    current_column_value += quoted_chars.rstrip()
                    num_chars += 1
                    break
            elif char == deliminter or char == newline:
                num_chars += 1
                break

            current_column_value += char

        columns.append(current_column_value)
        num_chars += len(current_column_value)

    return columns
