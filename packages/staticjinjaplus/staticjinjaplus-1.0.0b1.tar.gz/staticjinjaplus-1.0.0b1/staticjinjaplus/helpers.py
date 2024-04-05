from jinja2.utils import htmlsafe_json_dumps
from htmlmin import minify as minify_xml
from typing import Dict, Callable
from markupsafe import Markup
from staticjinja import Site
from jinja2 import Template
import os


def jinja_url(config: Dict) -> Callable:
    """Build a URL (relative or absolute) to a file relative to the output dir"""
    def inner(path: str, absolute: bool = False) -> str:
        url = config['BASE_URL'].rstrip('/') + '/' if absolute else '/'
        url += path.lstrip('/')

        return url

    return inner


def jinja_icon(config: Dict) -> Callable:
    """Embed the SVG markup of an SVG icon relative to the {assets dir}/icons directory"""
    def inner(name: str) -> Markup:
        with open(os.path.join(config['ASSETS_DIR'], 'icons', f'{name}.svg'), 'r') as f:
            return Markup(f.read())

    return inner


def jinja_tojsonm(config: Dict) -> Callable:
    """Serialize the given data to JSON, minifying (or not) the output given current configuration"""
    def inner(data: Dict) -> Markup:
        return htmlsafe_json_dumps(
            data,
            indent=None if config['MINIFY_JSON'] else 4,
            separators=(',', ':') if config['MINIFY_JSON'] else None
        )

    return inner


def jinja_dictmerge(left: Dict, right: Dict) -> Dict:
    """Merge two dicts"""
    return left | right


def minify_xml_template(site: Site, template: Template, **kwargs) -> None:
    """Minify rendered XML and HTML output from a Jinja template"""
    out = os.path.join(site.outpath, template.name)

    os.makedirs(os.path.dirname(out), exist_ok=True)

    with open(out, 'w', encoding=site.encoding) as f:
        f.write(
            minify_xml(
                site.get_template(template.name).render(**kwargs),
                remove_optional_attribute_quotes=False,
                remove_empty_space=True,
                remove_comments=True
            )
        )
