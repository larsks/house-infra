from pathlib import Path

from pyinfra.operations import files, server

from roles.gateways import acme, ddns
from roles.gateways.filters import EdgerouterFilters

template_dir = Path(__file__).parent / "templates"
script_dir = Path(__file__).parent / "scripts"

acme.apply()
ddns.apply()

config = files.template(
    name="Generate configuration from template",
    src=str(template_dir / "config.boot"),
    dest="config.new",
    jinja_env_kwargs={
        "trim_blocks": True,
        "extensions": [EdgerouterFilters],
    },
)

server.script(
    name="Apply configuration",
    src=str(script_dir / "apply-config.sh"),
    _if=config.did_change,
)
