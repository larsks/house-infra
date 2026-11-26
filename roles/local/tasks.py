from pyinfra import host
from pyinfra.operations import git

from globals import repos_dir

acme_repo_dir = repos_dir / "acme.sh"

git.repo(
    name="Ensure acme.sh repository is current",
    src=host.data.acme_repo_url,
    dest=str(acme_repo_dir),
    branch="master",
    pull=True,
    force=True,
)
