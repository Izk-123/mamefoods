# MAME Foods — Django + Unfold Admin

This project was assembled from the files you provided plus the Unfold
admin fixes discussed in chat (widget template path, dashboard, dark/light
CSS). A few things you should know before running it:

## What's real vs. placeholder

**Real (from your uploads, used as-is or lightly fixed):**
- `mamefoods/settings.py`, `mamefoods/urls.py`, `mamefoods/asgi.py`
- `main/models.py`, `main/views.py`, `main/forms.py`, `main/urls.py`,
  `main/apps.py`, `main/context_processors.py`
- `main/widgets.py` — kept, with a small fix: it now sets `id` and
  `accept` attrs itself, so `admin.py` doesn't need its own duplicate
  `DragDropImageWidget` class.
- `main/admin.py` — same as yours, but now imports the widget from
  `main/widgets.py` instead of redefining it.
- `templates/admin/base_site.html`, `templates/admin/dashboard.html`,
  `main/templates/widgets/dragdrop_image_widget.html`,
  `static/admin_custom.css` — the Unfold-compatible versions built
  earlier in this conversation (mobile-first, dark/light aware via
  Unfold's `.dark` class, Material Symbols icons, working drag & drop).

**Fixed bug you should know about:**
Your uploaded `base.html` did `{% extends "admin/base.html" %}` while
being saved *at* `templates/admin/base.html` — since Django checks your
project's `templates/` dir before Django's own admin app templates,
that file would extend itself and crash with `RecursionError` the first
time any admin page rendered. It's been removed; `base_site.html`
already extends the real Unfold `admin/base.html` correctly.

**Placeholders (not provided, created so the project actually runs):**
- All of `main/templates/main/*.html` (index, about, products,
  product_detail, blog, blog-single, contact, contact_success) and
  `main/templates/partials/product_list.html` — bare-bones pages with
  no styling, just enough to prove the URL/view/template wiring works.
  Your real site design (the one with hero slides, style.css, etc.)
  wasn't part of what you uploaded, so swap these for your actual
  templates and static assets.
- `static/img/logo.png` — not provided. `UNFOLD["SITE_ICON"]` and
  `SITE_LOGO"]` point at `img/logo.png`; add a real file there or the
  admin sidebar/login logo will 404 (harmless, just a broken image icon).

## Admin UI/UX upgrade (main/admin.py)

The biggest issue found: every admin class was built on plain
`django.contrib.admin.ModelAdmin` / `TabularInline`. Unfold's page chrome
(header, sidebar, dark mode) still applied, but every actual form widget
inside — text inputs, selects, checkboxes — was rendering as vanilla
Django, not Unfold's styled versions. `admin.py` was rewritten on top of
`unfold.admin.ModelAdmin` / `TabularInline` and now uses (all verified
against the installed `django-unfold==0.105.0`, live, over HTTP):

- **Fieldset tabs** — Product and SiteConfiguration forms are split into
  tabs (`'classes': ['tab']`) instead of one long scrolling page. The
  singleton `SiteConfiguration` form especially needed this — it had ~40
  fields in one flat form before.
- **Inline tabs** — the Product/Variant and Product/Image inlines each
  get their own tab (`tab = True`) instead of stacking under the fields.
- **Rich text (Trix WYSIWYG)** — `unfold.contrib.forms.widgets.WysiwygWidget`
  on long-form text fields (product descriptions, blog content, bios).
  Requires `unfold.contrib.forms` in `INSTALLED_APPS` (already added).
- **Modern dropdown filters** — `unfold.contrib.filters.admin` gives
  `RelatedDropdownFilter`, `ChoicesDropdownFilter`, `RangeDateFilter`
  instead of Django's plain sidebar filter list. Requires
  `unfold.contrib.filters` in `INSTALLED_APPS` (already added).
- **Status badges** — `@display(label={...})` on `Product.status_badge`
  and `ProductVariant.stock_status` render colored pills instead of
  plain text in the changelist.
- **Row action** — a "View on site" icon-button per product row
  (`actions_row`) opens the live product page in a new tab.
- **`compressed_fields` / `warn_unsaved_form` / `list_filter_submit`**
  on a shared `BaseModelAdmin` — tighter form spacing, an unsaved-changes
  warning, and an explicit "Apply" button on filters instead of an
  instant reload per click.
- `Category`/`Tag` were previously registered with bare
  `admin.site.register(...)`, which (per Unfold's own docs) silently
  falls back to the *unstyled* default admin form for that model. Both
  are now registered properly with `unfold.admin.ModelAdmin`.

One real bug caught by testing: naming a custom action method
`view_on_site` collides with Django's own built-in `ModelAdmin.view_on_site`
hook (different signature) and throws a `TypeError` on every change page —
renamed to `preview_on_site`.

## Dashboard & command palette upgrade

- **Environment label** — a "Development"/"Production" badge in the admin
  header (`UNFOLD["ENVIRONMENT"]`, driven by `settings.DEBUG`), so nobody
  mistakes one environment for the other.
- **Command palette (Cmd+K / Ctrl+K)** — built into Unfold already; turned
  on `"COMMAND": {"search_models": True}` so it searches actual product/
  category records, not just model names. Note: this queries the database
  on every keystroke-debounced search, so it's fine at this project's
  scale but worth restricting to specific models (`search_models: [...]`)
  if the catalog grows large.
- **Bento-grid dashboard** — replaced the uniform stat-card grid with a
  real bento layout (`templates/unfold/helpers/dashboard_default.html` +
  `.mf-bento`/`.mf-tile` classes in `admin_custom.css`): a 2×2 hero tile
  for certification status, a wide tile for team/blog/certification
  counts, and regular tiles for the rest — varied sizes instead of
  everything being the same shape.

All three were tested live (not just read from docs): logged into a real
running instance and confirmed the "Development" label renders, the
command palette's search-results markup is present, and the bento hero
tile renders with the right CSS classes.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env             # then edit SECRET_KEY

python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
python manage.py runserver
```

Visit:
- `http://127.0.0.1:8000/` — front-end (placeholder pages)
- `http://127.0.0.1:8000/admin/` — Unfold admin

## Notes

- `DEBUG = True` and `ALLOWED_HOSTS = ['*']` are hardcoded for local
  dev in `settings.py` — tighten both before deploying anywhere public.
- `SECRET_KEY` falls back to an insecure default if `.env` isn't set —
  don't ship that fallback to production.
- Static file changes (like `admin_custom.css`) need
  `collectstatic` (or a restart if you're serving straight from
  `STATICFILES_DIRS` in dev) plus a hard browser refresh to show up.
