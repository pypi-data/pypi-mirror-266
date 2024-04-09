# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fast_parse_time',
 'fast_parse_time.explicit.bp',
 'fast_parse_time.explicit.dmo',
 'fast_parse_time.explicit.dto',
 'fast_parse_time.explicit.svc',
 'fast_parse_time.implicit.bp',
 'fast_parse_time.implicit.dmo',
 'fast_parse_time.implicit.dto',
 'fast_parse_time.implicit.svc']

package_data = \
{'': ['*']}

install_requires = \
['baseblock', 'dateparser', 'openai', 'word2number']

setup_kwargs = {
    'name': 'fast-parse-time',
    'version': '0.1.12',
    'description': 'Natural Language (NLP) Extraction of Date and Time',
    'long_description': '# fast-parse-time\n',
    'author': 'Craig Trim',
    'author_email': 'craigtrim@gmail.com',
    'maintainer': 'Craig Trim',
    'maintainer_email': 'craigtrim@gmail.com',
    'url': 'https://github.com/craigtrim/fast-parse-time',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.11.5,<4.0.0',
}


setup(**setup_kwargs)
