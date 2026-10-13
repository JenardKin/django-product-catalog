from django.urls import path

from . import views

urlpatterns = [
    path("product-search/", views.product_search_view, name="product_search"),
    path(
        "category-autocomplete/",
        views.CategoryAutocomplete.as_view(),
        name="category-autocomplete",
    ),
    path("tag-autocomplete/", views.TagAutocomplete.as_view(), name="tag-autocomplete"),
]
