from host_data import backhaul_1, backhaul_2, gw_house, keg, office_sw_2, vmetrics

edgerouters = [
    ("gw.house", gw_house.data),
]

openwrt = [
    ("office-sw-2.house", office_sw_2.data),
]

vmetrics = [
    ("vmetrics.oddbit.com", vmetrics.data),
]

keg = [
    ("keg.house", keg.data),
]

wifilink = [
    ("backhaul-1.house", backhaul_1.data),
    ("backhaul-2.house", backhaul_2.data),
]
