from scapy.all import ARP, Ether, srp
import socket

def get_local_ip():
    try:
        # Get the IP address of the default gateway (router)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        print(f"Error obtaining local IP address: {e}")
        return None

def get_network_range(local_ip):
    ip_parts = local_ip.split('.')
    network_range = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.1/24"
    return network_range

def scan_network(network_range):
    print(f"Scanning network: {network_range}")
    arp = ARP(pdst=network_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp

    result = srp(packet, timeout=2, verbose=False)[0]

    devices = []
    for sent, received in result:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})

    return devices

def main():
    local_ip = get_local_ip()
    if not local_ip:
        print("Could not obtain local IP address.")
        return

    network_range = get_network_range(local_ip)
    devices = scan_network(network_range)

    if devices:
        print("Devices found on the network:")
        for device in devices:
            print(f"IP: {device['ip']}, MAC: {device['mac']}")
    else:
        print("No devices found.")

if __name__ == "__main__":
    main()
