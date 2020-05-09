from typing import Optional
from dataclasses import dataclass, field

import click
import requests
from cached_property import cached_property
from rocketchat_API.rocketchat import RocketChat


@click.group(context_settings=dict(auto_envvar_prefix='RCHAT'))
@click.option('--user', help='Username in RocketChat')
@click.option('--user-id', help='User id associated to a Token')
@click.option('--token', help='Personal Acces Token Name')
@click.option('--password', help='Password for user in RocketChat')
@click.option('--url', help='Url to the RocketChat server')
@click.version_option()
@click.pass_context
def cli(ctx, **kwargs):
    """Simple RocketChat command line client"""
    ctx.obj = Context(**kwargs)


@cli.command()
@click.option(
    '-t', '--to', required=True, help='Username or channel to chat to'
)
@click.argument('message', required=False)
@click.pass_context
def send(ctx, to, message):
    """Send messages to users or channels"""
    ctx.obj.api.chat_post_message(message, channel=to.strip('#'))


@dataclass
class Context:
    url: str = field()
    user: Optional[str] = field(default=None)
    password: Optional[str] = field(default=None)
    user_id: Optional[str] = field(default=None)
    token: Optional[str] = field(default=None)

    @cached_property
    def api(self) -> RocketChat:
        if not self.url:
            raise ValueError(
                'Missing RocketChat server url for connection. '
                'Use --url or set the RCHAT_URL envvar.'
            )

        return RocketChat(
            session=self.session,
            server_url=self.url,
            **self.credentials
        )

    @cached_property
    def session(self):
        return requests.Session()

    @property
    def credentials(self) -> dict:
        if self.user_id and self.token:
            return {'user_id': self.user_id, 'auth_token': self.token}
        elif self.user and self.password:
            return {'user': self.user, 'password': self.password}

        raise ValueError(
            'Missing authentication info. Either use user-id and token '
            'or user and pasword to provide your info.'
        )
