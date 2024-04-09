from staticjinjaplus.http import ThreadingHTTPServerWithConfig, SimpleEnhancedHTTPRequestHandler
from webassets import Environment as AssetsEnvironment
from staticjinjaplus import staticjinja_helpers
from importlib import util as importlib_util
from staticjinjaplus import jinja_helpers
from shutil import copytree, rmtree
from os import makedirs, path
from staticjinja import Site
from subprocess import call
from environs import Env
from typing import Dict
import locale
import sys


def load_config() -> Dict:
    """Load configuration from both `config.py` in the directory where staticjinjaplus is executed and environment
    variables, returning a dict representation of this configuration. Only uppercase variables are loaded"""

    # Set default config values
    config = {
        'LOCALE': None,
        'SERVE_PORT': 8080,
        'BASE_URL': 'http://localhost:8080/',
        'MINIFY_XML': False,
        'MINIFY_JSON': False,
        'TEMPLATES_DIR': 'templates',
        'OUTPUT_DIR': 'output',
        'STATIC_DIR': 'static',
        'ASSETS_DIR': 'assets',
        'ASSETS_BUNDLES': [],
        'CONTEXTS': [],
    }

    # Load and erase default config values from config.py, if the file exists
    try:
        spec = importlib_util.spec_from_file_location('config', 'config.py')
        actual_config = importlib_util.module_from_spec(spec)
        spec.loader.exec_module(actual_config)

        config.update({
            k: v for k, v in vars(actual_config).items() if k.isupper()
        })
    except FileNotFoundError:
        pass

    return config


def set_locale(config: Dict) -> None:
    """Set the system locale based on the LOCALE config"""
    if not config['LOCALE']:
        return

    locale_successfully_set = False

    for code in config['LOCALE']:
        try:
            locale.setlocale(locale.LC_ALL, code)

            locale_successfully_set = True

            print(f'System locale set to {code}')

            break
        except locale.Error:
            pass

    if not locale_successfully_set:
        print('Unable to set system locale', file=sys.stderr)


def build(config: Dict, watch: bool = False) -> None:
    """Build the site"""
    set_locale(config)

    webassets_cache = path.join(config['ASSETS_DIR'], '.webassets-cache')

    makedirs(webassets_cache, exist_ok=True)
    makedirs(config['STATIC_DIR'], exist_ok=True)
    makedirs(config['OUTPUT_DIR'], exist_ok=True)
    makedirs(config['ASSETS_DIR'], exist_ok=True)

    print('Copying static files from "{STATIC_DIR}" to "{OUTPUT_DIR}"...'.format(**config))

    copytree(
        config['STATIC_DIR'],
        config['OUTPUT_DIR'],
        dirs_exist_ok=True
    )

    print('Building from "{TEMPLATES_DIR}" to "{OUTPUT_DIR}"...'.format(**config))

    site = Site.make_site(
        searchpath=config['TEMPLATES_DIR'],
        outpath=config['OUTPUT_DIR'],
        mergecontexts=True,
        env_globals={
            'config': config,
            'url': jinja_helpers.url(config),
            'icon': jinja_helpers.icon(config),
        },
        filters={
            'tojsonm': jinja_helpers.tojsonm(config),
            'dictmerge': jinja_helpers.dictmerge,
        },
        contexts=config['CONTEXTS'] or None,
        rules=[
            (r'.*\.(html|xml)', staticjinja_helpers.minify_xml_template)
        ] if config['MINIFY_XML'] else None,
        extensions=['webassets.ext.jinja2.AssetsExtension'],
        env_kwargs={
            'trim_blocks': True,
            'lstrip_blocks': True,
        }
    )

    site.env.assets_environment = AssetsEnvironment(
        directory=config['OUTPUT_DIR'],
        url='/',
        cache=webassets_cache
    )

    site.env.assets_environment.append_path(config['ASSETS_DIR'])

    for name, args, kwargs in config['ASSETS_BUNDLES']:
        site.env.assets_environment.register(name, *args, **kwargs)

    site.render(watch)


def clean(config: Dict) -> None:
    """Delete and recreate the output directory"""
    print('Deleting and recreating "{OUTPUT_DIR}"...'.format(**config))

    if path.isdir(config['OUTPUT_DIR']):
        rmtree(config['OUTPUT_DIR'])

    makedirs(config['OUTPUT_DIR'], exist_ok=True)


def publish(config: Dict) -> None:
    """Publish the site (using `rsync` through SSH)"""
    print('Overriding some configuration values from environment variables...')

    env = Env()

    try:
        config.update({
            'BASE_URL': env.str('BASE_URL'),
            'MINIFY_XML': env.bool('MINIFY_XML', config['MINIFY_XML']),
            'MINIFY_JSON': env.bool('MINIFY_JSON', config['MINIFY_JSON']),
            'SSH_USER': env.str('SSH_USER'),
            'SSH_HOST': env.str('SSH_HOST'),
            'SSH_PORT': env.int('SSH_PORT', default=22),
            'SSH_PATH': env.str('SSH_PATH'),
        })
    except ValueError as e:
        print(e, file=sys.stderr)

    exit(call(
        'rsync --delete --exclude ".DS_Store" -pthrvz -c '
        '-e "ssh -p {SSH_PORT}" '
        '{} {SSH_USER}@{SSH_HOST}:{SSH_PATH}'.format(
            config['OUTPUT_DIR'].rstrip('/') + '/', **config
        )
    ))


def serve(config: Dict) -> None:
    """Serve the rendered site directory through HTTP"""
    print('Serving "{OUTPUT_DIR}" on http://localhost:{SERVE_PORT}/'.format(**config))

    with ThreadingHTTPServerWithConfig(
            ('127.0.0.1', config['SERVE_PORT']),
            SimpleEnhancedHTTPRequestHandler,
            directory=config['OUTPUT_DIR']
    ) as server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
