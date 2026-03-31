from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import redis
import matplotlib.pyplot as plt
import plotly.graph_objs as go
from io import BytesIO
import base64

app = FastAPI()

# Redis client
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# External API configuration
API_URLS = {
    'api1': 'https://api.example.com/data1',
    'api2': 'https://api.example.com/data2',
}

class FinancialData(BaseModel):
    source: str
    data: dict

@app.on_event("startup")
async def startup_event():
    # Fetch and cache data from external APIs
    async with httpx.AsyncClient() as client:
        for source, url in API_URLS.items():
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                redis_client.set(source, data)
            else:
                raise HTTPException(status_code=500, detail="Failed to fetch data from external API")

@app.get("/data/{source}", response_model=FinancialData)
async def get_financial_data(source: str):
    data = redis_client.get(source)
    if data:
        return FinancialData(source=source, data=data)
    else:
        raise HTTPException(status_code=404, detail="Data not found")

@app.get("/stats/{source}")
async def get_financial_stats(source: str):
    data = redis_client.get(source)
    if data:
        data = eval(data)  # Convert bytes to dict
        stats = {
            'max': max(data.values()),
            'min': min(data.values()),
            'avg': sum(data.values()) / len(data)
        }
        return stats
    else:
        raise HTTPException(status_code=404, detail="Data not found")

@app.get("/plot/{source}")
async def get_financial_plot(source: str):
    data = redis_client.get(source)
    if data:
        data = eval(data)  # Convert bytes to dict
        plt.figure(figsize=(10, 5))
        plt.plot(data.keys(), data.values())
        plt.xlabel('Key')
        plt.ylabel('Value')
        plt.title('Financial Data Plot')
        
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plot_url = base64.b64encode(buf.getvalue()).decode('utf-8')
        
        return {"plot": f"data:image/png;base64,{plot_url}"}
    else:
        raise HTTPException(status_code=404, detail="Data not found")

@app.get("/plotly/{source}")
async def get_financial_plotly(source: str):
    data = redis_client.get(source)
    if data:
        data = eval(data)  # Convert bytes to dict
        fig = go.Figure(data=go.Scatter(x=list(data.keys()), y=list(data.values()), mode='lines'))
        
        plot_url = fig.to_html(full_html=False)
        
        return {"plot": plot_url}
    else:
        raise HTTPException(status_code=404, detail="Data not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)