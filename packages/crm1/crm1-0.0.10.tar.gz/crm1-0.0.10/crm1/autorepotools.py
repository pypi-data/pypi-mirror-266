"""Don't import this module directly."""

from .types import Repository
from .utils import get_request

AUTOREPO_URL = "https://crm-repo.jojojux.de"


def get_all_repos():
    """Fetches all known repositories from the autorepo server."""
    address = f"{AUTOREPO_URL}/repo_mapping.json"
    response = get_request(address)
    return [Repository(repo) for repo in response["repos"].values()]
