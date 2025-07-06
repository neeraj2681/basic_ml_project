from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Simple Test API")

@app.get("/")
async def root():
    return {"message": "API is working!"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    print("Starting simple API...")
    uvicorn.run(app, host="0.0.0.0", port=8000) 