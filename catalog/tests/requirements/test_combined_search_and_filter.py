"""Requirement: combine the search and the filters."""

from catalog.models import MatchMode
from catalog.tests.requirements.base import (
    CategoryName,
    Query,
    RequirementsTestCase,
    Stock,
    TagName,
    titles,
)


class CombinedSearchAndFilterTests(RequirementsTestCase):
    def test_search_and_category(self):
        self.assertEqual(
            self.listed(Query.COPPER, categories=[CategoryName.WIRE]),
            titles(Stock.COPPER_WIRE, Stock.WIRE_CUTTER),
        )
        self.assertEqual(
            self.listed(Query.COPPER, categories=[CategoryName.TOOLS]),
            titles(Stock.WIRE_CUTTER),
        )

    def test_search_and_tag(self):
        self.assertEqual(
            self.listed(Query.WIRE, tags=[TagName.STEEL]), titles(Stock.WIRE_CUTTER)
        )

    def test_category_and_tag(self):
        self.assertEqual(
            self.listed(categories=[CategoryName.WIRE], tags=[TagName.STEEL]),
            titles(Stock.STEEL_CONDUIT, Stock.WIRE_CUTTER),
        )

    def test_search_category_and_tag_together(self):
        everything = {
            "search_query": Query.COPPER,
            "categories": [CategoryName.TOOLS],
            "tags": [TagName.STEEL],
        }
        self.assertEqual(self.listed(**everything), titles(Stock.WIRE_CUTTER))
        # Each extra condition only narrows the list. One that nothing satisfies
        # empties it.
        self.assertEqual(self.listed(**{**everything, "tags": [TagName.OUTDOOR]}), [])

    def test_match_modes_work_inside_a_combination(self):
        # In Wire, but without Steel.
        self.assertEqual(
            self.listed(
                categories=[CategoryName.WIRE],
                tags=[TagName.STEEL],
                tag_match=MatchMode.EXCLUDE_ANY,
            ),
            titles(Stock.COPPER_WIRE),
        )

    def test_a_combination_lists_each_product_once(self):
        # Wire Cutter is in both categories and has both tags.
        listed = self.listed(
            categories=[CategoryName.WIRE, CategoryName.TOOLS],
            tags=[TagName.COPPER, TagName.STEEL],
        )
        self.assertEqual(listed.count(Stock.WIRE_CUTTER.title), 1)
