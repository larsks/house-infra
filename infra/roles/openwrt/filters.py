import ipaddress
from dataclasses import dataclass

import jinja2
import jinja2.ext


@dataclass
class Port:
    pvid: int | None = None
    vlans: list[int] | None = None


class OpenwrtFilters(jinja2.ext.Extension):
    def __init__(self, environment: jinja2.Environment):
        super().__init__(environment)
        environment.filters["dhcp_pool"] = self.dhcp_pool
        environment.filters["vlan_ports"] = self.vlan_ports
        environment.filters["nth_host"] = self.nth_host

    def nth_host(self, cidr: str | None, host: int) -> str:
        if not cidr:
            raise ValueError("cidr is required when dhcp is enabled on a vlan")

        network = ipaddress.ip_network(cidr, strict=False)
        return f"{network.network_address + host}/{network.prefixlen}"

    def dhcp_pool(self, cidr: str | None) -> dict[str, int]:
        if not cidr:
            raise ValueError("cidr is required when dhcp is enabled on a vlan")

        network = ipaddress.ip_network(cidr, strict=False)
        start = 2
        limit = network.num_addresses - 3
        if limit < 1:
            raise ValueError(f"cidr {cidr} is too small to host a dhcp pool")

        return {"start": start, "limit": limit}

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
