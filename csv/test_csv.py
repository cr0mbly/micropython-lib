import io
import unittest
from csv import reader


class TestReader(unittest.TestCase):

    def test_reader_loads_file_object(self):
        csv_strings = [
            ['my', 'test', 'strings'],
            ['my', 'second', 'rows'],
        ]
        f = io.StringIO('my,test,strings\nmy,second,rows')

        csv_reader = reader(f)

        for index, row_list in enumerate(csv_reader):
            self.assertEqual(csv_strings[index], row_list)


if __name__ == '__main__':
    unittest.main()
