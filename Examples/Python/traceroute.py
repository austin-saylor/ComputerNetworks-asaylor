from scapy.all import *


def main() -> None:
    hostname = input("Enter host to trace: ")
    for i in range(1, 31):
        pkt = IP(dst=hostname, ttl=i)/UDP(dport=33434)
        reply = sr1(pkt, verbose=0, timeout=2)
        if reply is None:
            continue
        elif reply.type == 3:
            print(f"Done: {reply.src}")
            break
        else:
            print(f"{i} hops away: {reply.src}")

if __name__ == "__main__":
    main()