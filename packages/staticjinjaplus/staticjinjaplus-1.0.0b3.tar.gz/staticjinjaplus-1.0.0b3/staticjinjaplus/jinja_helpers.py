from jinja2.utils import htmlsafe_json_dumps
from typing import Dict, Callable
from markupsafe import Markup
from os import path


def url(config: Dict) -> Callable:
    """Build a relative or absolute URL to a file relative to the output dir"""
    def inner(path: str, absolute: bool = False) -> str:
        ret = config['BASE_URL'].rstrip('/') + '/' if absolute else '/'
        ret += path.lstrip('/')

        return ret

    return inner


def icon(config: Dict) -> Callable:
    """Embed the SVG markup of an SVG icon relative to the `{assets dir}/icons` directory"""
    def inner(name: str) -> Markup:
        with open(path.join(config['ASSETS_DIR'], 'icons', f'{name}.svg'), 'r') as f:
            return Markup(f.read())

    return inner


def tojsonm(config: Dict) -> Callable:
    """Serialize the given data to JSON, minifying (or not) the output in function of current configuration"""
    def inner(data: Dict) -> Markup:
        return htmlsafe_json_dumps(
            data,
            indent=None if config['MINIFY_JSON'] else 4,
            separators=(',', ':') if config['MINIFY_JSON'] else None
        )

    return inner


def dictmerge(left: Dict, right: Dict) -> Dict:
    """Merge two dicts"""
    return left | right
