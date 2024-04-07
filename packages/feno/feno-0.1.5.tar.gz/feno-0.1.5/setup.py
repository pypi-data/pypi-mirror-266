"""A script for update moodle vpl from github

See:
https://github.com/senapk/feno
"""

import pathlib
import re

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

here = pathlib.Path(__file__).parent.resolve()  # current path
long_description = (here / 'README.md').read_text(encoding='utf-8')  # Get the long description from the README file
with open(here / 'requirements.txt') as fp:  # read requirements.txt
    install_reqs = [r.rstrip() for r in fp.readlines() if not r.startswith('#')]


def get_version():
    file = here / 'src/feno/__init__.py'
    return re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]', file.read_text(), re.M).group(1)


setup(
    name='feno',  # Required https://packaging.python.org/specifications/core-metadata/#name
    version=get_version(),  # Required https://packaging.python.org/en/latest/single_source_version.html
    description='feno: Flexible Exercise Notation Organizer',  # Optional
    long_description=long_description,  # Optional
    long_description_content_type='text/markdown',  # Optional
    url='https://github.com/senapk/feno',  # Optional, project's main homepage
    author='David Sena Oliveira',  # Optional, name or the name of the organization which owns the project
    author_email='sena@ufc.br',  # Optional
    classifiers=['Development Status :: 3 - Alpha',  # 3 - Alpha, 4 - Beta, 5 - Production/Stable
                 'Operating System :: OS Independent',  # Operation system
                 'Topic :: Education',  # Topics
                 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',  # Pick your license as you wish
                 'Programming Language :: Python :: 3.8',
                 ],  # Classifiers help users find your project by categorizing it https://pypi.org/classifiers/
    keywords='programming, learning',  # Optional
    package_dir={'': 'src'},  # Optional, use if source code is in a subdirectory under the project root, i.e. `src/`
    packages=find_packages(where='src'),  # Required
    python_requires='>=3.7, <4',

    # For an analysis of "install_requires" vs pip's requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=install_reqs,  # Optional, additional pip packeges to be installed by this pacakge installation

    # dependencies). Users will be able to install these using the "extras"
    # syntax, for example: $ pip install sampleproject[dev]
    # Similar to `install_requires` above, these must be valid existing projects
    extras_require={'dev': ['check-manifest'],
                    'test': ['coverage'],
                    },  # Optional

    entry_points={'console_scripts': ['feno=feno.__main__:main', 'mdpp=feno.mdpp:main', 'filter=feno.filter:main', 'indexer=feno.indexer:main', 'check=feno.check:main'], },

    project_urls={'Bug Reports': 'https://github.com/senapk/feno/issues',
                  'Source': 'https://github.com/senapk/feno/',
                  },  # Optional https://packaging.python.org/specifications/core-metadata/#project-url-multiple-use
)
