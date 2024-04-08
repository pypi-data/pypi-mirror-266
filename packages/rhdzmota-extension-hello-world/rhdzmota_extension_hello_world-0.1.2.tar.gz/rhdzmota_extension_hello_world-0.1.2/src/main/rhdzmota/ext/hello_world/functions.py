from typing import Optional

from rhdzmota.ext.hello_world.enums import Salutation
from rhdzmota.ext.hello_world.settings import Environ


def hello(
        recipient: Optional[str] = None,
        salutation: Optional[Salutation] = None
) -> str:
    recipient = recipient or Environ.EXT_HELLO_WORLD_DEFAULT_RECIPIENT.value
    salutation = salutation or Salutation.STANDARD
    return f"{salutation.value}, {recipient}!"
