# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['feynamp', 'feynamp.form', 'feynamp.sympy']

package_data = \
{'': ['*']}

install_requires = \
['feynml>=0.2.26', 'feynmodel>=0.0.5', 'pqdm', 'python-form', 'sympy']

setup_kwargs = {
    'name': 'feynamp',
    'version': '0.0.9',
    'description': 'Compute Feynman diagrams',
    'long_description': '# FeynAmp\n\n[![PyPI version][pypi image]][pypi link] [![PyPI version][pypi versions]][pypi link]  ![downloads](https://img.shields.io/pypi/dm/feynamp.svg)\n\n[![test][a t image]][a t link]      [![Coverage Status][c t i]][c t l]  [![Codacy Badge](https://app.codacy.com/project/badge/Coverage/b7192679265b441cb534c9dc06d1b350)](https://app.codacy.com/gh/APN-Pucky/feynamp/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_coverage)   [![Codacy Badge](https://app.codacy.com/project/badge/Grade/b7192679265b441cb534c9dc06d1b350)](https://app.codacy.com/gh/APN-Pucky/feynamp/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)\n\n\n## Related\n\n* Mathematica: FormCalc, FeynCalc\n* Julia: https://arxiv.org/pdf/2310.07634.pdf\n\n[pypi image]: https://badge.fury.io/py/feynamp.svg\n[pypi link]: https://pypi.org/project/feynamp/\n[pypi versions]: https://img.shields.io/pypi/pyversions/feynamp.svg\n\n[a t link]: https://github.com/APN-Pucky/feynamp/actions/workflows/test.yml\n[a t image]: https://github.com/APN-Pucky/feynamp/actions/workflows/test.yml/badge.svg\n\n[c t l]: https://coveralls.io/github/APN-Pucky/feynamp?branch=master\n[c t i]: https://coveralls.io/repos/github/APN-Pucky/feynamp/badge.svg?branch=master\n',
    'author': 'Alexander Puck Neuwirth',
    'author_email': 'alexander@neuwirth-informatik.de',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/APN-Pucky/feynamp',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
