# pyright: reportUnknownMemberType=false, reportUnusedCallResult=false
from globals import roles_dir
from pyinfra import host, local

if "edgerouters" in host.groups:
    local.include(str(roles_dir / "edgerouters" / "tasks.py"))

if "openwrt" in host.groups:
    local.include(str(roles_dir / "openwrt" / "tasks.py"))
