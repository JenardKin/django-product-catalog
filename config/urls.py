from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    # Redirect the landing page to the product search page.
    path("", RedirectView.as_view(pattern_name="product_search", query_string=True)),
    # Authentication Urls
    path("", include("catalog.auth_urls")),
    # Catalog Urls
    path("catalog/", include("catalog.urls")),
]
