# rchat
![build](https://github.com/jvrsantacruz/rchat/workflows/build/badge.svg)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

A simple RocketChat command line client

    rchat --to #team "Hello World!"

## Usage

_rchat_ comes with a command line interface that allows you to send messages
either to groups or direct people:

    rchat --to @rita.cantaora "Hi Rita!"

The message can also be piped into the program via stdin:

    echo "Hi!" | rchat --to #team

See help for more information:

See `rchat --help`.

## Configuration

_rchat_ needs to know at least the server url and user credentials to use the
API. Those parameters can be given via _command line option_, set using an
_envvar_ or by setting them in a _config file_.

Base configuration options can be taken from the command line.
Arguments given in the command line will override any other configuration.

    --user TEXT      Username in RocketChat
    --user-id TEXT   User id associated to a Token
    --token TEXT     Personal Acces Token Name
    --password TEXT  Password for user in RocketChat
    --url TEXT       Url to the RocketChat server

They can also be set as a environment variable by prefixing them such as
`RCHAT_URL`. Arguments set this way will take precedence over the ones in the
config file.

To configure via file, place your parameters in [toml][] format at
`~/.config/rchat/config.toml`:

```toml
[rchat]
user_id = 'a1d3f4dd..'
token = 'fjXkkf..'
url = 'https://rocketchat.myserver.net'
```

A specific config file can be given by passing the `--config` option or setting
the `RCHAT_CONFIG` envvar.

Extra config files can be placed in the `conf.d` directory and all of them will
be merged together using [confight](https://github.com/avature/confight). Last
values found in these files will override the previous ones, so the complete
list of places to be searched, in the order that will be read are:

- `/etc/rchat/config.toml`
- `/etc/rchat/conf.d/*`
- `~/.config/rchat/config.toml`
- `~/.config/rchat/conf.d`

Meaning that the keys in files placed at `~/.config/rchat/conf.d` will override
the rest.

[toml]: https://github.com/toml-lang/toml

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

- [X] Send private messages
- [X] Send message from stdin
- [X] Send message from files
- [ ] Upload files
- [ ] Upload images
- [ ] Read messages
- [ ] Listen to new messages
- [ ] Autocomplete emojis
- [ ] Autocomplete users
- [ ] Autocomplete channels
- [ ] Config file
- [ ] Logging and debug
- [ ] Debian Packaging
- [ ] Bundled Packaging
- [ ] Pypi version
- [ ] Versioning script
- [ ] Improve startup time
- [ ] Define groups of users
- [ ] Allow to get reactions
- [ ] Allow for threads
- [ ] Implement (pre|post) message hooks
- [ ] Implement (pre|post) reaction hooks
- [ ] Autocomplete names
- [ ] Autocomplete channels
- [ ] Open editor to compose message
- [ ] Preview message in markdown viewer
- [ ] Autoformat input as verbatim
