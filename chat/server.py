import socket
import threading
import argparse
import os


class Server(threading.Thread):
    def __init__(self, host, port):
        super().__init__()
        self.connections = []
        self.host = host
        self.port = port

    def run(self):
        print(f"Creating socket...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            print(f"Binding to {self.host}:{self.port}...")
            sock.bind((self.host, self.port))
            sock.listen(1)
            print(f"Listening at {sock.getsockname()}")
        except Exception as e:
            print(f"Error binding to {self.host}:{self.port} - {e}")
            return

        while True:
            # Accept new connection
            sc, sockname = sock.accept()
            print(f"Connection from {sc.getpeername()} to {sc.getsockname()}")

            # Create new thread for this connection
            server_socket = ServerSocket(sc, sockname, self)
            server_socket.start()
            # Add the thread to active connections
            self.connections.append(server_socket)
            print(f"Ready to receive messages from {sc.getpeername()}")

    def broadcast(self, message, source):
        for connection in self.connections:
            # Send to all connected clients except the source client
            if connection.sockname != source:
                connection.send(message)

    def removeconnection(self, connection):
        self.connections.remove(connection)
        print(f"Connection {connection.sockname} removed")


class ServerSocket(threading.Thread):
    def __init__(self, sc, sockname, server):
        super().__init__()
        self.sc = sc
        self.sockname = sockname
        self.server = server

    def run(self):
        while True:
            try:
                message = self.sc.recv(1024).decode('ascii')
                if message:
                    print(f"{self.sockname} says: {message}")
                    self.server.broadcast(message, self.sockname)
                else:
                    print(f"{self.sockname} closed")
                    self.sc.close()
                    self.server.removeconnection(self)
                    return
            except Exception as e:
                print(f"Error receiving data from {self.sockname}: {e}")
                break

    def send(self, message):
        try:
            self.sc.sendall(message.encode('ascii'))
        except Exception as e:
            print(f"Error sending message to {self.sockname}: {e}")


def shutdown(server):
    while True:
        ipt = input("Type 'q' to shutdown the server: ")
        if ipt == "q":
            print("Closing server connections...")
            for connection in server.connections:
                connection.sc.close()

            print("Shutting down server")
            os._exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Server Chat")
    parser.add_argument('host', help='Interface server listens at')
    parser.add_argument('-p', metavar='port', type=int, default=1060, help='Server port (defaults to 1060)')

    args = parser.parse_args()

    print(f"Starting server on {args.host}:{args.p}...")

    # Create and start the server thread
    server = Server(args.host, args.p)
    server.start()

    # Start the shutdown thread
    shutdown_thread = threading.Thread(target=shutdown, args=(server,))
    shutdown_thread.start()
