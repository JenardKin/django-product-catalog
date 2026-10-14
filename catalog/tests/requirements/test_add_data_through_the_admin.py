"""Requirement: data can be added through the Django admin."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils.text import slugify

from catalog.models import Category, Product, Tag
from catalog.tests.requirements.base import (
    CategoryName,
    Stock,
    TagName,
)


class AddDataThroughTheAdminTests(TestCase):
    """Categories, tags and products can be created with the admin forms."""

    @classmethod
    def setUpTestData(cls):
        cls.admin = get_user_model().objects.create_superuser(
            "admin", "admin@example.com", "pw-admin-1"
        )

    def setUp(self):
        self.client.force_login(self.admin)

    def add(self, model, data):
        return self.client.post(reverse(f"admin:catalog_{model}_add"), data)

    @staticmethod
    def name_form(name):
        return {"name": name.value, "slug": slugify(name), "description": name.value}

    @staticmethod
    def product_form(item, **extra):
        return {
            "name": item.title,
            "slug": item.slug,
            "sku": item.sku,
            "description": item.description,
            **extra,
        }

    def add_a_category_and_a_tag(self):
        category, tag = CategoryName.WIRE, TagName.COPPER
        self.add("category", self.name_form(category))
        self.add("tag", self.name_form(tag))
        return Category.objects.get(name=category), Tag.objects.get(name=tag)

    def test_a_product_with_categories_and_tags_can_be_added(self):
        category, tag = self.add_a_category_and_a_tag()
        response = self.add(
            "product",
            self.product_form(
                Stock.COPPER_WIRE, categories=[category.pk], tags=[tag.pk]
            ),
        )
        self.assertEqual(response.status_code, 302)
        product = Product.objects.get()
        self.assertEqual(list(product.categories.all()), [category])
        self.assertEqual(list(product.tags.all()), [tag])

    def test_a_product_without_a_category_or_a_tag_is_refused(self):
        category, tag = self.add_a_category_and_a_tag()
        no_tag = self.add(
            "product", self.product_form(Stock.COPPER_WIRE, categories=[category.pk])
        )
        no_category = self.add(
            "product", self.product_form(Stock.COPPER_WIRE, tags=[tag.pk])
        )
        for response in (no_tag, no_category):
            self.assertEqual(response.status_code, 200)  # the form is shown again
            self.assertContains(response, "This field is required")
        self.assertFalse(Product.objects.exists())
