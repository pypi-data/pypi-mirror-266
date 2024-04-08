from types import SimpleNamespace

# We cannot use Enum here because `mypy` doesn't like it when we format those routes
# into strings. https://github.com/python/mypy/issues/15269
Routes = SimpleNamespace(
    healthcheck="healthcheck",
    username_login="login",
    api_key_login="login/api_key",
    get_token="get-token",
    current_user="current_user",
)
