"""Requirement: at least 5 categories, 10 tags and 20 products of sample data."""

from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from catalog.models import Category, Product, Tag


class SampleDataTests(TestCase):
    """The shipped CSV files meet the minimum sample data."""

    def setUp(self):
        call_command("seed_catalog", stdout=StringIO())

    def test_there_are_at_least_5_categories_10_tags_and_20_products(self):
        self.assertGreaterEqual(Category.objects.count(), 5)
        self.assertGreaterEqual(Tag.objects.count(), 10)
        self.assertGreaterEqual(Product.objects.count(), 20)

    def test_every_product_has_a_category_and_a_tag(self):
        self.assertFalse(Product.objects.filter(categories=None).exists())
        self.assertFalse(Product.objects.filter(tags=None).exists())
