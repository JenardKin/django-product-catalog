"""Requirement: search products by description."""

from catalog.tests.requirements.base import (
    Query,
    RequirementsTestCase,
    Stock,
    titles,
)


class SearchByDescriptionTests(RequirementsTestCase):
    def test_it_matches_part_of_a_description(self):
        self.assertEqual(self.listed(Query.TUBING_PART), titles(Stock.STEEL_CONDUIT))

    def test_it_ignores_upper_and_lower_case(self):
        self.assertEqual(
            self.listed(Query.TUBING_CAPITALS), titles(Stock.STEEL_CONDUIT)
        )

    def test_it_returns_every_product_whose_description_has_the_text(self):
        # "copper" is in the description of Wire Cutter and in the name of Copper Wire.
        self.assertEqual(
            self.listed(Query.COPPER), titles(Stock.COPPER_WIRE, Stock.WIRE_CUTTER)
        )

    def test_it_also_matches_the_name_and_the_sku(self):
        self.assertEqual(self.listed(Stock.FLOODLIGHT.title), titles(Stock.FLOODLIGHT))
        self.assertEqual(
            self.listed(Stock.WIRE_CUTTER.sku.lower()), titles(Stock.WIRE_CUTTER)
        )

    def test_text_that_matches_nothing_lists_nothing(self):
        self.assertEqual(self.listed(Query.NOTHING), [])
