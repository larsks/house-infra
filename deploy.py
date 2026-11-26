from pyinfra import host, local

from globals import roles_dir

if host.name == "@local":
    local.include(str(roles_dir / "local" / "tasks.py"))

if "gateways" in host.groups:
    local.include(str(roles_dir / "gateways" / "tasks.py"))

if "switches" in host.groups:
    local.include(str(roles_dir / "switches" / "tasks.py"))

if "remote" in host.groups:
    local.include(str(roles_dir / "vmetrics" / "tasks.py"))

if "diskstations" in host.groups:
    local.include(str(roles_dir / "keg" / "tasks.py"))

if "routers" in host.groups:
    local.include(str(roles_dir / "routers" / "tasks.py"))
