from django.db import models
from model_utils.models import TimeStampedModel


class SearchMetadataMixin(TimeStampedModel):
    """
    Abstract Model for catalog models shared searchable indexed fields.
    Adds created and modified fields inherited from TimeStampedModel
    """

    name = models.CharField(
        max_length=100,
        unique=True,  # sets unique index
        help_text="Display name. Must be unique.",
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,  # sets unique index
        help_text="URL-safe identifier, e.g. 'wire-cable'.",
    )
    description = models.CharField(
        max_length=500,
        blank=False,
        db_index=True,  # sets index for prefix searches
        help_text="Short description (up to 500 characters).",
    )

    class Meta:
        abstract = True
