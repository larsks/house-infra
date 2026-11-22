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
}
