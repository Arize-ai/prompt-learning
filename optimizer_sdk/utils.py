import os
from typing import Optional
from pydantic import SecretStr


def get_key_value(env_name: str, key: Optional[str] = None) -> SecretStr:
    if key is None:
        if os.getenv(env_name) is None:
            raise ValueError(f"Environment variable {env_name} is not set")
        key = str(os.getenv(env_name))
    return SecretStr(key)
