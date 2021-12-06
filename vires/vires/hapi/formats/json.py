#-------------------------------------------------------------------------------
#
# VirES HAPI - format encoding / decoding - JSON format subroutines
#
# Authors: Martin Paces <martin.paces@eox.at>
#-------------------------------------------------------------------------------
# Copyright (C) 2021 EOX IT Services GmbH
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


import json
from itertools import chain
from numpy import (
    str_, bytes_, bool_, float32, float64, datetime64,
    int8, int16, int32, int64, uint8, uint16, uint32, uint64,
    isfinite,
)
from .common import flatten_records, format_datetime64


# FIXME: JSON cannot encode IEEE-754 not-a-number and positive or negative
#        infinity not sure how these values should be encoded in the HAPI JSON
#        response. To make parsers happy, we convert these special values to
#        string parsable by Python float() and JS Number().

_JSON_FLOAT_FIX = {
    'nan': 'NaN',
    'inf': 'Infinity',
    '-inf': '-Infinity',
}


def json_float(value):
    return float(value) if isfinite(value) else _JSON_FLOAT_FIX[str(value)]


DEFAULT_JSON_FORMATTING = lambda v: v # simple pass-trough
JSON_FORMATTING = {
    str_: str,
    bytes_: lambda v: bytes(v).decode('ascii'),
    bool_: int,
    int8: int,
    int16: int,
    int32: int,
    int64: int,
    uint8: int,
    uint16: int,
    uint32: int,
    uint64: int,
    float32: json_float,
    float64: json_float,
    datetime64: format_datetime64,
}


def arrays_to_json_fragment(arrays, encoding='ascii', newline="\r\n"):
    """ Convert Numpy arrays into bytes array holding the JSON-encoded records."""
    newline = newline.encode(encoding)

    def _encode_records(arrays):
        for record in arrays_to_plain_records(arrays):
            yield newline
            yield json.dumps(record).encode(encoding)
            yield b","

    return b"".join(_encode_records(arrays))


def arrays_to_plain_records(arrays):
    """ Convert Numpy arrays into JSON serializable records."""
    field_formatting = [
        JSON_FORMATTING.get(array.dtype.type) or DEFAULT_JSON_FORMATTING
        for array in arrays
    ]

    scalar_flags = [not array.shape[1:] for array in arrays]
    arrays = [flatten_records(array) for array in arrays]

    for record in zip(*arrays):
        yield [
            item[0] if is_scalar else item
            for item, is_scalar in zip((
                [format_(item) for item in field]
                for field, format_ in zip(record, field_formatting)
            ), scalar_flags)
        ]
