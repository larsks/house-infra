from typing import override

from pyinfra import host
from pyinfra.api import FactBase, QuoteString, StringCommand
from pyinfra.operations import server

from roles.wifilink import nvram


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

    changed = nvram.set_nvram_multi(desired_nvram, name="Enable snmpd")

    server.shell(
        name="(Re)start snmpd",
        commands=[
            "stopservice snmp",
            "startservice snmp",
        ],
        _if=[
            changed.did_change,
            lambda: not host.get_fact(ProcessIsRunning, proc_name="snmpd"),
        ],
    )
