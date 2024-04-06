"""Don't import this module directly."""

from .. import spec
from .dependency import Dependency


class Mod:
    """This class represents a mod.

    Raises:
        ValueError: If the data is not of type spec.RMod
    """

    meta: spec.RMod
    """The raw data of the mod."""

    def __init__(self, data: spec.RMod):
        self.meta = data
        if not isinstance(self.meta, spec.RMod):
            raise ValueError("Invalid data type")

    @property
    def original_ext(self) -> dict:
        """This holds the original mod.ext data."""
        return self.meta.ext.to_dict()

    @property
    def id(self) -> str:
        """The ID of the mod."""
        return self.meta.id

    @property
    def depends(self) -> list[Dependency]:
        """The dependencies of the mod."""
        return [Dependency(dep) for dep in self.meta.deps]

    @property
    def suggests(self) -> list[Dependency]:
        """The suggestions of the mod."""
        if self.meta.ext.suggests is not None:
            return [Dependency(dep) for dep in self.meta.ext.suggests]
