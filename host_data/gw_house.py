from group_data.all import syslog_server
from lib.secrets import read_secret

data = {
    "_sudo": True,
    "address": "192.168.1.1/24",
    "ubnt_encrypted_password": read_secret("house/gw.house/users/ubnt"),
    "remote_syslog": {
        "enabled": True,
        "loghost": syslog_server,
        "loglevel": "info",
    },
    "scheduled_tasks": [
        {
            "name": "renew-certificate",
            "path": "/config/renew-certificate.sh",
            "args": "> /var/log/renew-certificate.log 2>&1",
            "interval": "1d",
        }
    ],
    "hosts_static_entries": [
        {"name": "gw.house", "address": "192.168.1.1"},
        {"name": "keg.house", "address": "192.168.1.99"},
    ],
    "dhcp_static_entries": [
        {
            "name": "backhaul-1",
            "ipaddress": "192.168.1.127",
            "macaddress": "10:da:43:8f:ab:68",
        },
        {
            "name": "backhaul-2",
            "ipaddress": "192.168.1.94",
            "macaddress": "10:da:43:8f:df:a3",
        },
        {
            "name": "colorprinter",
            "ipaddress": "192.168.1.51",
            "macaddress": "18:60:24:09:fe:21",
        },
        {
            "name": "office-sw-0",
            "ipaddress": "192.168.1.254",
            "macaddress": "78:d2:94:53:24:54",
        },
        {
            "name": "office-sw-1",
            "ipaddress": "192.168.1.253",
            "macaddress": "78:d2:94:41:3d:10",
        },
        {
            "name": "office-sw-2",
            "ipaddress": "192.168.1.252",
            "macaddress": "d8:94:03:9e:05:f7",
        },
        {
            "name": "orbi",
            "ipaddress": "192.168.1.5",
            "macaddress": "c8:9e:43:67:35:39",
        },
        {
            "name": "orbi-sat-office",
            "ipaddress": "192.168.1.7",
            "macaddress": "c8:9e:43:68:78:0b",
        },
        {
            "name": "orbi-sat-upstairs",
            "ipaddress": "192.168.1.6",
            "macaddress": "c8:9e:43:68:7c:97",
        },
        {
            "name": "svc-node-0",
            "ipaddress": "192.168.1.220",
            "macaddress": "fc:aa:14:fd:76:59",
        },
        {
            "name": "svc-node-1",
            "ipaddress": "192.168.1.221",
            "macaddress": "1c:1b:0d:fd:2e:44",
        },
        {
            "name": "keg.house",
            "ipaddress": "192.168.1.99",
            "macaddress": "00:11:32:b5:33:b9",
        },
    ],
    "dns_nameservers": ["1.1.1.1", "1.0.0.1"],
    "dynamic_dns_services": [
        {
            "interface": "eth0",
            "services": [
                {
                    "service": "noip",
                    "hostname": "oddbit.hopto.org",
                    "login": "lars@oddbit.com",
                    "password": read_secret("house/gw.house/noip_ddns_key"),
                    "server": "dynupdate.no-ip.com",
                }
            ],
        }
    ],
    "dns_static_entries": [
        {"name": ".keg.house", "address": "192.168.1.210"},
        {"name": "vmetrics.house", "address": "192.168.5.10"},
    ],
    "fw_rules_ipv4": [
        {
            "name": "LAN_IN",
            "description": "Connections from local network to router",
            "default_action": "accept",
            "rules": [
                {
                    "action": "accept",
                    "protocol": "tcp",
                    "destination": {"address": "192.168.1.1", "port": 22},
                    "log": False,
                }
            ],
        },
        {
            "name": "WAN_IN",
            "description": "Connections from WAN to local network",
            "default_action": "drop",
            "rules": [
                {
                    "action": "accept",
                    "description": "Allow established/related",
                    "state": ["established", "related"],
                },
                {
                    "action": "drop",
                    "description": "Drop invalid state",
                    "state": ["invalid"],
                },
            ],
        },
        {
            "name": "WAN_LOCAL",
            "description": "Connections from WAN to router",
            "default_action": "drop",
            "rules": [
                {
                    "action": "accept",
                    "description": "Allow established/related",
                    "state": ["established", "related"],
                },
                {
                    "action": "accept",
                    "description": "Allow inbound wireguard",
                    "protocol": "udp",
                    "destination": {"port": 51820},
                    "log": False,
                },
                {
                    "action": "drop",
                    "description": "Drop invalid state",
                    "state": ["invalid"],
                },
            ],
        },
    ],
    "fw_rules_ipv6": [
        {"name": "LANv6_IN", "default_action": "accept"},
        {
            "name": "WANv6_IN",
            "description": "WAN inbound traffic forwarded to LAN",
            "default_action": "drop",
            "rules": [
                {
                    "action": "accept",
                    "description": "Allow established/related sessions",
                    "state": ["established", "related"],
                },
                {
                    "action": "drop",
                    "description": "Drop invalid state",
                    "state": ["invalid"],
                },
                {"action": "accept", "protocol": "icmpv6"},
                {
                    "action": "accept",
                    "protocol": "tcp",
                    "destination": {"port": 22},
                },
            ],
        },
        {
            "name": "WANv6_LOCAL",
            "description": "WAN inbound traffic to the router",
            "default_action": "drop",
            "rules": [
                {
                    "action": "accept",
                    "description": "Allow established/related sessions",
                    "state": ["established", "related"],
                },
                {
                    "action": "drop",
                    "description": "Drop invalid state",
                    "state": ["invalid"],
                },
                {
                    "action": "accept",
                    "description": "Allow IPv6 icmp",
                    "protocol": "ipv6-icmp",
                },
                {
                    "action": "accept",
                    "description": "allow dhcpv6",
                    "protocol": "udp",
                    "destination": {"port": 546},
                    "source": {"port": 547},
                },
            ],
        },
    ],
    "authorized_keys": [
        {
            "name": "lars@oddbit.com",
            "type": "ssh-ed25519",
            "material": "AAAAC3NzaC1lZDI1NTE5AAAAIFVJHRH2xg2joG1xJIrNTalRkzT6BM8rQT+OXoFiKn16",
        },
    ],
    "wireguard_interfaces": [
        {
            "name": "wg0",
            "listen_port": "51820",
            "address": "192.168.5.1/24",
            "private_key": "/config/auth/wg0.private",
            "peers": [
                {
                    "description": "vmetrics",
                    "public_key": "1L1hxyk1y9Zu80r3JTZoIr3+sdAGIDZvnn/6KCwIrhc=",
                    "allowed_ips": "192.168.5.10/32",
                    "endpoint": "vmetrics.oddbit.com:51820",
                },
                {
                    "description": "client1",
                    "public_key": "7EjXlLzUMfoqzki9rN9au9hHVUV+2/QcVk04aRGBIzc=",
                    "allowed_ips": "192.168.5.20/32",
                },
                {
                    "description": "client2",
                    "public_key": "SWKBcTCig9KBZSiV6jVBb1fBqcosL9F9CI6zQ7YfhT8=",
                    "allowed_ips": "192.168.5.21/32",
                },
                {
                    "description": "client3",
                    "public_key": "xT4ddNbves0sNtXKZ7/HSuS1aBqx1fRt2nN8FKGCaDg=",
                    "allowed_ips": "192.168.5.22/32",
                },
            ],
        }
    ],
}
