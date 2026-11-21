from pathlib import Path

from pyinfra.operations import files

from globals import files_dir as shared_files_dir
from globals import repos_dir

acme_repo_dir = repos_dir / "acme.sh"
files_dir = Path(__file__).parent / "files"


def apply():
    certificate_files = [
        (acme_repo_dir / "acme.sh", "/config/acme.sh"),
        (files_dir / "issue-certificate.sh", "/config/issue-certificate.sh"),
        (files_dir / "renew-certificate.sh", "/config/renew-certificate.sh"),
        (shared_files_dir / "house-ca.crt", "/config/house-ca.crt"),
    ]

    for src, dest in certificate_files:
        files.put(name=f"Copy {Path(src).name} to {dest}", src=str(src), dest=str(dest))
