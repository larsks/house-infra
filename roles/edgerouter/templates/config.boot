{% macro render(tree, indent) %}
{% for key, value in tree.items() %}
{% if value is mapping %}
{{ indent }}{{ key }} {
{{ render(value, indent + '    ') -}}
{{ indent }}}
{% else %}
{{ indent }}{{ key }} {{ value }}
{% endif %}
{% endfor %}
{% endmacro %}
firewall {
    all-ping enable
    broadcast-ping disable
{% for ruleset in fw_rules_ipv6|default([]) %}
{{ render({'ipv6-name ' + ruleset.name: ruleset|fw_ruleset_tree}, '    ') -}}
{% endfor %}
    ipv6-receive-redirects disable
    ipv6-src-route disable
    ip-src-route disable
    log-martians enable
{% for ruleset in fw_rules_ipv4|default([]) %}
{{ render({'name ' + ruleset.name: ruleset|fw_ruleset_tree}, '    ') -}}
{% endfor %}
    receive-redirects disable
    send-redirects enable
    source-validation disable
    syn-cookies enable
}
interfaces {
    ethernet eth0 {
        address dhcp
        description Internet
        dhcpv6-pd {
            pd 0 {
                interface switch0 {
                    host-address ::1
                    prefix-id :0
                    service slaac
                }
                prefix-length 56
            }
            prefix-only
            rapid-commit enable
        }
        duplex auto
        firewall {
            in {
                ipv6-name WANv6_IN
                name WAN_IN
            }
            local {
                ipv6-name WANv6_LOCAL
                name WAN_LOCAL
            }
        }
        speed auto
    }
    ethernet eth1 {
        description Local
        duplex auto
        speed auto
    }
    ethernet eth2 {
        description Wifi
        duplex auto
        speed auto
    }
    ethernet eth3 {
        description Local
        duplex auto
        speed auto
    }
    ethernet eth4 {
        description Local
        duplex auto
        poe {
            output off
        }
        speed auto
    }
    loopback lo {
    }
    switch switch0 {
        address 192.168.1.1/24
        description Local
        firewall {
            in {
                name LAN_IN
            }
        }
        mtu 1500
        switch-port {
            interface eth1 {
            }
            interface eth2 {
            }
            interface eth3 {
            }
            interface eth4 {
            }
            vlan-aware disable
        }
    }
{% for wg in wireguard_interfaces %}
    wireguard {{ wg.name }} {
        address {{ wg.address }}
        listen-port {{ wg.listen_port }}
{% for peer in wg.peers|default([]) %}
        peer {{ peer.public_key }} {
            allowed-ips {{ peer.allowed_ips }}
            description {{ peer.description }}
{% if peer.endpoint is defined %}
            endpoint {{ peer.endpoint }}
{% endif %}
        }
{% endfor %}
        private-key {{ wg.private_key }}
        route-allowed-ips true
    }
{% endfor %}
}
protocols {}
service {
    dhcp-server {
        disabled false
        hostfile-update disable
        shared-network-name LAN {
            authoritative enable
            subnet 192.168.1.0/24 {
                default-router 192.168.1.1
                dns-server 192.168.1.1
                domain-name house
                lease 86400
                start 192.168.1.20 {
                    stop 192.168.1.150
                }
{% for entry in dhcp_static_entries|default([]) %}
                static-mapping {{ entry.name }} {
                    ip-address {{ entry.ipaddress }}
                    mac-address {{ entry.macaddress }}
                }
{% endfor %}
            }
        }
        static-arp disable
        use-dnsmasq enable
    }
    dns {
        forwarding {
            cache-size 150
            dhcp eth0
            listen-on switch0
            listen-on switch0.10
            name-server 1.1.1.1
            name-server 1.0.0.1
{% for entry in dns_static_entries %}
            options address=/{{ entry.name }}/{{ entry.address }}
{% endfor %}
        }
    }
    gui {
        cert-file /config/certs/server.combined
        http-port 80
        https-port 443
        older-ciphers disable
    }
    lldp {
        interface all {
            location {
                civic-based {
                    country-code us
                    ca-type 3 {
                        ca-value Belmont
                    }
                    ca-type 6 {
                        ca-value Livermore
                    }
                    ca-type 18 {
                        ca-value Rd
                    }
                }
            }
        }
    }
    nat {
        rule 5010 {
            description "masquerade for WAN"
            outbound-interface eth0
            type masquerade
        }
    }
    snmp {
        community monitor {
            authorization ro
        }
    }
    ssh {
        port 22
        protocol-version v2
    }
    unms {
        disable
    }
}
system {
    analytics-handler {
        send-analytics-report false
    }
    crash-handler {
        send-crash-report false
    }
    host-name ubnt
    login {
        user ubnt {
            authentication {
                encrypted-password {{ ubnt_encrypted_password }}
{% for key in authorized_keys %}
                public-keys {{ key.name }} {
                    key {{ key.material }}
                    type {{ key.type }}
                }
{% endfor %}
            }
            level admin
        }
    }
    ntp {
        server 0.ubnt.pool.ntp.org {
        }
        server 1.ubnt.pool.ntp.org {
        }
        server 2.ubnt.pool.ntp.org {
        }
        server 3.ubnt.pool.ntp.org {
        }
    }
    static-host-mapping {
{% for host in hosts_static_entries %}
        host-name {{ host.name }} {
            inet {{ host.address }}
        }
{% endfor %}
    }
    syslog {
        global {
            facility all {
                level notice
            }
            facility protocols {
                level debug
            }
        }
{% if (remote_syslog|default({})).enabled|default(false) %}
        host {{ remote_syslog.loghost }} {
            facility all {
                level {{ remote_syslog.loglevel }}
            }
        }
    }
{% endif %}
    task-scheduler {
{% for task in scheduled_tasks|default([]) %}
        task {{ task.name }} {
          executable {
              path {{ task.path }}
              arguments "{{ task.args }}"
          }
          interval {{ task.interval }}
        }
{% endfor %}
    }
    time-zone UTC
    traffic-analysis {
        dpi disable
        export enable
    }
}

/* Warning: Do not remove the following line. */
/* === vyatta-config-version: "config-management@1:conntrack@1:cron@1:dhcp-relay@1:dhcp-server@4:firewall@5:ipsec@5:nat@3:qos@1:quagga@2:suspend@1:system@5:ubnt-l2tp@1:ubnt-pptp@1:ubnt-udapi-server@1:ubnt-unms@2:ubnt-util@1:vrrp@1:vyatta-netflow@1:webgui@1:webproxy@1:zone-policy@1" === */
/* Release version: v3.0.1.5862409.250924.1407 */
