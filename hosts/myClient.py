import struct
import socket
import os
import sys

def send_file(sock, filepath):
    # extract the filename from the path and turn to bytes
    filename = os.path.basename(filepath).encode()
    fname_len = len(filename)

    fd = os.open(filepath, os.O_RDONLY) # open file to send
    content = b''
    while True:
        chunk = os.read(fd, 4096) # read contents in chunks
        if not chunk:
            break
        content += chunk
    os.close(fd)

    content_len = len(content) # get length of content to keep track of what is being sent to the server
    
    # encode the filename length into 4 bytes using big-endian   (i.e 00 00 00 07 "foo.txt")
    os.write(sock.fileno(), fname_len.to_bytes(4, 'big'))

    # send N bytes for the filename in ASCII
    os.write(sock.fileno(), filename)

    # encode content length into 4 bytes as well
    os.write(sock.fileno(), content_len.to_bytes(4, 'big'))
    
    # send M bytes for content
    total_sent = 0
    while total_sent < content_len:
        sent = os.write(sock.fileno(), content[total_sent:])
        total_sent += sent

    print(f"Sent: {filepath}")


def handle_connection(host, port, files):
    sock = socket.create_connection((proxy_host, proxy_port))
    for file in files:
        send_file(sock, file)
    
    sock.shutdown(socket.SHUT_WR)
    sock.close()



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
