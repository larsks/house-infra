from group_data.all import default_gateway, dns_servers

switch_macaddr = "d8:94:03:9e:05:f7"

data = {
    "dnsmasq_domain": "dev.house",
    "dnsmasq_lease_file": "/var/state/dhcp.leases",
    "dhcp_default_duid": "00049a2768f9437149ba9e329b202eb4a923",
    "ula_prefix": "fd65:4949:c2ae::/48",
    "switch_macaddr": switch_macaddr,
    "devices": [
        {"name": "switch", "type": "bridge", "macaddr": switch_macaddr},
    ],
    "interfaces": [
        {
            "label": "lan",
            "device": "switch.100",
            "proto": "static",
            "ipaddr": "192.168.1.252/24",
            "gateway": default_gateway,
            "dns": dns_servers,
        }
    ],
    "lldp_location": 'address country US city "Belmont" street "Livermore Rd" building "64" room "Office"',
    "vlans": [
        {"id": 1},
        {"id": 100},
        {"id": 101, "dhcp": True, "cidr": "192.168.101.0/24"},
        {"id": 102, "dhcp": True, "cidr": "192.168.102.0/24"},
    ],
    "ports": {
        "lan1": {"pvid": 100, "vlans": [1, 101, 102]},
        "lan2": {"pvid": 100, "vlans": [101, 102]},
        "lan3": {"pvid": 100, "vlans": [101, 102]},
        "lan4": {"pvid": 100, "vlans": [101, 102]},
        "lan5": {"pvid": 100, "vlans": [101, 102]},
        "lan6": {"pvid": 100, "vlans": [101, 102]},
        "lan7": {"pvid": 100, "vlans": [101, 102]},
        "lan8": {"pvid": 100, "vlans": [101, 102]},
        ######################################################################
        #
        #    9      11      13      15
        # ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐
        # │     │ │     │ │     │ │     │
        # │ 101 │ │ 101 │ │ 101 │ │ 101 │
        # │     │ │     │ │     │ │     │
        # └─────┘ └─────┘ └─────┘ └─────┘
        # ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐
        # │     │ │     │ │     │ │     │
        # │ 102 │ │ 102 │ │ 102 │ │ 102 │
        # │     │ │     │ │     │ │     │
        # └─────┘ └─────┘ └─────┘ └─────┘
        #   10      12      14      16
        ######################################################################
        "lan9": {"pvid": 101},
        "lan10": {"pvid": 102},
        "lan11": {"pvid": 101},
        "lan12": {"pvid": 102},
        "lan13": {"pvid": 101},
        "lan14": {"pvid": 102},
        "lan15": {"pvid": 101},
        "lan16": {"pvid": 102},
        "lan17": {"pvid": 100, "vlans": [101, 102]},
        "lan18": {"pvid": 100, "vlans": [101, 102]},
        "lan19": {"pvid": 100, "vlans": [101, 102]},
        "lan21": {"pvid": 100, "vlans": [101, 102]},
        "lan22": {"pvid": 100, "vlans": [101, 102]},
        "lan23": {"pvid": 1, "vlans": [101, 102]},
        "lan24": {"pvid": 100, "vlans": [101, 102]},
    },
}
