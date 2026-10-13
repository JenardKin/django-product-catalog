from dal import autocomplete

from ..models import Category, Tag


class NameAutocomplete(autocomplete.Select2QuerySetView):
    """
    Name lookup for the filter widgets using django-autocomplete-light.

    Returns a paginated list of objects filtered by the query string sent by the request
    """

    model = None

    def get_queryset(self):
        queryset = self.model.objects.all()
        if self.q:
            queryset = queryset.filter(name__icontains=self.q)
        return queryset


class CategoryAutocomplete(NameAutocomplete):
    model = Category


class TagAutocomplete(NameAutocomplete):
    model = Tag
