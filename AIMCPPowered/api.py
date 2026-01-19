from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# import subprocess

from client import LLMPlaywrightAgent


# initialize API
app = FastAPI()

# start up command and wait to ensure it is running before moving on
# process = subprocess.Popen(["npx", "-y", "@playwright/mcp@latest", "--port", "8931", "--headless"], shell=True)

class TaskItem(BaseModel):
    api_key: str
    task: str

@app.post("/run")
async def run_task(item: TaskItem):
    try:
        agent = LLMPlaywrightAgent(api_key=item.api_key)
        result = await agent.run(item.task)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
