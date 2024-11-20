from scapy.all import ARP, Ether, srp


target_ip = "200.168.56.1/24"
arp = ARP(pdst = target_ip)
ether = Ether(dst="ff:ff:ff:ff:ff:ff")
packet = ether/arp

def print_clients(clients):
    print("Available devices:")
    print("IP" + " "*18+"MAC")

    for client in clients:
        print("{:16}    {}".format(client['IP'], client['MAC']))

def main():
    result = srp(packet, timeout = 2)[0]

    clients = []

    for sent, received in result:
        clients.append({'IP': received.psrc, 'MAC': received.hwrc})
    
    print_clients(clients)


if __name__ == "__main__":
    main()