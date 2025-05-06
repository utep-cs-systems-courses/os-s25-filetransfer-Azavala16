import socket
import os
import sys
from threading import Thread

sys.path.append('/home/alex/OSHomeworks/Lab3/s25-archiver-Azavala16')
from mytar import extract_archive

class ServerWorker(Thread):

    # eacher server worker will handle its own client
    def __init__(self, conn, addr):
        super().__init__()
        self.conn = conn
        self.addr = addr

    def run(self):
        print(f"[thread {self.ident}] handling connection from {self.addr}")
        fd = self.conn.fileno()

        stdin_backup = os.dup(0)   # backup stdin (fd 0)
        os.dup2(fd, 0)             # redirect fd 0 to the socket
        
        try:
            extract_archive()     # call extract function (reads from stdin)
            print(f"[thread {self.ident}] extraction complete")
        finally:
            os.dup2(stdin_backup, 0)  # restore stdin
            os.close(stdin_backup)
            self.conn.close()
            print(f"[thread {self.ident}] connection closed")



def handle_client(host, port):

    # create listening socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # bind socket to a host and port number
    s.bind((host, port))
    s.listen(10) # up to ten connections

    print(f"threaded server listening on {host}:{port}...")

    try:
        while True:
            try:
                # accept connections, create communication socket
                conn, addr = s.accept()
                # create worker objects to handle client
                server_thread = ServerWorker(conn, addr)
                # execute worker
                server_thread.start()
            except KeyboardInterrupt:
                print("\nshutting down server...")
                break
    finally:
        s.close()
        print("server socket closed")


if __name__ == "__main__":
    handle_client("0.0.0.0", 50001)

