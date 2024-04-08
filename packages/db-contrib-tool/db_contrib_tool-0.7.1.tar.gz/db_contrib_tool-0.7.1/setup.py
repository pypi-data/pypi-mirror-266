# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['db_contrib_tool',
 'db_contrib_tool.clients',
 'db_contrib_tool.evg_aware_bisect',
 'db_contrib_tool.services',
 'db_contrib_tool.setup_mongot_repro_env',
 'db_contrib_tool.setup_repro_env',
 'db_contrib_tool.symbolizer',
 'db_contrib_tool.utils']

package_data = \
{'': ['*'], 'db_contrib_tool': ['config/*']}

install_requires = \
['Inject>=4.3.1,<5.0.0',
 'PyGithub==1.55',
 'PyYAML==6.0.1',
 'analytics-python==1.4.0',
 'click>=8.1.3,<9.0.0',
 'distro==1.6.0',
 'evergreen.py==3.6.14',
 'oauthlib==3.1.1',
 'packaging>=23.0,<24.0',
 'pkce==1.0.3',
 'pydantic==1.8.2',
 'requests-oauthlib==1.3.0',
 'requests==2.26.0',
 'retry>=0.9.2,<0.10.0',
 'structlog==21.4.0',
 'tenacity>=8.0.1,<9.0.0']

entry_points = \
{'console_scripts': ['db-contrib-tool = db_contrib_tool.cli:cli']}

