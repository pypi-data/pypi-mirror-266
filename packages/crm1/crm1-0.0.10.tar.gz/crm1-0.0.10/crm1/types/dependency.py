"""Don't import this module directly."""

from typing import TYPE_CHECKING, Optional, overload

from .. import spec

if TYPE_CHECKING:
    from .mod import Mod
    from .repository import Repository
    from .repository_pool import RepositoryPool


class Dependency:
    """A mod dependency."""

    id: str
    """The ID of the mod."""
    version: str
    """The version of the mod."""
    source: Optional[str]
    """The repository rootId of the mod."""
    mod: Optional["Mod"] = None

    def __init__(self, meta: spec.RDependency):
        self.id = meta.id
        self.version = meta.version
        self.source = meta.source
        self.mod = None

    @overload
    def resolve(self, pool: "RepositoryPool") -> "Mod":
        """Resolves the dependency using the given pool."""

    @overload
    def resolve(self, repo: "Repository") -> "Mod":
        """Resolves the dependency using the given repository."""

    def resolve(self, repo=None):
        """Above"""
        self.mod = repo.get_mod(self.id)
        return self.mod
