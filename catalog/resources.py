from import_export import fields, resources, widgets

from .models import Category, Product, Tag

# Map a resource class to each model and its fields for django-import-export usage


class CategoryResource(resources.ModelResource):
    class Meta:
        model = Category
        fields = ("name", "slug", "description")
        clean_model_instances = True  # run admin model validation on import
        import_id_fields = ("slug",)
        skip_unchanged = True


class TagResource(resources.ModelResource):
    class Meta:
        model = Tag
        fields = ("name", "slug", "description")
        clean_model_instances = True  # run admin model validation on import
        import_id_fields = ("slug",)
        skip_unchanged = True


class ProductResource(resources.ModelResource):
    # Link the many-to-many fields for Product model
    categories = fields.Field(
        column_name="categories",
        attribute="categories",
        widget=widgets.ManyToManyWidget(Category, separator="|", field="name"),
    )
    tags = fields.Field(
        column_name="tags",
        attribute="tags",
        widget=widgets.ManyToManyWidget(Tag, separator="|", field="name"),
    )

    def before_import_row(self, row, **kwargs):
        # Ensure imported product has at least one category and one tag.
        for name, singular in (("categories", "category"), ("tags", "tag")):
            if not self.fields[name].clean(row).exists():
                raise ValueError(f"A product needs at least one existing {singular}.")

    class Meta:
        model = Product
        fields = ("name", "slug", "description", "sku", "categories", "tags")
        export_order = fields
        import_id_fields = ("sku",)  # match by SKU field during import
        skip_unchanged = True
