CHANGELOG
=========

2.0.0 - 2021-02-15
------------------

* Consolidate `assets` and `pelican-webassets` plugins into a single project
* Support plugin auto-registration via new namespace plugin format on Pelican 4.5+
* Deprecate `ASSET_*` settings in favor of `WEBASSETS_*`
* Fix bug where an empty `THEME_STATIC_DIR` setting would create malformed URLs
