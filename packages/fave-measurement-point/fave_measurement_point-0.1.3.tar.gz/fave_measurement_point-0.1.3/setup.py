# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['fave_measurement_point']

package_data = \
{'': ['*']}

install_requires = \
['nptyping>=2.5.0,<3.0.0', 'numpy>=1.26.4,<2.0.0']

setup_kwargs = {
    'name': 'fave-measurement-point',
    'version': '0.1.3',
    'description': 'A library for defining and evaluating formant measurement point heuristics.',
    'long_description': '# fave-measurement-point\nA library for defining and evaluating formant measurement point heuristics.\n',
    'author': 'JoFrhwld',
    'author_email': 'JoFrhwld@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
