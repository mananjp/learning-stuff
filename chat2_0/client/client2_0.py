import socket
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import time
import json

HOST = '127.0.0.1'  # Server IP
PORT = 5000  # Server Port


class ModernChatClient:
    def __init__(self, root):
        self.root = root
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f2f5')

        # Set window title
        self.root.title("Escape Room")

        # Initialize variables
        self.username = None
        self.room = None
        self.client = None
        self.running = True
        self.chat_frame = None
        self.message_thread = None
        self.is_leaving = False  # Flag to prevent multiple leave prompts
        self.connected = False  # Flag to track connection status
        self.message_history = []  # Store message history

        # Create main container
        self.main_container = ttk.Frame(root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Show login frame first
        self.show_login_frame()

    def show_login_frame(self):
        """Display the login and room selection interface"""
        # Clean up existing frames if any
        for widget in self.main_container.winfo_children():
            widget.destroy()

        self.login_frame = ttk.Frame(self.main_container)
        self.login_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(self.login_frame, text="Escape Room",
                                font=("Helvetica", 24, "bold"))
        title_label.pack(pady=20)

        # Username entry
        username_frame = ttk.Frame(self.login_frame)
        username_frame.pack(pady=10)
        ttk.Label(username_frame, text="Username:").pack(side=tk.LEFT)
        self.username_entry = ttk.Entry(username_frame, width=30)
        self.username_entry.pack(side=tk.LEFT, padx=5)

        # Room selection
        room_frame = ttk.Frame(self.login_frame)
        room_frame.pack(pady=10)
        ttk.Label(room_frame, text="Room:").pack(side=tk.LEFT)
        self.room_entry = ttk.Entry(room_frame, width=30)
        self.room_entry.pack(side=tk.LEFT, padx=5)

        # Room actions
        actions_frame = ttk.Frame(self.login_frame)
        actions_frame.pack(pady=20)

        ttk.Button(actions_frame, text="Create Room",
                   command=self.create_room).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Join Room",
                   command=self.join_room).pack(side=tk.LEFT, padx=5)

        # Exit button
        exit_button = ttk.Button(self.login_frame, text="Exit",
                                 command=self.on_closing)
        exit_button.pack(pady=20)

    def create_room(self):
        """Handle room creation"""
        self.username = self.username_entry.get().strip()
        self.room = self.room_entry.get().strip()

        if not self.username or not self.room:
            messagebox.showerror("Error", "Please enter both username and room name!")
            return

        self.connect_to_server("create")

    def join_room(self):
        """Handle joining existing room"""
        self.username = self.username_entry.get().strip()
        self.room = self.room_entry.get().strip()

        if not self.username or not self.room:
            messagebox.showerror("Error", "Please enter both username and room name!")
            return

        self.connect_to_server("join")

    def connect_to_server(self, action):
        """Connect to the server and initialize chat"""
        try:
            # Close existing connection if any
            if self.client:
                try:
                    self.client.close()
                except:
                    pass
                self.client = None
                self.connected = False

            # Create new connection
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.settimeout(5)  # Set a timeout for connection
            self.client.connect((HOST, PORT))
            self.connected = True

            # Send user info to server with small delays to prevent flooding
            self.client.send(self.username.encode())
            time.sleep(0.1)  # Small delay between sends
            self.client.send(self.room.encode())
            time.sleep(0.1)  # Small delay between sends
            self.client.send(action.encode())

            # Wait for server response
            response = self.client.recv(1024).decode()

            # Handle different server responses
            if response == "room_not_found":
                messagebox.showerror("Error", "Room not found! Please create the room first.")
                self.client.close()
                self.client = None
                self.connected = False
                return
            elif response == "room_exists":
                messagebox.showerror("Error", "Room already exists! Please join instead.")
                self.client.close()
                self.client = None
                self.connected = False
                return
            elif response == "invalid_action":
                messagebox.showerror("Error", "Invalid action! Please try again.")
                self.client.close()
                self.client = None
                self.connected = False
                return
            elif response not in ["room_created", "room_joined"]:
                # Try to parse as JSON (chat history)
                try:
                    self.message_history = json.loads(response)
                    # Wait for the room_joined message
                    response = self.client.recv(1024).decode()
                    if response != "room_joined":
                        messagebox.showerror("Error", f"Server error: {response}")
                        self.client.close()
                        self.client = None
                        self.connected = False
                        return
                except json.JSONDecodeError:
                    messagebox.showerror("Error", f"Server error: {response}")
                    self.client.close()
                    self.client = None
                    self.connected = False
                    return

            # Show chat interface
            self.show_chat_frame()

            # Display chat history if available
            if self.message_history:
                for message in self.message_history:
                    self.display_message(message)

            # Start message receiving thread
            self.running = True
            self.message_thread = threading.Thread(target=self.receive_messages, daemon=True)
            self.message_thread.start()

        except socket.timeout:
            messagebox.showerror("Connection Error", "Connection timed out. Please try again.")
            if self.client:
                self.client.close()
                self.client = None
                self.connected = False
        except ConnectionRefusedError:
            messagebox.showerror("Connection Error", "Could not connect to server. Make sure the server is running.")
            if self.client:
                self.client.close()
                self.client = None
                self.connected = False
        except socket.error as e:
            messagebox.showerror("Connection Error", f"Unable to connect to server: {e}")
            if self.client:
                self.client.close()
                self.client = None
                self.connected = False
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {e}")
            if self.client:
                self.client.close()
                self.client = None
                self.connected = False

    def show_chat_frame(self):
        """Display the main chat interface"""
        # Clear login frame
        if hasattr(self, 'login_frame'):
            self.login_frame.destroy()

        # Create chat container
        chat_container = ttk.Frame(self.main_container)
        chat_container.pack(fill=tk.BOTH, expand=True)

        # Top bar with room info and navigation
        top_bar = ttk.Frame(chat_container)
        top_bar.pack(fill=tk.X, pady=5)

        # Room info
        room_info = ttk.Label(top_bar, text=f"Room: {self.room} | User: {self.username}",
                              font=("Helvetica", 12))
        room_info.pack(side=tk.LEFT, padx=5)

        # Navigation buttons
        nav_frame = ttk.Frame(top_bar)
        nav_frame.pack(side=tk.RIGHT, padx=5)

        back_button = ttk.Button(nav_frame, text="Back to Login",
                                 command=self.back_to_login)
        back_button.pack(side=tk.LEFT, padx=5)

        exit_button = ttk.Button(nav_frame, text="Exit",
                                 command=self.on_closing)
        exit_button.pack(side=tk.LEFT, padx=5)

        # Chat display area
        self.chat_frame = ttk.Frame(chat_container)
        self.chat_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.text_area = tk.Text(self.chat_frame, wrap=tk.WORD, state='disabled',
                                 font=("Helvetica", 10), bg='white')
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Message input area
        input_frame = ttk.Frame(chat_container)
        input_frame.pack(fill=tk.X, pady=5)

        self.message_entry = ttk.Entry(input_frame)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.message_entry.bind("<Return>", lambda e: self.send_message())

        send_button = ttk.Button(input_frame, text="Send", command=self.send_message)
        send_button.pack(side=tk.RIGHT)

    def back_to_login(self):
        """Handle returning to login screen"""
        if self.is_leaving:
            return
        
        if messagebox.askyesno("Leave Room", "Are you sure you want to leave the chat room?"):
            self.is_leaving = True
            # Stop the message receiving thread
            self.running = False

            # Close the client connection
            if self.client and self.connected:
                try:
                    self.client.send("leave".encode())
                    # Wait for server acknowledgment
                    try:
                        response = self.client.recv(1024).decode()
                        if response == "left_room":
                            print("Successfully left the room")
                    except:
                        pass
                except:
                    pass
                finally:
                    self.client.close()
                    self.client = None
                    self.connected = False

            # Clean up chat frame
            if hasattr(self, 'chat_frame'):
                self.chat_frame.destroy()

            # Reset variables
            self.username = None
            self.room = None
            self.is_leaving = False

            # Show login frame
            self.show_login_frame()

    def send_message(self):
        """Send a message to the chat room"""
        message = self.message_entry.get().strip()
        if message and self.connected:
            timestamp = datetime.now().strftime("%H:%M")
            formatted_message = f"[{timestamp}] {self.username}: {message}"
            try:
                self.client.send(formatted_message.encode())
                self.display_message(formatted_message)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to send message: {e}")
                self.connected = False
                self.back_to_login()  # Return to login if message sending fails
            self.message_entry.delete(0, tk.END)

    def receive_messages(self):
        """Receive and display messages"""
        while self.running and self.connected:
            try:
                message = self.client.recv(1024).decode()
                if not message:
                    self.connected = False
                    break
                if message == "left_room":
                    self.connected = False
                    break
                self.root.after(0, self.display_message, message)
            except socket.timeout:
                # Timeout is normal, continue the loop
                continue
            except socket.error:
                if not self.is_leaving:  # Only show error if we're not already leaving
                    self.root.after(0, lambda: messagebox.showerror("Connection Error", "Lost connection to server"))
                    self.root.after(0, self.back_to_login)
                self.connected = False
                break
            except Exception as e:
                print(f"Error receiving message: {e}")
                self.connected = False
                break

    def display_message(self, message):
        """Display received message in the text area"""
        try:
            self.text_area.config(state='normal')
            self.text_area.insert(tk.END, message + "\n")
            self.text_area.config(state='disabled')
            self.text_area.see(tk.END)
        except Exception as e:
            print(f"Error updating GUI: {e}")

    def on_closing(self):
        """Handle window closing"""
        if messagebox.askyesno("Exit", "Are you sure you want to exit the application?"):
            self.running = False
            if self.client and self.connected:
                try:
                    self.client.send("exit".encode())
                except:
                    pass
                self.client.close()
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ModernChatClient(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
