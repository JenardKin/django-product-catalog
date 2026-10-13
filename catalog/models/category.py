from .mixins import SearchMetadataMixin


class Category(SearchMetadataMixin):
    """
    Product category grouping model (e.g. "Conduit & Fittings").
    """

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name
