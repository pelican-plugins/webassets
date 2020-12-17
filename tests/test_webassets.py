# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

from codecs import open
import hashlib
import locale
from pathlib import Path
from shutil import rmtree
from tempfile import mkdtemp
import unittest

from pelican import Pelican, signals
from pelican.settings import read_settings
from pelican.tests.support import module_exists, mute

HERE = Path(__name__).parent / 'tests'
THEME_DIR = HERE / 'test_data'
CSS_REF = open(THEME_DIR / 'static' / 'css' / 'style.min.css').read()
CSS_HASH = hashlib.md5(CSS_REF.encode()).hexdigest()[0:8]
LOGGER_NAME = 'pelican.plugins.webassets'


@unittest.skipUnless(module_exists("webassets"), "webassets isn't installed")
@unittest.skipUnless(module_exists("sass"), "libsass isn't installed")
class TestWebAssets(unittest.TestCase):
    """Base class for testing webassets."""

    def setUp(self, override=None):
        from pelican.plugins import webassets

        self.temp_path = mkdtemp(prefix="pelicantests.")
        settings = {
            "WEBASSETS_CONFIG": [('libsass_style', 'compressed')],
            "PATH": THEME_DIR,
            "OUTPUT_PATH": self.temp_path,
            "PLUGINS": [webassets],
            "THEME": THEME_DIR,
            "LOCALE": locale.normalize("en_US"),
            "CACHE_CONTENT": False,
        }
        if override:
            settings.update(override)

        self.settings = read_settings(override=settings)
        pelican = Pelican(settings=self.settings)
        mute(True)(pelican.run)()

    def tearDown(self):
        rmtree(self.temp_path)

    def check_link_tag(self, css_file, html_file):
        """Check the presence of `css_file` in `html_file`."""

        link_tag = '<link rel="stylesheet" href="{}">'.format(css_file)
        with open(html_file) as html:
            self.assertRegex(html.read(), link_tag)


class TestWebAssetsRelativeURLS(TestWebAssets):
    """Test pelican with relative urls."""

    def setUp(self):
        TestWebAssets.setUp(self, override={"RELATIVE_URLS": True})

    def test_jinja2_ext(self):
        # Test that the Jinja2 extension was correctly added.

        from webassets.ext.jinja2 import AssetsExtension

        self.assertIn(
            AssetsExtension, self.settings["JINJA_ENVIRONMENT"]["extensions"])

    def test_compilation(self):
        # Compare the compiled css with the reference.
        gen_file = Path(
            self.temp_path) / 'theme' / '{}.min.css'.format(CSS_HASH)
        self.assertTrue(gen_file.is_file())

        with open(gen_file) as css_new:
            self.assertEqual(css_new.read(), CSS_REF)

    def test_template(self):
        # Look in the output files for the link tag.

        css_file = "./theme/{}.min.css".format(CSS_HASH)
        html_files = ["index.html", "archives.html",
                      "this-is-a-super-article.html"]

        for f in html_files:
            self.check_link_tag(css_file, Path(self.temp_path) / f)

        self.check_link_tag(
            "../theme/{}.min.css".format(CSS_HASH),
            Path(self.temp_path) / 'category' / 'yeah.html',
        )


class TestWebAssetsAbsoluteURLS(TestWebAssets):
    """Test pelican with absolute urls."""

    def setUp(self):
        TestWebAssets.setUp(
            self, override={"RELATIVE_URLS": False,
                            "SITEURL": "http://localhost"})

    def test_absolute_url(self):
        # Look in the output files for the link tag with absolute url.

        css_file = "http://localhost/theme/{}.min.css".format(CSS_HASH)
        html_files = ["index.html", "archives.html",
                      "this-is-a-super-article.html"]

        for f in html_files:
            self.check_link_tag(css_file, Path(self.temp_path) / f)


class TestWebAssetsConfigDeprecation(TestWebAssets):
    """Test pelican with old ASSET_* config variables"""

    def setUp(self):
        """
        to capture the logging output from pelican, we need to call
        'super().setUp' inside 'self.assertLogs()' in each test and not here
        """
        pass

    def test_asset_config_deprication(self):
        """ensure a deprication WARNING is emitted when using ASSET_CONFIG"""
        with self.assertLogs(LOGGER_NAME, level='WARNING') as log:
            super().setUp(override={
                'ASSET_CONFIG': [('TESTING', 'WEBASSETS_CONFIG')]})

            self.assertIn(
                'WARNING:pelican.plugins.webassets.webassets:ASSET_CONFIG has been '
                'deprecated in favor for WEBASSETS_CONFIG. Please update your '
                'config file.', log.output)


class DummyPlugin():
    """a dummy plugin to get the webassets configuration settings"""
    __name__ = 'webassets.dummy.plugin'

    def article_generator_init(self, generator):
        print('called')
        self.generator = generator

    def register(self):
        signals.generator_init.connect(self.article_generator_init)


class TestWebAssetsConfigSettings(TestWebAssets):
    """test if the config settings actually do what they should"""

    def setUp(self):
        """we will be using TestWebAssets.setUp in each test"""
        pass

    def get_generators(self, settings=None):
        """run pelican with the given settings and return the generators"""
        from pelican.plugins import webassets
        test_plugin = DummyPlugin()

        settings = settings or {}
        settings.update({'PLUGINS': [webassets, test_plugin]})
        super().setUp(settings)

        return test_plugin.generator

    def test_webassets_config(self):
        """ensure configuration settings are passed to the webassets module"""
        generator = self.get_generators({
            'WEBASSETS_CONFIG': [
                ('libsass_style', 'compressed'),
                ('testing_config', 'some random setting')]})

        config = generator.env.assets_environment.config
        self.assertIn('testing_config', config, 'The testing configuration '
                      'setting was not given to the webassets environment')

        self.assertEqual('some random setting', config['testing_config'],
                         'The testing configuration value was not given '
                         'to the webassets environment')


class TestDepricationDate(unittest.TestCase):
    """Is it time to remove the deprecation warnings?"""

    def test_after_2022(self):
        """ensure the next person must remove the deprecation warnings after 2022"""
        from datetime import datetime
        self.assertTrue(datetime.now().year < 2022,
                        'After 2 years, in the year 2022, we should remove '
                        'support and deprecation warnings for the ASSET_* '
                        'configuration settings')
