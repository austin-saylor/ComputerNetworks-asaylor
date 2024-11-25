import nmap
import socket
import threading
import argparse
import fcntl
import struct
from scapy.all import *
import ipaddress
from scapy.layers.l2 import getmacbyip

# Define target subnets
target_subnets = ["192.168.1.0/24", "192.168.2.0/24"]

def getMachineIP(interface):
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

def getARPSubnet(machine_ip, target_subnets):
    index = 0

    for subnet in target_subnets:
        target_ips = [str(ip) for ip in ipaddress.IPv4Network(subnet, strict=False)]

        for target_ip in target_ips:
            if (target_ip == machine_ip):
                arp_subnet = target_subnets[index]
                return arp_subnet
        
        index += 1
    
    return "255.255.255.255"

def getICMPSubnets(machine_ip, target_subnets):
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
    target_ips = [str(ip) for ip in ipaddress.IPv4Network(subnet, strict=False)]
    try:
        print("Sending ARP requests...")
        result = []
        for ip in target_ips:
            print("Scanning {}...".format(ip))
            request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip)
            ans, unans = srp(request, timeout=1, retry=0, iface="eth0", verbose=0)
            for sent, received in ans:
                print("ARP Response from IP: {}, MAC: {}".format(received.psrc, received.hwsrc))
                result.append({'IP': received.psrc, 'MAC': received.hwsrc})
        return result
    except Exception as e:
        print("Error during ARP scan: {}".format(e))
        return []

def icmp_scan(subnets, max_hosts=10):
    try:
        result = []
        for subnet in subnets:
            target_ips = [str(ip) for ip in ipaddress.IPv4Network(subnet, strict=False)]
            for ip in target_ips:
                response = sr1(IP(dst=ip) / ICMP(), timeout=1, verbose=0)
                if response:
                    print("ICMP Response from IP: {}".format(response.src))
                    result.append({'IP': response.src, 'MAC': '***'})
                if len(result) >= max_hosts:
                    print("Maximum hosts reached, stopping ICMP scan.")
                    break
        return result
    except Exception as e:
        print("Error during ICMP scan: {}".format(e))
        return []

def print_result(result):
    print("IP" + " "*14 + "MAC" + " "*18 + "Open Ports")
    print("-"*55)
    for device in result:
        print('{}     {}'.format(device['IP'], device['MAC']))

def main():
    interface = "eth0"

    machine_ip = getMachineIP(interface)
    arp_subnet = getARPSubnet(machine_ip, target_subnets)
    icmp_subnets = getICMPSubnets(machine_ip, target_subnets)

    ## print("ARP Subnet: {}".format(arp_subnet))
    ## print("ICMP Subnets: {}".format(icmp_subnets))

    arp_results = arp_scan(arp_subnet)
    print("ARP Scan Completed!\n\n")

    icmp_results = icmp_scan(icmp_subnets)
    print("ICMP Scan Completed!\n\n")

    results = arp_results + icmp_results

    print("ARP Results:")
    print_result(arp_results)

    print("\n\nICMP Results:")
    print_result(icmp_results)

    print("\n\nRESULTS:")
    print_result(results)



if __name__ == "__main__":
    main()
