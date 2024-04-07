import csv
from itertools import izip

logger = logging.getLogger(__file__)

class AmiCSV:

    def read_transpose_write(self, input, output):
        a = izip(*csv.reader(open("input.csv", "rb")))
        csv.writer(open("output.csv", "wb")).writerows(a)

    @classmethod
    def transpose(cls, a):
        """
        clever trick for transposing a 2-D array
        :param a: array
        :return: transposed array or None if bad arguments
        """
        if a is None or len(a.shape) != 2:
            return None
        b = izip(*a)
        return b