syslog_server = "192.168.1.211"
default_gateway = "192.168.1.1"
ntp_servers = [
    default_gateway,
]
dns_servers = [
    default_gateway,
]
wireguard_listen_port = 51820
snmp_ro_community = "monitor"
house_ssid = "vks-1"

# where to find acme.sh ACME client
acme_repo_url = "https://github.com/acmesh-official/acme.sh"
