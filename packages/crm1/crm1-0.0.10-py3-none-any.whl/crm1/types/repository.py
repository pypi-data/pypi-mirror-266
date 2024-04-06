"""Don't import this module directly."""

from typing import Optional, overload

from .. import utils
from .mod import Mod
from .. import spec


class Repository:
    """A repository."""

    address: Optional[str]
    """The address of the repository."""
    data: spec.RRepository
    """The raw data of the repository."""

    @overload
    def __init__(self, address: Optional[str], data: spec.RRepository):
        """Initializes a repository with an address and data."""

    @overload
    def __init__(self, address: str):
        """Initializes a repository with an address. The data will be fetched."""

    @overload
    def __init__(self, address: Optional[str], data: dict):
        """Initializes a repository with an address and data.
        The data will be converted to a spec.RRepository."""

    def __init__(self, address, data=None):
        if isinstance(data, dict):
            data = spec.RRepository.from_dict(data)
        self.address = address
        self.data = data
        if data is None:
            self.update()
        if not isinstance(self.data, spec.RRepository):
            raise ValueError("Invalid data type")
        if self.data.spec_version != 1:
            raise ValueError("Unsupported spec version", self.data.spec_version)

    def get_mod(self, id_: str) -> Optional[Mod]:
        """Gets a mod by its ID."""
        for mod in self.data.mods:
            if mod.id == id_:
                return Mod(mod)
        return None

    def has_mod(self, id_: str) -> bool:
        """Checks if a mod exists in the repository."""
        return self.get_mod(id_) is not None

    @property
    def root_id(self) -> str:
        """The root ID of the repository."""
        return self.data.root_id

    def update(self):
        """Updates the repository data."""
        self.data = utils.fetch_repository(self.address)
