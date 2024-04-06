"""Don't import this module directly."""

from typing import Optional, overload

from .. import spec
from .mod import Mod
from .repository import Repository


class RepositoryPool:
    """A pool of repositories."""

    repositories: dict[str, Repository]
    """The repositories in the pool."""

    def __init__(self):
        self.repositories = {}

    @overload
    def add_repository(self, address: str):
        """Adds a repository to the pool by providing the address."""

    @overload
    def add_repository(self, repo: spec.RRepository):
        """Adds a repository to the pool that has already been fetched."""

    @overload
    def add_repository(self, repo: Repository):
        """Adds a repository to the pool."""

    @overload
    def add_repository(self, data: dict[str, str]):
        """Adds a repository to the pool."""

    def add_repository(self, repo):
        """Above"""
        if isinstance(repo, str):
            repo = Repository(repo)
        if isinstance(repo, dict):
            repo = spec.RRepository.from_dict(repo)
        if isinstance(repo, spec.RRepository):
            repo = Repository(None, repo)
        self.repositories[repo.root_id] = repo

    def get_repository(self, root_id: str) -> Repository:
        """Gets a repository by its root ID."""
        return self.repositories[root_id]

    def get_mod(self, id_: str) -> Optional[Mod]:
        """Gets a mod by its ID."""
        for repo in self.repositories.values():
            mod = repo.get_mod(id_)
            if mod is not None:
                return mod
        return None

    def has_mod(self, id_: str) -> bool:
        """Checks if a mod exists in the pool."""
        return self.get_mod(id_) is not None

    def where_is(self, id_: str) -> Optional[Repository]:
        """Gets the repository that contains the mod."""
        for repo in self.repositories.values():
            if repo.has_mod(id_):
                return repo
        return None

    def update_repositories(self):
        """Updates all repositories in the pool."""
        for repo in self.repositories.values():
            repo.update()

    def __getitem__(self, key: str) -> Repository:
        return self.get_repository(key)


@overload
def make_pool(repos: list[Repository]) -> RepositoryPool:
    """Creates a repository pool from a list of repositories."""


@overload
def make_pool(*repos: Repository) -> RepositoryPool:
    """Creates a repository pool from multiple repositories."""


def make_pool(*repos):
    """Above"""
    if len(repos) == 1 and isinstance(repos[0], list):
        repos = repos[0]
    pool = RepositoryPool()
    for repo in repos:
        if not isinstance(repo, Repository):
            raise TypeError("Invalid repository", repo)
        pool.add_repository(repo)
    return pool
