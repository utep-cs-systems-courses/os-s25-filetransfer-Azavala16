import struct
import socket
import os
import sys

sys.path.append('/home/alex/OSHomeworks/Lab3/s25-archiver-Azavala16')
from mytar import create_archive # use create_archive functionality

def handle_connection(host, port, files):
    sock = socket.create_connection((host, port))

    sock_fd = sock.fileno()   # make a fd to to reference connection socket fd3
    stdout_backup = os.dup(1) # make a copy of stdout at fd4
    os.dup2(sock_fd, 1)       # make a copy of the reference to the socket where stdout was (fd1)

    try:
        create_archive(files) # archive files and send them through socket which is now referenced by fd1
    finally:
        os.dup2(stdout_backup, 1) # return stdout to reference fd1
        os.close(stdout_backup)
        sock.shutdown(socket.SHUT_WR)
        sock.close()
        print("Archive sent successfully")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 helloClient.py -s <proxy_host:proxy_port> <file1> [file2 ...]")
        sys.exit(1)

    # parse the proxy address (e.g., localhost:50000)
    proxy_address = sys.argv[2]
    proxy_host, proxy_port = proxy_address.split(":")
    proxy_host = proxy_host.strip()
    proxy_port = int(proxy_port.strip())

    # list of files to send
    files = sys.argv[3:]

    handle_connection(proxy_host, proxy_port, files)
