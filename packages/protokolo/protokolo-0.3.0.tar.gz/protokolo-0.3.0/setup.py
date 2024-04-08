# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['protokolo']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=22.1.0', 'click>=8.0']

entry_points = \
{'console_scripts': ['protokolo = protokolo.cli:main']}

setup_kwargs = {
    'name': 'protokolo',
    'version': '0.3.0',
    'description': 'Protokolo is a change log generator.',
    'long_description': "<!--\nSPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>\n\nSPDX-License-Identifier: CC-BY-SA-4.0 OR GPL-3.0-or-later\n-->\n\n# Protokolo\n\n[![Latest Protokolo version](https://img.shields.io/pypi/v/protokolo.svg)](https://pypi.python.org/pypi/protokolo)\n[![Supported Python versions](https://img.shields.io/pypi/pyversions/protokolo.svg)](https://pypi.python.org/pypi/protokolo)\n[![REUSE status](https://api.reuse.software/badge/codeberg.org/carmenbianca/protokolo)](https://api.reuse.software/info/codeberg.org/carmenbianca/protokolo)\n[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg)](https://github.com/RichardLitt/standard-readme)\n\nProtokolo is a change log generator.\n\nProtokolo allows you to maintain your change log entries in separate files, and\nthen finally aggregate them into a new section in CHANGELOG just before release.\n\n## Table of Contents\n\n- [Background](#background)\n- [Install](#install)\n- [Usage](#usage)\n- [Maintainers](#maintainers)\n- [Contributing](#contributing)\n- [License](#license)\n\n## Background\n\nChange logs are [a really good idea](https://keepachangelog.com/).\nUnfortunately, they are also a bit of a pain when combined with version control:\n\n- If two pull requests edit CHANGELOG, there is a non-zero chance that you'll\n  need to resolve a conflict when trying to merge them both.\n- Just after you make a release, you need to create a new section in CHANGELOG\n  for your next release. If you forget this busywork, new feature branches will\n  need to create this section, which increases the chance of merge conflicts.\n- If a feature branch adds a change log entry to the section for the next v1.2.3\n  release, and v1.2.3 subsequently releases without merging that feature branch,\n  then merging that feature branch afterwards would still add the change log\n  entry to the v1.2.3 section, even though it should now go to the v1.3.0\n  section.\n\nLife would be a lot easier if you didn't have to deal with these problems.\n\nEnter Protokolo. The idea is very simple: For every change log entry, create a\nnew file. Finally, just before release, compile the contents of those files into\na new section in CHANGELOG, and delete the files.\n\n## Install\n\nProtokolo is a regular Python package. You can install it using\n`pipx install protokolo`. Make sure that `~/.local/share/bin` is in your `$PATH`\nwith `pipx ensurepath`.\n\n## Usage\n\nFor full documentation and options, read the documentation at TODO.\n\n### Initial set-up\n\nTo set up your project for use with Protokolo, run `protokolo init`. This will\ncreate a `CHANGELOG.md` file (if one did not already exist) and a directory\nstructure under `changelog.d`. The directory structure uses the\n[Keep a Changelog](https://keepachangelog.com/) sections, and ends up looking\nlike this:\n\n```\n.\n├── changelog.d\n│   ├── added\n│   │   └── .protokolo.toml\n│   ├── changed\n│   │   └── .protokolo.toml\n│   ├── deprecated\n│   │   └── .protokolo.toml\n│   ├── fixed\n│   │   └── .protokolo.toml\n│   ├── removed\n│   │   └── .protokolo.toml\n│   ├── security\n│   │   └── .protokolo.toml\n│   └── .protokolo.toml\n├── CHANGELOG.md\n└── .protokolo.toml\n```\n\nThe `.protokolo.toml` files in `changelog.d` contain metadata for their\nrespective sections; the section title, heading level, and order. Their\ninclusion is mandatory.\n\nThe `.protokolo.toml` file in the root of the project contains configurations\nfor Protokolo that reduce the amount of typing you need to do when running\ncommands.\n\nIf a `CHANGELOG.md` file already existed, make sure to add a line containing\n`<!-- protokolo-section-tag -->` just before the heading of the latest release.\n\n### Adding entries\n\nTo add a change log entry, create the file `changelog.d/added/my_feature.md`,\nand write something like:\n\n```markdown\n- Added `--my-new-feature` option.\n```\n\nNote the item dash at the start; Protokolo does not add them for you. What you\nwrite is exactly what you get.\n\nYou can add more files. Change log entries in the same section (read: directory)\nare sorted alphabetically by their file name. If you want to make certain that\nsome change log entries go first or last, prefix the file with `000_` or `zzz_`.\nFor example, you can create `changelog.d/added/000_important_feature.md` to make\nit appear first.\n\n### Compiling your change log\n\nYou compile your change log with `protokolo compile`. This will take all change\nlog entries from `changelog.d` and put them in your `CHANGELOG.md`. If we run it\nnow, the following section is added after the `<!-- protokolo-section-tag -->`\ncomment:\n\n```markdown\n## ${version} - 2023-11-08\n\n### Added\n\n- Added important feature.\n\n- Added `--my-new-feature` option.\n```\n\nThe Markdown files in `changelog.d/added/` are deleted. You can manually replace\n`${version}` with a release version, or you can pass the option\n`--format version 1.0.0` to `protokolo compile` to format the heading at compile\ntime.\n\n## Maintainers\n\n- Carmen Bianca BAKKER <carmen@carmenbianca.eu>\n\n## Contributing\n\nThe code and issue tracker is hosted at\n<https://codeberg.org/carmenbianca/protokolo>. You are welcome to open any\nissues. For pull requests, bug fixes are always welcome, but new features should\nprobably be discussed in any issue first.\n\n## License\n\nAll code is licensed under GPL-3.0-or-later.\n\nAll documentation is licensed under CC-BY-SA-4.0 OR GPL-3.0-or-later.\n\nSome configuration files are licensed under CC0-1.0 OR GPL-3.0-or-later.\n\nThe repository is [REUSE](https://reuse.software)-compliant. Check the\nindividual files for their exact licensing.\n",
    'author': 'Carmen Bianca BAKKER',
    'author_email': 'carmen@carmenbianca.eu',
    'maintainer': 'Carmen Bianca BAKKER',
    'maintainer_email': 'carmen@carmenbianca.eu',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.11,<4.0',
}


setup(**setup_kwargs)
