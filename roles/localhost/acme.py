from pyinfra import host
from pyinfra.operations import git

from globals import repos_dir


def apply():
    git.repo(
        name="Ensure acme.sh repository is current",
        src=host.data.acme_repo_url,
        dest=str(repos_dir / "acme.sh"),
        branch="master",
        pull=True,
        force=True,
    )
