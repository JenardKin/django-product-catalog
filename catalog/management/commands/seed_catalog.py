import tablib
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from catalog.resources import CategoryResource, ProductResource, TagResource

SEED_DIR = settings.BASE_DIR / "seed"

# Order matters: products need categories and tags to exist first.
SEED_FILES = [
    ("categories.csv", CategoryResource),
    ("tags.csv", TagResource),
    ("products.csv", ProductResource),
]


class Command(BaseCommand):
    help = (
        "Load the sample categories, tags, and products from seed/*.csv using "
        "the same resources as the admin. Existing rows are updated to avoid "
        "duplication. If any file has an error, transaction is rolled back."
    )

    @transaction.atomic
    def handle(self, *args, **options):
        for filename, resource_class in SEED_FILES:
            path = SEED_DIR / filename
            try:
                text = path.read_text(encoding="utf-8")
            except FileNotFoundError:
                raise CommandError(f"Seed file not found: {path}") from None

            dataset = tablib.Dataset().load(text, format="csv")
            result = resource_class().import_data(dataset)

            if result.has_errors() or result.has_validation_errors():
                self.handle_seed_error(filename, result)

            totals = result.totals
            self.stdout.write(
                f"{filename}: {totals['new']} new, {totals['update']} updated, "
                f"{totals['skip']} unchanged"
            )

    def handle_seed_error(self, filename, result):
        lines = [f"{filename} could not be imported. Nothing was saved."]
        for row_number, errors in result.row_errors():
            lines.extend(f"  row {row_number}: {error.error}" for error in errors)
        for invalid in result.invalid_rows:
            lines.append(f"  row {invalid.number}: {invalid.error_dict}")
        raise CommandError("\n".join(lines))
