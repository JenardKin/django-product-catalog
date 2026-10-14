"""Requirement: models with the right relationships."""

from catalog.models import Category, Product, Tag
from catalog.tests.requirements.base import (
    CategoryName,
    RequirementsTestCase,
    Stock,
    TagName,
    titles,
    with_category,
    with_tag,
)


class ModelRelationshipTests(RequirementsTestCase):
    def test_a_product_has_several_categories_and_several_tags(self):
        cutter = Product.objects.get(sku=Stock.WIRE_CUTTER.sku)
        self.assertEqual(
            sorted(cutter.categories.values_list("name", flat=True)),
            sorted(Stock.WIRE_CUTTER.categories),
        )
        self.assertEqual(
            sorted(cutter.tags.values_list("name", flat=True)),
            sorted(Stock.WIRE_CUTTER.tags),
        )

    def test_a_category_lists_its_products(self):
        category = Category.objects.get(name=CategoryName.WIRE)
        self.assertEqual(
            sorted(category.products.values_list("name", flat=True)),
            titles(*with_category(CategoryName.WIRE)),
        )

    def test_a_tag_lists_its_products(self):
        tag = Tag.objects.get(name=TagName.STEEL)
        self.assertEqual(
            sorted(tag.products.values_list("name", flat=True)),
            titles(*with_tag(TagName.STEEL)),
        )
