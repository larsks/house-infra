from pathlib import Path

from pyinfra.operations import files

from globals import files_dir as shared_files_dir
from globals import repos_dir

acme_repo_dir = repos_dir / "acme.sh"
files_dir = Path(__file__).parent / "files"
keg_scripts_dir = Path("/volume1/scripts")


def apply():
    for dir, mode in [("deploy", "755"), ("data/acme", "750")]:
        files.directory(
            name=f"Ensure directory {dir} exists",
            path=str(keg_scripts_dir / dir),
            user="root",
            group="root",
            mode=mode,
            _sudo=True,
        )
    certificate_files = [
        (acme_repo_dir / "acme.sh", keg_scripts_dir / "acme.sh"),
        (
            acme_repo_dir / "deploy" / "synology_dsm.sh",
            keg_scripts_dir / "deploy" / "synology_dsm.sh",
        ),
        (files_dir / "issue-certificate.sh", keg_scripts_dir / "issue-certificate.sh"),
        (files_dir / "renew-certificate.sh", keg_scripts_dir / "renew-certificate.sh"),
        (shared_files_dir / "house-ca.crt", keg_scripts_dir / "house-ca.crt"),
    ]

    for src, dest in certificate_files:
        files.put(
            name=f"Copy {Path(src).name} to {dest}",
            src=str(src),
            dest=str(dest),
            _sudo=True,
        )
