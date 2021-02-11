# Web Assets: A Plugin for Pelican

[![Build Status](https://img.shields.io/github/workflow/status/pelican-plugins/webassets/build)](https://github.com/pelican-plugins/webassets/actions)
[![PyPI Version](https://img.shields.io/pypi/v/pelican-webassets)](https://pypi.org/project/pelican-webassets/)
![License](https://img.shields.io/pypi/l/pelican-webassets?color=blue)

This [Pelican](https://github.com/getpelican/pelican) plugin allows you to use
the [webassets][] module to perform a number
of useful asset management functions on your web site, such as:

* CSS minification (`cssmin`, `yui_css`, ...)
* CSS compiling (`less`, `sass`, ...)
* JS building (`uglifyjs`, `yui_js`, `closure`, ...)

Some other interesting abilities of [webassets][] include:

* [URL Expiry or
  "cache-busting"](https://webassets.readthedocs.io/en/latest/expiring.html),
  allowing you to set the cache headers for your assets long into the
  future, saving bandwidth and reducing page load-times
* a [`spritemapper`](https://yostudios.github.io/Spritemapper/) function to
  automatically combine multiple icons into one large image with corresponding
  position slices
* a `datauri` function to minimize the number of HTTP requests by
  replacing `url()` references in your stylesheets with internal
  in-line [data URIs](https://en.wikipedia.org/wiki/Data_URI_scheme)

For the complete list of what [webassets][] can do, check out the **included
filters** section in the [webassets
documentation](https://webassets.readthedocs.io/en/latest/builtin_filters.html).

## Installation

Getting started with [webassets][] couldn't be easier thanks to `pip`:

```shell-session
python -m pip install pelican-webassets
```

For more detailed plugin installation instructions, please refer to the
[Pelican Plugin Documentation](https://docs.getpelican.com/en/latest/plugins.html).

💡 **Keep in Mind:** Each function you use in your `{% asset filters %}`
arguments (more on this later) will need to be installed
separately. For example, if you wanted to use the `libsass` filter, you
will need to `pip install libsass`. You can even [create a custom
filter](https://webassets.readthedocs.io/en/latest/custom_filters.html)
if you wanted.

## Usage

With the plugin installed, include one or more `{% assets %}` tags
into your web site's templates to generate everything your web page will
need. For example, something like this in your template…

```html+jinja
{% assets filters="libsass,cssmin", output="css/style.min.css", "css/style.scss" %}
  <link rel="stylesheet" href="{{SITEURL}}/{{ASSET_URL}}">
{% endassets %}
```

… will tell [webassets][] to use `libsass` and `cssmin` to compile and
minify the `css/style.scss` file in your theme, and save the compiled
stylesheet as `css/style.min.css` in the output of your finished
website, along with the `link` element like this in your web page:

```html+jinja
<link href="{SITEURL}/{THEME_STATIC_DIR}/css/style.min.css?b3a7c807" rel="stylesheet">
```

🌠 **The More You Know:** The `ASSET_URL` variable is the concatenation
of your Pelican `THEME_STATIC_DIR` setting, the `output` argument, and
the "cache-busting" variable we already talked about.

### JavaScript Example

As another example, we can use the [webassets][] `closure_js` function to
combine, minify, and compress two files in your web site's theme, `js/jQuery.js`
and `js/widgets.js`:

```html+jinja
{% assets filters="closure_js", output="js/packed.js", "js/jQuery.js", "js/widgets.js" %}
 <script src="{{SITEURL}}/{{ASSET_URL}}"></script>
{% endassets %}
```

The resulting output will be a single `script` tag and its
corresponding file in your web site's generated output:

```html+jinja
<script src="{SITEURL}/{THEME_STATIC_DIR}/js/packed.js?00703b9d"></script>
```

## Configuration

Being a very small wrapper around the [webassets][] module, there are
only a few options that you may need.

#### WEBASSETS_DEBUG

By default, if Pelican is in DEBUG mode (`pelican -D ...`), this
plugin will put [webassets][] in DEBUG mode, to help you with
debugging. To override this behavior, set `WEBASSETS_DEBUG = False` to
always process files regardless of Pelican's DEBUG flag, or `True`
to always force [webassets][] into DEBUG mode.

```python
# put webassets into DEBUG mode if Pelican is
WEBASSETS_DEBUG = logger.getEffectiveLevel() <= logging.DEBUG
```

#### WEBASSETS_CONFIG

Some [webassets][] filters require extra configuration options to function
properly. You can use `WEBASSETS_CONFIG` to specify these options in a
list of `(key, value)` tuples that are passed along to the [webassets][]
environment.

```python
WEBASSETS_CONFIG = [
  ("closure_compressor_optimization", "ADVANCED_OPTIMIZATIONS"),
  ("libsass_style", "compressed")
]
```

#### WEBASSETS_BUNDLES

[Bundles](https://webassets.readthedocs.io/en/latest/bundles.html) are
a convenient way to group a collection of assets together along with
the information on how to properly process the files. The
`WEBASSETS_BUNDLES` option allows us to make these Bundles by taking a
list of `(name, args, kwargs)` arguments that will be passed to the
[webassets][] environment.

```python
WEBASSETS_BUNDLES = (
     ("my_bundle", ("colors.scss", "style.scss"),
     {"output': "style.min.css", "filters": ["libsass", "cssmin"]}),
)
```

Allowing you to simplify something like this in your web site's templates…

```html+jinja
{% assets filters="libsass,cssmin", output="style.min.css", "colors.scss", "style.scss" %}
```

… into this:

```html+jinja
{% assets 'my_bundle' %}
```

#### WEBASSETS_SOURCE_PATHS

If your raw assets are in directories other than your
`THEME_STATIC_PATHS`, you can supply additional directories to search
in with `WEBASSETS_SOURCE_PATHS`.

```python
WEBASSETS_SOURCE_PATHS = ["stylehseets", "javascript"]
```

## Contributing

Contributions are welcome and much appreciated. Every little bit
helps. You can contribute by improving the documentation, adding
missing features, and fixing bugs. You can also help out by reviewing
and commenting on [existing issues][].

To start contributing to this plugin, review the [Contributing to
Pelican][] documentation, beginning with the **Contributing Code**
section.

[existing issues]: https://github.com/pelican-plugins/webassets/issues
[Contributing to Pelican]: https://docs.getpelican.com/en/latest/contribute.html

## License

This project is licensed under the [AGPL-3.0
license](https://tldrlegal.com/license/gnu-affero-general-public-license-v3-(agpl-3.0))

![AGPL-3.0](https://img.shields.io/pypi/l/pelican-webassets?color=blue)


[webassets]: https://github.com/miracle2k/webassets
