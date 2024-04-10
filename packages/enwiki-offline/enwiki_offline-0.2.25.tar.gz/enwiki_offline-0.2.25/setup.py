# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['enwiki_offline']

package_data = \
{'': ['*']}

install_requires = \
['baseblock', 'dvc']

setup_kwargs = {
    'name': 'enwiki-offline',
    'version': '0.2.25',
    'description': 'Offline Access to Enwiki Entities',
    'long_description': '# enwiki-offline\n\n## Functions\n```python\ndef exists(entity: str) -> bool\n```\nPerforms a case insensitive search and returns True if a Wikipedia entry exists for the input entity.  Synonyms, Partial and Fuzzy searches are not supported.  Exact matches only.\n\n```python\ndef is_ambiguous(entity: str) -> bool\n```\nReturns True if multiple Wikipedia entries exist for this term.\n\n```python\ndef titles(entity: str) -> Optional[List[str]]\n```\nReturns all Wikipedia Titles for this input entity.\n\n## Use Existing Data\nScroll down to the `DVC` section and use the `dvc pull` command to access the data.\n\n## Parsing Wikipedia Titles\nThe latest enwiki file can be downloaded from https://dumps.wikimedia.org/enwiki/\n\nYou only need to do this if\n1. You don\'t want to refresh from DVC\n2. You have a different version of the enwiki file\n```sh\npoetry run python drivers/parse_enwiki_all_titles.py "/path/to/file/enwiki-20240301-all-titles"\n```\n\n## DVC (Data Version Control)\n\n### Initialize DVC and Configure S3 Remote\nIn your project root, initialize DVC if you haven\'t already, and configure your S3 bucket as the remote storage. Replace `enwikioffline` with your actual S3 bucket name if it\'s different. Run:\n\n```shell\ndvc init\ndvc remote add -d myremote s3://enwikioffline\ndvc remote modify myremote profile enwiki_offline\n```\n\nThis setup:\n- Initializes DVC in your project.\n- Adds your S3 bucket as the default remote storage.\n- Configures DVC to use the `enwiki_offline` AWS profile for S3 operations.\n\n### Track and Push Data with DVC\nTo track the resources folder and push it to S3, execute:\n```shell\ndvc add resources\ngit add resources.dvc .gitignore\ngit commit -m "Track resources folder with DVC"\ndvc push\n```\n\nThis process:\n- Tracks the `resources` folder with DVC, creating a .dvc file.\n- Commits the DVC files to Git.\n- Pushes the data to your S3 bucket using the configured AWS profile.\n\n### Pull Data with DVC\nTo retrieve the data managed by DVC, use:\n```sh\ndvc pull\n```\nThis command pulls the data from S3 into your local `resources` folder, based on the current DVC setup and the latest `resources.dvc` file in your repository.\n',
    'author': 'Craig Trim',
    'author_email': 'craigtrim@gmail.com',
    'maintainer': 'Craig Trim',
    'maintainer_email': 'craigtrim@gmail.com',
    'url': 'https://github.com/craigtrim/enwiki-offline',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.11.5,<4.0.0',
}


setup(**setup_kwargs)
