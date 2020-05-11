# rchat
![build](https://github.com/jvrsantacruz/rchat/workflows/Python%20package/badge.svg?branch=master) 
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

A simple RocketChat command line client

    rchat --to #team "Hello World!"

## Command line

rchat comes with a command line interface. See help for more information:

See `rchat --help`

## Development

From the root of the application directory, create a python environment,
install the application in development mode along with its dependencies and
run it locally:

    virtualenv env
    . env/bin/activate
    pip install --upgrade pip
    pip install -e . -r requirements.txt -r dev-requirements.txt

Tests can be run using *tox* (recommended):

    pip install tox
    tox

Or directly by calling *py.test*:

    python -m pytest

## TODO

- Send private messages
- Send message from files
- Send message from stdin
- Upload files
- Upload images
- Read messages
- Listen to new messages
- Autocomplete emojis
- Autocomplete users
- Autocomplete channels
- Config file
- Logging and debug
- Debian Packaging
- Bundled Packaging
- Pypi version
- Versioning script
- Improve startup time
- Define groups of users
- Allow to get reactions
- Allow for threads
- Implement (pre|post) message hooks
- Implement (pre|post) reaction hooks
- Autocomplete names
- Autocomplete channels
- Open editor to compose message
- Preview message in markdown viewer
- Autoformat input as verbatim
