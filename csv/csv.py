"""
Ported CSV module from IPython/csv.
Provides a similar feature set as the above version
but written fully in python
"""
import io

def reader(csvfile, dialect='excel', **fmtparams):
    """
    Reader class accepts an iterable object for csvfile
    """

    try:
        csv_iterable = iter(csvfile)
    except TypeError:
        raise Exception('csvfile must be of an iterable type')

    csv_row_list = []

    if hasattr(csvfile, 'read'):
        csv_row_list = csvfile.read().split('\n')

    for row in csvfile:
        yield row
