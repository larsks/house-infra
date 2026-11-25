from pathlib import Path

from pyinfra.operations import apk, files, server

from roles.switches.filters import OpenwrtFilters

template_dir = Path(__file__).parent / "templates"

apk.packages(
    name="Install required packages",
    packages=[
        "dnsmasq",
        "lldpd",
    ],
)

for section in [
    "system",
    "dhcp",
    "network",
    "firewall",
    "lldpd",
    "prometheus-node-exporter-ucode",
]:
    result = files.template(
        name=f"Update {section} configration",
        src=template_dir / f"{section}.uci",
        dest=f"/etc/config/{section}",
        jinja_env_kwargs={
            "trim_blocks": True,
            "extensions": [OpenwrtFilters],
        },
    )

    service = section
    if section == "dhcp":
        service = "dnsmasq"

    server.shell(
        name=f"Reload {section} configuration",
        commands=[f"/etc/init.d/{service} reload"],
        _if=result.did_change,
    )
