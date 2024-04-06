"""Don't import this module directly."""

from dataclasses import dataclass
from typing import Optional


from dataclasses_hjson import DataClassHjsonMixin


@dataclass
class RDependency(DataClassHjsonMixin):
    """Raw dependency data. This is used for deserialization."""

    id: str
    """The ID of the mod."""
    version: str
    """The version of the mod."""
    source: Optional[str]
    """The repository rootId of the mod."""
