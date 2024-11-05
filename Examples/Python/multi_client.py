import socket


def main() -> None:
    destinaddr = "127.0.0.1"
    destport = 1234

    username = input("Enter username: ")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((destaddr, destport))
        s.setblocking(False)

        s.send(username.encode())

        while True:
            send_msg = input("Send: ")
            if len(send_msg) > 0:
                s.send(send_msg.encode())
            try:
                recv_msg = s.recv(1024).decode()
                print(f"{recv_msg}")
            except:
                continue


if __name__ == "__main__":
    main()