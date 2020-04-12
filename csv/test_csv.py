import io
import unittest

from csv import (
    Error,
    QUOTE_ALL,
    QUOTE_NONNUMERIC,
    QUOTE_NONE,
    reader,
    writer,
    DictReader
)


class TestReader(unittest.TestCase):

    def test_reader_loads_file_object(self):
        file_io = io.StringIO('my,test,strings\nmy,second,rows')

        csv_reader = reader(file_io)

        excpected_csv_strings = [
            ['my', 'test', 'strings'],
            ['my', 'second', 'rows'],
        ]

        for index, row_list in enumerate(csv_reader):
            self.assertEqual(excpected_csv_strings[index], row_list)

    def test_reader_parses_carriage_return(self):
        file_io = io.StringIO('my,test,strings\rmy,second,rows')
        csv_reader = reader(file_io)

        excpected_csv_strings = [
            ['my', 'test', 'strings'],
            ['my', 'second', 'rows'],
        ]

        for index, row_list in enumerate(csv_reader):
            self.assertEqual(excpected_csv_strings[index], row_list)

    def test_reader_loads_non_file_iterables(self):
        csv_lists = ['my,test,strings', 'my,second,rows']

        csv_reader = reader(csv_lists)

        excpected_csv_strings = [
            ['my', 'test', 'strings'],
            ['my', 'second', 'rows'],
        ]

        for index, row_list in enumerate(csv_reader):
            self.assertEqual(
                excpected_csv_strings[index], row_list,
            )

    def test_reader_ignores_quote_characters(self):
        file_io = io.StringIO('my,"test\,strings"')
        csv_reader = reader(
            file_io, deliminter=',', quotechar=None, escapechar='\\',
        )
        self.assertEqual(['my', '"test,strings"'], next(csv_reader))

    def test_doublequote_combines_quotes(self):
        file_io_doublequoted = io.StringIO('my,test,strings""')

        csv_reader = reader(file_io_doublequoted, doublequote=True)
        self.assertEqual(['my', 'test', 'strings"'], next(csv_reader))

        file_io_doublequoted = io.StringIO('my,test,strings""')
        csv_reader = reader(file_io_doublequoted, doublequote=False)
        self.assertEqual(['my', 'test', 'strings""'], next(csv_reader))

    def test_skipinital_skips_initial_space(self):
        file_io = io.StringIO('my,test, strings')
        csv_reader = reader(file_io, deliminter=',', skipinitialspace=True)
        excpected_csv_strings = ['my', 'test', 'strings']
        self.assertEqual(excpected_csv_strings, next(csv_reader))

    def test_quote_nonnumeric_casts_numeric_values(self):
        file_io = io.StringIO('my,test, 1,2.0')
        csv_reader = reader(file_io, quoting=QUOTE_NONNUMERIC)
        excpected_csv_strings = ['my', 'test', 1.0, 2.0]
        self.assertEqual(excpected_csv_strings, next(csv_reader))

    def test_non_iterable_raises_exception(self):
        csv_reader = reader(None)
        self.assertRaises(Error, lambda: next(csv_reader))


class TestWriter(unittest.TestCase):

    def setUp(self):
        self.string_file = io.StringIO('')
        self.writer = writer(self.string_file)

    def test_writerow_saves_row_with_string_output(self):
        self.writer.writerow(['my', 'test', 'string'])
        self.assertEqual('my,test,string\r\n', self.string_file.getvalue())

    def test_writerows_saves_rows_with_string_output(self):
        self.writer.writerows([
            ['my', 'test', 'string'],
            ['my', 'second', 'row'],
        ])
        self.assertEqual(
            'my,test,string\r\nmy,second,row\r\n', self.string_file.getvalue()
        )

    def test_different_lineterminator_outputs_correct_termination(self):
        self.writer = writer(self.string_file, lineterminator='\n')
        self.writer.writerows([
            ['my', 'test', 'string'], ['my', 'second', 'row'],
        ])
        self.assertEqual(
            'my,test,string\nmy,second,row\n', self.string_file.getvalue(),
        )

    def test_quote_are_escaped_with_doublequotes(self):
        self.writer = writer(self.string_file, doublequote=True)
        self.writer.writerow(['my', 'test', '"string'])
        self.assertEqual('my,test,"""string"\r\n', self.string_file.getvalue())

    def test_none_are_cast_to_empty_strings(self):
        self.writer = writer(self.string_file)
        self.writer.writerow(['my', None, 'string'])
        self.assertEqual('my,,string\r\n', self.string_file.getvalue())

    def test_escaping_of_characters_is_present_when_set(self):
        self.writer = writer(
            self.string_file, doublequote=False, escapechar='\\'
        )
        self.writer.writerow(['my', 'test', '"string'])
        self.assertEqual('my,test,\\"string\r\n', self.string_file.getvalue())

    def test_quote_non_numeric(self):
        self.writer = writer(self.string_file, quoting=QUOTE_NONNUMERIC)
        self.writer.writerow(['my', 'test', 4.2, 2])
        self.assertEqual('"my","test",4.2,2\r\n', self.string_file.getvalue())

    def test_quote_all(self):
        self.writer = writer(self.string_file, quoting=QUOTE_ALL)
        self.writer.writerow(['my', '"test', 4.2, 2, None])
        self.assertEqual(
            '"my","""test","4.2","2",""\r\n', self.string_file.getvalue(),
        )

    def test_quote_none(self):
        self.writer = writer(
            self.string_file, quoting=QUOTE_NONE, escapechar='\\',
        )
        self.writer.writerow(['my', '"test', 4.2, 2, None])
        self.assertEqual(
            'my,\\"test,4.2,2,\r\n', self.string_file.getvalue(),
        )


class TestDictReader(unittest.TestCase):
    def setUp(self):
        self.file_io = io.StringIO('fruits,vegetables,meats\napple,spinach,pork')

    def test_fieldnames_are_loader_by_default(self):
        csv_reader = DictReader(self.file_io)
        self.assertEqual(
            ['fruits', 'vegetables', 'meats'], csv_reader.fieldnames,
        )

    def test_defined_fieldnames_override_default(self):
        csv_reader = DictReader(
            self.file_io, fieldnames=['column_1', 'column_2', 'column_3'],
        )
        self.assertEqual(
            ['column_1', 'column_2', 'column_3'], csv_reader.fieldnames,
        )

    def test_iterating_on_dict_reader_returns_dict_map(self):
        csv_reader = DictReader(self.file_io)
        self.assertDictEqual(
            {'fruits': 'apple', 'vegetables': 'spinach', 'meats': 'pork'},
            next(csv_reader),
        )

    def test_iterating_on_dict_reader_with_greater_fieldnames_uses_restval(self):
        self.file_io = io.StringIO('fruits,vegetables,meats\napple,spinach')
        csv_reader = DictReader(self.file_io, restval='N/A')
        self.assertDictEqual(
            {'fruits': 'apple', 'vegetables': 'spinach', 'meats': 'N/A'},
            next(csv_reader),
        )

    def test_iterating_on_dict_reader_with_greater_columns_uses_restkey(self):
        self.file_io = io.StringIO('fruits,vegetables\napple,spinach,boat,house,car')
        csv_reader = DictReader(self.file_io, restkey='outstanding_fields')
        self.assertDictEqual(
            {
                'fruits': 'apple',
                'vegetables': 'spinach',
                'outstanding_fields': ['boat', 'house', 'car']
            },
            next(csv_reader),
        )

if __name__ == '__main__':
    unittest.main()
