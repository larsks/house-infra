from pyinfra.operations import opkg

packages = (
    "ip-bridge",
    "ip-full",
    "lldpd",
)


def apply():
    for pkg in packages:
        opkg.packages(name=f"Install {pkg}", packages=pkg)
