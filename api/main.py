from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "success", "message": "FastAPI is running on Cloud Run!"}

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id, "description": f"This is item {item_id}"}

if __name__ == "__main__":
    # Cloud Run injects the PORT environment variable automatically
    port = int(os.environ.get("PORT", 8080))
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)