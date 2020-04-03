#-------------------------------------------------------------------------------
#
# VirES CSV format reader - tests
#
# Authors: Martin Paces <martin.paces@eox.at>
#-------------------------------------------------------------------------------
# Copyright (C) 2019 EOX IT Services GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies of this Software or works derived from this Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#-------------------------------------------------------------------------------
#pylint: disable=missing-docstring

from unittest import TestCase, main
from io import StringIO
from numpy import dtype, array, nan
from numpy.testing import assert_equal
from vires.readers import (
    InvalidFileFormat, read_csv_data, reduce_int_type, sanitize_custom_data,
)
from vires.util import cached_property
from vires.readers.tests.data import TEST1_CSV_FILE, TEST2_CSV_FILE

class CSVReaderTestMixIn(TestCase):
    TEST_CSV_FILE = None
    N_RECORDS = None

    @cached_property
    def data(self):
        return self.load_data()

    def load_data(self):
        return read_csv_data(self.TEST_CSV_FILE)

    def assert_type_and_shape(self, variable, shape, dtype_string):
        data = self.data[variable]
        self.assertEqual(data.shape, (self.N_RECORDS,) + shape)
        self.assertEqual(data.dtype, dtype(dtype_string))

    def assert_not_present(self, variable):
        self.assertFalse(variable in self.data)


class TestCSVReader(CSVReaderTestMixIn, TestCase):
    TEST_CSV_FILE = TEST1_CSV_FILE
    N_RECORDS = 5

    def test_timestamp(self):
        self.assert_type_and_shape('Timestamp', (), '<M8[ms]')

    def test_scalar_float(self):
        self.assert_type_and_shape('F', (), 'float64')

    def test_vector_float(self):
        self.assert_type_and_shape('B_NEC', (3,), 'float64')

    def test_scalar_int(self):
        self.assert_type_and_shape('Flags_B', (), 'int64')

    def test_scalar_mixed_int_float(self):
        self.assert_type_and_shape('ASM_Freq_Dev', (), 'float64')


class TestCSVReaderSanitized(CSVReaderTestMixIn, TestCase):
    TEST_CSV_FILE = TEST2_CSV_FILE
    N_RECORDS = 5

    @cached_property
    def data(self):
        return sanitize_custom_data({
            field: reduce_int_type(values)
            for field, values in self.load_data().items()
        })

    def test_mjd2000(self):
        self.assert_type_and_shape('MJD2000', (), 'float')

    def test_timestamp(self):
        self.assert_type_and_shape('Timestamp', (), '<M8[ms]')

    def test_bnec_vector(self):
        self.assert_type_and_shape('B_NEC', (3,), 'float')

    def test_bnec_scalars(self):
        self.assert_not_present('B_N')
        self.assert_not_present('B_E')
        self.assert_not_present('B_C')

    def test_reduced_uint8(self):
        self.assert_type_and_shape('row', (), 'uint8')

    def test_reduced_int8(self):
        self.assert_type_and_shape('int8', (), 'int8')


class TestCSVReaderSpecialCase(TestCase):

    def test_mixed_types_timestamp_string(self):
        source = StringIO("variable,fill\n,A\n2020-01-01T00:00:00,B\n")
        with self.assertRaises(InvalidFileFormat):
            read_csv_data(source)

        source = StringIO("variable\n2020-01-01T00:00:00\nXXX\n")
        with self.assertRaises(InvalidFileFormat):
            read_csv_data(source)

    def test_mixed_types_timestamp_float_string(self):
        source = StringIO("variable\n2020-01-01T00:00:00\n0.1\nXXX\n")
        with self.assertRaises(InvalidFileFormat):
            read_csv_data(source)

    def test_mixed_types_timestamp_float(self):
        source = StringIO("variable\n2020-01-01T00:00:00\n0.1\n")
        with self.assertRaises(InvalidFileFormat):
            read_csv_data(source)

    def test_mixed_types_float_int(self):
        source = StringIO("variable\n2\n0.1\n3\n")
        assert_equal(read_csv_data(source)['variable'], array([2, 0.1, 3]))
        source = StringIO("variable\n0.1\n2\n0.3\n")
        assert_equal(read_csv_data(source)['variable'], array([0.1, 2, 0.3]))

    def test_mixed_types_float_str(self):
        source = StringIO("variable\n1\nX\n3\n")
        assert_equal(read_csv_data(source)['variable'], array([1, nan, 3]))
        source = StringIO("variable\n.1\nX\n.3\n")
        assert_equal(read_csv_data(source)['variable'], array([.1, nan, .3]))
        #source = StringIO("variable\nX\n2\n.3\n")
        #assert_equal(read_csv_data(source)['variable'], array([nan, 2, .3]))


if __name__ == "__main__":
    main()
