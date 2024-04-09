# -*- coding: utf-8 -*-
from pathlib import Path
from setuptools import find_packages, setup
import os
from datetime import datetime

if os.path.exists('./.env'):
    from dotenv import load_dotenv
    load_dotenv()

version = '1.0.18'

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')


REQUIREMENTS_FILE = os.environ.get('REQUIREMENTS_FILE', 'requirements.txt')
with open((this_directory / REQUIREMENTS_FILE)) as f:
    requirements = f.read().splitlines()

cli_build_module = f'''
def print_cli_build_info() -> str:
    return f'cli_build: "{os.environ.get('BUILD_JOB_ID', '??')}", cli_version: "{version}", released_on="{datetime.now().isoformat()}")'
'''

directory = os.path.join('chkp_harmony_endpoint_management_cli', 'generated')
if not os.path.exists(directory):
    os.makedirs(directory)

with open(os.path.join(directory, 'build_info.py'), 'w', encoding='utf-8') as file:
    file.write(cli_build_module)
with open(os.path.join(directory, '__init__.py'), 'w', encoding='utf-8') as file:
    file.write('')

package_data = {'': ['*']}

setup_kwargs = {
    'name': "chkp-harmony-endpoint-management-cli",
    'version': version,
    'keywords': 'harmony, endpoint, cli, checkpoint',
    'license': 'MIT',
    'description': 'Harmony Endpoint Official CLI',
    'long_description': long_description,
    'long_description_content_type': "text/markdown",
    'author': 'Haim Kastner',
    'author_email': 'haimk@checkpoint.com',
    'maintainer': 'Haim Kastner',
    'maintainer_email': 'haimk@checkpoint.com',
    'url': 'https://github.com/CheckPointSW/harmony-endpoint-management-cli',
    'packages': find_packages(exclude=['tests']),
    'package_data': package_data,
    'data_files': [('', ['requirements.txt'])],
    'install_requires': requirements,
    'python_requires': '>=3.8,<4.0',
    'entry_points': {
        'console_scripts': [
            'chkp_harmony_endpoint_management_cli=chkp_harmony_endpoint_management_cli.index:main_function',
        ],
    },
}

setup(**setup_kwargs)

