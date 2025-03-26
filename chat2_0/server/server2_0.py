import socket
import threading
import argparse
import time
import json
import os

# Default host and port
DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 5000

# Thread-safe data structures
clients = {}  # {client_socket: {"username": str, "room": str}}
active_rooms = set()  # Track active rooms
room_history = {}  # {room_name: [message1, message2, ...]}
lock = threading.Lock()  # Lock for thread-safe operations

# Create a directory for chat history if it doesn't exist
HISTORY_DIR = "chat_history"
if not os.path.exists(HISTORY_DIR):
    os.makedirs(HISTORY_DIR)

def load_room_history(room):
    """Load chat history for a room from file."""
    history_file = os.path.join(HISTORY_DIR, f"{room}.json")
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_room_history(room, history):
    """Save chat history for a room to file."""
    history_file = os.path.join(HISTORY_DIR, f"{room}.json")
    try:
        with open(history_file, 'w') as f:
            json.dump(history, f)
    except Exception as e:
        print(f"Error saving history for room {room}: {e}")

def create_server(host, port):
    """Create and initialize the server socket."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow reuse of address
    server.bind((host, port))
    server.listen()
    return server

def broadcast(message, room, sender_socket=None):
    """Send a message to all users in a specific chat room."""
    with lock:
        disconnected_clients = []
        for client, info in clients.items():
            if info["room"] == room and client != sender_socket:
                try:
                    client.send(message.encode())
                except socket.error:
                    disconnected_clients.append(client)
        
        # Clean up disconnected clients
        for client in disconnected_clients:
            remove_client(client)

def remove_client(client):
    """Remove a client from the active clients list and clean up the room."""
    with lock:
        if client in clients:
            room = clients[client]["room"]
            username = clients[client]["username"]
            del clients[client]
            print(f"Cleaned up client connection for {username}")
            
            # Check if room is empty by counting remaining clients in the room
            remaining_clients = sum(1 for info in clients.values() if info["room"] == room)
            if remaining_clients == 0:
                active_rooms.discard(room)
                print(f"Room {room} is now empty and has been removed")
            else:
                print(f"Room {room} still has {remaining_clients} clients")

def handle_client(client):
    """Handle communication for a single client."""
    try:
        # Set socket timeout for receiving messages
        client.settimeout(1.0)  # 1 second timeout
        
        # Receive client information
        username = client.recv(1024).decode()
        if not username:
            print("Empty username received")
            return
            
        room = client.recv(1024).decode()
        if not room:
            print("Empty room received")
            return
            
        action = client.recv(1024).decode()
        if not action:
            print("Empty action received")
            return

        # Handle room creation/joining
        with lock:
            if action == "create":
                if room in active_rooms:
                    client.send("room_exists".encode())
                    client.close()
                    return
                active_rooms.add(room)
                # Load existing history if any
                room_history[room] = load_room_history(room)
                client.send("room_created".encode())
                print(f"Created new room: {room}")
            elif action == "join":
                if room not in active_rooms:
                    client.send("room_not_found".encode())
                    client.close()
                    return
                # Load existing history if not already loaded
                if room not in room_history:
                    room_history[room] = load_room_history(room)
                # Send history to the new client
                history_json = json.dumps(room_history[room])
                client.send(history_json.encode())
                time.sleep(0.1)  # Small delay between sends
                client.send("room_joined".encode())
                print(f"User {username} joined room: {room}")
            else:
                client.send("invalid_action".encode())
                client.close()
                return

            # Add client to clients dictionary
            clients[client] = {"username": username, "room": room}

        print(f"📢 {username} {'created' if action == 'create' else 'joined'} room: {room}")
        broadcast(f"🔵 {username} joined the chat!", room, client)

        while True:
            try:
                message = client.recv(1024).decode()
                if not message:
                    break
                if message.lower() == "exit":
                    print(f"❌ {username} left the chat.")
                    broadcast(f"❌ {username} left the chat.", room, client)
                    break
                elif message.lower() == "leave":
                    print(f"❌ {username} left the room.")
                    broadcast(f"❌ {username} left the room.", room, client)
                    remove_client(client)
                    client.send("left_room".encode())  # Inform the client they left
                    break
                
                # Add message to room history
                with lock:
                    if room in room_history:
                        room_history[room].append(message)
                        # Save history to file
                        save_room_history(room, room_history[room])
                
                broadcast(message, room, client)
            except socket.timeout:
                # Timeout is normal, continue the loop
                continue
            except socket.error:
                print(f"Socket error for {username}")
                break

    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        remove_client(client)
        try:
            client.close()
        except socket.error:
            pass

def main():
    """Main server function."""
    parser = argparse.ArgumentParser(description="Start the server")
    parser.add_argument('host', type=str, nargs='?', default=DEFAULT_HOST, help="The host address")
    parser.add_argument('-p', '--port', type=int, default=DEFAULT_PORT, help="The port number")

    args = parser.parse_args()

    try:
        server = create_server(args.host, args.port)
        print(f"🚀 Server started on {args.host}:{args.port}")
        print("Press Ctrl+C to stop the server")

        while True:
            try:
                client, address = server.accept()
                print(f"✅ New connection from {address}")
                threading.Thread(target=handle_client, args=(client,), daemon=True).start()
            except Exception as e:
                print(f"Error accepting connection: {e}")
                continue

    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        try:
            server.close()
        except socket.error:
            pass

if __name__ == "__main__":
    main()
