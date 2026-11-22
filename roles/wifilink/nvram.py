from typing import override

from pyinfra import host
from pyinfra.api import FactBase, QuoteString, StringCommand, operation


class NvramValue(FactBase):
    """Read a single dd-wrt nvram variable."""

    @override
    def command(self, var_name: str) -> StringCommand:
        return StringCommand("nvram", "get", QuoteString(var_name))

    @override
    def process(self, output: list[str]):
        return output[0] if output else None


@operation()
def set_nvram(var_name: str, desired_value: str):
    current_value = host.get_fact(NvramValue, var_name)

    if current_value != desired_value:
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
            changed = True
            yield StringCommand(
                "nvram",
                "set",
                QuoteString(f"{var_name}={desired_value}"),
            )

    if changed:
        yield StringCommand("nvram", "commit")
