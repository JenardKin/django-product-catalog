"""Requirement: an HTML page where a user searches and filters."""

from django.urls import reverse

from catalog.tests.requirements.base import (
    RequirementsTestCase,
    Stock,
)


class SearchPageTests(RequirementsTestCase):
    """The HTML page where a user searches and filters."""

    def page(self):
        return self.client.get(reverse("product_search"))

    def test_the_page_has_the_search_box_and_both_filters(self):
        response = self.page()
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        for field in ("search_query", "categories", "tags"):
            with self.subTest(field=field):
                self.assertIn(f'name="{field}"', html)

    def test_the_page_lists_the_products_and_their_categories_and_tags(self):
        html = self.page().content.decode()
        cutter = Stock.WIRE_CUTTER
        self.assertIn(f"{len(Stock)} products found", html)
        self.assertIn(f"Categories: {', '.join(sorted(cutter.categories))}", html)
        self.assertIn(f"Tags: {', '.join(sorted(cutter.tags))}", html)

    def test_the_page_is_open_to_anyone_without_signing_in(self):
        self.client.logout()
        self.assertEqual(self.page().status_code, 200)
