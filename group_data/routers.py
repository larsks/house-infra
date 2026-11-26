from pathlib import Path

from globals import roles_dir
from group_data.all import house_ssid, ntp_servers, syslog_server
from lib.secrets import read_secret

ssh_config_file = str(roles_dir / "routers" / "files" / "ssh_config")
house_wifi_password = read_secret("house/wifi/vks-1/password")
rc_startup_dir = Path("/jffs/etc/rc_startup.d")

# fmt: off
nvram_config = {
    "wl0_mode":          "sta",         # Station mode, unbridged. DD-WRT treats eth1
    "eth1_bridged":      "0",           # (2.4ghz wifi) as the WAN interface and
    "wan_proto":         "dhcp",        # acquires the management ip with DHCP.

    "wl0_gmode":         "2",           # mixed network mode
    "wl0_nmode":         "2",
    "wl0_net_mode":      "mixed",

    "wl0_ssid":          house_ssid,    # set up connection to house wifi
    "wl0_security_mode": "psk2",
    "wl0_akm":           "psk2",
    "wl0_crypto":        "aes",
    "wl0_wpa_psk":       house_wifi_password,
    "wl0_wpa_gtk_rekey": "3600",

    "wl1_net_mode":      "acn-mixed",
    "wl1_gmode":         "1",
    "wl1_nmode":         "2",
    "wl1_txpwruser":     "0",
    "wl1_txpower":       "71",
    "wl1_bw":            "80",
    "wl1_nbw_cap":       "3",
    "wl1_chanspec":      "149/80",
    "wl1_channel":       "149",
    "wl1_nbw":           "80",         # not derived correctly for sta-mode radios at
    "wl1_nctrlsb":       "ll",         # boot; set explicitly so chanspec negotiation works

    "wl_mode":           "sta",         # apparently a fallback value

    "syslogd_rem_ip":    syslog_server, # configure syslog and ntp
    "syslogd_enable":    "1",
    "ntp_enable":        "1",
    "ntp_server":        " ".join(ntp_servers),

    "dnsmasq_enable":    "0",           # we're never acting as a dhcp server
    "probe_blacklist":   "vlan1",
    "wl0_afterburner":   "off",
    "arp_spoofing":      "0",
    "block_ident":       "0",
    "block_multicast":   "0",
    "sfe":               "2",
    "ctf_disable":       "0",
    "block_wan":         "0",
    "shownf":            "0",           # disable new features panel in web ui
    "fw_disable":        "1",           # one of many attempts to disable firewall...

    # ...but it turns out that we need to flush this manually.
    "rc_firewall":       "iptables -F\niptables -t nat -F",

    # Space-separated list of vlans that will be trunked over the wireless
    # backhaul.
    "trunk_vlans":       "101 102",

    # Run startup scripts.
    "rc_startup":        f"run-parts {rc_startup_dir}",
}
# fmt: on
