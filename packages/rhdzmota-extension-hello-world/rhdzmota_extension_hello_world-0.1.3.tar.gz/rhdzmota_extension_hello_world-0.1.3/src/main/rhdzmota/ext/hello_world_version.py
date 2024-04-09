import os

from rhdzmota.version import Version


version = Version.from_path(
    name="hello_world_version",
    dirpath=os.path.dirname(__file__),
)
