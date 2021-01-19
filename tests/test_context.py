import pytest
from hamcrest import assert_that, has_entries, instance_of, is_
from rchat.cli import Context

URL = "https://localhost:9999"
USER = "user"
PASS = "pass"
USER_ID = "user-id"
TOKEN = "token"


class TestContext:
    def test_it_should_require_an_url(self):
        with pytest.raises(ValueError):
            Context(url="")

    def test_it_should_require_token_credentials(self):
        ctx = Context(url=URL, user="", password="", user_id="", token="")

        with pytest.raises(ValueError):
            ctx.credentials

    def test_it_should_prefer_token_credentials(self):
        ctx = Context(
            url=URL, user=USER, password=PASS, user_id=USER_ID, token=TOKEN
        )

        assert_that(
            ctx.credentials, has_entries(user_id=USER_ID, auth_token=TOKEN)
        )

    def test_it_should_take_user_credentials(self):
        ctx = Context.build(dict(url=URL, user=USER, password=PASS))

        assert_that(ctx.credentials, has_entries(user=USER, password=PASS))

    def test_it_should_not_fail_with_invalid_fields(self):
        ctx = Context.build(
            dict(url=URL, user=USER, password=PASS, unkown="💩")
        )

        assert_that(ctx, is_(instance_of(Context)))
