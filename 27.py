from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain import LangChain

app = FastAPI()

# Define the LangChain model
class LangChainModel:
    def __init__(self):
        self.agents = {
            "tech_support": "TechSupportAgent",
            "sales": "SalesAgent",
            "general": "GeneralInquiriesAgent"
        }

    def route_query(self, query):
        if "tech" in query.lower():
            return self.agents["tech_support"]
        elif "buy" in query.lower() or "purchase" in query.lower():
            return self.agents["sales"]
        else:
            return self.agents["general"]

# Define the request model
class QueryRequest(BaseModel):
    query: str

# Initialize LangChain model
langchain_model = LangChainModel()

# Define the endpoint
@app.post("/query/")
async def query(request: QueryRequest):
    agent = langchain_model.route_query(request.query)
    if agent == "TechSupportAgent":
        response = tech_support_agent(request.query)
    elif agent == "SalesAgent":
        response = sales_agent(request.query)
    elif agent == "GeneralInquiriesAgent":
        response = general_inquiries_agent(request.query)
    else:
        raise HTTPException(status_code=400, detail="Agent not found")
    return {"agent": agent, "response": response}

# Dummy AI agent functions
def tech_support_agent(query):
    return f"Tech support response for: {query}"

def sales_agent(query):
    return f"Sales response for: {query}"

def general_inquiries_agent(query):
    return f"General inquiries response for: {query}"