#-------------------------------------------------------------------------------
#
# Process Utilities - Input Parsers
#
# Project: VirES
# Authors: Martin Paces <martin.paces@eox.at>
#
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
import re
from collections import OrderedDict
from eoxmagmod import read_model_shc
from eoxserver.services.ows.wps.exceptions import InvalidInputValueError
from vires.util import get_color_scale, get_model
from vires.models import ProductCollection
from .time_series_product import ProductTimeSeries
from .model_magmod import MagneticModel
from .filters import ScalarRangeFilter, VectorComponentRangeFilter

RE_FILTER_NAME = re.compile(r'(^[^[]+)(?:\[([0-9])\])?$')
RE_RESIDUAL_VARIABLE = re.compile(r'(.+)_res([ABC])([ABC])')


def parse_style(input_id, style):
    """ Parse style value and return the corresponding colour-map object. """
    if style is None:
        return None
    try:
        return get_color_scale(style)
    except ValueError:
        raise InvalidInputValueError(
            input_id, "Invalid style identifier %r!" % style
        )


def parse_collections(input_id, source):
    """ Parse input collections definitions. """
    result = {}
    if not isinstance(source, dict):
        raise InvalidInputValueError(
            input_id, "JSON object expected!"
        )
    # resolve collection ids
    for label, collection_ids in source.iteritems():
        if not isinstance(collection_ids, (list, tuple)):
            raise InvalidInputValueError(
                input_id, "A list of collection identifiers expected for "
                "label %r!" % label
            )
        available_collections = dict(
            (obj.identifier, obj) for obj in ProductCollection.objects.filter(
                identifier__in=collection_ids
            )
        )
        try:
            result[label] = [
                available_collections[id_] for id_ in collection_ids
            ]
        except KeyError as exc:
            raise InvalidInputValueError(
                input_id, "Invalid collection identifier %r! (label: %r)" %
                (exc.args[0], label)
            )

    range_types = []
    master_rtype = None
    for label, collections in result.items():
        # master (first collection) must be always defined
        if len(collections) < 1:
            raise InvalidInputValueError(
                input_id, "Collection list must have at least one item!"
                " (label: %r)" % label
            )
        # master (first collection) must be always of the same range-type
        if master_rtype is None:
            master_rtype = collections[0].range_type
            range_types = [master_rtype] # master is always the first
        else:
            if master_rtype != collections[0].range_type:
                raise InvalidInputValueError(
                    input_id, "Master collection type mismatch!"
                    " (label: %r; )" % label
                )

        # slaves are optional
        # slaves' order does not matter

        # collect slave range-types
        slave_rtypes = []

        # for one label multiple collections of the same renge-type not allowed
        for rtype in (collection.range_type for collection in collections[1:]):
            if rtype == master_rtype or rtype in slave_rtypes:
                raise InvalidInputValueError(
                    input_id, "Multiple collections of the same type "
                    "are not allowed! (label: %r; )" % label
                )
            slave_rtypes.append(rtype)

        # collect all unique range-types
        range_types.extend(
            rtype for rtype in slave_rtypes if rtype not in range_types
        )

    # convert collections to product time-series
    return dict(
        (label, [ProductTimeSeries(collection) for collection in collections])
        for label, collections in result.iteritems()
    )


def parse_model(input_id, model_id, shc, shc_input_id="shc"):
    """ Parse model identifier and returns the corresponding model."""
    if model_id == "Custom_Model":
        try:
            model = read_model_shc(shc)
        except ValueError:
            raise InvalidInputValueError(
                shc_input_id, "Failed to parse the custom model coefficients."
            )
    else:
        model = get_model(model_id)
        if model is None:
            raise InvalidInputValueError(
                input_id, "Invalid model identifier %r!" % model_id
            )
    return model


def parse_models(input_id, model_ids, shc, shc_input_id="shc"):
    """ Parse model identifiers and returns an ordered dictionary
    the corresponding models.
    """
    models = OrderedDict()
    if model_ids.strip():
        for model_id in (id_.strip() for id_ in model_ids.split(",")):
            models[model_id] = parse_model(
                input_id, model_id, shc, shc_input_id
            )
    return models


def parse_models2(input_id, model_ids, shc, shc_input_id="shc"):
    """ Parse model identifiers and returns a list of the model sources. """
    models = parse_models(input_id, model_ids, shc, shc_input_id)
    return [MagneticModel(id_, model) for id_, model in models.iteritems()]


def parse_filters(input_id, filter_string):
    """ Parse filters' string. """
    try:
        filters = OrderedDict()
        if filter_string.strip():
            for item in filter_string.split(";"):
                name, bounds = item.split(":")
                name = name.strip()
                if not name:
                    raise ValueError("Invalid empty filter name!")
                lower, upper = [float(v) for v in bounds.split(",")]
                if name in filters:
                    raise ValueError("Duplicate filter %r!" % name)
                filters[name] = (lower, upper)
    except ValueError as exc:
        raise InvalidInputValueError(input_id, exc)
    return filters


def parse_filters2(input_id, filter_string):
    """ Parse filters' string and return list of the filter objects. """

    def _get_filter(name, vmin, vmax):
        match = RE_FILTER_NAME.match(name)
        if match is None:
            raise InvalidInputValueError(
                input_id, "Invalid filter name %r" % name
            )
        variable, component = match.groups()
        if component is None:
            return ScalarRangeFilter(variable, vmin, vmax)
        else:
            return VectorComponentRangeFilter(
                variable, int(component), vmin, vmax
            )

    return [
        _get_filter(name, vmin, vmax) for name, (vmin, vmax)
        in parse_filters(input_id, filter_string).iteritems()
    ]


def parse_variables(input_id, variables_strings):
    """ Variable parsers.  """
    variables_strings = str(variables_strings.strip())
    if variables_strings:
        variables = [var.strip() for var in variables_strings.split(',')]
        residual_variables = [
            (variable, match.groups()) for variable, match in (
                (var, RE_RESIDUAL_VARIABLE.match(var)) for var in variables
            ) if match
        ]
        return (variables, residual_variables)
    else:
        return [], []
