#-------------------------------------------------------------------------------
#
# Project: EOxServer <http://eoxserver.org>
# Authors: Martin Paces <martin.paces@eox.at>
#
#-------------------------------------------------------------------------------
# Copyright (C) 2017 EOX IT Services GmbH
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

from optparse import make_option
from logging import getLogger
from django.conf import settings
from django.core.management.base import BaseCommand
from eoxserver.resources.coverages.management.commands import CommandOutputMixIn
from vires.orbit_counter import update_orbit_counter_file
from vires.cached_products import (
    update_cached_product, simple_cached_product_updater,
)

DEPRECATION_WARNING = (
    "The 'vires_update_orbit_counter' command is deprecated! "
    "Use 'vires_update_cached_file' instead."
)

class Command(CommandOutputMixIn, BaseCommand):
    """ Update Swarm orbit counter files from the given source.
    """
    help = DEPRECATION_WARNING
    option_list = BaseCommand.option_list + (
        make_option(
            "-a", "--alpha-url", "--alpha-filename", "--alpha",
            dest="filename_a", action="store", default=None,
            help="Alpha orbit number counter source (-, file-name, or URL)."
        ),
        make_option(
            "-b", "--beta-url", "--beta-filename", "--beta",
            dest="filename_b", action="store", default=None,
            help="Beta orbit number number source (-, file-name, or URL)."
        ),
        make_option(
            "-c", "--charlie-url", "--charlie-filename", "--charlie",
            dest="filename_c", action="store", default=None,
            help="Charlie orbit number number source (-, file-name, or URL)."
        ),
    )

    cached_products = [
        ("filename_a", settings.VIRES_ORBIT_COUNTER_FILE['A']),
        ("filename_b", settings.VIRES_ORBIT_COUNTER_FILE['B']),
        ("filename_c", settings.VIRES_ORBIT_COUNTER_FILE['C']),
    ]

    def handle(self, *args, **kwargs):
        logger = getLogger(__name__)
        logger.warn(DEPRECATION_WARNING)

        for opt_name, destination in self.cached_products:
            if kwargs[opt_name] is not None:
                update_cached_product(
                    [kwargs[opt_name]], destination,
                    simple_cached_product_updater(update_orbit_counter_file),
                    tmp_extension=".tmp.cdf", logger=logger,
                )
