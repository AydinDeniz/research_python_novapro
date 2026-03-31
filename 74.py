from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import paramiko
import time
from influxdb import InfluxDBClient

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app)

# InfluxDB configuration
influx_client = InfluxDBClient(host="localhost", port=8086, database="performance_metrics")

# SSH configuration for remote hosts
remote_hosts = [
    {"hostname": "remote_host1", "username": "user1", "password": "password1"},
    {"hostname": "remote_host2", "username": "user2", "password": "password2"},
]

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on("connect")
def handle_connect():
    print("Client connected")
    emit("message", {"data": "Connected"})

def collect_metrics():
    while True:
        for host in remote_hosts:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host["hostname"], username=host["username"], password=host["password"])

            stdin, stdout, stderr = ssh.exec_command("top -bn1 | grep 'Cpu(s)'")
            cpu_usage = stdout.read().decode().strip().split()[1].rstrip('%')

            stdin, stdout, stderr = ssh.exec_command("free -m | awk 'NR==2{printf \"%.2f%%\", $3*100/$2 }'")
            memory_usage = stdout.read().decode().strip()

            stdin, stdout, stderr = ssh.exec_command("df -h | awk '$NF==\"/\"{printf \"%s\",  $5}'")
            disk_usage = stdout.read().decode().strip()

            ssh.close()

            data = [
                {
                    "measurement": "server_performance",
                    "tags": {
                        "host": host["hostname"]
                    },
                    "fields": {
                        "cpu_usage": float(cpu_usage),
                        "memory_usage": float(memory_usage.rstrip('%')),
                        "disk_usage": disk_usage
                    }
                }
            ]

            influx_client.write_points(data)
            socketio.emit("metrics", {"host": host["hostname"], "cpu_usage": cpu_usage, "memory_usage": memory_usage, "disk_usage": disk_usage})

        time.sleep(10)

if __name__ == "__main__":
    socketio.start_background_task(collect_metrics)
    socketio.run(app, debug=True)