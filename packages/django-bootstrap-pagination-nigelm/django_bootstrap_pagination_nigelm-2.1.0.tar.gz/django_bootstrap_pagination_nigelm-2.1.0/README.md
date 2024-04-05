# Django Bootstrap Pagination

<!-- prettier-ignore-start -->
[![PyPi version](https://img.shields.io/pypi/v/django-bootstrap-pagination-nigelm.svg)](https://pypi.python.org/pypi/django-bootstrap-pagination-nigelm)
[![PyPi downloads](https://img.shields.io/pypi/dm/django-bootstrap-pagination-nigelm.svg)](https://pypi.python.org/pypi/django-bootstrap-pagination-nigelm)
<!-- prettier-ignore-end -->

## Current Version

Version: `2.1.0`

## Original Package

This package was originally found at
<https://github.com/jmcclell/django-bootstrap-pagination>

This version has had some modifications to work with later versions of Django,
and some additional functionality is being grafted in. This is still a work in
progress.

## Bootstrap Compatibility

| Versions | Bootstrap     | Notes                                           |
| -------- | ------------- | ----------------------------------------------- |
| < 2.0.0  |               | See original                                    |
| >= 2.0.0 | 3.x, 4.x, 5.x | Works effectively with versions over this range |

This application serves to make using Twitter's Bootstrap Pagination styles work
seamlessly with Django Page objects. By passing in a Page object and one or more
optional arguments, Bootstrap pagination bars and pagers can be rendered with
very little effort.

Compatible with Django 3.x and 4.x and with Bootstrap versions from 3.x through
5.x

## Installation

### PIP

This will install the latest stable release from PyPi.

```bash
    pip install django-bootstrap-pagination-nigelm
```

### Download

Download the latest stable distribution from:

<http://pypi.python.org/pypi/django-bootstrap-pagination-nigelm>

Download the latest development version from:

github @ <https://github.com/nigelm/django-bootstrap-pagination-nigelm>

## Usage

### Setup

Make sure you include bootstrap_pagination in your installed_apps list in
settings.py:

```python
    INSTALLED_APPS = (
        'bootstrap_pagination',
    )
```

Additionally, include the following snippet at the top of any template that
makes use of the pagination tags:

```django
    {% load bootstrap_pagination %}
```

Finally, make sure that you have the request context processor enabled:

```python
    TEMPLATES = [
        {
            # ...
            'OPTIONS': {
                context_processors': [
                    # ...
                    'django.template.context_processors.request',
                ]
            }
        }
    ]
```

### `bootstrap_paginate`

All Optional Arguments:-

- `range` - Defines the maximum number of page links to show. Ignored in elided
  mode.
- `elided` - Boolean value - if true then the page is in elided mode, where the
  first and last sets of pages, and a group of pages around the current page are
  shown, with an ellipsis entry wherever a set of pages are skipped.
- `on_each_side` - number of pages shown before/after the current page in elided
  mode. Default value 3.
- `on_ends` - number of pages shown at the start/finish of the set of pages in
  elided mode. Default value 2.
- `show_prev_next` - Boolean. Defines whether or not to show the Previous and
  Next links. (Accepts `"true"` or `"false"`)
- `previous_label` - The label to use for the Previous link
- `next_label` - The label to use for the Next link
- `ellipsis_label` - The text to display for skipped page sets. Defaults to
  `&hellip;`
- `show_first_last` - Boolean. Defines whether or not to show the First and Last
  links. (Accepts `"true"` or `"false"`)
- `first_label` - The label to use for the First page link
- `last_label` - The label to use for the Last page link
- `show_index_range` - Boolean, defaults to "false". If "true" shows index range
  of items instead of page numbers in the paginator. For example, if paginator
  is configured for 50 items per page, show_index_range="true" will display
  [1-50, 51-100, **101-150**, 151-200, 201-250, etc.] rather than [1, 2, **3**,
  4, 5, etc.].
- `url_view_name` - A named URL reference (such as one that might get passed
  into the URL template tag) to use as the URL template. Must be resolvable by
  the `reverse()` function. **If this option is not specified, the tag simply
  uses a relative url such as `?page=1` which is fine in most situations**
- `url_param_name` - Determines the name of the `GET` parameter for the page
  number. The default is `"page"`. If no **url_view_name** is defined, this
  string is appended to the url as `?{{url_param_name}}=1`.
- `url_extra_args` - **Only valid when url_view_name is set.** Additional
  arguments to pass into `reverse()` to resolve the URL.
- `url_extra_kwargs` - **Only valid when `url_view_name` is set.** Additional
  named arguments to pass into `reverse()` to resolve the URL. Additionally, the
  template tag will add an extra parameter to this for the page, as it is
  assumed that if given a url_name, the page will be a named variable in the URL
  regular expression. In this case, the `url_param_name` continues to be the
  string used to represent the name. That is, by default, `url_param_name` is
  equal to `page` and thus it is expected that there is a named `page` argument
  in the URL referenced by `url_view_name`. This allows us to use pretty
  pagination URLs such as `/page/1`
- `extra_pagination_classes` - A space separated list of CSS class names that
  will be added to the top level `<ul>` HTML element. In particular, this can be
  utilized in Bootstrap 4 installations to add the appropriate alignment classes
  from Flexbox utilities: eg: `justify-content-center`
- `hx_target` - For use with HTMX pages, sets the target id, it will also change
  all the links to use `hx-get` instead of `href` and adds a
  `hx-swap="OuterHTML"`

#### Basic Usage

The following will show a pagination bar with a link to every page, a previous
link, and a next link:

```django
    {% bootstrap_paginate page_obj %}
```

The following will show a pagination bar with at most 10 page links, a previous
link, and a next link:

```django
    {% bootstrap_paginate page_obj range=10 %}
```

The following will show a pagination bar with at most 10 page links, a first
page link, and a last page link:

```django
    {% bootstrap_paginate page_obj range=10 show_prev_next="false"
       show_first_last="true" %}
```

#### Advanced Usage

Given a url configured such as:

```python
    archive_index_view = ArchiveIndexView.as_view(
        date_field='date',
        paginate_by=10,
        allow_empty=True,
        queryset=MyModel.all(),
        template_name='example/archive.html'
    )

    urlpatterns = patterns(
        'example.views',
        url(r'^$', archive_index_view, name='archive_index'),
        url(r'^page/(?P<page>\d+)/$', archive_index_view,
            name='archive_index_paginated'))
```

We could simply use the basic usage (appending ?page=#) with the _archive_index_
URL above, as the _archive_index_view_ class based generic view from django
doesn't care how it gets the page parameter. However, if we want pretty URLs,
such as those defined in the _archive_index_paginated_ URL (ie: /page/1), we
need to define the URL in our template tag:

```django
    {% bootstrap_paginate page_obj url_view_name="archive_index_paginated" %}
```

Because we are using a default page parameter name of "page" and our URL
requires no other parameters, everything works as expected. If our URL required
additional parameters, we would pass them in using the optional arguments
**url_extra_args** and **url_extra_kwargs**. Likewise, if our page parameter had
a different name, we would pass in a different **url_param_name** argument to
the template tag.

### `bootstrap_pager`

A much simpler implementation of the Bootstrap Pagination functionality is the
Pager, which simply provides a Previous and Next link.

All Optional Arguments:-

- `previous_label` - Defines the label for the Previous link
- `next_label` - Defines the label for the Next link
- `previous_title` - Defines the link title for the previous link
- `next_title` - Defines the link title for the next link
- `centered` - Boolean. Defines whether or not the links are centered. Defaults
  to false. (Accepts "true" or "false")
- `url_view_name` - A named URL reference (such as one that might get passed
  into the URL template tag) to use as the URL template. Must be resolvable by
  the `reverse()` function. **If this option is not specified, the tag simply
  uses a relative url such as `?page=1` which is fine in most situations**
- `url_param_name` - Determines the name of the `GET` parameter for the page
  number. Th default is `"page"`. If no `url_view_name` is defined, this string
  is appended to the url as `?{{url_param_name}}=1`.
- `url_extra_args` - **Only valid when `url_view_name` is set.** Additional
  arguments to pass into `reverse()` to resolve the URL.
- `url_extra_kwargs` - **Only valid when `url_view_name` is set.** Additional
  named arguments to pass into `reverse()` to resolve the URL. Additionally, the
  template tag will add an extra parameter to this for the page, as it is
  assumed that if given a url_name, the page will be a named variable in the URL
  regular expression. In this case, the `url_param_name` continues to be the
  string used to represent the name. That is, by default, `url_param_name` is
  equal to `"page"` and thus it is expected that there is a named `page`
  argument in the URL referenced by `url_view_name`. This allows us to use
  pretty pagination URLs such as `/page/1`
- `url_anchor` - The anchor to use in URLs. Defaults to `None`
- `extra_pager_classes` - A space separated list of CSS class names that will be
  added to the top level `<ul>` HTML element. This could be used to, as an
  example, add a class to prevent the pager from showing up when printing.

#### Normal Usage

Usage is basically the same as for bootstrap_paginate. The simplest usage is:

```django
    {% bootstrap_pager page_obj %}
```

A somewhat more advanced usage might look like:

```django
    {% bootstrap_pager page_obj previous_label="Newer Posts" next_label="Older Posts"
       url_view_name="post_archive_paginated" %}
```
