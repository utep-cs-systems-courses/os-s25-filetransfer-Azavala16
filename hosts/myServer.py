import socket
import os
import sys
sys.path.append('/home/alex/OSHomeworks/Lab3/s25-archiver-Azavala16')

from mytar import extract_archive

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
                os._exit(0)
            else:
                conn.close() # close the copy of the communication socket the parent got since child handles it 
                             # parent makes use of the listening socket to accept new connections

    finally:
        s.close() # free file descriptor referencing listening socket
        print("server socket closed")


def receive_files(conn, addr):
    print(f"child forked, [PID {os.getpid()}] connected by {addr}")
    fd = conn.fileno() # get fd to reference the socket for each new client connection
    
    stdin_backup = os.dup(0) # make copy of stdin
    os.dup2(fd, 0)           # make the fd for communication socket point to fd0

    try:
        extract_archive()
        print(f"[PID {os.getpid()}] extraction complete")
    finally:
        os.dup2(stdin_backup, 0) # return fd0 to point stdin
        os.close(stdin_backup)   # close backup
        conn.close()             # close communication socket
        print(f"[PID {os.getpid()} connection closed]")


if __name__ == "__main__":
    handle_client("0.0.0.0", 50001)

