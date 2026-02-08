from fastapi import FastAPI, HTTPException
import os
from google.cloud import storage
import json
from google.cloud import run_v2
from pydantic import BaseModel
from typing import Any

class SimulationRequestBody(BaseModel):
    desc: str


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "success", "message": "FastAPI is running on Cloud Run!"}

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id, "description": f"This is item {item_id}"}

@app.get("/get-result/{execution_id}")
def get_simulation_result(execution_id: str):
    try:
        bucket_name = os.environ.get("RESULTS_BUCKET")
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        
        blob = bucket.blob(f"results/sim_{execution_id}.json")
        
        if not blob.exists():
            raise HTTPException(status_code=404, detail="Simulation result not found yet.")
        
        # This is a blocking call, but 'def' handles it in a thread pool
        content = blob.download_as_text()
        return json.loads(content)
    except Exception as e:
        print(f"Error fetching from GCS: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/run-simulation")
def trigger_sumo_job(body: SimulationRequestBody):
    client = run_v2.JobsClient()
    
    # Define the full path to your job
    project = "commute-time-v1" # or use os.environ.get("GOOGLE_CLOUD_PROJECT")
    location = "us-central1"
    job_name = "sumo-simulation-job"
    
    job_path = f"projects/{project}/locations/{location}/jobs/{job_name}"

    # Build typed overrides via the client module to avoid static-import issues
    container_override = run_v2.types.ContainerOverride(
        args=[body.desc]
    )

    overrides_obj = run_v2.types.JobOverrides(
        container_overrides=[container_override]
    )

    request = run_v2.RunJobRequest(
        name=job_path,
        overrides=overrides_obj
    )
    
    try:
        
            
        # Trigger the execution
        operation = client.run_job(request=request)
        # The execution name looks like 'sumo-simulation-job-xyz123'
        execution_id = operation.metadata.name.split('/')[-1]
        
        return {"status": "started", "execution_id": execution_id}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to start simulation")


@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(body: ChatRequest):
    """Dummy chat endpoint returning a canned response based on input."""
    user_msg = (body.message or "").strip()
    # Very simple dummy logic
    if not user_msg:
        reply = "Please send a message."
    elif "hello" in user_msg.lower():
        reply = "Hi there! This is a dummy reply from the server." 
    else:
        reply = f"You said: {user_msg}. (This is a dummy server response.)"

    return {"reply": reply}

if __name__ == "__main__":
    # Cloud Run injects the PORT environment variable automatically
    port = int(os.environ.get("PORT", 8080))
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)