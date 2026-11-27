from host_data import (
    backhaul_1,
    backhaul_2,
    gw_house,
    keg,
    office_sw_2,
    office_sw_3,
    vmetrics,
)

gateways = [
    ("gw.house", gw_house.data),
]

routers = [
    ("backhaul-1.house", backhaul_1.data),
    ("backhaul-2.house", backhaul_2.data),
]

switches = [
    ("office-sw-2.house", office_sw_2.data),
    ("office-sw-3.house", office_sw_3.data),
]

diskstations = [
    ("keg.house", keg.data),
]

remote = [
    ("vmetrics.oddbit.com", vmetrics.data),
]
