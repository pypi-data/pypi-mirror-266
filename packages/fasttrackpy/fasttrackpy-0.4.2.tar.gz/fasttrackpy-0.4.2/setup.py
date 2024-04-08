# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['fasttrackpy', 'fasttrackpy.patterns', 'fasttrackpy.processors']

package_data = \
{'': ['*'], 'fasttrackpy': ['resources/*']}

install_requires = \
['aligned-textgrid>=0.6.2,<0.7.0',
 'click>=8.1.7,<9.0.0',
 'cloup>=3.0.3,<4.0.0',
 'joblib>=1.3.2,<2.0.0',
 'matplotlib>=3.8.2,<4.0.0',
 'polars>=0.20.18,<0.21.0',
 'praat-parselmouth>=0.4.3,<0.5.0',
 'pytest-cov>=4.1.0,<5.0.0',
 'pytest>=7.4.3,<8.0.0',
 'pyyaml>=6.0.1,<7.0.0',
 'tqdm>=4.66.1,<5.0.0']

extras_require = \
{':python_version >= "3.10" and python_version < "3.12"': ['scipy>=1.11.3,<2.0.0',
                                                           'numpy>=1.26.1,<2.0.0'],
 ':sys_platform != "win32"': ['python-magic>=0.4.27,<0.5.0'],
 ':sys_platform == "win32"': ['python-magic-bin>=0.4.14,<0.5.0']}

entry_points = \
{'console_scripts': ['fasttrack = fasttrackpy.cli:fasttrack']}

setup_kwargs = {
    'name': 'fasttrackpy',
    'version': '0.4.2',
    'description': 'A python implementation of FastTrack',
    'long_description': '# FastTrackPy\n[![PyPI](https://img.shields.io/pypi/v/fasttrackpy)](https://pypi.org/project/fasttrackpy/)\n[![Python CI](https://github.com/JoFrhwld/fasttrackpy/actions/workflows/test-and-run.yml/badge.svg)](https://github.com/JoFrhwld/fasttrackpy/actions/workflows/test-and-run.yml) [![codecov](https://codecov.io/gh/FastTrackiverse/fasttrackpy/graph/badge.svg?token=GOAWY4B5C8)](https://codecov.io/gh/FastTrackiverse/fasttrackpy) <a href="https://codeclimate.com/github/JoFrhwld/fasttrackpy/maintainability"><img src="https://api.codeclimate.com/v1/badges/6725fded174b21a3c59f/maintainability" /></a> [![DOI](https://zenodo.org/badge/580169086.svg)](https://zenodo.org/badge/latestdoi/580169086)\n\n\nGoal: A FastTrack python implementation with importable modules\n\n## Installation\n\n```bash\npip install fasttrackpy\n```\n\n## Usage\n\n```bash\nfasttrack --file audio.wav --output formants.csv\n```\n',
    'author': 'JoFrhwld',
    'author_email': 'JoFrhwld@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://fasttrackiverse.github.io/fasttrackpy/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<3.12',
}


setup(**setup_kwargs)
