from scapy.all import ICMP, IP, sr1, sr

target_ip = "192.168.2.0/24"  # Change to the subnet of the Ubuntu VPC
packet = IP(dst=target_ip)/ICMP()

def print_clients(clients: list) -> None:
    print("Available devices:")
    print("IP" + " "*18+"MAC (if available)")

    for client in clients:
        print("{:16}    {}".format(client['IP'], client.get('MAC', 'N/A')))

def main() -> None:
    print("Sending ICMP Echo Requests...")
    result = sr(IP(dst=target_ip)/ICMP(), timeout=2, verbose=0)[0]

    clients = []

    for sent, received in result:
        clients.append({'IP': received.src})

    print_clients(clients)

if __name__ == "__main__":
    main()
