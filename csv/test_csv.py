import io
import unittest
from csv import reader


class TestReader(unittest.TestCase):

    def test_reader_loads_file_object(self):
        file_io = io.StringIO('my,test,strings\nmy,second,rows')

        csv_reader = reader(file_io)

        excpected_csv_strings = [
            ['my', 'test', 'strings'],
            ['my', 'second', 'rows'],
        ]

        for index, row_list in enumerate(csv_reader):
            self.assertEqual(
                excpected_csv_strings[index], row_list,
            )

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
        file_io = io.StringIO('my,"test,strings"\nmy,second,rows')
        csv_reader = reader(file_io)

        excpected_csv_strings = [
            ['my', '"test,strings"'],
            ['my', 'second', 'rows'],
        ]

        for index, row_list in enumerate(csv_reader):
            self.assertEqual(
                excpected_csv_strings[index], row_list,
            )

    def test_non_iterable_raises_exception(self):
        csv_reader = reader(None)
        self.assertRaises(TypeError, lambda: next(csv_reader))


if __name__ == '__main__':
    unittest.main()
