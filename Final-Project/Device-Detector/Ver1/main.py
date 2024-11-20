from scapy.all import ARP, Ether, srp


target_ip = "192.168.1.1/24"
arp = ARP(pdst = target_ip)
ether = Ether(dst="ff:ff:ff:ff:ff:ff")
packet = ether/arp

def print_clients(clients: list) -> None:
    print("Available devices:")
    print("IP" + " "*18+"MAC")

    for client in clients:
        print("{:16}    {}".format(client['IP'], client['MAC']))

def main() -> None:
    result = srp(packet, timeout = 2)[0]

    clients = []

    for sent, received in result:
        clients.append({'IP': received.psrc, 'MAC': received.hwsrc})
    
    print_clients(clients)


if __name__ == "__main__":
    main()