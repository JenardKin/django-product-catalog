from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.paginator import Paginator
from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.views.decorators.vary import vary_on_headers

from ..forms import ProductFilterForm
from ..models import MatchMode, Product, SortOrder

# Search form control sets
NO_FILTER_VALUES = {"", "any"}
FILTER_KEYS = {"search_query", "categories", "tags", "category_match", "tag_match"}


def _filters_active(params, name):
    """
    Checks if the filters are active
    """
    return any(value.strip() for value in params.getlist(name))


@require_GET
@vary_on_headers("HX-Request", "HX-History-Restore-Request")
def product_search_view(request):
    """
    Single endpoint for product search form. Either returns a full page template
    or just the results fragment via htmx.


    Improvements can be made from caching this shared endpoint and creating
    a proper invalidation when data changes so repeat database queries
    are avoided.
    """

    # Retrieve form data from request GET parameters and validate to get cleaned_data
    form = ProductFilterForm(request.GET or None)
    form.is_valid()
    data = getattr(form, "cleaned_data", {})

    # Use the ProductQuerySet methods to filter and sort product queryset based
    # on form data.
    products = (
        Product.objects.search_query(data.get("search_query"))
        .categorized_as(
            data.get("categories", []),
            data.get("category_match") or MatchMode.ANY,
        )
        .tagged_as(
            data.get("tags", []),
            data.get("tag_match") or MatchMode.ANY,
        )
    )
    ordering = SortOrder(data.get("sort") or SortOrder.NAME_ASC)

    # Categories and tags are shown for every row; prefetch them in two queries
    # and sort by ordering fields
    products = products.prefetch_related("categories", "tags").order_by(
        *ordering.order_by_fields
    )

    # Build the Django Paginator class
    pagination = settings.PAGINATION_SETTINGS
    # A page size of 0 or less would make the paginator divide by zero
    if pagination["PAGE_SIZE"] <= 0:
        raise ImproperlyConfigured(
            "PAGINATION_SETTINGS['PAGE_SIZE'] must be greater than 0, "
            f"got {pagination['PAGE_SIZE']}."
        )
    paginator = Paginator(products, pagination["PAGE_SIZE"])
    page = paginator.get_page(request.GET.get("page"))
    page_range = list(
        paginator.get_elided_page_range(
            page.number,
            on_each_side=pagination["PAGES_EACH_SIDE"],
            on_ends=pagination["PAGES_AT_ENDS"],
        )
    )

    # Strip the page number from the querystring to keep the filters
    # in the pagination links
    params = request.GET.copy()
    params.pop("page", None)

    # Drives the "Clear All Filters" button: shown only when something is set.
    has_filters = any(
        value.strip() not in NO_FILTER_VALUES
        for key, values in params.lists()
        if key in FILTER_KEYS
        for value in values
    )

    # Determine if a full page reload or fragment via htmx
    is_fragment = bool(request.htmx) and not request.htmx.history_restore_request

    context = {
        "form": form,
        "page": page,
        "page_range": page_range,
        "ellipsis": Paginator.ELLIPSIS,
        "has_filters": has_filters,
        "is_fragment": is_fragment,
        "querystring": params.urlencode(),
        "has_categories": _filters_active(params, "categories"),
        "has_tags": _filters_active(params, "tags"),
    }

    template = (
        "catalog/search_results.html" if is_fragment else "catalog/product_search.html"
    )
    return render(request, template, context)
