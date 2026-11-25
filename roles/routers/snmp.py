from pathlib import Path
from typing import override

from pyinfra import host
from pyinfra.api import FactBase, QuoteString, StringCommand
from pyinfra.operations import files, server

from roles.routers import nvram

files_dir = Path(__file__).parent / "files"
remote_scripts_dir = Path("/jffs/scripts")
remote_rc_startup_dir = host.data.rc_startup_dir
wireless_stats_script = remote_scripts_dir / "snmp-wireless-stats.lua"
wrapper_script = remote_scripts_dir / "snmpd-wrapper.sh"
setup_script = remote_rc_startup_dir / "configure-snmpd-wrapper.sh"

# NET-SNMP-MIB::netSnmpPlaypen, the subtree net-snmp reserves for this
# kind of unregistered, local use. Must match the BASE OID (and the
# wireless_stats_script path above) hardcoded into snmpd-wrapper.sh.
wireless_stats_oid = ".1.3.6.1.4.1.8072.9999"


class ProcessIsRunning(FactBase):
    """Return True if the named process is running"""

    @override
    def command(self, proc_name: str) -> StringCommand:
        return StringCommand(
            "ps", "-o", "comm", "|", "grep", QuoteString(proc_name), "||", ":"
        )

    @override
    def process(self, output: list[str]) -> bool:
        return True

    @override
    def default(self) -> bool:
        return False


def apply():
    desired_nvram = {
        "snmpd_enable": "1",
        "snmpd_rocommunity": host.data.snmp_ro_community,
        "block_snmp": "0",
        "snmpd_sysname": host.name,
    }

    nvram.set_nvram_multi(desired_nvram, name="Enable snmpd")

    files.directory(
        name=f"Ensure directory {remote_scripts_dir} exists",
        path=str(remote_scripts_dir),
        mode="0755",
    )

    files.directory(
        name=f"Ensure directory {remote_rc_startup_dir} exists",
        path=str(remote_rc_startup_dir),
        mode="0755",
    )

    script = files.put(
        name=f"Install {wireless_stats_script.name}",
        src=str(files_dir / wireless_stats_script.name),
        dest=str(wireless_stats_script),
    )

    files.file(
        name=f"Ensure permission on {wireless_stats_script.name}",
        path=str(wireless_stats_script),
        user="root",
        group="root",
        mode="0755",
    )

    # dd-wrt's own boot-time snmpd setup has no nvram-driven extension
    # point for extra directives (there's no "snmpd_conf" or similar
    # it actually reads), it truncates /tmp/snmpd/snmpd.conf on every
    # (re)start, and it restarts snmpd on its own at points we can't
    # fully enumerate (observed: right after NTP sync) -- so patching
    # the conf once, whether via nvram or stopservice/startservice,
    # doesn't stick. Instead snmpd-wrapper.sh is bind-mounted over the
    # real /usr/sbin/snmpd so it patches the conf on *every*
    # invocation, however it's triggered; configure-snmpd-wrapper.sh
    # sets that mount up and is both the rc_startup entry and the
    # thing we invoke here to apply a change without waiting for a
    # reboot or an unrelated dd-wrt restart to come along.
    wrapper = files.put(
        name=f"Install {wrapper_script.name}",
        src=str(files_dir / wrapper_script.name),
        dest=str(wrapper_script),
    )

    files.file(
        name=f"Ensure permission on {wrapper_script.name}",
        path=str(wrapper_script),
        user="root",
        group="root",
        mode="0755",
    )

    setup = files.put(
        name=f"Install {setup_script.name}",
        src=str(files_dir / setup_script.name),
        dest=str(setup_script),
    )

    files.file(
        name=f"Ensure permission on {setup_script.name}",
        path=str(setup_script),
        user="root",
        group="root",
        mode="0755",
    )

    server.shell(
        name="(Re)apply snmpd wrapper / restart snmpd",
        commands=[str(setup_script)],
        _if=lambda: any(
            (
                script.did_change(),
                wrapper.did_change(),
                setup.did_change(),
                not host.get_fact(ProcessIsRunning, proc_name="snmpd"),
            )
        ),
    )
