"""Requirement: filter products by category."""

from catalog.models import MatchMode
from catalog.tests.requirements.base import (
    CategoryName,
    RequirementsTestCase,
    Stock,
    titles,
)


class FilterByCategoryTests(RequirementsTestCase):
    def test_one_category_lists_only_its_products(self):
        self.assertEqual(
            self.listed(categories=[CategoryName.TOOLS]),
            titles(Stock.CLAW_HAMMER, Stock.WIRE_CUTTER),
        )

    def test_several_categories_list_products_in_any_of_them(self):
        self.assertEqual(
            self.listed(categories=[CategoryName.WIRE, CategoryName.LIGHTING]),
            titles(
                Stock.COPPER_WIRE,
                Stock.STEEL_CONDUIT,
                Stock.WIRE_CUTTER,
                Stock.FLOODLIGHT,
            ),
        )

    def test_all_of_lists_only_products_in_every_selected_category(self):
        self.assertEqual(
            self.listed(
                categories=[CategoryName.WIRE, CategoryName.TOOLS],
                category_match=MatchMode.ALL,
            ),
            titles(Stock.WIRE_CUTTER),
        )
