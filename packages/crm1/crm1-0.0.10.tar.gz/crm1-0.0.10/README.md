# ``crm1`` Python package

This package is a Python implementation of the CRM-1 specification.

You can find the specification [here](https://github.com/CRModders/CRM-1/).

## Installation

You can install the package using pip:

```bash
pip install crm1
```

## Usage

```python
"""Usage example for the crm1 module."""

from crm1 import Repository, RepositoryPool, autorepo, make_pool

# You can get a repository from a URL
repo1 = Repository("https://crm-repo.jojojux.de/repo.json")
repo2 = "https://repo.crmodders.dev/repository.hjson"

# Now we create a pool and add the repositories to it
pool = RepositoryPool()
pool.add_repository(repo1)
# The RepositoryPool class can also take a string, a RRepository or a dict as a repository, it will automatically create a Repository object
# A RRRepository is a dataclass that holds the raw data of a repository
pool.add_repository(repo2)

# You could also use the autorepo module to get all repositories known to the Autorepo at https://crm-repo.jojojux.de/repo_mapping.json
repos = autorepo.get_all_repos()
# You can also use the make_pool function to create a pool from a list of repositories
pool2 = make_pool(repos)

# Now we can get a mod from the pool
mod = pool.get_mod("dev.crmodders.flux")
print(mod.meta.name)  # This will print "Flux API", the mods name

print(mod.meta.ext.changelog) # The mod.meta.ext attribute holds the CommonModExt object, which add typing and docs to commonly used fileds the mod.ext dict.
# The unknown fields are stored in the mod.meta.ext.others attribute, which is a dict.
# If you want to get the original mod.ext dict, you can use mod.original_ext.

# Now we load a different mod
mod2 = pool.get_mod("com.nikrasoff.seamlessportals")

# We can now iterate over the dependencies of the mod
for dep in mod2.depends:
    dep.id = "dev.crmodders.flux"  # Ignore this line, this is required because the de.jojojux.crm-repo repository has a bug, see https://github.com/J0J0HA/CRM-1-Autorepo/issues/6
    print(dep.mod)  # This will print None, because the dependency was not yet resolved
    # We can resolve the dependency by calling the resolve method and providing a repository or a pool to search in
    print(
        dep.resolve(pool)
    )  # This will print the mod object, as it is returned by the resolve method, but is also stored in the dependency object at dep.mod
    # We can now access the mod object from the dependency object
    print(
        dep.mod.meta.name
    )  # This will print the name of the mod, in this case "Flux API". If the dependency could not be resolved, the dep.mod attribute will still be None

```

Everything is typed and documented, so you can use your IDE's autocomplete and documentation features to explore the functionality of the package.

## Helpers

### Versions

The ```helpers.versions``` module provides classes to work with versions and version ranges.

```python
from crm1.helpers.versions import Version, VersionRange, range_from_maven_string


range1 = VersionRange.from_string("[1.0,2.0.1)")
print(range1.lower, range1.lower_mode)
# 1.0.0 VersionEndMode.INCLUSIVE
print(range1.upper, range1.upper_mode)
# 2.0.1 VersionEndMode.EXCLUSIVE

range2 = VersionRange.from_string("(1.0,]")
print(range2.lower, range2.lower_mode)
# 1.0.0 VersionEndMode.EXCLUSIVE
print(range2.upper, range2.upper_mode)
# None VersionEndMode.INCLUSIVE

vers1 = Version.from_string("1.0")
vers2 = Version.from_string("2.0.1")
vers3 = Version.from_string("20.1")

print(vers1 in range1)
# True
print(vers2 in range1)
# False
print(vers3 in range1)
# False
print(vers1 in range2)
# False
print(vers2 in range2)
# True
print(vers3 in range2)
# True


print(str(range_from_maven_string(">=1.0")))
# [1.0.0,)
print(str(range_from_maven_string(">1.0")))
# (1.0.0,)
print(str(range_from_maven_string("<1.0")))
# (,1.0.0)
print(str(range_from_maven_string("<=1.0")))
# (,1.0.0]
print(str(range_from_maven_string("1.0")))
# 1.0.0
print(str(range_from_maven_string("*")))
# (,)
```

## License

This package is licensed under the MIT license. You can find the full license text in the [LICENSE](LICENSE) file.
