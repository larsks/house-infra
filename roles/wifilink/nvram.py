from typing import override

from pyinfra import host
from pyinfra.api import FactBase, QuoteString, StringCommand, operation

_changed_hosts: set[str] = set()


def _mark_changed() -> None:
    _changed_hosts.add(host.name)


def any_changed() -> bool:
    """Return True if any nvram value has changed for the current host."""
    return host.name in _changed_hosts


class NvramValue(FactBase):
    """Read a single dd-wrt nvram variable."""

    @override
    def command(self, var_name: str) -> StringCommand:
        return StringCommand("nvram", "get", QuoteString(var_name))

    @override
    def process(self, output: list[str]):
        return "\n".join(output) if output else None


@operation()
def set_nvram(var_name: str, desired_value: str):
    current_value = host.get_fact(NvramValue, var_name)

    if current_value != desired_value:
        _mark_changed()
        yield StringCommand(
            "nvram",
            "set",
            QuoteString(f"{var_name}={desired_value}"),
        )


@operation()
def set_nvram_multi(values: dict[str, str]):
    changed = False

    for var_name, desired_value in values.items():
        current_value = host.get_fact(NvramValue, var_name)

        if current_value != desired_value:
            _mark_changed()
            changed = True
            yield StringCommand(
                "nvram",
                "set",
                QuoteString(f"{var_name}={desired_value}"),
            )

    if changed:
        yield StringCommand("nvram", "commit")
