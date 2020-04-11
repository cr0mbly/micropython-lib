import io
import unittest

from csv import reader, writer, QUOTE_NONNUMERIC


class TestReader(unittest.TestCase):

    def test_reader_loads_file_object(self):
        file_io = io.StringIO('my,test,strings\nmy,second,rows')

        csv_reader = reader(file_io)

        excpected_csv_strings = [
            ['my', 'test', 'strings'],
            ['my', 'second', 'rows'],
        ]

        for index, row_list in enumerate(csv_reader):
            self.assertEqual( excpected_csv_strings[index], row_list)

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

        excpected_csv_strings = ['my', '"test,strings"']

        self.assertEqual(
            excpected_csv_strings, next(csv_reader),
        )

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
        self.assertRaises(TypeError, lambda: next(csv_reader))


class TestWriter(unittest.TestCase):

    def setUp(self):
        self.string_file = io.StringIO('')
        self.writer = writer(self.string_file)

    def test_writerow_saves_row_with_string_output(self):
        self.writer.writerow(['my', 'test', 'string'])
        self.assertEqual(
            'my,test,string\r\n', self.string_file.getvalue()
        )

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
            'my,test,string\nmy,second,row\n', self.string_file.getvalue()
        )

    def test_quote_are_escaped_with_doublequotes(self):
        self.writer = writer(self.string_file, doublequote=True)
        self.writer.writerow(['my', 'test', '"string'])
        self.assertEqual(
            'my,test,"""string"\r\n', self.string_file.getvalue()
        )

    def test_escaping_of_characters_is_present_when_set(self):
        self.writer = writer(
            self.string_file, doublequote=False, escapechar='\\'
        )
        self.writer.writerow(['my', 'test', '"string'])
        self.assertEqual(
            'my,test,\\"string\r\n', self.string_file.getvalue()
        )

    def test_quote_non_numeric(self):
        self.writer = writer(self.string_file, quoting=QUOTE_NONNUMERIC)
        self.writer.writerow(['my', 'test', 4.2, 2])
        self.assertEqual('"my","test",4.2,2\r\n', self.string_file.getvalue())


if __name__ == '__main__':
    unittest.main()
