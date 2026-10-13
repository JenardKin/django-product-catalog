from .mixins import SearchMetadataMixin


class Tag(SearchMetadataMixin):
    """
    Tag attribute model for Products (e.g. 'UL-listed', 'copper').
    """

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
