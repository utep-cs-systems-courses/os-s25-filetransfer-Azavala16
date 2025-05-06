import struct
import socket
import os
import sys
from threading import Thread

sys.path.append('/home/alex/OSHomeworks/Lab3/s25-archiver-Azavala16')
from mytar import create_archive  # use create_archive functionality

def handle_connection(host, port, files):
    sock = socket.create_connection((host, port))

    sock_fd = sock.fileno()   # get socket fd
    stdout_backup = os.dup(1) # backup stdout
    os.dup2(sock_fd, 1)       # redirect stdout to socket

    try:
        create_archive(files) # archive and send
    finally:
        os.dup2(stdout_backup, 1) # restore stdout
        os.close(stdout_backup)
        sock.shutdown(socket.SHUT_WR)
        sock.close()
        print(f"[{files}] Archive sent successfully from thread.")

# class to create workers using threads
class ClientWorker(Thread):
    def __init__(self, host, port, files):
        super().__init__()
        self.host = host
        self.port = port
        self.files = files

    # make each worker make its own connection with its own socket and args
    def run(self):
        handle_connection(self.host, self.port, self.files)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 threadedClient.py -s <host:port> <file1> [file2 ...]")
        sys.exit(1)

    proxy_address = sys.argv[2]
    proxy_host, proxy_port = proxy_address.split(":")
    proxy_port = int(proxy_port)

    files = sys.argv[3:]

    handle_connection(proxy_host, proxy_port, files)

    # simulate each thread to act as a client by making worker objects
    #clients = [ClientWorker(proxy_host, proxy_port, files) for _ in range(3)]

    #for client in clients:
    #    client.start()
    
    # main thread waits until all workers are finished
    #for client in clients:
    #    client.join()

