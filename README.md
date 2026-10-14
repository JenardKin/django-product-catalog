# Django Product Catalog

A Django project that models products, categories and tags, with a page to search and
filter products.

## Purpose

- **Models with relationships.** `Product`, `Category` and `Tag`. A product belongs
  to one or more categories and has one or more tags (many-to-many).
- **Sample data through the Django admin.** At least 5 categories, 10 tags and 20
  products. The project ships 6, 12 and 50 as CSV files in `seed/`. Load them with the
  `seed_catalog` command (step 5 below) or with each model's **Import** button in the
  admin (categories, then tags, then products). Records can also be added with the
  admin forms.
- **A search and filter page.** Search by description, filter by category, filter by
  tags, and combine all three.
- **A front end built with Django templates and htmx.**

## Code overview

```
manage.py, pyproject.toml        Django's entry point; the Ruff settings
requirements.txt, requirements-dev.txt, .env.example, .gitignore
.vscode/                         editor settings (format on save with Ruff)
config/                          project settings and the root URLs
catalog/
  models/
    mixins.py                    SearchMetadataMixin: name, slug, description, timestamps
    category.py, tag.py          Category and Tag
    product.py                   Product, its queryset (search and filters), MatchMode, SortOrder
  migrations/                    the database migration
  admin/
    product.py                   product, category and tag admins, with import and export
    user.py                      the restricted user admin
  resources.py                   django-import-export resources (CSV import and export)
  forms.py                       the search and filter form
  views/
    product_search.py            the search view
    autocomplete_filters.py      category and tag autocomplete endpoints
  urls.py, auth_urls.py          catalog pages, and the site-level login and logout
  templates/catalog/             the search page, results, pagination and login templates
  static/catalog/js/htmx.min.js  htmx, included as a file (no build step)
  signals.py, apps.py            login and logout messages, and their registration
  management/commands/           seed_users and seed_catalog
  tests/requirements/            tests for the requirements (python manage.py test)
seed/                            the sample data (CSV)
```

Key parts for the requirements:

- **Models** (`catalog/models/product.py`). `Product` has two many-to-many fields,
  `categories` and `tags`. All three models share `SearchMetadataMixin` (`name`,
  `slug`, `description`, timestamps). `Product` adds a unique `sku`, check constraints
  against empty values, and an index on `(name, sku)`.
- **Sample data** (`catalog/admin/`, `catalog/resources.py`, `seed/`). Every model is
  registered in the admin, with autocomplete pickers for categories and tags on the
  product form. django-import-export loads the CSV files through the **Import**
  button, and `seed_catalog` runs the same import code from the command line.
- **Search** (`ProductQuerySet.search_query()`). A case-insensitive partial match
  (`icontains`) on the description, which also matches the name and SKU through `Q`
  objects.
- **Filters** (`categorized_as()` and `tagged_as()`). Each takes one or several values
  and a match mode: any of, all of, none of, or not all of. A shared helper finds the
  matching product ids in the many-to-many join table and filters with `pk__in`, so
  each product appears once and no `DISTINCT` is needed. "All of" counts the matches
  with a `Count` annotation.
- **Combining** (`catalog/views/product_search.py`). Each queryset method returns a
  queryset, so the view chains them. The values come from one GET form
  (`ProductFilterForm`), and the result is then sorted and paginated (10 per page,
  set by `PAGINATION_SETTINGS` in `config/settings.py`).

  ```python
  products = (
      Product.objects.search_query(text)
      .categorized_as(categories, category_match)
      .tagged_as(tags, tag_match)
  )
  ```
- **The page** (`catalog/templates/catalog/`). A Django template with the search box,
  the sort order, the category and tag autocomplete boxes
  (django-autocomplete-light) and the results.

## Versions and dependencies

- **Python 3.14**, **Django 5.2** and **SQLite** (the Django default, no setup).

| Package                   | Version | Used for                                               |
| ------------------------- | ------- | ------------------------------------------------------ |
| django                    | 5.2     | the framework                                          |
| django-import-export      | 4.4.1   | importing and exporting the sample data in the admin   |
| django-model-utils        | 5.0.0   | `created` / `modified` timestamps on the models    |
| django-autocomplete-light | 5.0.0   | category and tag autocomplete on the search page       |
| dalf                      | 0.7.2   | autocomplete filters in the admin product list         |
| django-htmx               | 1.29.0  | htmx support for the search view                       |
| python-dotenv             | 1.2.4   | reading settings from the`.env` file                 |
| whitenoise                | 6.12.0  | serving static files when`DJANGO_DEBUG` is `False` |
| ruff (dev only)           | 0.17.0  | linting and formatting (`pyproject.toml`)            |

I used **uv** for the Python version and the virtual environment, and **Ruff** for
linting and formatting. Neither is required: plain `venv` and `pip` will work.

## How to run it

