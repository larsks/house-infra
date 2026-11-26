import subprocess

from pyinfra import host
from pyinfra.operations import git, server

from globals import repos_dir, src_dir

acme_repo_dir = repos_dir / "acme.sh"
update_ddns_record_dir = src_dir / "update-ddns-record"

git.repo(
    name="Ensure acme.sh repository is current",
    src=host.data.acme_repo_url,
    dest=str(acme_repo_dir),
    branch="master",
    pull=True,
    force=True,
)

needs_build = (
    subprocess.run(
        ["make", "-q", "function.zip"], cwd=update_ddns_record_dir, check=False
    ).returncode
    != 0
)

if needs_build:
    server.shell(
        name="Build update-ddns-record Lambda function.zip",
        commands=["make function.zip"],
        _chdir=str(update_ddns_record_dir),
    )
