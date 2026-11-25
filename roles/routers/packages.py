from pyinfra.operations import opkg

packages = (
    "ip-bridge",
    "ip-full",
    "lldpd",
    "lua",
    "luaposix",
)


def apply():
    opkg.update(name="Update opkg package lists")
    for pkg in packages:
        opkg.packages(name=f"Install {pkg}", packages=pkg, update=False)
