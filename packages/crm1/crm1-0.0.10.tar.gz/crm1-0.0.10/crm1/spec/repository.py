"""Don't import this module directly."""

from dataclasses import dataclass


from .mod import RMod
from dataclasses_hjson import DataClassHjsonMixin


@dataclass
class RRepository(DataClassHjsonMixin):
    """Raw repository data. This is used for deserialization."""

    spec_version: int
    """The version of the repository specification."""
    last_updated: int
    """The timestamp of the last update of the repository."""
    root_id: str
    """The root ID of the repository."""
    mods: list[RMod]
    """A list of mods in the repository."""
