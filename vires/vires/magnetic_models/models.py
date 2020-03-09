#-------------------------------------------------------------------------------
#
# Magnetic models - definition of all available magnetic models
#
# Authors: Martin Paces <martin.paces@eox.at>
#-------------------------------------------------------------------------------
# Copyright (C) 2018 EOX IT Services GmbH
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
#pylint: disable=too-few-public-methods

from os.path import basename
from logging import getLogger
from numpy import inf
from eoxmagmod.data import CHAOS_STATIC_LATEST, IGRF12, IGRF13, LCS1, MF7
from eoxmagmod import (
    load_model_shc,
    load_model_swarm_mma_2c_internal,
    load_model_swarm_mma_2c_external,
    load_model_swarm_mma_2f_geo_internal,
    load_model_swarm_mma_2f_geo_external,
    load_model_swarm_mio_internal,
    load_model_swarm_mio_external,
)
from eoxmagmod.time_util import decimal_year_to_mjd2000
from eoxmagmod.magnetic_model.parser_shc import parse_shc_header

from ..util import cached_property
from ..file_util import FileChangeMonitor
from .files import (
    ModelFileWithLiteralSource,
    CachedModelFileWithSourceFile,
    CachedComposedModelFile,
)


DIPOLE_MODEL = "IGRF"
IGRF12_SOURCE = "SW_OPER_AUX_IGR_2__19000101T000000_20191231T235959_0102"
IGRF13_SOURCE = "SW_OPER_AUX_IGR_2__19000101T000000_20241231T235959_0103"
CHAOS_STATIC_SOURCE = basename(CHAOS_STATIC_LATEST)
LCS1_SOURCE = basename(LCS1)
MF7_SOURCE = basename(MF7)


class ModelFactory():
    """ Model factory class. """
    def __init__(self, loader, model_files):
        self.loader = loader
        self.model_files = model_files
        self._tracker = FileChangeMonitor()

    @cached_property
    def files(self):
        """ Get list of files required by this model. """
        return [model_file.filename for model_file in self.model_files]

    @property
    def model_changed(self):
        """ Check if the model files changed. """
        return self._tracker.changed(*self.files)

    def __call__(self):
        """ Create new model instance. """
        return self.loader(*self.files)

    @property
    def sources(self):
        """ Load model sources. """
        return [model_file.sources for model_file in self.model_files]


class ModelCache():
    """ Model cache class. """
    def __init__(self, model_factories, model_aliases=None, logger=None):
        self.logger = logger or getLogger(__name__)
        self.model_factories = model_factories
        self.model_aliases = model_aliases or {}
        self.cache = {}
        self.sources = {}

    def get_model(self, model_id):
        """ Get model for given identifier. """
        model, _ = self.get_model_with_sources(model_id)
        return model

    def get_model_with_sources(self, model_id):
        """ Get model with sources for given identifier. """
        model_id = self.model_aliases.get(model_id, model_id)

        model_factory = self.model_factories.get(model_id)
        if not model_factory:
            return None, None # invalid model id

        model = self.cache.get(model_id)
        if model_factory.model_changed or not model:
            self.cache[model_id] = model = model_factory()
            self.sources[model_id] = sources = model_factory.sources
            self.logger.info("%s model loaded", model_id)
        else:
            sources = self.sources[model_id]
        return model, sources


MODEL_ALIASES = {
    "IGRF": "IGRF13",
    "MCO_SHA_2X": "CHAOS-Core",
    "CHAOS-6-Core": "CHAOS-Core",
    "CHAOS-6-Static": "CHAOS-Static",
    "CHAOS-6-MMA-Primary": "CHAOS-MMA-Primary",
    "CHAOS-6-MMA-Secondary": "CHAOS-MMA-Secondary",
}


def shc_validity_reader(filename):
    """ SHC model validity reader. """
    return _shc_validity_reader(filename, decimal_year_to_mjd2000)


def _shc_validity_reader(filename, to_mjd2000):
    """ Low-level SHC model validity reader. """
    with open(filename) as file_in:
        header = parse_shc_header(file_in)
    return (
        to_mjd2000(header["validity_start"]), to_mjd2000(header["validity_end"])
    )


def mio_validity_reader(_):
    """ MIO model validity reader. """
    return (-inf, +inf)


