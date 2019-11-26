#-------------------------------------------------------------------------------
#
# Cached product management command.
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
#pylint: disable=missing-docstring

from logging import getLogger
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from eoxserver.resources.coverages.management.commands import CommandOutputMixIn
from vires.aux_kp import update_kp
from vires.aux_dst import update_dst
from vires.aux_f107 import update_aux_f107_2_
from vires.orbit_counter import update_orbit_counter_file
from vires.model_mma import (
    merge_mma_sha_2f, filter_mma_sha_2f, merge_mma_sha_2c, filter_mma_sha_2c,
)
from vires.cached_products import (
    copy_file, update_cached_product, simple_cached_product_updater,
    InvalidSourcesError,
)


class Command(CommandOutputMixIn, BaseCommand):

    help = """ Update cached product. """

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            "product_type", help="Product type",
            choices=list(sorted(CACHED_PRODUCTS)),
        )
        parser.add_argument(
            "source", nargs="+", help="Source filename or URL."
        )

    def handle(self, *args, **kwargs):
        product_type = kwargs['product_type']
        source = kwargs['cource']
        product_info = CACHED_PRODUCTS[product_type]
        try:
            update_cached_product(
                sources=source,
                destination=product_info["filename"],
                updater=product_info.get("updater", copy_file),
                filter_=product_info.get("filter"),
                tmp_extension=product_info.get("tmp_extension"),
                logger=getLogger(__name__)
            )
        except InvalidSourcesError as exc:
            raise CommandError(str(exc))


def configure_cached_product(product_type, **kwargs):
    """ Cached product configuration. """
    if product_type in CACHED_PRODUCTS:
        CACHED_PRODUCTS[product_type].update(kwargs)


# load the default cached products
CACHED_PRODUCTS = {
    product_type: {"filename": filename}
    for product_type, filename
    in getattr(settings, "VIRES_CACHED_PRODUCTS", {}).iteritems()
}

configure_cached_product(
    "MMA_CHAOS6",
    updater=merge_mma_sha_2c,
    filter=filter_mma_sha_2c,
    tmp_extension=".tmp.cdf"
)

configure_cached_product(
    "MMA_SHA_2C",
    updater=merge_mma_sha_2c,
    filter=filter_mma_sha_2c,
    tmp_extension=".tmp.cdf"
)

configure_cached_product(
    "MMA_SHA_2F",
    updater=merge_mma_sha_2f,
    filter=filter_mma_sha_2f,
    tmp_extension=".tmp.cdf"
)

configure_cached_product(
    "AUX_F10_2_",
    updater=simple_cached_product_updater(update_aux_f107_2_),
    tmp_extension=".tmp.cdf"
)

for spacecraft in getattr(settings, "VIRES_SPACECRAFTS", []):
    configure_cached_product(
        "AUX%sORBCNT" % spacecraft,
        label="Swarm %s orbit counter" % spacecraft,
        updater=simple_cached_product_updater(update_orbit_counter_file),
        tmp_extension=".tmp.cdf"
    )

    #configure_cached_product(
    #    "AUX%sODBGEO" % spacecraft,
    #    label=(
    #        "Swarm %s orbit directions in geographic coordinates"
    #        % spacecraft
    #    ),
    #    tmp_extension=".tmp.cdf"
    #)

    #configure_cached_product(
    #    "AUX%sODBMAG" % spacecraft,
    #    label=(
    #        "Swarm %s orbit directions in magnetic (QD) coordinates"
    #        % spacecraft
    #    ),
    #    tmp_extension=".tmp.cdf"
    #)


CACHED_PRODUCTS.update({
    "GFZ_AUX_DST": {
        "filename": settings.VIRES_AUX_DB_DST,
        "label": 'Dst-index',
        "updater": simple_cached_product_updater(update_dst),
        "tmp_extension": ".tmp.cdf",
    },
    "GFZ_AUX_KP": {
        "filename": settings.VIRES_AUX_DB_KP,
        "label": 'Kp-index',
        "updater": simple_cached_product_updater(update_kp),
        "tmp_extension": ".tmp.cdf",
    },
})
