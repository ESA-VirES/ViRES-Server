#-------------------------------------------------------------------------------
#
# product collection management - common utilities
#
# Authors: Martin Paces <martin.paces@eox.at>
#-------------------------------------------------------------------------------
# Copyright (C) 2023 EOX IT Services GmbH
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

from os.path import isfile
from vires.models import ProductLocation
from .._common import Subcommand, time_spec


class ProductCollectionSelectionSubcommand(Subcommand):
    """ Product collection selection subcommand. """

    def add_arguments(self, parser):
        parser.add_argument("identifier", nargs="*")
        parser.add_argument(
            "-t", "--product-type", dest="product_type", action='append', help=(
                "Optional filter on the collection product types. "
                "Multiple product types are allowed."
            )
        )
        parser.add_argument(
            "-m", "--mission", dest="mission", action="append", help=(
                "Optional filter on the mission type. "
                "Multiple missions are allowed."
            )
        )
        parser.add_argument(
            "-s", "--spacecraft", dest="spacecraft", action="append", help=(
                "Optional filter on the spacecraft identifier. "
                "Multiple spacecrafts are allowed."
            )
        )
        parser.add_argument(
            "-g", "--grade", "--class", dest="grade", action="append", help=(
                "Optional filter on the product grade (class). "
                "Multiple values are allowed. "
            )
        )

    def select_collections(self, query, **kwargs):
        """ Select products based on the CLI parameters. """
        query = query.prefetch_related("type", "spacecraft")

        product_types = set(kwargs["product_type"] or [])
        if product_types:
            query = query.filter(type__identifier__in=product_types)

        missions = set(kwargs["mission"] or [])
        if missions:
            query = query.filter(spacecraft__mission__in=missions)

        spacecrafts = set(kwargs["spacecraft"] or [])
        if spacecrafts:
            query = query.filter(spacecraft__spacecraft__in=spacecrafts)

        grades = set(kwargs["grade"] or [])
        if grades:
            query = query.filter(grade__in=grades)

        query = self._select_collections_by_id(query, **kwargs)

        return query

    def _select_collections_by_id(self, query, **kwargs):
        identifiers = set(kwargs["identifier"])
        if identifiers:
            query = query.filter(identifier__in=identifiers)
        return query


class ProductCollectionSelectionProtectedSubcommand(ProductCollectionSelectionSubcommand):
    """ Product collection selection subcommand requiring --all if no id given."""

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "-a", "--all", dest="select_all", action="store_true", default=False,
            help="Select all product collections."
        )

    def _select_collections_by_id(self, query, **kwargs):
        identifiers = set(kwargs['identifier'])
        if identifiers or not kwargs['select_all']:
            query = query.filter(identifier__in=identifiers)
            if not identifiers:
                self.warning(
                    "No identifier selected and no collection will be removed. "
                    "Use the --all option to remove all matched items."
                )
        return query