```bash
# 1. Clone the repository
git clone https://github.com/JenardKin/django-product-catalog.git
cd django-product-catalog

# 2. Create and activate a virtual environment
python -m venv .venv            # or: uv venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # macOS / Linux

# 3. Install the dependencies
pip install -r requirements.txt            # or: uv pip install -r requirements.txt
pip install -r requirements-dev.txt        # optional: adds Ruff

# 4. Create the .env file
cp .env.example .env            # macOS / Linux
copy .env.example .env          # Windows

# 5. Create the database, the demo users, and the sample data
python manage.py migrate
python manage.py seed_users
python manage.py seed_catalog

# 6. Collect the static files
python manage.py collectstatic --noinput

# 7. Start the server
python manage.py runserver
```

- Search page: [http://127.0.0.1:8000/catalog/product-search/](http://127.0.0.1:8000/catalog/product-search/) (the site root
  redirects there)
- Admin: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

The `.env` file is git-ignored and optional. Without it the project runs with debug on
and a placeholder secret key. Its settings are `DJANGO_SECRET_KEY` (required when
`DJANGO_DEBUG` is `False`), `DJANGO_DEBUG` (default `True`) and `DJANGO_ALLOWED_HOSTS`
(comma-separated). See `.env.example`.

`seed_users` creates three demo users with these default passwords, for local review
only:

| Username          | Default password  | Access Level                                  |
| ----------------- | ----------------- | --------------------------------------------- |
| `superuser`     | `Sup3rUs3r`     | everything                                    |
| `administrator` | `Administr@tor` | add, change and delete catalog data and users |
| `readonly`      | `R3@d0nly`      | view only                                     |

These passwords are public, so never use them anywhere real. They can be changed in
the `.env` file with `SEED_SUPERUSER_PASSWORD`, `SEED_ADMINISTRATOR_PASSWORD` and
`SEED_READONLY_PASSWORD` (see `.env.example`), set before running `seed_users`. A user
that already exists keeps its password unless you run
`python manage.py seed_users --reset-passwords`.

## Front end and build instructions

The front end is Django templates and [htmx](https://htmx.org/). htmx is included as a
static file, so there is no build step and no extra dependency: run `collectstatic`
and `runserver`.

## Assumptions and notes

- A product's SKU is unique and identifies it. Product names may repeat. Category and
  tag names are unique.
- Every description is required and limited to 500 characters.
- A product needs at least one category and one tag. The admin form and the CSV import
  enforce this. The database cannot, because a many-to-many link is stored in a
  separate table.
- This is a local demo setup: `DEBUG` is on by default and `ALLOWED_HOSTS` is empty.

## Improvement areas

- **Full-text search, by database.** The search box uses `icontains`
  (`LIKE '%term%'`), which a regular index, including the one on `description`, cannot
  serve. That is fine at this size. As the catalog grows:
  - *PostgreSQL:* `pg_trgm` with a GIN index speeds up the existing filter with no
    change to the view. `django.contrib.postgres.search` (`SearchVector`,
    `SearchQuery`, `SearchRank`) adds ranked, word-based search.
  - *SQLite (used here):* an FTS5 virtual table with the `trigram` tokenizer, created
    in a `RunSQL` migration and kept in sync with triggers. Terms need 3 or more
    characters, so shorter ones keep the `icontains` fallback.
- **Database-level "at least one category and tag".** A many-to-many cannot be
  constrained, but a required foreign key (for example a main category) would be.
- **Caching.** A search takes about 10 ms at 5,000 products, so none is needed yet.
  Caching the whole view is unsafe because the page header is per user. The options
  are to cache the result count per filter set, or to cache the results and
  invalidate them on product changes.

## Code quality

Linting and formatting use [Ruff](https://docs.astral.sh/ruff/), configured in
`pyproject.toml` (migrations are excluded):

```bash
ruff check .
ruff format .
```

## Tests

```bash
python manage.py test
```

There is one test file per requirement in `catalog/tests/requirements/`:

| File | Requirement |
| ---- | ----------- |
| `test_model_relationships.py` | products, categories and tags are related correctly |
| `test_sample_data.py` | at least 5 categories, 10 tags and 20 products |
| `test_add_data_through_the_admin.py` | data can be added with the admin forms |
| `test_search_page.py` | the page where a user searches and filters |
| `test_search_by_description.py` | search by description |
| `test_filter_by_category.py` | filter by category |
| `test_filter_by_tags.py` | filter by tags, with each match mode |
| `test_combined_search_and_filter.py` | combine the search and the filters |

`base.py` holds the shared test data (the products, categories and tags, defined as
enums). Run only these tests with `python manage.py test catalog.tests.requirements`,
or one file with, for example,
`python manage.py test catalog.tests.requirements.test_filter_by_tags`.

## AI Assistance

In line with the AI policy, this section documents how AI tooling was used. Claude Code
served as a development aid. Any AI-generated code has been reviewed, modified, and
extended by myself so that the data models, query design, and overall architecture
reflect my own decisions, knowledge, and experience.

### Where AI was used

- **Project scaffolding:** initial configuration, including the VS Code settings
  (`.vscode/`), Ruff settings in `pyproject.toml`, `.gitignore` and dependency files.
- **First-pass drafts:** early versions of the models, admin and import/export
  configuration, seed commands, search and filtering, templates, and this README.
  Each draft was a starting point that was then reworked.
- **Review and verification:** checking code for errors, drafting tests, and
  reviewing changes. All suggestions were evaluated before being accepted.
