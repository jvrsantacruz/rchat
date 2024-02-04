from dataclasses import dataclass, field, fields
from functools import cached_property
from typing import Any

import requests
from rocketchat_API.rocketchat import RocketChat

from rchat.exc import Error


@dataclass
class Context:
    url: str | None = field(default=None)
    user: str | None = field(default=None)
    password: str | None = field(default=None)
    user_id: str | None = field(default=None)
    token: str | None = field(default=None)
    aliases: dict[str, str] | None = field(default_factory=dict)

    @classmethod
    def build(cls, config: dict[str, Any]):
        known_fields = {f.name for f in fields(cls)}
        if invalid_fields := set(config) - known_fields:
            print(f"WARNING: ignoring unknown config fields {invalid_fields}")
        return cls(**{f: config[f] for f in set(config) & known_fields})

    def __post_init__(self):
        if not self.url:
            raise ValueError(
                "Missing RocketChat server url for connection. "
                "Use --url or set the RCHAT_URL envvar."
            )

    @cached_property
    def api(self) -> RocketChat:
        if not self.url:
            raise Error("Missing url")
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
