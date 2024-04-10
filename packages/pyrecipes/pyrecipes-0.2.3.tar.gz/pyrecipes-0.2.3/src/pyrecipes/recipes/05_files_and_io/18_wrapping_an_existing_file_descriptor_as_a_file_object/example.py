"""
You have an integer file descriptor corresponding to an already open I/O
channel on the operating system (e.g. file, pipe, socket etc.) and you want
to wrap a higher level Python file object around it.
"""
import os
from socket import socket, AF_INET, SOCK_STREAM
from pathlib import Path

filename = Path(__file__).parent / "somefile.txt"


def echo_client(client_sock, addr):
    print("Got connection from", addr)

    # Make text-mode file wrappers for socket reading/writing
    client_in = open(client_sock.fileno(), "rt", encoding="latin-1", closefd=False)
    client_out = open(client_sock.fileno(), "wt", encoding="latin-1", closefd=False)

    # Echo lines back to the client using file I/O
    for line in client_in:
        client_out.write(line)
        client_out.flush()
    client_sock.close()


def echo_server(address):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind(address)
    sock.listen(1)
    while True:
        client, addr = sock.accept()
        echo_client(client, addr)


def example_1():
    # Open a low-level file descriptor
    fd = open(str(filename.resolve()), os.O_WRONLY | os.O_CREAT)

    # Turn into a proper file
    f = open(fd, "wt")
    f.write("hello world\n")
    f.close()


def main():
    pass


if __name__ == "__main__":
    main()