setup_kwargs = {
    'name': 'db-contrib-tool',
    'version': '0.7.1',
    'description': "The `db-contrib-tool` - MongoDB's tool for contributors.",
    'long_description': '# db-contrib-tool\n\nThe `db-contrib-tool` - MongoDB\'s tools for contributors.\n\n## Table of contents\n\n- [db-contrib-tool](#db-contrib-tool)\n  - [Table of contents](#table-of-contents)\n  - [Description](#description)\n  - [Dependencies](#dependencies)\n  - [Installation](#installation)\n  - [Usage](#usage)\n  - [Contributor\'s Guide (local development)](#contributors-guide-local-development)\n    - [Install project dependencies](#install-project-dependencies)\n    - [Run command line tool (local development)](#run-command-line-tool-local-development)\n    - [Run linters](#run-linters)\n    - [Run tests](#run-tests)\n    - [Pre-commit](#pre-commit)\n    - [Testing changes in mongo](#testing-changes-in-mongo)\n    - [Testing changes locally](#testing-changes-locally)\n    - [Versioning](#versioning)\n    - [Code Review](#code-review)\n    - [Deployment](#deployment)\n\n## Description\n\nThe command line tool with various subcommands:\n- `bisect`\n  - [README.md](src/db_contrib_tool/evg_aware_bisect/README.md)\n  - performs an evergreen-aware git-bisect to find the \'last passing version\' and \'first failing version\' of mongo\n- `setup-repro-env`\n  - [README.md](src/db_contrib_tool/setup_repro_env/README.md)\n  - downloads and installs:\n    - particular MongoDB versions\n    - debug symbols\n    - artifacts (including resmoke, python scripts etc)\n    - python venv for resmoke, python scripts etc\n- `symbolize`\n  - [README.md](src/db_contrib_tool/symbolizer/README.md)\n  - Symbolizes stacktraces from recent `mongod` and `mongos` binaries compiled in Evergreen, including patch builds, mainline builds, and release/production builds.\n  - Requires authenticating to an internal MongoDB symbol mapping service.\n\n## Dependencies\n\n- Python 3.9 or later (python3 from the [MongoDB Toolchain](https://github.com/10gen/toolchain-builder/blob/master/INSTALL.md) is highly recommended)\n\n## Installation\n\nMake sure [dependencies](#dependencies) are installed.\nUse [pipx](https://pypa.github.io/pipx/) to install db-contrib-tool that will be available globally on your machine:\n\n```bash\npython3 -m pip install pipx\npython3 -m pipx ensurepath\n```\n\nInstalling db-contrib-tool:\n\n```bash\npython3 -m pipx install db-contrib-tool\n```\n\nUpgrading db-contrib-tool:\n\n```bash\npython3 -m pipx upgrade db-contrib-tool\n```\n\nIn case of installation errors, some of them may be related to pipx and could be fixed by re-installing pipx.\n\nRemoving pipx completely (WARNING! This will delete everything that is installed and managed by pipx):\n\n```bash\npython3 -m pip uninstall pipx\nrm -rf ~/.local/pipx  # in case you\'re using the default pipx home directory\n```\n\nNow you can try to install again from scratch.\n\n## Usage\n\nPrint out help message:\n\n```bash\ndb-contrib-tool --help\n```\n\nFor more information see [description](#description) section.\n\n## Contributor\'s Guide (local development)\n\n### Install project dependencies\n\nThis project uses [poetry](https://python-poetry.org/) for dependency management.\n\n```bash\npoetry install\n```\n\n### Run command line tool (local development)\n\nSome subcommands like `bisect` and `symbolize` could be tested from the db-contrib-tool repo root:\n\n```bash\npoetry run db-contrib-tool --help\n```\n\nFor `setup-repro-env` some features can also be tested from the db-contrib-tool repo root,\nbut full features are available when running from mongo repo root.\nSee [testing changes locally](#testing-changes-locally) section.\n\n### Run linters\n\n```bash\npoetry run isort src tests\npoetry run black src tests\n```\n\n### Run tests\n\n```bash\npoetry run pytest\n```\n\n### Pre-commit\n\nThis project has [pre-commit](https://pre-commit.com/) configured. Pre-commit will run\nconfigured checks at git commit time.<br>\nTo enable pre-commit on your local repository run:\n```bash\npoetry run pre-commit install\n```\n\nTo run pre-commit manually:\n```bash\npoetry run pre-commit run\n```\n\n### Testing changes in mongo\n\nThis tool is used to help run tests in the mongodb/mongo repository. On occasion, it may be\ndesirable to run a mongodb-mongo-* patch build with in-flight changes to this repository. The\nfollowing steps can be taken to accomplish that.\n\n- Create a branch with the changes you wish to test.\n- Push the branch to the origin repository: `git push -u origin <branch_name>`.\n- In the "mongo" repository, edit the [evergreen/prelude_db_contrib_tool.sh](https://github.com/10gen/mongo/blob/bbdc1347cdf2533f81b6fd05715c4ef1a092f5a6/evergreen/prelude_db_contrib_tool.sh#L12)\n  to install from the git repository instead of from pypi:\n\n  ```bash\n  pipx install "git+ssh://git@github.com/<user_name>/db-contrib-tool.git@<branch_name>" || exit 1\n  ```\n\n- Create a patch build.\n\nThe patch build should now pull down the changes from your branch instead of using the published\ndb-contrib-tool.\n\n**Note**: Since the db-contrib-tool is pulled from your branch, if you need to make additional\nchanges to the tool, you can just push to the branch and then restart the desired tasks. There is\nno need to create an additional patch build unless you also need to make updates to the mongo\nrepository.\n\n### Testing changes locally\n\nPipx installation recommendations can be found in [installation](#installation) section.\n\nThe tool can be installed via pipx from your local repo:\n\n```bash\npython3 -m pipx install /path/to/db-contrib-tool/repo/root/dir\n```\n\nIf the tool is already installed you can force install an updated version using --force flag:\n\n```bash\npython3 -m pipx install --force /path/to/db-contrib-tool/repo/root/dir\n```\n\nAfter these steps you can run in-development version of db-contrib-tool from any directory:\n\n```bash\ndb-contrib-tool --help\n```\n\n### Versioning\n\nThis project uses [semver](https://semver.org/) for versioning.\nPlease include a description what is added for each new version in `CHANGELOG.md`.\n\n### Code Review\n\nPlease open a GitHub Pull Request for code review.\nThis project uses the [Evergreen Commit Queue](https://docs.devprod.prod.corp.mongodb.com/evergreen/Project-Configuration/Commit-Queue).\nAdd a PR comment with `evergreen merge` to trigger a merge.\n\n### Deployment\n\nDeployment to pypi is done by [deploy](https://spruce.mongodb.com/commits/db-contrib-tool?taskNames=deploy)\ntask of `db-contrib-tool` project in Evergreen.\nA new version in Evergreen is created on merges to `main` branch.\n',
    'author': 'DAG team',
    'author_email': 'dev-prod-dag@mongodb.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/10gen/db-contrib-tool',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
