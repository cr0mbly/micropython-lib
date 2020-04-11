"""
Ported CSV module from CPython/csv.
Provides a similar feature set as the above version
but written fully in python
"""
QUOTE_MINIMAL = 0
QUOTE_NONNUMERIC = 2


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
    except TypeError:
        raise TypeError('csvfile must be of an iterable type')

    for string_row in _get_next_string_row(csv_iterable):
        yield _convert_string_to_columns(
            string_row, deliminter, quotechar, escapechar,
            skipinitialspace, doublequote, quoting,
        )


def _get_next_string_row(csvfile):
    """
    Resolves the next CSV row. Searches for either line break
    or return carriages in search of result.
    """
    if hasattr(csvfile, 'read'):
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
                # Test if next character is also a quotechar.
                if sub_string[index + 1] == quotechar:
                    current_column_value += (
                        quotechar if doublequote else quotechar * 2
                    )
                    num_chars += 2
                    break

                # Preform look ahead for next quote char,
                # search to next quotechar if present.
                next_quote_pos = sub_string[index:].find(quotechar)
                if next_quote_pos != -1:
                    quoted_chars = sub_string[next_quote_pos:]
                    current_column_value += quoted_chars.rstrip()
                    num_chars += 1
                    break
            elif (
                quotechar is None
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
            except ValueError:
                pass

        columns.append(current_column_value)
    return columns


class writer:
    """
    CSV writer accepts a writable file object and exposes two methods
     - writerow
     - writerows
    to update fileobject with passed in list/iterable of lists
    """
    def __init__(
        self, csvfile, deliminter=',', lineterminator='\r\n', quotechar='"',
        escapechar=None, doublequote=True, skipinitialspace=False,
        quoting=QUOTE_MINIMAL,
    ):
        if not hasattr(csvfile, 'write'):
            raise TypeError('csvfile must have a write method present to use.')
        if not doublequote and escapechar is None:
            raise TypeError('need to escape, but no escapechar set')

        self.csvfile = csvfile
        self.deliminter = deliminter
        self.lineterminator = lineterminator
        self.quotechar = quotechar
        self.escapechar = escapechar
        self.doublequote = doublequote
        self.quoting = quoting

    def writerow(self, csvrow):
        string_row = ''
        for index, column in enumerate(csvrow, start=1):
            is_numeric_character = True
            try:
                float(column)
            except ValueError:
                is_numeric_character = False

            column = str(column)

            if not is_numeric_character:
                column = (
                    column.replace(self.quotechar, self.quotechar*2)
                    if self.doublequote and self.escapechar is None
                    else column.replace(
                        self.quotechar, self.escapechar + self.quotechar
                    )
                )
            if (
                self.deliminter in column
                or self.quoting == QUOTE_NONNUMERIC
                or (self.quotechar in column and self.escapechar is None)
                and self.quoting == QUOTE_MINIMAL
            ):
                if (
                    self.quoting == QUOTE_MINIMAL
                    or (
                        self.quoting == QUOTE_NONNUMERIC
                        and not is_numeric_character
                    )
                ):
                    column = self.quotechar + column + self.quotechar

            string_row += (
                column + self.deliminter if index < len(csvrow) else column
            )

        self.csvfile.write(string_row + self.lineterminator)
        return len(string_row)

    def writerows(self, csvrows):
        """
        Taking an iterable of lists writes each
        computed row to the instanciated file object.
        """
        try:
            csv_iterable = iter(csvrows)
        except TypeError:
            raise TypeError('csvrows must be of an iterable type')

        for row in csv_iterable:
            self.writerow(row)
