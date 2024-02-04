"""Simplistic rocket chat command line client"""
import logging
import sys
from functools import wraps
from typing import TYPE_CHECKING

import click

from rchat.config import get_config
from rchat.context import Context

if TYPE_CHECKING:
    from rocketchat_API.rocketchat import RocketChat


def error_handling(function):
    """Handle errors for click commands"""

    @wraps(function)
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


@click.group("rchat", context_settings={"auto_envvar_prefix": "RCHAT"})
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
        ctx.obj = get_context(kwargs)
    except ValueError as error:
        raise click.BadParameter(str(error)) from error


def get_context(kwargs):
    return Context.build(get_config(kwargs))


def resolve_alias(to: str, aliases: dict[str, str]) -> str:
    return str(aliases.get(to) or to)


@cli.command()
@click.option(
    "-t", "--to", required=True, help="Username or channel to chat to"
)
@click.option(
    "-F", "--from-file", type=click.File(), help="Path to file to send"
)
@click.option(
    "--code",
    is_flag=True,
    help="Present message as code wrapped in markdown triple backticks",
)
@click.option(
    "--lang",
    help="Combine with --code to set a specific highlighting scheme. "
    "eg: 'python'",
)
@click.argument("message", required=False)
@click.pass_context
@error_handling
def send(ctx, to, message, from_file, code: bool | None, lang: str | None):
    """Send messages to @users or #channels"""
    if from_file:
        message = from_file.read()
    elif not message:
        stdin = click.get_text_stream("stdin")
        if not message and not stdin.isatty():
            message = stdin.read().strip()

    if not message:
        raise click.BadArgumentUsage("Message cannot be empty")

    if code:
        prefix = f"{lang}\n" if lang else ""
        message = f"```{prefix}{message}```"

    ctx.obj.api.chat_post_message(
        message, channel=resolve_alias(to, ctx.obj.aliases)
    )
