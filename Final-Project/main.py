import sys
import socket
import fcntl
import struct
import ipaddress
from scapy.all import *

# 8.5-minute runtime with /24
# 30-second runtime with /28

def get_ip(interface):
    """
    Get the ip address of the machine on the specified interface.

    :param interface: string representing the interface that the 
                      ip address will be extracted from.
    :return: string representing the ip address on the interface.
    """

    # Create a socket to use for ip extraction
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Retrieve the IP address
        ip_address = fcntl.ioctl(
            s.fileno(),
            0x8915,
            struct.pack('256s', interface[:15].encode('utf-8'))
        )[20:24]
        return socket.inet_ntoa(ip_address)
    except IOError:
        return None

def get_subnets(machine_ip, target_subnets):
    """
    Determine which of the target subnets the machine is on,
    then return that subnet as the target subnet for the ARP scan
    and return the rest of the subnets as the target subnets for the
    ICMP scan.

    :param machine_ip: string representing the ip address of the machine.
    :param target_subnet: list of strings representing the target subnets
    :return: tuple[str, list[str]] - a string representing the target subnet for
             the ARP scan and a list of strings representing the target subnet(s)
             for the ICMP scan. 
    """
    index = 0

    arp_subnet = ""
    icmp_subnets = []
    for subnet in target_subnets:
        match = False
        target_ips = [str(ip) for ip in ipaddress.IPv4Network(subnet, strict=False)]

        for target_ip in target_ips:
            if (target_ip == machine_ip):
                match = True

                # If the ip matches the machine, set the current subnet as the ARP subnet
                arp_subnet = target_subnets[index]
                break
            else:
                continue
        
        if match == False:
            # If there is no match on the subnet, add it to the ICMP subnets
            icmp_subnets.append(target_subnets[index])
        
        index += 1
    
    if not arp_subnet:
        arp_subnet = "255.255.255.255"
    if not icmp_subnets:
        icmp_subnets = ["255.255.255.255"]
    
    return arp_subnet, icmp_subnets

def arp_scan(subnet):
    """
    Execute an ARP scan on the given subnet.

    :param subnet: string representing the subnet being scanned.
    :return: list of lists - a list of strings representing the
             online ip addresses detected and a list of strings
             representing their corresponding mac addresses.
    """
    print("Running ARP Scan...")
    target_ips = [str(ip) for ip in ipaddress.IPv4Network(subnet, strict=False)]
    try:
        print("ARP: Sending ARP requests...")
        ips = []
        macs = []
        for ip in target_ips:
            print("ARP: Scanning {}...".format(ip))

            # Send an ARP request
            request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip)
            ans, unans = srp(request, timeout=1, retry=0, iface="eth0", verbose=0)
            for sent, received in ans:
                # If a response is received, add the ip and mac to their lists
                ips.append(received.psrc)
                macs.append(received.hwsrc)
        result = [ips, macs]
        print("ARP Scan Completed!\n\n")
        return result
    except Exception as e:
        print("Error during ARP scan: {}".format(e))
        return []

def icmp_scan(target_subnets):
    """
    Execut an ICMP scan on the given subnet(s).

    :param target_subnets: list of strings representing the subnets
                           being scanned.
    :return: list of strings representing the online ip addresses detected.
    """
    print("Running ICMP Scan...")
    try:
        result = []
        for subnet in target_subnets:
            target_ips = [str(ip) for ip in ipaddress.IPv4Network(subnet, strict=False)]
            for ip in target_ips:
                print("ICMP: Scanning {}...".format(ip))

                # Send an ICMP request
                response = sr1(IP(dst=ip) / ICMP(), timeout=1, verbose=0)
                if response:
                    # If there is a response, add the ip address to the result
                    result.append(response.src)
        print("ICMP Scan Completed!\n\n")
        return result
    except Exception as e:
        print("Error during ICMP scan: {}".format(e))
        return []

def port_scan(target_ips, n):
    """
    Execute a port scan on ports 1 through 'p' on the given
    ip addresses.

    :param target_ips: list of strings representing the ip addresses
                       being scanned.
    :param p: integer representing the number of ports to be checked.
    :return: list of integers representing the ports that are open.
    """
    print("Running port Scan...")

    # Create a socket to be used for the scan
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = []

    for target_ip in target_ips:
        ports = []
        for i in range(n):
            try:
                # Use the socket to attempt a connection on the current port
                connection = s.connect((target_ip, i))

                # If the connection is successful, add the port to the list
                ports.append(i)
            except:
                continue
        result.append(ports)
    print("Port Scan Completed!\n\n")
    return result


def print_results(results):
    """
    Print the results from the scans.

    :param results: list of lists representing the results of the
                    different scans.
    :return: None.
    """

    # Extract the results from the different scans
    arp_results, icmp_results, port_results = results

    # Gather IP and MAC results
    ips = arp_results[0] + icmp_results
    macs = arp_results[1]

    # Align the length of 'port_results' with 'ips'
    while len(port_results) < len(ips):
        port_results.append([])

    # Print the header
    print("\n\n" + " "*23 + "RESULTS:")
    print("IP" + " "*14 + "MAC" + " "*19 + "Open Ports")
    print("-"*55)

    i = 0
    for device in ips:
        # Handle printing of the mac address results
        mac = ""
        if 0 <= i < len(macs):
            mac = macs[i]
        else:
            mac = "*"*17
        
        # Handle printing of the port results
        ports = ", ".join(map(str, port_results[i])) if port_results[i] else "None"

        # Print details on the current device
        print('{}     {}     {}'.format(ips[i], mac, ports))
        i += 1


def main():
    # Define explicit settings for the scans
    interface = "eth0"
    target_subnets = ["192.168.1.0/28", "192.168.2.0/28"]

    # Get the machine IP and the subnets to be targeted by ARP and ICMP scans
    machine_ip = get_ip(interface)
    arp_subnet, icmp_subnets = get_subnets(machine_ip, target_subnets)

    # Run ARP and ICMP scans
    arp_results = arp_scan(arp_subnet)
    icmp_results = icmp_scan(icmp_subnets)

    # Gather the IPs found by both scans
    target_ips = arp_results[0] + icmp_results

    # Run a port scan on the online IPs
    port_results = port_scan(target_ips, 100)

    # Gather and print results
    results = [arp_results, icmp_results, port_results]
    print_results(results)


if __name__ == "__main__":
    main()