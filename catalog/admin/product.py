from dalf.admin import DALFModelAdmin, DALFRelatedFieldAjaxMulti
from django import forms
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from ..models import Category, Product, Tag
from ..resources import CategoryResource, ProductResource, TagResource


class SearchMetadataAdminMixin:
    """
    Admin mixin for models inheriting SearchMetadataMixin.
    """

    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}
    # Form order: the slug comes after the name and description it is built from.
    fields = ("name", "description", "slug")

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        # The description is a short CharField (limited to 500 characters), but
        # a multi-line box is easier to write in.
        if db_field.name == "description":
            kwargs["widget"] = forms.Textarea(attrs={"rows": 3, "cols": 60})
        return super().formfield_for_dbfield(db_field, request, **kwargs)


@admin.register(Category)
class CategoryAdmin(SearchMetadataAdminMixin, ImportExportModelAdmin):
    # django-import-export resource class for Category model
    resource_classes = [CategoryResource]
    list_display = ("name", "slug", "modified")


@admin.register(Tag)
class TagAdmin(SearchMetadataAdminMixin, ImportExportModelAdmin):
    # django-import-export resource class for Tag model
    resource_classes = [TagResource]
    list_display = ("name", "slug", "modified")


@admin.register(Product)
class ProductAdmin(SearchMetadataAdminMixin, DALFModelAdmin, ImportExportModelAdmin):
    # django-import-export resource class for Product model
    resource_classes = [ProductResource]
    search_fields = ("name", "slug", "sku", "description")
    list_display = ("name", "sku", "modified")
    # django autocomplete filter (dalf) for categories and tags filter optimization
    list_filter = (
        ("categories", DALFRelatedFieldAjaxMulti),
        ("tags", DALFRelatedFieldAjaxMulti),
    )
    autocomplete_fields = ("categories", "tags")
    prepopulated_fields = {"slug": ("name", "sku")}
    fields = ("name", "description", "slug", "sku", "categories", "tags")
