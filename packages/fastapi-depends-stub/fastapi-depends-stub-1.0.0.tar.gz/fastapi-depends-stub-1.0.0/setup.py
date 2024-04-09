# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fastapi_depends_stub']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'fastapi-depends-stub',
    'version': '1.0.0',
    'description': 'Prevent FastAPI from digging into real dependencies attributes detecting them as request data.',
    'long_description': None,
    'author': 'Timur Kasimov',
    'author_email': 'tkasimov@icloud.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
