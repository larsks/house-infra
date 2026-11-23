from pathlib import Path

from pyinfra import host
from pyinfra.operations import files, server

from roles.wifilink import nvram, snmp

files_dir = Path(__file__).parent / "files"
remote_scripts_dir = Path("/jffs/scripts")

nvram.set_nvram("router_name", host.name)
nvram.set_nvram_multi(host.data.nvram_config, name="Set wifi backhaul nvram config")
snmp.apply()

scripts = (
    (
        files_dir / "configure-transit-link.sh",
        remote_scripts_dir / "configure-transit-link.sh",
        "0755",
    ),
    (
        files_dir / "udhcpc-br0.sh",
        remote_scripts_dir / "udhcpc-br0.sh",
        "0755",
    ),
)

for src, dest, mode in scripts:
    files.put(
        name=f"Install {dest.name}",
        src=str(src),
        dest=str(dest),
    )

    files.file(
        name=f"Ensure permission on {dest.name}",
        path=str(dest),
        user="root",
        group="root",
        mode=mode,
    )

if not host.data.get("skip_reboot"):
    server.reboot(
        name="Reboot router after nvram changes",
        delay=10,
        reboot_timeout=600,
        _if=nvram.any_changed,
    )
