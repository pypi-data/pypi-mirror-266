"""env.py."""
import os
from typing import Optional

from strangeworks.core.config.base import DEFAULT_PROFILE_NAME, ConfigSource
from strangeworks.core.utils import is_empty_str


class EnvConfig(ConfigSource):
    """Obtain configuration from environment variables.

    Environment variables are expected to be in the following format:
        STRANGEWORKS_CONFIG_{profile}_{key}
    where `profile` and `key` are non-empty strings in uppercase
    letters.
    """

    def get(self, key: str, profile: str = DEFAULT_PROFILE_NAME) -> Optional[str]:
        """Retrieve the values from environment variables.

        The method will convert all lowercase key or profile values to uppercase.
        """
        if is_empty_str(key) or is_empty_str(profile):
            return None

        env_var = EnvConfig._get_envvar_name(key=key, profile=profile)
        return os.getenv(env_var)

    def set(
        self, profile: str = DEFAULT_PROFILE_NAME, overwrite: bool = False, **params
    ):
        """Set method for environment variables.

        Existing environment variables will be updated only if overwrite is set
        to True.
        """
        for key, val in params.items():
            envvar_name = EnvConfig._get_envvar_name(key=key, profile=profile)
            # overwrite existing envvars only if overwrite is True.
            if envvar_name not in os.environ or overwrite:
                os.environ[envvar_name] = val

    @staticmethod
    def _get_envvar_name(key: str, profile: str = DEFAULT_PROFILE_NAME):
        return f"STRANGEWORKS_CONFIG_{profile.upper()}_{key.upper()}"
