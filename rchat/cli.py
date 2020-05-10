"""Simplistic rocket chat command line client"""
import logging
import functools
from typing import Optional
from dataclasses import dataclass, field

import click
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

    return handler


@click.group("rchat", context_settings=dict(auto_envvar_prefix="RCHAT"))
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
        ctx.obj = Context(**kwargs)
    except ValueError as error:
        raise click.BadParameter(str(error)) from error


@cli.command()
@click.option(
    "-t", "--to", required=True, help="Username or channel to chat to"
)
@click.argument("message", required=False)
@click.pass_context
@error_handling
def send(ctx, to, message):
    """Send messages to @users or #channels"""
    if not message:
        stdin = click.get_text_stream("stdin")
        if not message and not stdin.isatty():
            message = stdin.read().strip()

    if not message:
        raise click.BadArgumentUsage("Message cannot be empty")

    ctx.obj.api.chat_post_message(message, channel=to)


@dataclass
class Context:
    url: str = field()
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
