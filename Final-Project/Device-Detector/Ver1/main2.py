import threading
from scapy.all import srp, Ether, ARP, sr, IP, ICMP
import ipaddress

def get_active_hosts_arp(subnet, iface):
    """
    Perform ARP scan on a subnet.
    """
    print("Starting ARP scan on {}...".format(subnet))
    try:
        ans, _ = srp(
            Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=str(subnet)),
            timeout=2,
            retry=1,
            iface=iface,
            verbose=0
        )
        results = [{'IP': received.psrc, 'MAC': received.hwsrc} for sent, received in ans]
        return results
    except Exception as e:
        print("Error during ARP scan: {}".format(e))
        return []

def get_active_hosts_icmp(subnet):
    """
    Perform ICMP scan on a subnet.
    """
    print("Starting ICMP scan on {}...".format(subnet))
    try:
        ans, _ = sr(
            IP(dst=str(subnet)) / ICMP(),
            timeout=2,
            retry=1,
            verbose=0
        )
        results = [{'IP': received.src, 'MAC': 'N/A'} for sent, received in ans]
        return results
    except Exception as e:
        print("Error during ICMP scan: {}".format(e))
        return []

def scan_subnets(target_subnets, iface):
    results = []
    threads = []

    for subnet in target_subnets:
        # Perform ARP scan in a separate thread
        t = threading.Thread(target=lambda: results.extend(get_active_hosts_arp(subnet, iface)))
        threads.append(t)
        t.start()

        # Perform ICMP scan in a separate thread
        t = threading.Thread(target=lambda: results.extend(get_active_hosts_icmp(subnet)))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    return results

def print_result(results):
    print("{:<15} {:<17}".format("IP", "MAC"))
    print("-" * 30)
    for device in results:
        print("{:<15} {:<17}".format(device['IP'], device['MAC']))

if __name__ == "__main__":
    target_subnets = ["192.168.1.0/24", "192.168.2.0/24"]
    iface = "eth0"  # Replace with your interface
    results = scan_subnets(target_subnets, iface)
    print("\nScan Results:")
    print_result(results)
