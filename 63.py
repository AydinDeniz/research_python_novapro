import socket
import multiprocessing
import time
import random

tasks = []
results = {}
workers = {}

def handle_client(conn, addr):
    print(f"New connection from {addr}")
    workers[addr] = time.time()
    while True:
        data = conn.recv(1024).decode()
        if not data:
            break
        parts = data.split()
        if parts[0] == "REGISTER":
            print(f"Worker {addr} registered")
        elif parts[0] == "PULL":
            if tasks:
                task = tasks.pop(0)
                conn.sendall(task.encode())
            else:
                conn.sendall(b"NO_TASK")
        elif parts[0] == "PUSH":
            result = " ".join(parts[1:])
            results[result] = time.time()
            conn.sendall(b"ACK")
        elif parts[0] == "HEARTBEAT":
            workers[addr] = time.time()
            conn.sendall(b"ACK")
    conn.close()
    del workers[addr]
    print(f"Connection from {addr} closed")

def add_task(task):
    tasks.append(task)

def monitor_workers():
    while True:
        time.sleep(5)
        current_time = time.time()
        for addr, last_heartbeat in list(workers.items()):
            if current_time - last_heartbeat > 10:
                print(f"Worker {addr} timed out")
                del workers[addr]

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 65432))
    server.listen(5)
    print("Server listening on port 65432")

    monitor_process = multiprocessing.Process(target=monitor_workers)
    monitor_process.start()

    while True:
        conn, addr = server.accept()
        client_process = multiprocessing.Process(target=handle_client, args=(conn, addr))
        client_process.start()

if __name__ == "__main__":
    main()
    
import socket
import time
import random

def execute_task(task):
    time.sleep(random.randint(1, 5))  # Simulate task execution
    return f"Result for {task}"

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("localhost", 65432))
    client.sendall(b"REGISTER")
    print("Registered with server")

    while True:
        client.sendall(b"PULL")
        task = client.recv(1024).decode()
        if task == "NO_TASK":
            time.sleep(1)
            continue
        print(f"Received task: {task}")
        result = execute_task(task)
        client.sendall(f"PUSH {result}".encode())
        print(f"Pushed result: {result}")

        client.sendall(b"HEARTBEAT")
        time.sleep(random.randint(1, 3))

if __name__ == "__main__":
    main()