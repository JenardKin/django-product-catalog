import re
from enum import Enum, StrEnum

from django.test import TestCase
from django.urls import reverse
from django.utils.text import slugify

from catalog.models import Category, Product, Tag


class CategoryName(StrEnum):
    WIRE = "Wire"
    TOOLS = "Tools"
    LIGHTING = "Lighting"


class TagName(StrEnum):
    COPPER = "Copper"
    STEEL = "Steel"
    OUTDOOR = "Outdoor"


class Stock(Enum):
    """
    Test Data Enum
    """

    COPPER_WIRE = (
        "Copper Wire",
        "W-1",
        "Solid copper building wire",
        (CategoryName.WIRE,),
        (TagName.COPPER,),
    )
    STEEL_CONDUIT = (
        "Steel Conduit",
        "C-1",
        "Metal tubing that protects wiring",
        (CategoryName.WIRE,),
        (TagName.STEEL,),
    )
    CLAW_HAMMER = (
        "Claw Hammer",
        "T-1",
        "Hammer with a steel head",
        (CategoryName.TOOLS,),
        (TagName.STEEL,),
    )
    WIRE_CUTTER = (
        "Wire Cutter",
        "T-2",
        "Side cutters for copper wire",
        (CategoryName.TOOLS, CategoryName.WIRE),
        (TagName.COPPER, TagName.STEEL),
    )
    FLOODLIGHT = (
        "Floodlight",
        "L-1",
        "Outdoor LED light",
        (CategoryName.LIGHTING,),
        (TagName.OUTDOOR,),
    )

    def __init__(self, title, sku, description, categories, tags):
        self.title = title
        self.sku = sku
        self.description = description
        self.categories = categories
        self.tags = tags

    @property
    def slug(self):
        return slugify(f"{self.title} {self.sku}")


class Query(StrEnum):
    """Search texts, chosen for the stock above."""

    TUBING_PART = "tubin"  # only in the description of Steel Conduit
    TUBING_CAPITALS = "TUBING"
    COPPER = "copper"  # in a name, in a description, and in a tag
    WIRE = "wire"
    NOTHING = "zzz-no-match"


def titles(*products):
    """The sorted titles of these products, as the search page lists them."""
    return sorted(product.title for product in products)


def with_category(name):
    return [product for product in Stock if name in product.categories]


def with_tag(name):
    return [product for product in Stock if name in product.tags]


class RequirementsTestCase(TestCase):
    """The products of ``Stock``, with their categories and tags."""

    @classmethod
    def setUpTestData(cls):
        cls.ids = {}
        for name in CategoryName:
            category = Category.objects.create(
                name=name.value, slug=slugify(name), description=name.value
            )
            cls.ids[name] = category.pk
        for name in TagName:
            tag = Tag.objects.create(
                name=name.value, slug=slugify(name), description=name.value
            )
            cls.ids[name] = tag.pk
        for item in Stock:
            product = Product.objects.create(
                name=item.title,
                slug=item.slug,
                sku=item.sku,
                description=item.description,
            )
            product.categories.set([cls.ids[name] for name in item.categories])
            product.tags.set([cls.ids[name] for name in item.tags])

    def listed(
        self,
        search_query=None,
        categories=(),
        tags=(),
        category_match=None,
        tag_match=None,
    ):
        """The product titles the search page lists, sorted.

        The arguments are the form's fields. Categories and tags are given by name.
        """
        params = {}
        if search_query is not None:
            params["search_query"] = search_query
        if categories:
            params["categories"] = [self.ids[name] for name in categories]
        if tags:
            params["tags"] = [self.ids[name] for name in tags]
        if category_match:
            params["category_match"] = category_match
        if tag_match:
            params["tag_match"] = tag_match
        response = self.client.get(reverse("product_search"), params)
        self.assertEqual(response.status_code, 200)
        return sorted(
            re.findall(r"<strong>([^<]+)</strong>", response.content.decode())
        )
