import socket
import threading

HOST = "127.0.0.1"
PORT = 5001

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print("✅ Server is running...")

clients = {}       # conn → username
user_mode = {}     # username → broadcast/private
pairs = {}         # username → partner
lock = threading.Lock()

#  Broadcast
def broadcast(message, sender=None):
    for conn in list(clients.keys()):
        try:
            if conn != sender:
                conn.send(message.encode("utf-8"))
        except:
            remove_client(conn)

#  Private message
def send_to_partner(sender, message):
    if sender in pairs:
        partner = pairs[sender]

        for conn, username in clients.items():
            if username == partner:
                conn.send(f"[PRIVATE] {sender}: {message}".encode("utf-8"))

#  Remove client
def remove_client(conn):
    with lock:
        if conn in clients:
            username = clients[conn]

            # remove from pair
            if username in pairs:
                partner = pairs[username]
                del pairs[partner]
                del pairs[username]
                user_mode[partner] = "broadcast"

            del clients[conn]
            del user_mode[username]

            print(f"{username} disconnected")
            broadcast(f"🔴 {username} left the chat")

#  Connect users
def connect_users(user1, user2):
    pairs[user1] = user2
    pairs[user2] = user1

    user_mode[user1] = "private"
    user_mode[user2] = "private"

#  Handle client
def handle_client(conn, addr):
    print(f"📡 Connection from {addr}")

    try:
        conn.send("USERNAME".encode())
        username = conn.recv(1024).decode()

        with lock:
            clients[conn] = username
            user_mode[username] = "broadcast"

        print(f"✅ {username} joined")
        broadcast(f"🟢 {username} joined the chat")

        while True:
            data = conn.recv(1024)
            if not data:
                break

            message = data.decode()

            #  show users
            if message == "/users":
                user_list = ", ".join(clients.values())
                conn.send(f"👥 Users: {user_list}".encode())

            #  connect private
            elif message.startswith("/connect"):
                target = message.split(" ")[1]

                if target in clients.values():
                    connect_users(username, target)
                    conn.send(f"🔗 Connected with {target}".encode())
                else:
                    conn.send("❌ User not found".encode())

            #  back to broadcast
            elif message == "/back":
                if username in pairs:
                    partner = pairs[username]
                    del pairs[partner]
                    del pairs[username]
                    user_mode[partner] = "broadcast"

                user_mode[username] = "broadcast"
                conn.send("🔄 Back to broadcast".encode())

            #  send message
            else:
                if user_mode[username] == "private":
                    send_to_partner(username, message)
                else:
                    broadcast(f"{username}: {message}", conn)

    except:
        pass

    remove_client(conn)
    conn.close()

while True:
    conn, addr = server.accept()
    thread = threading.Thread(target=handle_client, args=(conn, addr))
    thread.start()