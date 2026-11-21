from pathlib import Path

from pyinfra import host
from pyinfra.operations import apt, files, systemd

template_dir = Path(__file__).parent / "templates"


def apply():
    apt.packages(
        name="Install required packages",
        packages=[
            "wireguard-tools",
        ],
    )

    files.directory(
        name="Ensure wireguard directory exists",
        path="/etc/wireguard",
        user="root",
        group="root",
        mode="0755",
    )

    for interface in host.data.wireguard_interfaces:
        config = files.template(
            name=f"Generate configuration for wg interface {interface['name']}",
            src=str(template_dir / "wg.conf"),
            dest=f"/etc/wireguard/{interface['name']}.conf",
            jinja_env_kwargs={"trim_blocks": True},
            interface=interface,
        )

        systemd.service(
            name=f"Ensure wg interface {interface['name']} is active",
            service=f"wg-quick@{interface['name']}.service",
            enabled=True,
            running=True,
            restarted=config.did_change,
        )
