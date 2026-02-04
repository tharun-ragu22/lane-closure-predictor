from fastapi import FastAPI, HTTPException
import os
from google.cloud import storage
import json
from google.cloud import run_v2

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
def trigger_sumo_job():
    client = run_v2.JobsClient()
    
    # Define the full path to your job
    project = "commute-time-v1" # or use os.environ.get("GOOGLE_CLOUD_PROJECT")
    location = "us-central1"
    job_name = "sumo-simulation-job"
    
    job_path = f"projects/{project}/locations/{location}/jobs/{job_name}"
    
    try:
        # Trigger the execution
        operation = client.run_job(name=job_path)
        # The execution name looks like 'sumo-simulation-job-xyz123'
        execution_id = operation.metadata.name.split('/')[-1]
        
        return {"status": "started", "execution_id": execution_id}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to start simulation")

if __name__ == "__main__":
    # Cloud Run injects the PORT environment variable automatically
    port = int(os.environ.get("PORT", 8080))
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)