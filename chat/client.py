import socket
import threading
import os
import sys
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk


class Send(threading.Thread):
    # Listens for user input and sends messages to the server
    def __init__(self, sock, name, messages):
        super().__init__()
        self.sock = sock
        self.name = name
        self.messages = messages

    def run(self):
        while True:
            message = sys.stdin.readline().strip()
            if message == 'QUIT':
                self.sock.sendall(f'Server: {self.name} has left the chat.'.encode('ascii'))
                self.sock.close()
                os._exit(0)
            else:
                self.sock.sendall(f'{self.name}: {message}'.encode('ascii'))
                # Use 'after' to safely update the GUI from the sending thread
                self.messages.after(0, lambda: self.update_chat(f'{self.name}: {message}'))

    def update_chat(self, message):
        # Add message to the chat window
        self.messages.insert(tk.END, message)
        self.messages.after(0, lambda: self.messages.yview(tk.END))  # Auto-scroll to the bottom


class Receive(threading.Thread):
    # Listens for messages from the server and updates the GUI
    def __init__(self, sock, messages):
        super().__init__()
        self.sock = sock
        self.messages = messages

    def run(self):
        while True:
            try:
                message = self.sock.recv(1024).decode('ascii')
                if message:
                    # Use 'after' to safely update the GUI from the receiving thread
                    self.messages.after(0, lambda: self.update_chat(message))
                else:
                    print('Connection lost. Closing...')
                    self.sock.close()
                    os._exit(0)
            except Exception as e:
                print(f"Error receiving message: {e}")
                self.sock.close()
                os._exit(0)

    def update_chat(self, message):
        # Add received message to the chat window
        self.messages.insert(tk.END, message)
        self.messages.after(0, lambda: self.messages.yview(tk.END))  # Auto-scroll to the bottom


class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.name = None
        self.messages = None
        self.is_connected = False  # Track connection state

    def start(self):
        print(f'Trying to connect to {self.host}:{self.port}')
        try:
            self.sock.connect((self.host, self.port))  # Attempt to connect
            self.is_connected = True  # Update the connection status
            print(f'Connected to {self.host}:{self.port}')
        except Exception as e:
            print(f"Error connecting to server: {e}")
            return  # Exit if connection fails

        send_thread = Send(self.sock, self.name, self.messages)
        receive_thread = Receive(self.sock, self.messages)

        send_thread.start()
        receive_thread.start()

        self.sock.sendall(f'Server: {self.name} has joined the chat.'.encode('ascii'))
        print(f'You can leave the room by typing "QUIT".')

    def send(self, textInput):
        if not self.is_connected:
            print("Error: Not connected to server.")
            return  # Do not send if not connected

        message = textInput.get().strip()
        textInput.delete(0, tk.END)
        self.messages.insert(tk.END, f'{self.name}: {message}')
        self.messages.after(0, lambda: self.messages.yview(tk.END))  # Auto-scroll to the bottom

        if message == 'QUIT':
            self.sock.sendall(f'Server: {self.name} has left the chat.'.encode('ascii'))
            print('Quitting...')
            self.sock.close()
            os._exit(0)
        else:
            self.sock.sendall(f'{self.name}: {message}'.encode('ascii'))


def main(host, port):
    # Ask for the user's name before starting the GUI
    client = Client(host, port)
    client.name = input('Enter your name: ')  # Prompt for name here before launching GUI
    print(f'Welcome {client.name}! Ready to send and receive messages.')

    # Create the Tkinter GUI window
    window = tk.Tk()
    window.title('Chat')
 #   window.iconphoto(True, ImageTk.PhotoImage(Image.open('logo.png').resize((32, 32), Image.Resampling.LANCZOS)))

    fromMessage = tk.Frame(master=window)
    scrollbar = ttk.Scrollbar(master=fromMessage, orient=tk.VERTICAL)
    messages = tk.Listbox(master=fromMessage, height=20, width=50, yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y, expand=tk.FALSE)
    messages.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    fromEntry = tk.Frame(master=window)
    textInput = tk.Entry(master=fromEntry)
    textInput.pack(fill=tk.BOTH, expand=True)
    textInput.bind('<Return>', lambda x: client.send(textInput))  # Bind <Return> key
    textInput.insert(0, "Write your message here...")

    btnSend = tk.Button(master=window, text='Send', command=lambda: client.send(textInput))  # Send button
    fromEntry.grid(row=1, column=0, padx=10, sticky='ew')
    btnSend.grid(row=1, column=1, pady=10, sticky='ew')

    window.rowconfigure(0, minsize=500, weight=1)
    window.rowconfigure(1, minsize=50, weight=0)
    window.columnconfigure(0, minsize=500, weight=1)
    window.columnconfigure(1, minsize=200, weight=0)

    client.messages = messages  # Assign the messages listbox to client

    # Start the client connection in a separate thread after GUI setup
    threading.Thread(target=client.start, daemon=True).start()  # Start connection in a separate thread

    window.mainloop()  # Start the Tkinter main loop


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Client for the chat application")
    parser.add_argument('host', help='Server host (e.g., 127.0.0.1)')
    parser.add_argument('-p', metavar='port', type=int, default=1060, help='Server port (defaults to 1060)')

    args = parser.parse_args()

    main(args.host, args.p)
