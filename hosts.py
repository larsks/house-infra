from host_data import gw_house, keg, office_sw_2, vmetrics, backhaul_1, backhaul_2

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
    ("backhaul-1", backhaul_1.data),
    ("backhaul-2", backhaul_2.data),
]
