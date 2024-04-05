# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sufficiency_data_transform']

package_data = \
{'': ['*']}

install_requires = \
['chardet>=5.2.0,<6.0.0', 'pandas>=2.2.1,<3.0.0', 'python-decouple>=3.8,<4.0']

setup_kwargs = {
    'name': 'sufficiency-data-transform',
    'version': '0.1.0',
    'description': 'temp repo for liia sufficiency data transform',
    'long_description': 'This is a temporary repo that hosts code which needs to be plugged into the liia-tools-pipeline.\n\nThe input data used in this process are the output files generated at the end of the 903 pipeline.\n\n## Setup\n1. Create a `.env` file whose content should be a copy of the `env.sample` file.\n2. In your `.env` file, assign the input and output variables to directories you choose. Ensure that your path ends with `\\`.\n3. In the command line, do `poetry install` and then `poetry shell` to install dependencies.\n4. Then `python -m sufficiency_data_transform` to run the tool and generate the output files.\n\nDummy input data can be gotten from [this location](https://socialfinanceltd.sharepoint.com/:f:/s/Digi/Elr6MmNuznVBm6M3YWSlXqIBWRTv6Pb19eVe2HI_FdTXjw?e=TbZQYL). Care should be taken so that it is **never pushed** on GitHub. \nYou can create an empty directory to which the outputs should be sent.\n\nIn production, the goal will be to return the new output files to the same location where the input files were gotten from.',
    'author': 'tab1tha',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.11,<4.0',
}


setup(**setup_kwargs)
