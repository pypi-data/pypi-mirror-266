# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ocui',
 'ocui.oci',
 'ocui.oci.command',
 'ocui.oci.dataclass',
 'ocui.oci.serialization',
 'ocui.ui',
 'ocui.ui.base']

package_data = \
{'': ['*'], 'ocui': ['res/*'], 'ocui.ui.base': ['css/*']}

install_requires = \
['appdirs>=1.4,<1.5', 'textual>=0.41,<0.42', 'toml>=0.10,<0.11']

entry_points = \
{'console_scripts': ['ocui = ocui.app:main']}

setup_kwargs = {
    'name': 'ocui',
    'version': '0.1.0',
    'description': 'This is a simple and handy text based GUI utility for dealing with boring and repetitive tasks when managing containers.',
    'long_description': "# `ocui`\n\n[![Python package](https://github.com/fishinthecalculator/ocui/actions/workflows/python-package.yml/badge.svg?branch=main)](https://github.com/fishinthecalculator/ocui/actions/workflows/python-package.yml) \n![Python versions](https://raw.githubusercontent.com/fishinthecalculator/ocui/main/.img/python.svg)\n![License](https://raw.githubusercontent.com/fishinthecalculator/ocui/main/.img/license.svg)\n\n`ocui` is a terminal user interface to facilitate the most common tasks around OCI containers running on a single host.\n\n![ocui screenshot](https://raw.githubusercontent.com/fishinthecalculator/ocui/main/.img/screenshot.png)\n\n## Contributing\n\nAll contributions are welcome. If you have commit access please remember to setup the authentication hook with\n\n```bash\ncp etc/git/pre-push .git/hooks/pre-push\n```\n\n## License\n\nUnless otherwise stated all the files in this repository are to be considered under the GPL 3.0 terms. You are more than welcome to open issues or send patches.\n\n## Helpful initiatives\n\n- This project started during SUSE's [Hack Week 23](https://hackweek.opensuse.org), where I had the time to participate [a project](https://hackweek.opensuse.org/23/projects/forklift-text-based-gui-utility-for-dealing-with-containers) to implement something like `ocui`.\n- This project is clearly strongly inspired from [K9s](https://k9scli.io/). Without it I would probably never had found the inspiration for `ocui`.\n- The endless nice TUI managers from the community, starting from `top` to `htop`, `glances` and all the others.\n",
    'author': 'Giacomo Leidi',
    'author_email': 'giacomo.leidi@suse.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
