"""
Ported CSV module from CPython/csv.
Provides a similar feature set as the above version
but written fully in python
"""
QUOTE_MINIMAL = 0
QUOTE_ALL = 1
QUOTE_NONNUMERIC = 2
QUOTE_NONE = 3


class Error(Exception):
    """
    Stub CSV exception
    """


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
        raise Error('csvfile must be of an iterable type')

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
            raise Error('need to escape, but no escapechar set')

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
            # Cast None values.
            column = '' if column is None else column

            # Ignore quote handling and parse row.
            if self.quoting == QUOTE_NONE:
                if isinstance(column, str):
                    column = column.replace(
                        self.quotechar, self.escapechar + self.quotechar
                    )
                string_row += (
                    str(column) + self.deliminter
                    if index < len(csvrow)
                    else column
                )
                continue

            # Preform integer check.
            is_numeric_character = True
            try:
                float(column)
            except ValueError:
                is_numeric_character = False

            # Convert any non string object to string.
            column = str(column)

            # Escape current field if required.
            if not is_numeric_character:
                column = (
                    column.replace(self.quotechar, self.quotechar*2)
                    if self.doublequote and self.escapechar is None
                    else column.replace(
                        self.quotechar, self.escapechar + self.quotechar
                    )
                )

            # Tack on any extra quoting depending on Quoting type.
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

            # Quote any column that hasn't been already if
            # QUOTE_ALL is selected.
            if (
                self.quoting == QUOTE_ALL
                and (
                    column == ''
                    or (
                        column[0] != self.quotechar
                        or column[-1] != self.quotechar
                    )
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
            raise Error('csvrows must be of an iterable type')

        for row in csv_iterable:
            self.writerow(row)


class DictReader:
    """
    DictReader returns a dictionary object of CSV rows matching the headers
    of the file or defined fieldnames with the matching ordered row columns.
    Set restkey/restval to define what default values should be set for columns
    that don't match the number of fieldheaders or the default values when
    there are more fieldheaders then rows.
    """
    def __init__(
        self, csvfile, fieldnames=None, restkey=None, restval=None,
        *args, **kwargs
    ):
        self._reader = reader(csvfile, *args, **kwargs)
        self.restkey = restkey
        self.restval = restval

        if fieldnames is None:
            self.fieldnames = next(self._reader)
        else:
            self.fieldnames = fieldnames

    def __next__(self):
        row_list = next(self._reader)
        row_dict = {}
        for index, header in enumerate(self.fieldnames):
            if index < len(row_list):
                row_dict[header] = row_list[index]
            else:
                row_dict[header] = self.restval

        if len(self.fieldnames) >= len(row_list):
            return row_dict
        else:
            row_dict[self.restkey] = row_list[index + 1:]
            return row_dict


class DictWriter:
    """
    DictWriter takes rows of dictionary objects and writes them to the passed
    in file object corresponding to the column names laid out in the
    fieldnames kwarg.
    """
    def __init__(
        self, f, fieldnames, restval='', extrasaction='raise', *args, **kwargs
    ):
        self._csvwriter = writer(f, *args, **kwargs)
        self.fieldnames = fieldnames
        self.restval=restval
        self.extrasaction=extrasaction

    def writeheader(self):
        return self._csvwriter.writerow(self.fieldnames)

    def writerow(self, rowdict):
        if self.extrasaction == 'raise':
            extra_fields = set(rowdict.keys()) - set(self.fieldnames)
            if extra_fields:
                raise ValueError(
                    'dict contains fields not in fieldnames: '
                    + ', '.join(extra_fields)
                )

        return self._csvwriter.writerow([
            rowdict.get(column_header, self.restval)
            for column_header in self.fieldnames
        ])

    def writerows(self, rowdicts):
        for row in rowdicts:
            self.writerow(row)
