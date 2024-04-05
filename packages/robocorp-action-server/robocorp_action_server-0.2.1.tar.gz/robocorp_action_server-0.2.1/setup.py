# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['robocorp',
 'robocorp.action_server',
 'robocorp.action_server._preload_actions',
 'robocorp.action_server._robo_utils',
 'robocorp.action_server.migrations',
 'robocorp.action_server.package',
 'robocorp.action_server.vendored_deps',
 'robocorp.action_server.vendored_deps.action_package_handling',
 'robocorp.action_server.vendored_deps.package_deps',
 'robocorp.action_server.vendored_deps.package_deps.conda_impl',
 'robocorp.action_server.vendored_deps.package_deps.pip_impl',
 'robocorp.action_server.vendored_deps.termcolors']

package_data = \
{'': ['*'], 'robocorp.action_server': ['bin/*']}

install_requires = \
['aiohttp>=3.9.3,<4.0.0',
 'fastapi>=0.110.0,<0.111.0',
 'fastjsonschema>=2.19.1,<3.0.0',
 'jsonschema>=4.19.2,<5.0.0',
 'msgspec>=0.18,<0.19',
 'psutil>=5,<6',
 'pydantic>=2.4.2,<3.0.0',
 'pyyaml>=6,<7',
 'requests>=2,<3',
 'robocorp-actions>=0.1.0,<0.2.0',
 'termcolor>=2.4.0,<3.0.0',
 'uvicorn>=0.23.2,<0.24.0',
 'websockets>=12.0,<13.0']

entry_points = \
{'console_scripts': ['action-server = robocorp.action_server.cli:main']}

setup_kwargs = {
    'name': 'robocorp-action-server',
    'version': '0.2.1',
    'description': 'Robocorp local task server',
    'long_description': '# robocorp-action-server\n\n[Robocorp Action Server](https://github.com/robocorp/robocorp#readme) is a Python framework designed to simplify the deployment of actions (AI or otherwise).\n\nAn `action` in this case is defined as a Python function (which has inputs/outputs defined), which is served by the `Robocorp Action Server`.\n\nThe `Robocorp Action Server` automatically generates an OpenAPI spec for your Python code, enabling different AI/LLM Agents to understand and call your Action. It also manages the Action lifecycle and provides full traceability of what happened during runs.\n\n## 1. Install Action Server\n\nAction Server is available as a stand-alone fully signed executable and via `pip install robocorp-action-server`.\n> We recommend the executable to prevent confusion in case you have multiple/crowded Python environments, etc.\n\n#### For macOS\n\n```sh\n# Install Robocorp Action Server\nbrew update\nbrew install robocorp/tools/action-server \n```\n\n#### For Windows\n\n```sh\n# Download Robocorp Action Server\ncurl -o action-server.exe https://downloads.robocorp.com/action-server/releases/latest/windows64/action-server.exe\n\n# Add to PATH or move to a folder that is in PATH\nsetx PATH=%PATH%;%CD%\n```\n\n#### For Linux\n\n```sh\n# Download Robocorp Action Server\ncurl -o action-server https://downloads.robocorp.com/action-server/releases/latest/linux64/action-server\nchmod a+x action-server\n\n# Add to PATH or move to a folder that is in PATH\nsudo mv action-server /usr/local/bin/\n```\n\n## 2. Run your first Action\n\n```sh\n# Bootstrap a new project using this template.\n# You\'ll be prompted for the name of the project (directory):\naction-server new\n\n# Start Action Server \ncd my-project\naction-server start --expose\n```\n\n👉 You should now have an Action Server running locally at: [http://localhost:8080](http://localhost:8080), so open that in your browser and the web UI will guide you further.\n\n👉 Using the `--expose` -flag, you also get a public internet-facing URL (something like "https://twently-cuddly-dinosaurs.robocorp.link") and the related token. These are the details that you need to configure your AI Agent to have access to your Action\n\n## What do you need in your Action Package\n\nAn `Action Package` is currently defined as a local folder that contains at least one Python file containing an action entry point (a Python function marked with `@action` -decorator from `robocorp.actions`).\n\nThe `package.yaml` file is required for specifying the Python environment and dependencies for your Action ([RCC](https://github.com/robocorp/rcc/) will be used to automatically bootstrap it and keep it updated given the `package.yaml` contents).\n\n> Note: the `package.yaml` is optional if the action server is not being used as a standalone (i.e.: if it was pip-installed it can use the same python environment where it\'s installed).\n\n### Bootstrapping a new Action\n\nStart new projects with:\n\n`action-server new`\n\nNote: the `action-server` executable should be automatically added to your python installation after `pip install robocorp-action-server`, but if for some reason it wasn\'t pip-installed, it\'s also possible to use `python -m robocorp.action_server` instead of `action-server`.\n\nAfter creating the project, it\'s possible to serve the actions under the current directory with:\n\n`action-server start`\n\nFor example: When running `action-server start`, the action server will scan for existing actions under the current directory, and it\'ll start serving those.\n\nAfter it\'s started, it\'s possible to access the following URLs:\n\n- `/index.html`: UI for the Action Server.\n- `/openapi.json`: Provides the openapi spec for the action server.\n- `/docs`: Provides access to the APIs available in the server and a UI to test it.\n\n## Documentation\n\nExplore our [docs](https://github.com/robocorp/robocorp/tree/master/action_server/docs) for extensive documentation.\n\n## Changelog\n\nA list of releases and corresponding changes can be found in the [changelog](https://github.com/robocorp/robocorp/blob/master/action_server/docs/CHANGELOG.md).\n',
    'author': 'Fabio Z.',
    'author_email': 'fabio@robocorp.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/robocorp/robocorp/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
