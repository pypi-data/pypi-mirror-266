# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['i_bip_wallet']

package_data = \
{'': ['*']}

install_requires = \
['ecdsa>=0.18.0,<0.19.0', 'pycryptodomex>=3.20.0,<4.0.0']

setup_kwargs = {
    'name': 'i-bip-wallet',
    'version': '1.0.0rc2',
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
