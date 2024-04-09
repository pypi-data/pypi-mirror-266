# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['phantombuster', 'phantombuster.remoter']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.3,<9.0.0',
 'pandas>=2.0,<3.0',
 'polars>=0.19.12,<0.20.0',
 'pyarrow>=15,<16',
 'pysam>=0.20.0,<0.21.0',
 'regex>=2022.10.31,<2023.0.0',
 'scipy>=1.10.1,<2.0.0',
 'trio>=0.22.0,<0.23.0',
 'zmq>=0.0.0,<0.0.1']

entry_points = \
{'console_scripts': ['phantombuster = phantombuster.cli:phantombuster']}

setup_kwargs = {
    'name': 'phantombuster',
    'version': '0.12.0',
    'description': '',
    'long_description': '',
    'author': 'Simon Haendeler',
    'author_email': 'simon.emanuel.haendeler@univie.ac.at',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<3.13',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
