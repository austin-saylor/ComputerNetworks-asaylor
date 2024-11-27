import sys
import socket
import threading
import argparse
import fcntl
import struct
from scapy.all import *
import ipaddress
from scapy.layers.l2 import getmacbyip

# 8.5-minute runtime with /24
# 30-second runtime with /28

def get_ip(interface):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        ip_address = fcntl.ioctl(
            s.fileno(),
            0x8915,
            struct.pack('256s', interface[:15].encode('utf-8'))
        )[20:24]
        return socket.inet_ntoa(ip_address)
    except IOError:
        return None

def get_arp_subnet(machine_ip, target_subnets):
    index = 0

    for subnet in target_subnets:
        target_ips = [str(ip) for ip in ipaddress.IPv4Network(subnet, strict=False)]

        for target_ip in target_ips:
            if (target_ip == machine_ip):
                arp_subnet = target_subnets[index]
                return arp_subnet
        
        index += 1
    
    return "255.255.255.255"

def get_icmp_subnets(machine_ip, target_subnets):
    index = 0

    icmp_subnets = []
    for subnet in target_subnets:
        match = False
        target_ips = [str(ip) for ip in ipaddress.IPv4Network(subnet, strict=False)]

        for target_ip in target_ips:
            if (target_ip == machine_ip):
                match = True
                break
            else:
                continue
        
        if match == False:
            icmp_subnets.append(target_subnets[index])
        
        index += 1
    
    if icmp_subnets:
        return icmp_subnets

    return "255.255.255.255"

def arp_scan(subnet):
    print("Running ARP Scan...")
    target_ips = [str(ip) for ip in ipaddress.IPv4Network(subnet, strict=False)]
    try:
        print("ARP: Sending ARP requests...")
        ips = []
        macs = []
        for ip in target_ips:
            print("ARP: Scanning {}...".format(ip))
            request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip)
            ans, unans = srp(request, timeout=1, retry=0, iface="eth0", verbose=0)
            for sent, received in ans:
                #result.append({'IP': received.psrc, 'MAC': received.hwsrc})
                ips.append(received.psrc)
                macs.append(received.hwsrc)
        result = [ips, macs]
        print("ARP Scan Completed!\n\n")
        return result
    except Exception as e:
        print("Error during ARP scan: {}".format(e))
        return []

def icmp_scan(target_subnets, max_hosts=10):
    print("Running ICMP Scan...")
    try:
        result = []
        for subnet in target_subnets:
            target_ips = [str(ip) for ip in ipaddress.IPv4Network(subnet, strict=False)]
            for ip in target_ips:
                print("ICMP: Scanning {}...".format(ip))
                response = sr1(IP(dst=ip) / ICMP(), timeout=1, verbose=0)
                if response:
                    result.append(response.src)
        print("ICMP Scan Completed!\n\n")
        return result
    except Exception as e:
        print("Error during ICMP scan: {}".format(e))
        return []

def port_scan(target_ips, p):
    print("Running port Scan...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = []

    for target_ip in target_ips:
        ports = []
        for i in range(p):
            try:
                connection = s.connect((target_ip, i))
                ports.append(i)
            except:
                continue
        result.append(ports)
    print("Port Scan Completed!\n\n")
    return result


def print_results(results):
    arp_results, icmp_results, port_results = results

    ips = arp_results[0] + icmp_results
    macs = arp_results[1]

    while len(port_results) < len(ips):
        port_results.append([])  # Placeholder for no port results

    print("\n\n" + " "*23 + "RESULTS:")
    print("IP" + " "*14 + "MAC" + " "*19 + "Open Ports")
    print("-"*55)

    i = 0
    for device in ips:
        mac = ""
        if 0 <= i < len(macs):
            mac = macs[i]
        else:
            mac = "*"*17
        
        ports = ", ".join(map(str, port_results[i])) if port_results[i] else "None"

        print('{}     {}     {}'.format(ips[i], mac, ports))
        i += 1


def main():
    interface = "eth0"
    target_subnets = ["192.168.1.0/28", "192.168.2.0/28"]

    machine_ip = get_ip(interface)
    arp_subnet = get_arp_subnet(machine_ip, target_subnets)
    icmp_subnets = get_icmp_subnets(machine_ip, target_subnets)

    arp_results = arp_scan(arp_subnet)

    icmp_results = icmp_scan(icmp_subnets)

    target_ips = arp_results[0] + icmp_results

    port_results = port_scan(target_ips, 100)

    results = [arp_results, icmp_results, port_results]
    print_results(results)


if __name__ == "__main__":
    main()