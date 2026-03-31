import paho.mqtt.client as mqtt
import random
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# MQTT broker details
BROKER_ADDRESS = "mqtt.eclipse.org"
BROKER_PORT = 1883

# Sensor data generation
def generate_sensor_data():
    temperature = round(random.uniform(20, 30), 2)
    humidity = round(random.uniform(40, 60), 2)
    gps = (round(random.uniform(-90, 90), 6), round(random.uniform(-180, 180), 6))
    return temperature, humidity, gps

# MQTT publisher
def on_publish(client, userdata, result):
    print("Data published.")

client = mqtt.Client()
client.on_publish = on_publish
client.connect(BROKER_ADDRESS, BROKER_PORT)

while True:
    temperature, humidity, gps = generate_sensor_data()
    data = f"Temperature: {temperature}, Humidity: {humidity}, GPS: {gps}"
    client.publish("sensor/data", data)
    time.sleep(1)

# MQTT subscriber and real-time visualization
temperatures = []
humidities = []
times = []

def on_message(client, userdata, message):
    data = message.payload.decode()
    parts = data.split(", ")
    temperature = float(parts[0].split(": ")[1])
    humidity = float(parts[1].split(": ")[1])
    temperatures.append(temperature)
    humidities.append(humidity)
    times.append(time.time())

subscriber = mqtt.Client()
subscriber.on_message = on_message
subscriber.connect(BROKER_ADDRESS, BROKER_PORT)
subscriber.subscribe("sensor/data")
subscriber.loop_start()

fig, (ax1, ax2) = plt.subplots(2, 1)
line1, = ax1.plot(times, temperatures)
line2, = ax2.plot(times, humidities)

def update(frame):
    line1.set_xdata(times)
    line1.set_ydata(temperatures)
    line2.set_xdata(times)
    line2.set_ydata(humidities)
    ax1.relim()
    ax1.autoscale_view()
    ax2.relim()
    ax2.autoscale_view()
    return line1, line2

ani = FuncAnimation(fig, update, interval=1000)
plt.show()