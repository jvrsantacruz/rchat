import json
import os
from unittest.mock import ANY, Mock, patch

import pytest
from click.testing import CliRunner
from hamcrest import (all_of, assert_that, contains_string, has_properties,
                      is_, starts_with)
from rchat.cli import Context, cli
from rocketchat_API.rocketchat import RocketChat

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
    "to": dict(long="--to", default=CHANNEL),
    "from_file": dict(long="--from-file", default=FROM_FILE),
    "code": dict(long="--code", default=None, flag=True),
    "lang": dict(long="--lang", default=None),
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
def api():
    with patch("rchat.context.RocketChat") as api:
        yield api.return_value


@pytest.fixture
def context(api):
    with patch("rchat.cli.Context") as ctx:
        ctx.build.return_value.api = api
        yield ctx


@pytest.fixture
def config() -> dict:
    config_values = {"url": URL, "user_id": USER_ID, "token": TOKEN}
    with patch("rchat.cli.get_config") as get_config:
        get_config.return_value = config_values
        yield config_values


class Base:
    def run(self, *args, **kwargs):
        runner = CliRunner()
        invoke_kwargs = {}
        invoke_kwargs.setdefault("input", kwargs.pop("input", None))
        return runner.invoke(
            cli, self.complete_command(args, kwargs), **invoke_kwargs
        )

    def complete_command(
        self, command: tuple[str], options: dict[str, str | default]
    ) -> list[str]:
        """Append default options"""
        command: list[str] = list(command)
        for key, value in options.items():
            meta = OPTIONS.get(key)
            if meta is None:
                raise ValueError(f"Unknown option {key}")

            if value is default:
                value = meta["default"]

            if meta.get("base"):
                command.insert(0, value)
                command.insert(0, meta["long"])
            elif meta.get("flag"):
                command.append(meta["long"])
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

    def test_it_should_handle_uncontrolled_errors(self, context):
        context.build.side_effect = Exception("Boom!")

        result = self.run("send")

        assert_that(result.stdout, contains_string("Boom!"))
        assert_that(result.exit_code, is_(1))

    def test_it_should_read_config_from_file(self, environ, context, tmp_path):
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

        result = self.run("send", "test", config=str(path), to=default)

        context.build.assert_called_with(
            dict(server=URL, password=PASS, user=USER)
        )
        assert_that(result.exit_code, is_(0))


class TestCliSend(Base):
    def test_it_should_validate_at_least_one_recipient(self, config):
        result = self.run("send", url=default)

        assert_that(
            result.output,
            all_of(
                contains_string("Missing option"),
                contains_string("'--to'"),
            ),
        )
        assert_that(result.exit_code, is_(2))

    def test_it_should_validate_at_least_one_message(self, config):
        result = self.run("send", url=default, to=default)

        assert_that(result.output, contains_string("Message cannot be empty"))
        assert_that(result.exit_code, is_(2))

    def test_it_should_send_messages_to_channels(self, api, config):
        message = "Hello World!"

        result = self.run("send", message, to=default, url=default)

        api.chat_post_message.assert_called_with(message, channel=CHANNEL)
        assert_that(result.exit_code, is_(0))

    def test_it_should_get_input_from_stdin(self, api, config):
        message = "Hello World!"

        result = self.run("send", to=default, url=default, input=message)

        api.chat_post_message.assert_called_with(message, channel=CHANNEL)
        assert_that(result.exit_code, is_(0))

    def test_it_should_send_file_contents(self, api, config, tmp_path):
        path = tmp_path / FROM_FILE
        with path.open("w") as stream:
            stream.write(FILE_CONTENTS)

        result = self.run("send", to=default, url=default, from_file=path)

        api.chat_post_message.assert_called_with(
            FILE_CONTENTS, channel=CHANNEL
        )
        assert_that(result.exit_code, is_(0))

    def test_it_should_resolve_aliases(self, api, config):
        alias = "my-alias"
        real_name = "@my-long-name"
        message = "Hello!"
        config["aliases"] = {alias: real_name}

        result = self.run("send", message, to=alias)

        api.chat_post_message.assert_called_with(message, channel=real_name)
        assert_that(result.exit_code, is_(0))

    def test_it_should_present_messages_as_code(self, api, config):
        message = "Hello!\nWrapped!"

        result = self.run("send", message, to=default, code="true")

        assert_that(result, has_properties(exit_code=is_(0)))
        api.chat_post_message.assert_called_with(
            f"```{message}```", channel=CHANNEL
        )

    def test_it_should_add_lang_highlighting_to_code(self, api, config):
        message = "Hello!\nWrapped!"

        result = self.run(
            "send", message, to=default, code="true", lang="python"
        )

        assert_that(result, has_properties(exit_code=is_(0)))
        api.chat_post_message.assert_called_with(
            f"```python\n{message}```", channel=CHANNEL
        )
