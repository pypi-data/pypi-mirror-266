# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lenu', 'lenu.data', 'lenu.ml', 'lenu.ml.test']

package_data = \
{'': ['*']}

install_requires = \
['importlib-resources>=5.7.1,<6.0.0',
 'pandas>=1.4.2,<2.0.0',
 'pydantic>=1.9.0,<2.0.0',
 'requests>=2.27.1,<3.0.0',
 'scikit-learn>=1.0.2,<2.0.0',
 'torch>=1.13.1,<2.0.0',
 'transformers>=4.26.0,<5.0.0',
 'typer[all]>=0.4.1,<0.5.0',
 'types-requests>=2.27.16,<3.0.0']

entry_points = \
{'console_scripts': ['lenu = lenu.console:app']}

setup_kwargs = {
    'name': 'lenu',
    'version': '0.2.2',
    'description': 'Legal Entity Name Understanding',
    'long_description': '\n<h1 align="center">\nLENU - Legal Entity Name Understanding \n</h1>\n\n---------------\n\n<h1 align="center">\n<a href="https://gleif.org">\n<img src="http://sdglabs.ai/wp-content/uploads/2022/07/gleif-logo-new.png" width="220" alt="">\n</a>\n</h1><br>\n<h3 align="center">in collaboration with</h3> \n<h1 align="center">\n<a href="https://sociovestix.com">\n<img src="https://sociovestix.com/img/svl_logo_centered.svg" width="700px">\n</a>\n</h1><br>\n\n---------------\n\n[![License](https://img.shields.io/github/license/Sociovestix/lenu.svg)](https://github.com/Sociovestix/lenu/blob/main/LICENSE)\n![](https://img.shields.io/badge/python-3.8%20%7C%203.9-blue)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\n\n**LENU** is a python library that helps to understand and work with Legal Entity Names\nin the context of the [Legal Entity Identifier](https://www.gleif.org/en/about-lei/introducing-the-legal-entity-identifier-lei) (LEI) Standard (ISO 17441)\nas well as the [Entity Legal Form (ELF) Code List](https://www.gleif.org/en/about-lei/code-lists/iso-20275-entity-legal-forms-code-list) Standard (ISO 20275).  \n\nThe library utilizes Machine Learning with Transformers and scikit-learn. It provides and utilizes pre-trained ELF Detection models published at https://huggingface.co/Sociovestix. This code as well as the LEI data and models are distributed under Creative Commons Zero 1.0 Universal license.\n\nThe project was started in November 2021 as a collaboration of the [Global Legal Entity Identifier Foundation](https://gleif.org) (GLEIF) and\n[Sociovestix Labs](https://sociovestix.com) with the goal to explore how Machine Learning can support in detecting the legal form (ELF Code) from a legal name. \n\nIt provides:\n- an interface to download [LEI](https://www.gleif.org/en/lei-data/gleif-golden-copy/download-the-golden-copy#/) and [ELF Code](https://www.gleif.org/en/about-lei/code-lists/iso-20275-entity-legal-forms-code-list) data from GLEIF\'s public website\n- an interface to train and make use of Machine Learning models to classify ELF Codes from given Legal Names\n- an interface to use pre-trained ELF Detection models published on https://huggingface.co/Sociovestix\n---\n\n## Dependencies\n**LENU** requires\n- python (>=3.8, <3.10)\n- [scikit-learn](https://scikit-learn.org/) - Provides Machine Learning functionality for token based modelling\n- [transformers](https://huggingface.co/docs/transformers/index) - Download and applying Neural Network Models\n- [pytorch](https://pytorch.org/) - Machine Learning Framework to train Neural Network Models\n- [pandas](https://pandas.pydata.org/) - For reading and handling data\n- [Typer](https://typer.tiangolo.com/) - Adds the command line interface\n- [requests](https://docs.python-requests.org/en/latest/) and [pydantic](https://pydantic-docs.helpmanual.io/) - For downloading LEI data from GLEIF\'s website\n\n## Installation\n\nvia PyPI:\n```shell\npip install lenu\n```\n\nFrom github:\n```shell\npip install https://github.com/Sociovestix/lenu\n```\n\nEditable install from locally cloned repository\n```shell\ngit clone https://github.com/Sociovestix/lenu\npip install -e lenu\n```\n\n## Usage\n\nCreate folders for LEI and ELF Code data and to store your models\n\n```shell\nmkdir data\nmkdir models\n```\n\nDownload LEI data and ELF Code data into your `data` folder\n```shell\nlenu download\n```\n\nTrain a (default) ELF Code Classification model. An ELF Classification model is always Jurisdiction specific and \nwill be trained from Legal Names from this Jurisdiction.\n\nExamples: \n```shell\nlenu train DE       # Germany\nlenu train US-DE    # United States - Delaware\nlenu train IT       # Italy\n\n# enable logging to see more information like the number of samples and accuracy\nlenu --enable-logging train CH \n```\n\nIdentify ELF Code by using a model. The tool will return the best scoring ELF Codes. \n```shell\nlenu elf DE "Hans Müller KG"\n#   ELF Code                  Entity Legal Form name Local name     Score\n# 0     8Z6G                              Kommanditgesellschaft  0.979568\n# 1     V2YH                       Stiftung des privaten Rechts  0.001141\n# 2     OL20  Einzelunternehmen, eingetragener Kaufmann, ein...  0.000714\n```\n\nYou can also use pre-trained models, which is recommended in most cases:\n```shell\n# Model available at https://huggingface.co/Sociovestix/lenu_DE\nlenu elf Sociovestix/lenu_DE "Hans Müller KG"  \n#  ELF Code      Entity Legal Form name Local name     Score\n#0     8Z6G                  Kommanditgesellschaft  0.999445\n#1     2HBR  Gesellschaft mit beschränkter Haftung  0.000247\n#2     FR3V       Gesellschaft bürgerlichen Rechts  0.000071\n```\n\n## Support and Contributing\nFeel free to reach out to either [Sociovestix Labs](https://sociovestix.com/contact) or [GLEIF](https://www.gleif.org/contact/contact-information)\nif you need support in using this library, in utilizing LEI data in general, or in case you would like to contribute to this library in any form.\n',
    'author': 'aarimond',
    'author_email': 'alexander.arimond@sociovestix.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
