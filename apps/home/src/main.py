from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI(
    title="Home API",
    description="A simple FastAPI application",
    version="1.0.0"
)

class HealthResponse(BaseModel):
    status: str

@app.get("/", response_model=HealthResponse)
async def health_check():
    return {"status": "healthy"}

def main():
    uvicorn.run("src.main:app", host="0.0.0.0", port=3030, reload=True)

if __name__ == "__main__":
    main()