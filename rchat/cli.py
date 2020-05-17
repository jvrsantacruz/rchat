"""Simplistic rocket chat command line client"""
import functools
import logging
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import click
import confight
import requests
from cached_property import cached_property
from rocketchat_API.rocketchat import RocketChat


def error_handling(function):
    """Handle errors for click commands"""

    @functools.wraps(function)
    def handler(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except click.ClickException:
            raise  # let click handle those
        except Exception as error:  # pylint: disable=broad-except
            logging.exception(error)
            click.secho("Error: " + str(error), fg="red", err=True)
            sys.exit(1)

    return handler


@click.group("rchat", context_settings=dict(auto_envvar_prefix="RCHAT"))
@click.option(
    "--config", type=click.Path(dir_okay=False), help="Username in RocketChat"
)
@click.option("--user", help="Username in RocketChat")
@click.option("--user-id", help="User id associated to a Token")
@click.option("--token", help="Personal Acces Token Name")
@click.option("--password", help="Password for user in RocketChat")
@click.option("--url", help="Url to the RocketChat server")
@click.version_option()
@click.pass_context
@error_handling
def cli(ctx, **kwargs):
    """Simple RocketChat command line client"""
    try:
        ctx.obj = Context(**get_config(kwargs))
    except ValueError as error:
        raise click.BadParameter(str(error)) from error


def get_config(overrides: Dict[str, Any]) -> Dict[str, Any]:
    """Read the config and merge with cli options"""
    overrides = {k: v for k, v in overrides.items() if v is not None}
    config_path = overrides.pop("config", None)
    if config_path:
        config = confight.load_paths([config_path])
    else:
        config = confight.load_user_app("rchat")
    config = config.get("rchat") or {}
    config.update(**overrides)
    return config


@cli.command()
@click.option(
    "-t", "--to", required=True, help="Username or channel to chat to"
)
@click.option(
    "-F", "--from-file", type=click.File(), help="Path to file to send"
)
@click.argument("message", required=False)
@click.pass_context
@error_handling
def send(ctx, to, message, from_file):
    """Send messages to @users or #channels"""
    if from_file:
        message = from_file.read()
    elif not message:
        stdin = click.get_text_stream("stdin")
        if not message and not stdin.isatty():
            message = stdin.read().strip()

    if not message:
        raise click.BadArgumentUsage("Message cannot be empty")

    ctx.obj.api.chat_post_message(message, channel=to)


@dataclass
class Context:
    url: Optional[str] = field(default=None)
    user: Optional[str] = field(default=None)
    password: Optional[str] = field(default=None)
    user_id: Optional[str] = field(default=None)
    token: Optional[str] = field(default=None)

    def __post_init__(self):
        if not self.url:
            raise ValueError(
                "Missing RocketChat server url for connection. "
                "Use --url or set the RCHAT_URL envvar."
            )

    @cached_property
    def api(self) -> RocketChat:
        return RocketChat(
            session=self.session, server_url=self.url, **self.credentials
        )

    @cached_property
    def session(self):
        return requests.Session()

    @property
    def credentials(self) -> dict:
        if self.user_id and self.token:
            return {"user_id": self.user_id, "auth_token": self.token}
        if self.user and self.password:
            return {"user": self.user, "password": self.password}

        raise ValueError(
            "Missing authentication info. Either use user-id and token "
            "or user and pasword to provide your info."
        )
