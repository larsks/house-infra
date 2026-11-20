from lib.secrets import read_secret

data = {
    "_sudo": True,
    "wireguard_interfaces": [
        {
            "name": "house",
            "listen_port": 51820,
            "address": "192.168.5.10/24",
            "private_key": read_secret(
                "vmetrics.oddbit.com/wireguard/house_private_key"
            ),
            "peers": [
                {
                    "description": "gw.house",
                    "public_key": "nohnQn6XVnxM/jDNNh5GGe8qaFq7mKZelObvihnuA28=",
                    "allowed_ips": ["192.168.5.0/24", "192.168.1.0/24"],
                    "endpoint": "oddbit.hopto.org:51820",
                }
            ],
        }
    ],
}
