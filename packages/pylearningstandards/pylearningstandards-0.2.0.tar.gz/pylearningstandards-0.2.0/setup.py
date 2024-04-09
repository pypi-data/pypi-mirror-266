# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['py_learning_standards']

package_data = \
{'': ['*']}

install_requires = \
['dataclass-wizard>=0.22.3,<0.23.0', 'pyld>=2.0.4,<3.0.0']

setup_kwargs = {
    'name': 'pylearningstandards',
    'version': '0.2.0',
    'description': '',
    'long_description': '',
    'author': 'Daniel Auerbach',
    'author_email': 'auerbach@ict.usc.edu',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8.4,<4.0.0',
}


setup(**setup_kwargs)
