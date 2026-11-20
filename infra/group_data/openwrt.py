from group_data.all import ntp_servers, syslog_server

system = {
    "log_ip": syslog_server,
    "log_protocol": "udp",
}

ntp = {
    "enabled": True,
    "servers": ntp_servers,
}

dnsmasq_rebind_protection = 0
dnsmasq_rebind_localhost = 1
dnsmasq_authoritative = 1
dnsmasq_lease_file = "/tmp/dhcp.leases"

ssh_file_transfer_protocol = "scp"

node_exporter_listen_interface = "*"
node_exporter_listen_port = 9100
node_exporter_http_keepalive = 70