MODEL_FACTORIES = {
    "IGRF12": ModelFactory(
        lambda file_: load_model_shc(file_, interpolate_in_decimal_years=True),
        [ModelFileWithLiteralSource(IGRF12, IGRF12_SOURCE, shc_validity_reader)]
    ),
    "IGRF13": ModelFactory(
        lambda file_: load_model_shc(file_, interpolate_in_decimal_years=True),
        [ModelFileWithLiteralSource(IGRF13, IGRF13_SOURCE, shc_validity_reader)]
    ),
    "CHAOS-Static": ModelFactory(
        load_model_shc,
        [ModelFileWithLiteralSource(
            CHAOS_STATIC_LATEST, CHAOS_STATIC_SOURCE, shc_validity_reader
        )]
    ),
    "CHAOS-Core": ModelFactory(
        load_model_shc,
        [CachedModelFileWithSourceFile("MCO_SHA_2X", shc_validity_reader)]
    ),
    "LCS-1": ModelFactory(
        load_model_shc,
        [ModelFileWithLiteralSource(LCS1, LCS1_SOURCE, shc_validity_reader)]
    ),
    "MF7": ModelFactory(
        load_model_shc,
        [ModelFileWithLiteralSource(MF7, MF7_SOURCE, shc_validity_reader)]
    ),
    "MCO_SHA_2C": ModelFactory(
        load_model_shc,
        [CachedModelFileWithSourceFile("MCO_SHA_2C", shc_validity_reader)]
    ),
    "MCO_SHA_2D": ModelFactory(
        load_model_shc,
        [CachedModelFileWithSourceFile("MCO_SHA_2D", shc_validity_reader)]
    ),
    "MLI_SHA_2C": ModelFactory(
        load_model_shc,
        [CachedModelFileWithSourceFile("MLI_SHA_2C", shc_validity_reader)]
    ),
    "MLI_SHA_2D": ModelFactory(
        load_model_shc,
        [CachedModelFileWithSourceFile("MLI_SHA_2D", shc_validity_reader)]
    ),
    "MMA_SHA_2C-Primary": ModelFactory(
        load_model_swarm_mma_2c_external,
        [CachedComposedModelFile("MMA_SHA_2C")]
    ),
    "MMA_SHA_2C-Secondary": ModelFactory(
        load_model_swarm_mma_2c_internal,
        [CachedComposedModelFile("MMA_SHA_2C")]
    ),
    "MMA_SHA_2F-Primary": ModelFactory(
        load_model_swarm_mma_2f_geo_external,
        [CachedComposedModelFile("MMA_SHA_2F")]
    ),
    "MMA_SHA_2F-Secondary": ModelFactory(
        load_model_swarm_mma_2f_geo_internal,
        [CachedComposedModelFile("MMA_SHA_2F")]
    ),
    "MIO_SHA_2C-Primary": ModelFactory(
        load_model_swarm_mio_external,
        [CachedModelFileWithSourceFile("MIO_SHA_2C", mio_validity_reader)]
    ),
    "MIO_SHA_2C-Secondary": ModelFactory(
        load_model_swarm_mio_internal,
        [CachedModelFileWithSourceFile("MIO_SHA_2C", mio_validity_reader)]
    ),
    "MIO_SHA_2D-Primary": ModelFactory(
        load_model_swarm_mio_external,
        [CachedModelFileWithSourceFile("MIO_SHA_2D", mio_validity_reader)]
    ),
    "MIO_SHA_2D-Secondary": ModelFactory(
        load_model_swarm_mio_internal,
        [CachedModelFileWithSourceFile("MIO_SHA_2D", mio_validity_reader)]
    ),
    "CHAOS-MMA-Primary": ModelFactory(
        load_model_swarm_mma_2c_external,
        [CachedComposedModelFile("MMA_CHAOS_")]
    ),
    "CHAOS-MMA-Secondary": ModelFactory(
        load_model_swarm_mma_2c_internal,
        [CachedComposedModelFile("MMA_CHAOS_")]
    ),
}

# list of all available models
MODEL_LIST = list(MODEL_FACTORIES) + list(MODEL_ALIASES)

MODEL_CACHE = ModelCache(MODEL_FACTORIES, MODEL_ALIASES)
