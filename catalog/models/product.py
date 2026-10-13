from django.db import models
from django.db.models import Count, Q

from .category import Category
from .mixins import SearchMetadataMixin
from .tag import Tag


class MatchMode(models.TextChoices):
    """
    Determines how the matching many-to-many filters on the Product Search Form should
    apply to the queryset.
    """

    ANY = "any", "Any of"  # includes objects matched to anything selected
    ALL = "all", "All of"  # includes objects matched to everything selected
    EXCLUDE_ANY = (
        "exclude_any",
        "None of (exclude any)",
    )  # excludes objects matched to anything selected
    EXCLUDE_ALL = (
        "exclude_all",
        "Not all of (exclude all)",
    )  # excludes objects matched to everything selected


class SortOrder(models.TextChoices):
    """
    Sort order choices for the Product Search Form results.
    """

    NAME_ASC = "name", "Name (A to Z)"  # sort order by name ascending
    NAME_DESC = "name_desc", "Name (Z to A)"  # sort order by name descending
    SKU_ASC = "sku", "SKU (A to Z)"  # sort order by SKU ascending
    SKU_DESC = "sku_desc", "SKU (Z to A)"  # sort order by SKU descending

    @property
    def order_by_fields(self):
        """
        Property to translate the sort order choice into a tuple of fields
        for sorting the queryset. Used by queryset.order_by()
        """
        if self == SortOrder.NAME_ASC:
            return ("name", "sku")
        if self == SortOrder.NAME_DESC:
            return ("-name", "-sku")
        if self == SortOrder.SKU_ASC:
            return ("sku",)
        return ("-sku",)  # SKU_DESC


class ProductQuerySet(models.QuerySet):
    """
    Chainable filters used by the product search page with an & (AND) operator.
    """

    def search_query(self, text):
        """Case insensitive partial match on the name, description or SKU."""
        text = (text or "").strip()
        if not text:
            return self
        return self.filter(
            Q(name__icontains=text)
            | Q(sku__icontains=text)
            | Q(description__icontains=text)
        )

    def categorized_as(self, categories, mode=MatchMode.ANY):
        """
        Filter products by categories by delegating to _match_m2m_filter helper.
        """
        through = self.model.categories.through
        return self._match_m2m_filter(through, "category_id", categories, mode)

    def tagged_as(self, tags, mode=MatchMode.ANY):
        """
        Filter products by tags by delegating to _match_m2m_filter helper.
        """
        through = self.model.tags.through
        return self._match_m2m_filter(through, "tag_id", tags, mode)

    def _match_m2m_filter(self, through, relational_field_name, objects, mode):
        """
        Filter products by a many-to-many relation, using the through table
        and the relational field name.

        The mode parameter determines how the filter is applied on the queryset.
        """
        mode = MatchMode(mode)
        ids = {obj.pk for obj in objects}

        # Check if there are objects to filter by. If not, return queryset
        if not ids:
            return self

        # Query the join table to get a list of product IDS that match the filters
        # set by the mode on the relational field

        links = through.objects.filter(**{f"{relational_field_name}__in": ids})

        # Keep only products linked to every filter selected by ensuring count matches.
        if mode in (MatchMode.ALL, MatchMode.EXCLUDE_ALL):
            links = (
                links.values("product_id")
                .annotate(matched=Count(relational_field_name, distinct=True))
                .filter(matched=len(ids))
            )

        # Build product id filter based on mode (exclude or include)
        product_ids = links.values("product_id")

        if mode in (MatchMode.EXCLUDE_ANY, MatchMode.EXCLUDE_ALL):
            return self.exclude(pk__in=product_ids)
        return self.filter(pk__in=product_ids)


class Product(SearchMetadataMixin):
    """
    Product model for a catalog application.

    The Stock Keeping Unit (SKU) is the unique identifier whereas the name and
    description are metadata for search and display. Even though it is unique,
    the SKU is not ideal as a Primary Key since it could be changed anytime.
    """

    # Redefine name field to remove unique constraint from the SearchMetadataMixin
    name = models.CharField(
        max_length=100,
        blank=False,
        help_text=("Display name of the product."),
    )
    sku = models.CharField(
        "Stock Keeping Unit",
        max_length=50,
        unique=True,
        blank=False,
        help_text=(
            "SKU (Stock Keeping Unit), a unique identifier for the product, "
            "e.g. 'WIR-1234'."
        ),
    )

    categories = models.ManyToManyField(
        Category,
        related_name="products",
        help_text="A product needs at least one category and can belong to several.",
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="products",
        help_text="A product needs at least one tag and can have several.",
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        ordering = ["name"]
        indexes = [
            # Add composite index for name and sku to optimize search queries
            models.Index(fields=["name", "sku"], name="product_name_sku_idx"),
        ]
        constraints = [
            # Ensure that name, description, and SKU are not populated as empty
            # strings at the database level.
            models.CheckConstraint(
                condition=~models.Q(name=""),
                name="product_name_not_empty",
            ),
            models.CheckConstraint(
                condition=~models.Q(description=""),
                name="product_description_not_empty",
            ),
            models.CheckConstraint(
                condition=~models.Q(sku=""),
                name="product_sku_not_empty",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.sku})"
