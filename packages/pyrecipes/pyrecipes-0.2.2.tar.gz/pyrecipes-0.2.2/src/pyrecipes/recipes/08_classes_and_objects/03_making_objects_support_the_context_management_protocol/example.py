"""
You want to make your objects support the context-management
protocol (the with statement).
"""
from socket import socket, AF_INET, SOCK_STREAM
from functools import partial


class LazyConnection:
    def __init__(self, address, family=AF_INET, type=SOCK_STREAM):
        self.address = address
        self.family = family
        self.type = type
        self.sock = None

    def __enter__(self):
        if self.sock is not None:
            raise RuntimeError("Already connected")
        self.sock = socket(self.family, self.type)
        self.sock.connect(self.address)
        return self.sock

    def __exit__(self, exc_ty, exc_val, tb):
        self.sock.close()
        self.sock = None


def main():
    conn = LazyConnection(("www.python.org", 80))
    # Connection closed
    with conn as s:
        print("conn.__enter__() executes: connection opens", end="\n\n")
        s.send(b"GET /index.html HTTP/1.0\r\n")
        s.send(b"Host: www.python.org\r\n")
        s.send(b"\r\n")
        resp = b"".join(iter(partial(s.recv, 8192), b""))
        print(resp.decode())
        print("conn.__exit__() executes: connection closes")


if __name__ == "__main__":
    main()
