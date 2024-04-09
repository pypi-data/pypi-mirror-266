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
    'version': '0.0.1',
    'description': 'Neo Sapiens - Pytorch',
    'long_description': '[![Multi-Modality](agorabanner.png)](https://discord.gg/qUtxnK2NMf)\n\n# Python Package Template\nA easy, reliable, fluid template for python packages complete with docs, testing suites, readme\'s, github workflows, linting and much much more\n\n\n## Installation\n\nYou can install the package using pip\n\n```bash\npip install -e .\n```\n\n# Usage\n```python\nprint("hello world")\n\n```\n\n\n\n### Code Quality 🧹\n\n- `make style` to format the code\n- `make check_code_quality` to check code quality (PEP8 basically)\n- `black .`\n- `ruff . --fix`\n\n### Tests 🧪\n\n[`pytests`](https://docs.pytest.org/en/7.1.x/) is used to run our tests.\n\n### Publish on PyPi 🚀\n\n**Important**: Before publishing, edit `__version__` in [src/__init__](/src/__init__.py) to match the wanted new version.\n\n```\npoetry build\npoetry publish\n```\n\n### CI/CD 🤖\n\nWe use [GitHub actions](https://github.com/features/actions) to automatically run tests and check code quality when a new PR is done on `main`.\n\nOn any pull request, we will check the code quality and tests.\n\nWhen a new release is created, we will try to push the new code to PyPi. We use [`twine`](https://twine.readthedocs.io/en/stable/) to make our life easier. \n\nThe **correct steps** to create a new realease are the following:\n- edit `__version__` in [src/__init__](/src/__init__.py) to match the wanted new version.\n- create a new [`tag`](https://git-scm.com/docs/git-tag) with the release name, e.g. `git tag v0.0.1 && git push origin v0.0.1` or from the GitHub UI.\n- create a new release from GitHub UI\n\nThe CI will run when you create the new release.\n\n# Docs\nWe use MK docs. This repo comes with the zeta docs. All the docs configurations are already here along with the readthedocs configs.\n\n\n\n# License\nMIT\n',
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
