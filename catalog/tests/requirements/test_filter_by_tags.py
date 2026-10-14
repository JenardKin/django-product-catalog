"""Requirement: filter products by tags."""

from catalog.models import MatchMode
from catalog.tests.requirements.base import (
    RequirementsTestCase,
    Stock,
    TagName,
    titles,
)


class FilterByTagsTests(RequirementsTestCase):
    """Every match mode, for tags. Categories use the same code path."""

    def test_one_tag_lists_only_its_products(self):
        self.assertEqual(
            self.listed(tags=[TagName.COPPER]),
            titles(Stock.COPPER_WIRE, Stock.WIRE_CUTTER),
        )

    def test_several_tags_list_products_with_any_of_them(self):
        self.assertEqual(
            self.listed(tags=[TagName.COPPER, TagName.STEEL]),
            titles(
                Stock.COPPER_WIRE,
                Stock.STEEL_CONDUIT,
                Stock.CLAW_HAMMER,
                Stock.WIRE_CUTTER,
            ),
        )

    def test_all_of_lists_only_products_with_every_selected_tag(self):
        self.assertEqual(
            self.listed(tags=[TagName.COPPER, TagName.STEEL], tag_match=MatchMode.ALL),
            titles(Stock.WIRE_CUTTER),
        )

    def test_none_of_leaves_out_products_with_any_selected_tag(self):
        self.assertEqual(
            self.listed(tags=[TagName.COPPER], tag_match=MatchMode.EXCLUDE_ANY),
            titles(Stock.STEEL_CONDUIT, Stock.CLAW_HAMMER, Stock.FLOODLIGHT),
        )

    def test_not_all_of_leaves_out_products_with_every_selected_tag(self):
        self.assertEqual(
            self.listed(
                tags=[TagName.COPPER, TagName.STEEL],
                tag_match=MatchMode.EXCLUDE_ALL,
            ),
            titles(
                Stock.COPPER_WIRE,
                Stock.STEEL_CONDUIT,
                Stock.CLAW_HAMMER,
                Stock.FLOODLIGHT,
            ),
        )
