from typing import override

from pyinfra import host, logger, state
from pyinfra.api import FactBase, QuoteString, StringCommand, operation
from pyinfra.api.output import format_text
from pyinfra.operations.util.files import generate_color_diff

_changed_hosts: set[str] = set()


def _mark_changed() -> None:
    _changed_hosts.add(host.name)


def any_changed() -> bool:
    """Return True if any nvram value has changed for the current host."""
    return host.name in _changed_hosts


def _log_diff(var_name: str, current_value: str | None, desired_value: str) -> None:
    if not state.config.DIFF:
        return

    host.log(f"Will set {format_text(var_name, bold=True)}", logger.info)

    current_lines = [current_value] if current_value is not None else []
    for line in generate_color_diff(current_lines, [desired_value]):
        logger.info("  %s", line)
    logger.info("")


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
        _log_diff(var_name, current_value, desired_value)
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
            _log_diff(var_name, current_value, desired_value)
            yield StringCommand(
                "nvram",
                "set",
                QuoteString(f"{var_name}={desired_value}"),
            )

    if changed:
        yield StringCommand("nvram", "commit")
