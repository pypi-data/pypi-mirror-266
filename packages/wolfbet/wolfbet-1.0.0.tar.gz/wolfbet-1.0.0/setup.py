# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wolfbet', 'wolfbet.core']

package_data = \
{'': ['*']}

install_requires = \
['colorama>=0.4.6,<0.5.0', 'http-injector>=1.0.4,<2.0.0']

setup_kwargs = {
    'name': 'wolfbet',
    'version': '1.0.0',
    'description': '',
    'long_description': '',
    'author': 'DesKaOne',
    'author_email': 'DesKaOne@users.noreply.github.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
