import os
import enum


class Environ(enum.Enum):
    EXT_HELLO_WORLD_DEFAULT_RECIPIENT = os.environ.get(
        "EXT_HELLO_WORLD_DEFAULT_RECIPIENT",
        default="World",
    )
