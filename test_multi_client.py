import threading
import socket
import ssl
import json
import time

SERVER_IP = "192.168.56.101"
SERVER_PORT = 9999
CERTFILE = "server.crt"

def send_json(conn, data):
    message = json.dumps(data) + "\n"
    conn.sendall(message.encode())

def recv_json(conn):
    data = b""
    while True:
        chunk = conn.recv(4096)
        if not chunk:
            return None
        data += chunk
        if b"\n" in data:
            break
    return json.loads(data.decode().strip())

def run_client(client_id, username, password, commands):
    """Simulates one complete client session"""
    try:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.load_verify_locations(CERTFILE)
        context.check_hostname = False

        raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn = context.wrap_socket(raw_socket, server_hostname="localhost")
        conn.connect((SERVER_IP, SERVER_PORT))

        start_time = time.time()

        # Login
        recv_json(conn)  # welcome message
        send_json(conn, {"username": username, "password": password})
        response = recv_json(conn)

        if response["status"] != "success":
            print(f"[Client {client_id}] Login FAILED")
            return

        token = response["token"]
        print(f"[Client {client_id}] Logged in as '{username}'")

        # Send commands
        for cmd in commands:
            send_json(conn, {"token": token, "command": cmd})
            result = recv_json(conn)
            print(f"[Client {client_id}] CMD='{cmd}' → STATUS={result['status']}")

        # Exit
        send_json(conn, {"token": token, "command": "exit"})
        recv_json(conn)

        end_time = time.time()
        print(f"[Client {client_id}] Done in {end_time - start_time:.2f} seconds")
        conn.close()

    except Exception as e:
        print(f"[Client {client_id}] Error: {e}")

# ── Define clients and what they do ──────────────────────
clients = [
    (1, "admin", "admin123", ["whoami", "ls", "pwd"]),
    (2, "user1", "pass123",  ["date", "hostname", "uname"]),
    (3, "admin", "admin123", ["pwd", "whoami", "uptime"]),
    (4, "user1", "pass123",  ["ls", "date", "pwd"]),
    (5, "admin", "admin123", ["hostname", "whoami", "ls"]),
]

# ── Launch all clients simultaneously ────────────────────
print(f"[*] Launching {len(clients)} clients simultaneously...\n")
overall_start = time.time()

threads = []
for client_id, username, password, commands in clients:
    t = threading.Thread(
        target=run_client,
        args=(client_id, username, password, commands)
    )
    threads.append(t)

# Start all at same time
for t in threads:
    t.start()

# Wait for all to finish
for t in threads:
    t.join()

overall_end = time.time()
print(f"\n[*] All {len(clients)} clients completed!")
print(f"[*] Total time: {overall_end - overall_start:.2f} seconds")