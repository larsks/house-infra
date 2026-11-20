from pathlib import Path

from globals import files_dir as shared_files_dir
from globals import repos_dir
from lib.git import ensure_git_repo
from pyinfra.operations import files, python, server

acme_repo_url = "https://github.com/acmesh-official/acme.sh"
acme_repo_dir = repos_dir / "acme.sh"
files_dir = Path(__file__).parent / "files"


def apply():
    python.call(
        name="Ensure local checkout of acme.sh is current",
        function=ensure_git_repo,
        work_tree=acme_repo_dir,
        repo_url=acme_repo_url,
    )

    certificate_files = [
        (acme_repo_dir / "acme.sh", "/config/acme.sh"),
        (files_dir / "issue-certificate.sh", "/config/issue-certificate.sh"),
        (files_dir / "renew-certificate.sh", "/config/renew-certificate.sh"),
        (shared_files_dir / "house-ca.crt", "/config/house-ca.crt"),
    ]

    for src, dest in certificate_files:
        files.put(name=f"Copy {src} to {dest}", src=str(src), dest=str(dest))
