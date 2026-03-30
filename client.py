import socket
import ssl
import json

SERVER_IP = "10.137.47.15"  
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




def start_client():
    # Create SSL context for client
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.load_verify_locations(CERTFILE)   
    context.check_hostname = False            
    
    raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Wrap with SSL
    conn = context.wrap_socket(raw_socket, server_hostname="localhost")

    print(f"[*] Connecting to {SERVER_IP}:{SERVER_PORT}...")
    conn.connect((SERVER_IP, SERVER_PORT))
    print("[*] Connected! SSL Handshake successful.\n")

    try:
        # ── Step 1: Receive welcome and send login ──
        welcome = recv_json(conn)
        print(f"Server: {welcome['message']}")

        username = input("Username: ")
        password = input("Password: ")

        send_json(conn, {"username": username, "password": password})

        # ── Step 2: Receive login response ──
        response = recv_json(conn)
        print(f"\nServer: {response['message']}")

        if response["status"] != "success":
            print("[-] Login failed. Exiting.")
            return

        token = response["token"]
        print(f"[+] Session token received.")
        print("-" * 40)

        # ── Step 3: Command loop ──
        while True:
            command = input("\n$ Enter command (or 'exit'): ").strip()

            if not command:
                continue

            send_json(conn, {"token": token, "command": command})
            result = recv_json(conn)

            if command.lower() == "exit":
                print(result["message"])
                break

            # Display result
            print(f"\n[Status: {result['status']}]")
            print(result["output"])

    except (ConnectionResetError, BrokenPipeError):
        print("\n[-] Server disconnected.")
    except json.JSONDecodeError:
        print("\n[-] Bad response from server.")
    except Exception as e:
        print(f"\n[-] Error: {e}")
    finally:
        conn.close()
        print("[*] Connection closed.")

if __name__ == "__main__":
    start_client()