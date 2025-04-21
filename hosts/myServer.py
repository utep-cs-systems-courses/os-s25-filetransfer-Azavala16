import socket
import os
import sys

def recv_exact(fd, size):
    data = b''
    while len(data) < size:
        chunk = os.read(fd, size - len(data))
        if not chunk:
            raise ConnectionError("connection closed prematurely")
        data += chunk
    return data


def handle_client(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(10) # up to 10 connections allowed
    print(f"listening on {host}:{port}...")
    
    try:
        while True:
            try:
                conn, addr = s.accept()
            except KeyboardInterrupt:
                print("\nshutting down server..")
                break

            pid = os.fork()  # fork child, parent and child will have a copy of the listening and communication sockets
            if pid == 0:     # child forked successfully
                s.close()    # close listening socket and handle file reception using child
                receive_files(conn, addr) # child still uses communication socket
            else:
                conn.close() # close the copy of the communication socket the parent got since child handles it 
                             # parent makes use of the listening socket to accept new connections

    finally:
        try:
            s.shutdown(socket.SHUT_RDWR) # end communication from both ends of the socket
        except OSError:
            pass
        s.close() # free file descriptor referencing listening socket
        print("server socket closed")


def receive_files(conn, addr):
    print(f"child forked, [PID {os.getpid()}] connected by {addr}")
    fd = conn.fileno() # get fd to reference the socket for each new client connection

    try:
        while True:
            # get 4 bytes for filename length
            try:
                raw_fname_len = recv_exact(fd, 4)
            except ConnectionError:
                break
            fname_len = int.from_bytes(raw_fname_len, 'big')

            # get filename
            filename = recv_exact(fd, fname_len).decode()

            # get 4 bytes for content length
            raw_content_len = recv_exact(fd, 4)
            content_len = int.from_bytes(raw_content_len, 'big')

            # get content
            content = recv_exact(fd, content_len)

            # save file
            f = os.open(filename, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
            os.write(f, content)
            os.close(f)

            print(f"[PID {os.getpid()}] Received and saved: {filename}")

    except Exception as e:
        os.write(2, f"Error: {str(e)}\n".encode())
    finally:
        conn.close() # close file descriptor referencing communication socket
        print(f"[PID {os.getpid()}]  connection closed")
        os._exit(0) # child exits

if __name__ == "__main__":
    handle_client("0.0.0.0", 50001)

