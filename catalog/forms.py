from dal import autocomplete
from django import forms

from .models import Category, MatchMode, SortOrder, Tag


class ProductFilterForm(forms.Form):
    """GET form for the product search page. Every field is optional."""

    search_query = forms.CharField(
        label="Search",
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Search name, description, or SKU",
                "aria-label": "Search",
            }
        ),
    )

    # Use django-autocomplete-light widget for categories and tags filter
    # for autocomplete dropdown and lazy loading of list of categories and tags.

    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=autocomplete.ModelSelect2Multiple(
            url="category-autocomplete",
            attrs={
                # placeholder text when no category is selected
                "data-placeholder": "Any category",
                "data-width": "100%",
            },
        ),
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=autocomplete.ModelSelect2Multiple(
            url="tag-autocomplete",
            attrs={
                # placeholder text when no tag is selected
                "data-placeholder": "Any tag",
                "data-width": "100%",
            },
        ),
    )

    # How the selected filters and sort are combined to build a query;
    # see ProductQuerySet._match_m2m_filter().

    category_match = forms.ChoiceField(
        label="Category match",
        choices=MatchMode.choices,
        initial=MatchMode.ANY,
        required=False,
        widget=forms.Select(attrs={"class": "auto-update"}),
    )

    tag_match = forms.ChoiceField(
        label="Tag match",
        choices=MatchMode.choices,
        initial=MatchMode.ANY,
        required=False,
        widget=forms.Select(attrs={"class": "auto-update"}),
    )

    sort = forms.ChoiceField(
        label="Sort by",
        choices=SortOrder.choices,
        initial=SortOrder.NAME_ASC,
        required=False,
        widget=forms.Select(attrs={"class": "auto-update"}),
    )
