from pyinfra import host
from pyinfra.operations import git


def apply():
    git.repo(
        name="Ensure secrets repository is current",
        src=host.data.secrets_repo_url,
        dest="secrets",
        branch="main",
        pull=True,
        force=True,
    )
