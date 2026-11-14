from dataclasses import dataclass


@dataclass
class Port:
    pvid: int | None = None
    vlans: list[int] | None = None


class FilterModule:
    """Filters for working with openwrt"""

    def filters(self):
        return {"vlan_ports": self.vlan_ports}

    def vlan_ports(self, vlan: str | int, ports: dict[str, Port]) -> list[str]:
        vlan = int(vlan)
        res: list[str] = []
        for name, _port in ports.items():
            port = Port(**_port)
            if port.pvid is not None and int(port.pvid) == vlan:
                res.append(name)
            if port.vlans is not None and vlan in [int(v) for v in port.vlans]:
                res.append(f"{name}:t")

        return res
