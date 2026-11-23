from globals import roles_dir
from lib.secrets import read_secret

ssh_config_file = str(roles_dir / "wifilink" / "files" / "ssh_config")
house_wifi_password = read_secret("house/wifi/vks-1/password")

nvram_config = {
    "wl0_mode": "wet",
    "wl0_net_mode": "mixed",
    "wl0_ssid": "vks-1",
    "wl0_security_mode": "psk2",
    "wl0_akm": "psk2",
    "wl0_crypto": "aes",
    "wl0_wpa_psk": house_wifi_password,
    "wl0_wpa_gtk_rekey": "3600",
    "dnsmasq_enable": "0",
    "syslogd_rem_ip": "192.168.1.211",
    "syslogd_enable": "1",
    "ntp_enable": "1",
    "ntp_server": "192.168.1.1",
    "wl0_afterburner": "off",
    "arp_spoofing": "0",
    "block_ident": "0",
    "block_multicast": "0",
    "block_wan": "0",
    # dd-wrt builds its standard WAN/firewall ruleset (treating eth2 as a
    # WAN face, blocking remote admin ports, etc.) AFTER rc_startup runs,
    # so flushing it from configure-transit-link.sh doesn't stick. This is
    # the one firmware hook ("Firewall" script, Administration > Commands)
    # that runs after that ruleset is built.
    "rc_firewall": "iptables -F\niptables -t nat -F",
}
