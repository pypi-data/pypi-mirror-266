# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['drive',
 'drive.cluster',
 'drive.factory',
 'drive.filters',
 'drive.log',
 'drive.models',
 'drive.plugins',
 'drive.utilities',
 'drive.utilities.callbacks',
 'drive.utilities.parser']

package_data = \
{'': ['*']}

install_requires = \
['igraph>=0.10.4,<0.11.0',
 'numpy>=1.24.2,<2.0.0',
 'pandas>=1.5.3,<2.0.0',
 'rich-argparse>=1.3.0,<2.0.0',
 'scipy>=1.10.1,<2.0.0']

entry_points = \
{'console_scripts': ['drive = drive.drive:main']}

setup_kwargs = {
    'name': 'drive-ibd',
    'version': '2.7.0',
    'description': 'cli tool to identify networks of individuals who share IBD segments overlapping loci of interest',
    'long_description': '[![Documentation Status](https://readthedocs.org/projects/drive-ibd/badge/?version=latest)](https://drive-ibd.readthedocs.io/en/latest/?badge=latest)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![PyPI version](https://badge.fury.io/py/drive-ibd.svg)](https://badge.fury.io/py/drive-ibd)\n\n# DRIVE:\n\nThis repository contains the source code for the tool DRIVE (Distant Relatedness for Identification and Variant Evaluation) is a novel approach to IBD-based genotype inference used to identify shared chromosomal segments in dense genetic arrays. DRIVE implements a random walk algorithm that identifies clusters of individuals who pairwise share an IBD segment overlapping a locus of interest. This tool was developed in python by the Below Lab at Vanderbilt University. The documentation for how to use this tool can be found here [DRIVE documentation](https://drive-ibd.readthedocs.io/en/latest/)\n\n## Installing DRIVE:\nDRIVE is available on PYPI and can easily be installed using the following command:\n\n```bash\npip install drive-ibd\n```\nIt is recommended to install DRIVE within a virtual environment such as venv, or conda. More information about this process can be found within the documentation.\n\nIf the user wishes to develop DRIVE or install the program from source then they can clone the repository. This process is described under the section called "Github Installation" in the documentation.\n\n### Reporting issues:\nIf you wish to report a bug or propose a feature you can find templates under the .github/ISSUE_TEMPLATE directory.\n\n',
    'author': 'James Baker',
    'author_email': 'james.baker@vanderbilt.edu',
    'maintainer': 'James Baker',
    'maintainer_email': 'james.baker@vanderbilt.edu',
    'url': 'https://drive-ibd.readthedocs.io/en/latest/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9, !=2.7.*, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*, !=3.6.*, !=3.7.*, !=3.8.*',
}


setup(**setup_kwargs)
