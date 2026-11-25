from pathlib import Path

from pyinfra import host
from pyinfra.operations import files, server

from roles.routers import nvram, packages, snmp

files_dir = Path(__file__).parent / "files"
remote_scripts_dir = Path("/jffs/scripts")
remote_rc_startup_dir = host.data.rc_startup_dir

nvram.set_nvram("router_name", host.name)
nvram.set_nvram_multi(
    host.data.nvram_config | host.data.host_nvram_config,
    name="Set wifi backhaul nvram config",
)

directories = (
    (remote_scripts_dir, "0755"),
    (remote_rc_startup_dir, "0755"),
)

scripts = (
    (
        files_dir / "configure-root-profile.sh",
        remote_rc_startup_dir / "configure-root-profile.sh",
        "0755",
        None,
    ),
    (
        files_dir / "start-lldpd.sh",
        remote_rc_startup_dir / "start-lldpd.sh",
        "0755",
        None,
    ),
    (
        files_dir / "mount_opt.sh",
        remote_rc_startup_dir / "mount_opt.sh",
        "0755",
        None,
    ),
    (
        files_dir / "configure-transit-link.sh",
        remote_rc_startup_dir / "configure-transit-link.sh",
        "0755",
        None,
    ),
)

files_to_delete = (
    remote_scripts_dir / "configure-transit-link.sh",
    remote_scripts_dir / "udhcpc-br0.sh",
)

for path, mode in directories:
    files.directory(
        name=f"Ensure directory {path} exists",
        path=str(path),
        mode=mode,
    )

for src, dest, mode, handler in scripts:
    res = files.put(
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

    if handler is not None:
        handler(res.did_change)

for path in files_to_delete:
    files.file(
        name=f"Ensure {path} is absent",
        path=str(path),
        present=False,
    )

# Installed before snmp.apply() below restarts snmpd, since that
# restart execs snmp-wireless-stats.lua and needs lua/luaposix
# already in place.
packages.apply()

snmp.apply()

if not host.data.get("skip_reboot"):
    server.reboot(
        name="Reboot router after nvram changes",
        delay=10,
        reboot_timeout=600,
        _if=nvram.any_changed,
    )
