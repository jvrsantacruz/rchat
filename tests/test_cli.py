from typing import List, Optional, Dict, Tuple, Union
from unittest.mock import patch, PropertyMock, Mock

import pytest
from click.testing import CliRunner
from hamcrest import (
    assert_that,
    has_entries,
    is_,
    starts_with,
    contains_string,
    all_of,
)
from rocketchat_API.rocketchat import RocketChat

from rchat.cli import cli

URL = "https://localhost:9999"
USER = "user"
PASS = "pass"
USER_ID = "user-id"
TOKEN = "token"
PERSON = "user.name"
CHANNEL = "#channel"
OPTIONS = {
    "url": dict(long="--url", default=URL, base=True),
    "user": dict(long="--user", default=USER, base=True),
    "user_id": dict(long="--user_id", default=USER_ID, base=True),
    "password": dict(long="--password", default=PASS, base=True),
    "token": dict(long="--token", default=TOKEN, base=True),
    "to": dict(long="--to", default=CHANNEL, base=False),
}


class default:
    """Placeholder for default value"""


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
        command = list(command)
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

    def test_it_should_validate_there_is_an_url_on_usage(self):
        result = self.run("send")

        assert_that(
            result.output, contains_string("Missing RocketChat server url")
        )
        assert_that(result.exit_code, is_(2))


class TestCliSend(Base):
    def test_it_should_validate_at_least_one_recipient(self):
        result = self.run("send", url=default)

        assert_that(
            result.output,
            all_of(
                contains_string("Missing option"), contains_string("'--to'"),
            ),
        )
        assert_that(result.exit_code, is_(2))

    def test_it_should_validate_at_least_one_message(self):
        result = self.run("send", url=default, to=default)

        assert_that(result.output, contains_string("Message cannot be empty"))
        assert_that(result.exit_code, is_(2))

    def test_it_should_send_messages_to_channels(self):
        message = "Hello World!"
        api = Mock(RocketChat)

        with patch("rchat.cli.Context.api", new_callable=PropertyMock) as mock:
            mock.return_value = api
            result = self.run("send", message, to=default, url=default)

        api.chat_post_message.assert_called_with(message, channel=CHANNEL)
        assert_that(result.exit_code, is_(0))

    def test_it_should_get_input_from_stdin(self):
        message = "Hello World!"
        api = Mock(RocketChat)

        with patch("rchat.cli.Context.api", new_callable=PropertyMock) as mock:
            mock.return_value = api
            result = self.run("send", to=default, url=default, input=message)

        api.chat_post_message.assert_called_with(message, channel=CHANNEL)
        assert_that(result.exit_code, is_(0))
