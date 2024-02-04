from typing import Any

import confight

from rchat.exc import Error


def get_config(overrides: dict[str, Any]) -> dict[str, Any]:
    """Read the config and merge with cli options"""
    overrides = {k: v for k, v in overrides.items() if v is not None}
    config_path = overrides.pop("config", None)
    try:
        if config_path:
            config = confight.load_paths([config_path])
        else:
            config = confight.load_user_app("rchat")
    except Error as error:  # pylint: disable=broad-except
        raise Error(
            f"Could not load config ({config_path}): {error}"
        ) from error

    config = config.get("rchat") or {}
    config.update(**overrides)
    return config
