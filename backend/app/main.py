from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from .agents import run_agentic_workflow
import logging
from .tools import tavily_tool
logging.basicConfig(level= logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.post("/api/agent")
async def handle_agent(request:Request):

    data = await request.json()
    user_query = data.get("query","")
    logger.info(f"Request recieved from user")
    result = run_agentic_workflow(user_query)
    logger.info("result generated for the query")
    return JSONResponse({"data":result})

