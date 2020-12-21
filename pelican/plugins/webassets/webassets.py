# -*- coding: utf-8 -*-
"""
Asset management plugin for Pelican
===================================

This plugin allows you to use the `webassets`_ module to manage assets such as
CSS and JS files.

The ASSET_URL is set to a relative url to honor Pelican's RELATIVE_URLS
setting. This requires the use of SITEURL in the templates::

    <link rel="stylesheet" href="{{ SITEURL }}/{{ ASSET_URL }}">

.. _webassets: https://webassets.readthedocs.org/

"""
import logging
import os

from pelican import signals

logger = logging.getLogger(__name__)

try:
    import webassets
    from webassets import Environment
    from webassets.ext.jinja2 import AssetsExtension
except ImportError:
    webassets = None


def add_jinja2_ext(pelican):
    """Add Webassets to Jinja2 extensions in Pelican settings."""

    if "JINJA_ENVIRONMENT" in pelican.settings:  # pelican 3.7+
        pelican.settings["JINJA_ENVIRONMENT"]["extensions"].append(AssetsExtension)
    else:
        pelican.settings["JINJA_EXTENSIONS"].append(AssetsExtension)


def create_assets_env(generator):
    """Define the assets environment and pass it to the generator."""

    theme_static_dir = generator.settings["THEME_STATIC_DIR"]
    assets_destination = os.path.join(generator.output_path, theme_static_dir)
    generator.env.assets_environment = Environment(
        assets_destination, theme_static_dir or "."
    )

    # TODO: remove deprecated variables in 2022
    for variable in [
        "ASSET_CONFIG",
        "ASSET_DEBUG",
        "ASSET_BUNDLES",
        "ASSET_SOURCE_PATHS",
    ]:

        if variable not in generator.settings:
            continue

        logger.warning(
            "%s has been deprecated in favor for %s. Please update your "
            "config file.",
            variable,
            variable.replace("ASSET", "WEBASSETS"),
        )

    # use WEBASSETS_CONFIG over ASSET_CONFIG
    for key, value in generator.settings.get(
        "WEBASSETS_CONFIG", generator.settings.get("ASSET_CONFIG", [])
    ):

        logger.debug("webassets: adding config: '%s' -> '%s'", key, value)
        generator.env.assets_environment.config[key] = value

    # use WEBASSETS_BUNDLES over ASSET_BUNDLES
    for name, args, kwargs in generator.settings.get(
        "WEBASSETS_BUNDLES", generator.settings.get("ASSET_BUNDLES", [])
    ):

        logger.debug("webassets: registering bundle: '%s'", name)
        generator.env.assets_environment.register(name, *args, **kwargs)

    # prefer WEBASSETS_DEBUG -> ASSET_DEBUG -> logger.level
    in_debug = generator.settings.get(
        "WEBASSETS_DEBUG",
        generator.settings.get(
            "ASSET_DEBUG", logger.getEffectiveLevel() <= logging.DEBUG
        ),
    )

    if in_debug is True:
        logger.debug("webassets: running in DEBUG mode")
    generator.env.assets_environment.debug = in_debug

    # prefer WEBASSETS_SOURCE_PATHS over ASSET_SOURCE_PATHS
    extra_paths = generator.settings.get(
        "WEBASSETS_SOURCE_PATHS", generator.settings.get("ASSET_SOURCE_PATHS", [])
    )

    for path in generator.settings["THEME_STATIC_PATHS"] + extra_paths:
        full_path = os.path.join(generator.theme, path)
        logger.debug("webassets: using assets in '%s'", full_path)
        generator.env.assets_environment.append_path(full_path)


def register():
    """Plugin registration."""
    if webassets is None:
        logger.warning("failed to load 'webassets' dependencies")
        return

    signals.initialized.connect(add_jinja2_ext)
    signals.generator_init.connect(create_assets_env)
