# Run with `--chdir local` so that pyinfra loads only local/group_data, not
# the main project's group data (which reads from the secrets repository
# this deploy is responsible for cloning). Paths are relative to local/.
from pyinfra import host
from pyinfra.operations import git

git.repo(
    name="Ensure secrets repository is current",
    src=host.data.secrets_repo_url,
    dest="../secrets",
    branch="main",
    pull=True,
    force=True,
)

git.repo(
    name="Ensure acme.sh repository is current",
    src=host.data.acme_repo_url,
    dest="../repos/acme.sh",
    branch="master",
    pull=True,
    force=True,
)
