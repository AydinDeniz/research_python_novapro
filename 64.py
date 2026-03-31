import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient
import json

# InfluxDB setup
influx_client = InfluxDBClient(host='localhost', port=8086)
influx_client.create_database('iot_data')
influx_client.switch_database('iot_data')

# MQTT setup
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("sensor/readings")

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    json_body = [
        {
            "measurement": "sensor_readings",
            "tags": {
                "sensor_id": data["sensor_id"]
            },
            "fields": {
                "temperature": data["temperature"],
                "humidity": data["humidity"]
            }
        }
    ]
    influx_client.write_points(json_body)

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect("mqtt.eclipse.org", 1883, 60)
mqtt_client.loop_forever()
from aiohttp import web
import aiohttp_cors
import asyncio
import json
from influxdb import InfluxDBClient

influx_client = InfluxDBClient(host='localhost', port=8086)
influx_client.switch_database('iot_data')

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == 'get_data':
                query = 'SELECT * FROM sensor_readings ORDER BY time DESC LIMIT 10'
                result = influx_client.query(query)
                data = result.raw['series'][0]['values']
                await ws.send_json(data)
        elif msg.type == aiohttp.WSMsgType.ERROR:
            print(f'ws connection closed with exception {ws.exception()}')

    print('websocket connection closed')
    return ws

app = web.Application()
app.router.add_route('GET', '/ws', websocket_handler)

cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
})

for route in list(app.router.routes()):
    cors.add(route)

web.run_app(app)