#-------------------------------------------------------------------------------
#
# Process Utilities - variables input parsers
#
# Authors: Martin Paces <martin.paces@eox.at>
#-------------------------------------------------------------------------------
# Copyright (C) 2016 EOX IT Services GmbH
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
# pylint: disable=too-many-branches,unused-argument

import re

RE_SUBTRACTED_VARIABLE = re.compile(r'(.+)_(?:res|diff)([ABC])([ABC])')


def parse_variables(input_id, variables_strings):
    """ Variable parsers.  """
    variables_strings = str(variables_strings.strip())
    return [
        var.strip() for var in variables_strings.split(',')
    ] if variables_strings else []


def get_subtracted_variables(variables):
    """ Extract subtracted variables from a list of all variables. """
    return [
        (variable, match.groups()) for variable, match in (
            (var, RE_SUBTRACTED_VARIABLE.match(var)) for var in variables
        ) if match
    ]
