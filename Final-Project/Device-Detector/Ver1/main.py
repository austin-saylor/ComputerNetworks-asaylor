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
            0x8915,  # SIOCGIFADDR
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
        print("Scanning subnet {}...".format(subnet))
        target_ips = [str(ip) for ip in ipaddress.IPv4Network(subnet, strict=False)]

        for target_ip in target_ips:
            print("Comparing IPs...")
            if (target_ip == machine_ip):
                print("**********{} AND {} ARE EQUAL**********".format(target_ip, machine_ip))
                match = True
                break
            else:
                print("{} and {} are NOT equal.".format(target_ip, machine_ip))
        
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
        print("Sending ARP requests...")
        ips = []
        macs = []
        for ip in target_ips:
            print("Scanning {}...".format(ip))
            request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip)
            ans, unans = srp(request, timeout=1, retry=0, iface="eth0", verbose=0)
            for sent, received in ans:
                print("ARP Response from IP: {}, MAC: {}".format(received.psrc, received.hwsrc))
                #result.append({'IP': received.psrc, 'MAC': received.hwsrc})
                ips.append(received.psrc)
                macs.append(received.hwsrc)
        result = [ips, macs]
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
                response = sr1(IP(dst=ip) / ICMP(), timeout=1, verbose=0)
                if response:
                    print("ICMP Response from IP: {}".format(response.src))
                    #result.append({'IP': response.src, 'MAC': '***'})
                    result.append(response.src)
        return result
    except Exception as e:
        print("Error during ICMP scan: {}".format(e))
        return []

def os_scan(target_subnets):
    print("Running OS Scan...")
    ## Create custom TCP SYN packet
    result = []
    for subnet in target_subnets:
        target_ips = [str(ip) for ip in ipaddress.IPv4Network(subnet, strict=False)]
        for ip in target_ips:
            packet = IP(dst=ip)/TCP(dport=80, flags="S")
            response = sr1(packet, timeout=2, verbose=0)
            
            if response:
                ## Analyze TCP window size and TTL
                if response.ttl <= 32:
                    result.append("Linux/Unix")
                elif (response.ttl > 32) and (response.ttl <= 64):
                    result.append("Windows")
                else:
                    result.append("Unknown OS")
    return result

def port_scan(target_ips, p):
    print("Running port Scan...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = []

    for target_ip in target_ips:
        ports = []
        for i in range(p):
            try:
                connection = s.connect((target_ip, i))
                print("Port {} is open on {}!".format(i, target_ip))
                ports.append(i)
            except:
                continue
        result.append(ports)
    return result


def print_results(results):
    arp_results = results[0]
    icmp_results = results[1]
    os_results = results[2]

    ips = arp_results[0] + icmp_results
    macs = arp_results[1]

    print("IP" + " "*14 + "MAC" + " "*19 + "OS")
    print("-"*55)

    i = 0
    for device in ips:
        mac = ""
        if 0 <= i < len(macs):
            mac = macs[i]
        else:
            mac = "*"*17
        print('{}     {}     {}'.format(ips[i], mac, os_results[i]))
        i += 1


def main():
    interface = "eth0"
    target_subnets = ["192.168.1.0/28", "192.168.2.0/28"]

    machine_ip = get_ip(interface)
    arp_subnet = get_arp_subnet(machine_ip, target_subnets)
    icmp_subnets = get_icmp_subnets(machine_ip, target_subnets)

    arp_results = arp_scan(arp_subnet)
    target_ips = arp_results[0]
    print("ARP Scan Completed!\n\n")

    icmp_results = icmp_scan(icmp_subnets)
    print("ICMP Scan Completed!\n\n")

    os_results = os_scan(target_subnets)

    port_results = port_scan(target_ips, 100)

    results = [arp_results, icmp_results, os_results]

    print("\n\nRESULTS:")
    print_results(results)
    print(port_results)


if __name__ == "__main__":
    main()
