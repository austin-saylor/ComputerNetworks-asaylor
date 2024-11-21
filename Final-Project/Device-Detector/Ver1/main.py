from scapy.all import ICMP, IP, Ether, ARP, sr, srp

# Define the target subnet
target_ip = "192.168.2.0/24"  # Change to the subnet you want to scan

# Function to print clients
def print_clients(clients: list) -> None:
    print("Available devices:")
    print("IP" + " "*18 + "MAC (if available)")
    for client in clients:
        print("{:16}    {}".format(client['IP'], client.get('MAC', 'N/A')))

# Main function
def main() -> None:
    print("Sending ICMP Echo Requests...")
    clients = []

    # ICMP Scan
    try:
        result = sr(IP(dst=target_ip) / ICMP(), timeout=2, verbose=0)[0]
        for sent, received in result:
            clients.append({'IP': received.src, 'MAC': 'N/A'})  # Initially no MAC
    except KeyboardInterrupt:
        print("Script interrupted!")
        exit()

    # ARP Scan for MAC addresses
    print("Performing ARP Scan for MAC addresses...")
    result_arp = srp(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=target_ip), timeout=2, verbose=0)[0]
    for sent, received in result_arp:
        # Match the IPs with their MAC addresses
        clients.append({'IP': received.psrc, 'MAC': received.hwsrc})

    # Remove duplicates
    unique_clients = {client['IP']: client for client in clients}  # Deduplicate based on IP

    print_clients(list(unique_clients.values()))

if __name__ == "__main__":
    main()
