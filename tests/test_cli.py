import os
from typing import Dict, List, Tuple, Union
from unittest.mock import ANY, Mock, patch

import pytest
from click.testing import CliRunner
from hamcrest import all_of, assert_that, contains_string, is_, starts_with
from rocketchat_API.rocketchat import RocketChat

from rchat.cli import Context, cli

URL = "https://localhost:9999"
USER = "user"
PASS = "pass"
USER_ID = "user-id"
TOKEN = "token"
PERSON = "user.name"
CHANNEL = "#channel"
CONFIG = "./my-empty-config.toml"
FROM_FILE = "./my-empty-text-file"
OPTIONS = {
    "url": dict(long="--url", default=URL, base=True),
    "user": dict(long="--user", default=USER, base=True),
    "user_id": dict(long="--user_id", default=USER_ID, base=True),
    "password": dict(long="--password", default=PASS, base=True),
    "token": dict(long="--token", default=TOKEN, base=True),
    "config": dict(long="--config", default=CONFIG, base=True),
    "to": dict(long="--to", default=CHANNEL, base=False),
    "from_file": dict(long="--from-file", default=FROM_FILE, base=False),
}
FILE_CONTENTS = """
\t💩 file contents
"""


class default:
    """Placeholder for default value"""


@pytest.fixture()
def environ():
    previous = os.environ.copy()
    for key in previous:
        if key.startswith("RCHAT_"):
            os.environ.pop(key)

    yield previous
    os.environ.update(previous)


@pytest.fixture
def context():
    with patch("rchat.cli.Context") as context_type:
        context = Mock(Context)
        context.api = Mock(RocketChat)
        context_type.return_value = context
        yield context


class Base:
    def run(self, *args, **kwargs):
        runner = CliRunner()
        invoke_kwargs = {}
        invoke_kwargs.setdefault("input", kwargs.pop("input", None))
        return runner.invoke(
            cli, self.complete_command(args, kwargs), **invoke_kwargs
        )

    def complete_command(
        self, command: Tuple[str], options: Dict[str, Union[str, default]]
    ) -> List[str]:
        """Append default options"""
        command: List[str] = list(command)
        for key, value in options.items():
            meta = OPTIONS[key]
            if value is default:
                value = meta["default"]

            if meta["base"]:
                command.insert(0, value)
                command.insert(0, meta["long"])
            else:
                command.extend([meta["long"], value])

        return command


class TestCli(Base):
    def test_it_should_display_version(self):
        result = self.run("--version")

        assert_that(result.output, starts_with("rchat, version "))
        assert_that(result.exit_code, is_(0))

    def test_it_should_display_help(self):
        result = self.run("--help")

        assert_that(result.exit_code, is_(0))

    def test_it_should_validate_there_is_an_url_on_usage(self, environ):
        result = self.run("send", config=default)

        assert_that(
            result.output, contains_string("Missing RocketChat server url")
        )
        assert_that(result.exit_code, is_(2))

    @patch("rchat.cli.Context")
    def test_it_should_handle_uncontrolled_errors(self, context):
        context.side_effect = Exception("Boom!")

        result = self.run("send")

        assert_that(result.stdout, contains_string("Boom!"))
        assert_that(result.exit_code, is_(1))

    def test_it_should_read_config_from_file(self, environ, tmp_path):
        path = tmp_path / "config.toml"
        with path.open("w") as stream:
            stream.write(
                f"""
[rchat]
server = "{URL}"
user = "{USER}"
password = "{PASS}"
                         """
            )

        with patch("rchat.cli.Context") as context:
            result = self.run("send", "test", config=str(path), to=default,)

        context.assert_called_with(server=URL, password=PASS, user=USER)
        assert_that(result.exit_code, is_(0))


class TestCliSend(Base):
    def test_it_should_validate_at_least_one_recipient(self, environ):
        result = self.run("send", url=default)

        assert_that(
            result.output,
            all_of(
                contains_string("Missing option"), contains_string("'--to'"),
            ),
        )
        assert_that(result.exit_code, is_(2))

    def test_it_should_validate_at_least_one_message(self, environ):
        result = self.run("send", url=default, to=default)

        assert_that(result.output, contains_string("Message cannot be empty"))
        assert_that(result.exit_code, is_(2))

    def test_it_should_send_messages_to_channels(self, context, environ):
        message = "Hello World!"

        result = self.run("send", message, to=default, url=default)

        context.api.chat_post_message.assert_called_with(
            message, channel=CHANNEL
        )
        assert_that(result.exit_code, is_(0))

    def test_it_should_get_input_from_stdin(self, context, environ):
        message = "Hello World!"

        result = self.run("send", to=default, url=default, input=message)

        context.api.chat_post_message.assert_called_with(
            message, channel=CHANNEL
        )
        assert_that(result.exit_code, is_(0))

    def test_it_should_send_file_contents(self, context, tmp_path):
        path = tmp_path / FROM_FILE
        with path.open("w") as stream:
            stream.write(FILE_CONTENTS)

        result = self.run("send", to=default, url=default, from_file=path)

        context.api.chat_post_message.assert_called_with(
            FILE_CONTENTS, channel=CHANNEL
        )
        assert_that(result.exit_code, is_(0))
