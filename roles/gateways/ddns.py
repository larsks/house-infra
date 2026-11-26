from pathlib import Path

from pyinfra.operations import files

template_dir = Path(__file__).parent / "templates"
files_dir = Path(__file__).parent / "files"


def apply():
    files.template(
        name="Configure DDNS update token",
        src=str(template_dir / "ddns.env"),
        dest="/config/auth/ddns.env",
        mode="600",
        jinja_env_kwargs={
            "trim_blocks": True,
        },
    )

    files.file(
        name="Remove stale Route53 credentials",
        path="/config/auth/aws.env",
        present=False,
    )

    files.put(
        name="Install DDNS update hook shim (persistent copy)",
        src=str(files_dir / "update-ddns.sh"),
        dest="/config/scripts/update-ddns.sh",
        mode="755",
    )

    files.put(
        name="Install DDNS update hook shim (/etc, wiped on reboot)",
        src=str(files_dir / "update-ddns.sh"),
        dest="/etc/dhcp3/dhclient-exit-hooks.d/update-ddns",
        mode="755",
    )

    files.put(
        name="Install DDNS update hook script",
        src=str(files_dir / "update-ddns-run.sh"),
        dest="/config/scripts/update-ddns-run.sh",
        mode="755",
    )

    files.put(
        name="Install post-config.d hook re-installer",
        src=str(files_dir / "install-ddns-hook.sh"),
        dest="/config/scripts/post-config.d/install-ddns-hook",
        mode="755",
    )
