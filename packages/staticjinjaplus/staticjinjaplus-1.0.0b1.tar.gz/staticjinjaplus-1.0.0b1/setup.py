# Original setup.py template: https://github.com/kennethreitz/setup.py

from setuptools import find_packages, setup, Command
from shutil import rmtree
import io
import os
import sys

NAME = 'staticjinjaplus'
DESCRIPTION = 'An opinionated sweet spot between staticjinja and a full-blown static site generator.'
URL = 'https://github.com/EpocDotFr/staticjinjaplus'
EMAIL = 'contact.nospam@epoc.nospam.fr'
AUTHOR = 'Maxime "Epoc" Gross'
REQUIRES_PYTHON = '>=3.12'
VERSION = None  # Pulled from staticjinjaplus/__version__.py

REQUIRED = [
    'staticjinja~=5.0',
    'webassets~=2.0',
    'htmlmin~=0.1',
    'cssutils~=2.10',
    'jsmin~=3.0',
]

EXTRAS = {
    'dev': {
        'build~=1.2',
        'twine~=5.0',
    }
}

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Operating System :: OS Independent',
    'Environment :: Web Environment',
    'Topic :: Software Development :: Libraries',
    'Topic :: Text Processing :: Markup :: HTML',
    'Topic :: Text Processing :: Markup :: Markdown',
    'Programming Language :: Python :: 3.12',
    'Intended Audience :: Developers',
]

PROJECT_URLS = {
    'Documentation': 'https://github.com/EpocDotFr/staticjinjaplus#readme',
    'Source': 'https://github.com/EpocDotFr/staticjinjaplus',
    'Tracker': 'https://github.com/EpocDotFr/staticjinjaplus/issues',
    'Changelog': 'https://github.com/EpocDotFr/staticjinjaplus/releases',
}

here = os.path.abspath(os.path.dirname(__file__))

try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

about = {}

if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")

    with open(os.path.join(here, project_slug, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION


class UploadCommand(Command):
    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel distribution…')
        os.system('"{0}" -m build --sdist --wheel'.format(sys.executable))

        self.status('Uploading the package to PyPI via Twine…')
        os.system('twine upload dist/*')

        self.status('Pushing git tags…')
        os.system('git tag v{0}'.format(about['__version__']))
        os.system('git push --tags')

        sys.exit()


setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(),
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    license='DBAD',
    entry_points={
        'console_scripts': [
            'staticjinjaplus = staticjinjaplus.cli:cli',
        ]
    },
    classifiers=CLASSIFIERS,
    cmdclass={
        'upload': UploadCommand,
    },
    project_urls=PROJECT_URLS
)