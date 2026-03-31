# Prompt 100

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn
import numpy as np
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt
from io import BytesIO
import base64

app = FastAPI()

class SensorData(BaseModel):
    value: float

sensor_data = []
model = IsolationForest(contamination=0.01)
is_fitted = False

html = """
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard</title>
</head>
<body>
    <h1>Live Sensor Data</h1>
    <img id="graph" src="" />
    <script>
        var ws = new WebSocket("ws://localhost:8000/ws");
        ws.onmessage = function(event) {
            var img = document.getElementById('graph');
            img.src = "data:image/png;base64," + event.data;
        };
    </script>
</body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_json()
        sensor_data.append(data['value'])
        if len(sensor_data) > 100 and not is_fitted:
            model.fit(np.array(sensor_data).reshape(-1, 1))
            is_fitted = True
        prediction = model.predict(np.array(sensor_data[-1:]).reshape(-1, 1))
        plt.plot(sensor_data)
        for (i, v) in enumerate(sensor_data):
            color = "red" if prediction[0] == -1 else "blue"
            plt.scatter(i, v, c=color)
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        graph = base64.b64encode(image_png)
        graph = graph.decode('utf-8')
        buffer.close()
        await websocket.send_text(graph)
        plt.clf()

@app.post("/data")
async def post_data(data: SensorData):
    sensor_data.append(data.value)
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)