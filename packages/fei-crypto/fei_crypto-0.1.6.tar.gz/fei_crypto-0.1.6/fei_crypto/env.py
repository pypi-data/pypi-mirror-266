import os


def env(env_name: str) -> str:
    return os.getenv(env_name)
