import socket
import threading

HOST = "127.0.0.1"
PORT = 5001

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

username = input("Enter username: ")

#  Receive
def receive():
    while True:
        try:
            msg = client.recv(1024).decode()

            if msg == "USERNAME":
                client.send(username.encode())
            else:
                print(msg)

        except:
            print("❌ Disconnected from server")
            client.close()
            break

#  Send
def send():
    while True:
        try:
            msg = input()
            client.send(msg.encode())
        except:
            break

# ✅ Threads
threading.Thread(target=receive).start()
threading.Thread(target=send).start()