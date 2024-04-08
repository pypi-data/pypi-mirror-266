# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['http_injector',
 'http_injector._adapter',
 'http_injector._context',
 'http_injector._utils',
 'http_injector._utils._certificate']

package_data = \
{'': ['*']}

install_requires = \
['chardet>=5.2.0,<6.0.0',
 'httpx[http2,socks]>=0.27.0,<0.28.0',
 'requests>=2.31.0,<3.0.0']

setup_kwargs = {
    'name': 'http-injector',
    'version': '1.0.5',
    'description': '',
    'long_description': 'pip install http_injector',
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
