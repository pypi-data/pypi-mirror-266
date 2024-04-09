# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['droughty',
 'droughty.cube_parser',
 'droughty.droughty_core',
 'droughty.droughty_cube',
 'droughty.droughty_dbml',
 'droughty.droughty_dbt',
 'droughty.droughty_docs',
 'droughty.droughty_jinjasql.jinjasql',
 'droughty.droughty_lookml',
 'droughty.droughty_resolve']

package_data = \
{'': ['*'],
 'droughty': ['.ipynb_checkpoints/*'],
 'droughty.droughty_dbt': ['.ipynb_checkpoints/*']}

install_requires = \
['GitPython>=3.1.41,<4.0.0',
 'Markdown==3.4.1',
 'PyYAML>=6.0,<7.0',
 'glom==23.1.1',
 'jinja2>=3.1.2,<4.0.0',
 'lkml==1.3.1',
 'numpy==1.24.2',
 'openai==0.26.5',
 'pandas==1.5.3',
 'pandas_dedupe==1.5.0',
 'pandas_gbq==0.19.1',
 'protobuf>=4.0',
 'pyarrow==14.0.1',
 'ruamel-yaml==0.17.21',
 'six==1.16.0',
 'snowflake-connector-python>=3.0.0,<4.0.0',
 'snowflake-sqlalchemy>=1.4.6,<2.0.0',
 'sqlalchemy>=1.4.0,<2.0.0']

entry_points = \
{'console_scripts': ['droughty = droughty.main:start']}

setup_kwargs = {
    'name': 'droughty',
    'version': '0.11.0',
    'description': 'droughty is an analytics engineering toolkit, helping keep your workflow dry.',
    'long_description': '\\#\\#\\#\\# droughty. \\#\\# adjective, drought·i·er, drought·i·est. \\#\\#\ndry.\n\nDroughty helps keep your workflow *ah hem* dry\n\n------------------------------------------------------------------------\n\n**What is droughty?**\n\ndroughty is an analytics engineering toolkit. It takes warehouse\nmetadata and outputs semantic files.\n\nCurrent tools and supported platforms are:\n\n-   lookml - generates a lkml with views, explores and measures from a\n    warehouse schema\n-   dbt - generates a base schema from specified warehouse schemas.\n    Includes standard testing routines\n-   dbml - generates an ERD based on the warehouse layer of your\n    warehouse. Includes pk, fk relationships\n-   cube - generates a cube schema including dimensions, integrations\n    and meassures\n\nThe purpose of this project is to automate the repetitive, dull elements\nof analytics engineering in the modern data stack. It turns out this\nalso leads to cleaner projects, less human error and increases the\nlikelihood of the basics getting done\\...\n\n**Documentation**\n\nInstallation, configuration and usage documentation can be found on\n[ReadTheDocs](https://droughty.readthedocs.io/en/latest/)\n\n**Installation**\n\ndroughty is available through [pip](https://pypi.org/project/droughty):\n\n    pip install droughty\n',
    'author': 'Lewis',
    'author_email': 'lewischarlesbaker@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/lewischarlesbaker/droughty',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.12',
}


setup(**setup_kwargs)
