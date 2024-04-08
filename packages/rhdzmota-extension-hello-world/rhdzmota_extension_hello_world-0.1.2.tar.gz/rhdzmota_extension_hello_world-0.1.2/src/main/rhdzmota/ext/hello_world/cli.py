from typing import Optional

from rhdzmota.interface.cli import CLIBase
from rhdzmota.ext.hello_world.functions import hello
from rhdzmota.ext.hello_world.enums import Salutation


class CLI(CLIBase):

    def hello(
            self,
            recipient: Optional[str] = None,
            salutation: Optional[str] = None,
    ) -> str:
        if salutation:
            salutation = Salutation[salutation.upper()]
        return hello(recipient=recipient, salutation=salutation)
