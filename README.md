# CN-SSL-
# 🔐 Secure Remote Command Execution System

A secure client-server application that allows authenticated clients to execute
commands remotely over an SSL/TLS encrypted TCP connection.
Built as part of the Computer Networks course (UE24CS252B) at PES University.

---

## 📋 Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Setup Guide](#setup-guide)
- [Usage](#usage)
- [Security](#security)
- [Demo](#demo)

---

## 📌 Overview

This project implements a **Secure Remote Command Execution System** similar
to a simplified SSH. Clients connect to a remote server over TCP with SSL/TLS
encryption, authenticate using credentials, and execute whitelisted commands
remotely.

**Course:** Computer Networks (UE24CS252B)  
**Institution:** PES University, Bengaluru  
**Protocol:** TCP with SSL/TLS  
**Language:** Python 3  

---

## 🏗️ Architecture
```
┌──────────┐          ┌─────────────────────────────┐
│ CLIENT 1 │──SSL/TLS►│                             │
└──────────┘          │         SERVER              │
┌──────────┐          │  ┌──────────────────────┐   │
│ CLIENT 2 │──SSL/TLS►│  │  Authentication      │   │
└──────────┘          │  ├──────────────────────┤   │
┌──────────┐          │  │  Command Dispatcher  │   │
│ CLIENT 3 │──SSL/TLS►│  ├──────────────────────┤   │
└──────────┘          │  │  Audit Logger        │   │
                      │  ├──────────────────────┤   │
                      │  │  Thread Pool         │   │
                      │  └──────────────────────┘   │
                      └─────────────────────────────┘
```

### Communication Flow
```
CLIENT                         SERVER
  │                               │
  │──── TCP Connect (port 9999) ─►│
  │◄─── SSL Certificate ──────────│
  │──── Verify Certificate ───────│
  │       SSL TUNNEL ESTABLISHED  │
  │──── {username, password} ────►│
  │◄─── {token} ──────────────────│
  │──── {token, command} ────────►│
  │◄─── {status, output} ─────────│
```

---

## ✨ Features

- **SSL/TLS Encryption** — All communication encrypted using SSL certificates
- **Authentication** — SHA256 hashed password verification
- **Session Tokens** — Secure random tokens issued after login
- **Command Whitelist** — Only safe commands can be executed
- **Multi-Client Support** — Multiple clients served simultaneously via threads
- **Audit Logging** — Every command logged with timestamp, user, IP, status
- **User Management** — Admin can register, list, and delete users
- **Edge Case Handling** — Abrupt disconnections, SSL errors, invalid input

---

## 📁 Project Structure
```
secure-rce/
│
├── server/
│   ├── server.py        # Main server - socket, SSL, threading
│   ├── auth.py          # Authentication and user management
│   ├── logger.py        # Audit logging
│   ├── server.crt       # SSL certificate (public)
│   ├── server.key       # SSL private key (keep secret)
│   └── users.json       # User database (auto-created)
│
├── client/
│   ├── client.py              # Main client
│   ├── test_multi_client.py   # Multi-client test script
│   └── server.crt             # Copy of server certificate
│
├── docs/
│   └── architecture.png       # Architecture diagram
│
├── audit.log            # Generated at runtime
└── README.md
```

---

## ⚙️ Requirements

- Python 3.8 or above
- OpenSSL (for certificate generation)
- No external libraries needed — uses only Python standard library

Check Python version:
```bash
python --version
```

---

## 🚀 Setup Guide

### Step 1 — Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/secure-rce.git
cd secure-rce
```

### Step 2 — Generate SSL Certificates
Run this once in the project folder:
```bash
openssl req -x509 -newkey rsa:4096 -keyout server.key -out server.crt -days 365 -nodes -subj "/CN=localhost"
```
This creates:
- `server.key` — private key (never share this)
- `server.crt` — public certificate (copy to client)

### Step 3 — Copy certificate to client folder
```bash
# On Windows
copy server.crt client\server.crt

# On Linux/Mac
cp server.crt client/server.crt
```

### Step 4 — Configure client IP
Open `client/client.py` and update:
```python
SERVER_IP = "192.168.1.x"   # replace with your server's IP
```

Find server IP:
```bash
# Windows
ipconfig

# Linux
ip a
```

### Step 5 — Allow port through firewall (Windows server)
Run CMD as Administrator:
```bash
netsh advfirewall firewall add rule name="SecureRCE" dir=in action=allow protocol=TCP localport=9999
```

---

## 🖥️ Usage

### Starting the Server
```bash
cd server
python server.py
```
Expected output:
```
[*] Server running on port 9999
[*] Waiting for connections...
```

### Connecting a Client
```bash
cd client
python client.py
```
Expected output:
```
[*] Connecting to 192.168.1.x:9999...
[*] Connected! SSL Handshake successful.
Server: Welcome! Please login.
Username:
```

### Default Credentials
| Username | Password  | Role  |
|----------|-----------|-------|
| admin    | admin123  | Admin |
| user1    | pass123   | User  |

> ⚠️ Change default passwords before use

### Available Commands
| Command | Description |
|---------|-------------|
| `dir` | List directory contents |
| `whoami` | Show current user |
| `hostname` | Show machine name |
| `ipconfig` | Show network config |
| `echo <text>` | Print text |
| `date` | Show current date |
| `ver` | Show OS version |
| `exit` | Disconnect from server |

### Admin Only Commands
| Command | Description |
|---------|-------------|
| `register <user> <pass>` | Register new user |
| `listusers` | Show all users |
| `deleteuser <user>` | Delete a user |

---

## 🔒 Security

| Feature | Implementation |
|---------|---------------|
| Encryption | SSL/TLS on every connection |
| Password Storage | SHA256 hashing |
| Session Management | Random 32-char tokens |
| Command Safety | Whitelist only |
| Audit Trail | Full logging |
| Thread Safety | threading.Lock() |
| Timeout | 10 second command limit |

---

## 📊 Demo

### Single Client
```
$ python client.py

[*] Connected! SSL Handshake successful.
Username: admin
Password: ********

[+] Session token received.
$ Enter command: whoami
[Status: success]
DESKTOP-XXXXX\admin

$ Enter command: dir
[Status: success]
Volume in drive C...

$ Enter command: rm -rf /
[Status: blocked]
Command 'rm' is not allowed.
```

### Multiple Clients
```bash
python test_multi_client.py
```
```
[*] Launching 5 clients simultaneously...
[Client 1] Logged in as 'admin'
[Client 2] Logged in as 'user1'
[Client 3] Logged in as 'admin'
[Client 4] Logged in as 'user1'
[Client 5] Logged in as 'admin'
[*] All 5 clients completed!
[*] Total time: 1.23 seconds
```

---

## 📝 Audit Log Sample
```
[2024-01-15 10:30:45] USER=admin IP=192.168.1.5 CMD=LOGIN STATUS=SUCCESS
[2024-01-15 10:30:47] USER=admin IP=192.168.1.5 CMD=dir STATUS=SUCCESS
[2024-01-15 10:30:49] USER=admin IP=192.168.1.5 CMD=rm STATUS=BLOCKED
[2024-01-15 10:30:51] USER=admin IP=192.168.1.5 CMD=EXIT STATUS=SUCCESS
```

Make sure your folder looks like this:
```
secure-rce/
├── server/
│   ├── server.py
│   ├── auth.py
│   ├── logger.py
│   └── server.crt
├── client/
│   ├── client.py
│   ├── test_multi_client.py
│   └── server.crt
├── .gitignore
└── README.md
``

