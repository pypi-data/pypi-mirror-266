# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['neo_sapiens']

package_data = \
{'': ['*']}

install_requires = \
['pydantic', 'swarms']

setup_kwargs = {
    'name': 'neo-sapiens',
    'version': '0.0.2',
    'description': 'Neo Sapiens - Pytorch',
    'long_description': '[![Multi-Modality](agorabanner.png)](https://discord.gg/qUtxnK2NMf)\n\n# Neo Sapiens\n\n\n## install\n`$ pip install -U swarms neo-sapiens`\n\n\n## usage\n\n\n\n# License\nMIT\n',
    'author': 'Kye Gomez',
    'author_email': 'kye@apac.ai',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/kyegomez/NeoSapiens',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
