# House infrastructure

This directory contains:

- [PyInfra] code for managing devices (in this directory), and
- [Docker compose] projects for deploying services (in the [services/](services) directory)

[pyinfra]: https://pyinfra.com/
[docker compose]: https://docs.docker.com/compose/

## Network architecture

![A network architecture diagram](docs/network.svg)

### House network

[FIOS] terminates at `gw.house`, an [Edgerouter-X] 5-port wired Ethernet router. This
connects to a [Netgear Orbi R750] with two satellites, which provide WiFi access to the house. There is a Ethernet connection between `gw.house` and `office-sw-2`, an HPE 1920 24-port switch running [OpenWrt]. This switch provides physical connectivity for devices in the downstairs office.

### Wireless backhaul

There is a second HPE 1920 switch in the upstairs work room named `office-sw-3` that provides physical connectivity to devices in that room. A pair of [Netgear R6400v1] routers are used to create a wireless backhaul between `office-sw-2` and `office-sw-3`:

- Router `backhaul-1` is located upstairs, where it connects to `office-sw-3`. `backhaul-1` is configured as a 5ghz access point.
- Router `backhaul-2` is located downstairs, where it connects to `office-sw-2`. `backhaul-2` is configured as a 5ghz station.

A [VXLAN] channel between the two routers carries VLANs 101 and 102 between the two switches.

The network configuration on the routers looks like this:

Bridges:

- `br0` carries only `vlan1`. This is managed by DD-WRT.
- `trunk0` connects `eth0` (the CPU port) with `transit` (the vxlan channel)

Unbridged interfaces:

- `eth1` is the 2.4ghz wireless interface, which is attached to the house wifi network for management access and exporting logs/emtrics.
- `eth2` is the 5ghz network interface and the transit link on the `100.64.64.0/29` network

For reference purposes, the interface configuration on `backhaul-1` looks like this:

```sh
backhaul-1 ~ # brctl show
bridge name bridge id         STP enabled interfaces
br0         8000.10da438fab68 no          vlan1
trunk0      8000.10da438fab66 no          eth0
                                          transit
backhaul-1 ~ # ip addr
1: lo: <LOOPBACK,MULTICAST,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 brd 127.255.255.255 scope host lo
       valid_lft forever preferred_lft forever
2: teql0: <NOARP> mtu 1500 qdisc noop state DOWN group default qlen 100
    link/void
3: ctf0: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN group default qlen 1000
    link/ether 00:23:6a:00:00:00 brd ff:ff:ff:ff:ff:ff
4: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel master trunk0 state UNKNOWN group default qlen 1000
    link/ether 10:da:43:8f:ab:66 brd ff:ff:ff:ff:ff:ff
5: vlan1@eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue master br0 state UP group default qlen 1000
    link/ether 10:da:43:8f:ab:66 brd ff:ff:ff:ff:ff:ff
7: eth1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UNKNOWN group default qlen 1000
    link/ether 10:da:43:8f:ab:68 brd ff:ff:ff:ff:ff:ff
    inet 192.168.1.127/24 brd 192.168.1.255 scope global eth1
       valid_lft forever preferred_lft forever
8: eth2: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1600 qdisc fq_codel state UNKNOWN group default qlen 1000
    link/ether 10:da:43:8f:ab:79 brd ff:ff:ff:ff:ff:ff
    inet 100.64.64.1/29 brd 100.64.64.7 scope global eth2
       valid_lft forever preferred_lft forever
9: br0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
    link/ether 10:da:43:8f:ab:68 brd ff:ff:ff:ff:ff:ff
    inet 10.18.25.1/29 brd 10.18.25.7 scope global br0
       valid_lft forever preferred_lft forever
10: trunk0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
    link/ether 10:da:43:8f:ab:66 brd ff:ff:ff:ff:ff:ff
11: transit: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue master trunk0 state UNKNOWN group default qlen 1000
    link/ether ba:4b:b0:7e:32:da brd ff:ff:ff:ff:ff:ff
```

The configuration on `backhaul-2` is identical but for different addresses.

See [configure-transit-link.sh](roles/routers/files/configure-transit-link.sh) for details on how networking on the routers is configured.

[edgerouter-x]: https://store.ui.com/us/en/products/er-x
[FIOS]: https://www.verizon.com/home/internet/fios-fastest-internet
[orbi r750]: https://support.netgear.com/support/product/rbr750
[openwrt]: https://openwrt.org/
[netgear r6400v1]: https://support.netgear.com/support/product/r6400
[vxlan]: https://en.wikipedia.org/wiki/VXLAN
