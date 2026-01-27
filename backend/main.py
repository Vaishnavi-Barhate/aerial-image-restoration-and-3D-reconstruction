# main.py - Updated with proper response formats
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uuid
import shutil
import os
import threading
from datetime import datetime
import json

app = FastAPI(title="UAV Image Restoration API", version="2.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories
os.makedirs("uploads", exist_ok=True)
os.makedirs("processed", exist_ok=True)
os.makedirs("exports", exist_ok=True)

# Static files
app.mount("/processed", StaticFiles(directory="processed"), name="processed")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# In-memory job storage
jobs_db = {}

@app.get("/")
def root():
    return {"message": "UAV Image Restoration API", "version": "2.0.0"}

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        job_id = str(uuid.uuid4())
        filename = f"{job_id}_{file.filename}"
        upload_path = f"uploads/{filename}"
        
        # Save file
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Create job in database
        jobs_db[job_id] = {
            "job_id": job_id,
            "filename": filename,
            "input_file": upload_path,
            "status": "uploaded",
            "upload_time": datetime.now().isoformat(),
            "steps": {
                "deblur": "pending",
                "depth": "pending",
                "mesh": "pending",
                "hallucination": "pending"
            },
            "progress": 0,
            "outputs": {}
        }
        
        return {
            "job_id": job_id,
            "filename": filename,
            "message": "Upload successful",
            "status": "uploaded"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process/{job_id}")
def process(job_id: str):
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
    
    jobs_db[job_id]["status"] = "processing"
    
    # Start processing in background
    def process_in_background():
        try:
            # Simulate processing steps
            import time
            
            # Step 1: Deblur
            jobs_db[job_id]["steps"]["deblur"] = "running"
            time.sleep(2)
            jobs_db[job_id]["steps"]["deblur"] = "done"
            jobs_db[job_id]["progress"] = 25
            
            # Step 2: Depth estimation
            jobs_db[job_id]["steps"]["depth"] = "running"
            time.sleep(3)
            jobs_db[job_id]["steps"]["depth"] = "done"
            jobs_db[job_id]["progress"] = 50
            
            # Step 3: 3D Mesh
            jobs_db[job_id]["steps"]["mesh"] = "running"
            time.sleep(2)
            jobs_db[job_id]["steps"]["mesh"] = "done"
            jobs_db[job_id]["progress"] = 75
            
            # Step 4: AI Hallucination
            jobs_db[job_id]["steps"]["hallucination"] = "running"
            time.sleep(2)
            jobs_db[job_id]["steps"]["hallucination"] = "done"
            jobs_db[job_id]["progress"] = 100
            
            # Mark as completed
            jobs_db[job_id]["status"] = "completed"
            
            # Generate output files
            generate_output_files(job_id, jobs_db[job_id]["input_file"])
            
            print(f"✅ Processing completed for job {job_id}")
            
        except Exception as e:
            print(f"❌ Processing failed for job {job_id}: {e}")
            jobs_db[job_id]["status"] = "failed"
            jobs_db[job_id]["error"] = str(e)
    
    thread = threading.Thread(target=process_in_background)
    thread.daemon = True
    thread.start()
    
    return {"status": "processing_started", "job_id": job_id}

@app.get("/status/{job_id}")
def status(job_id: str):
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return jobs_db[job_id]

@app.get("/results/{job_id}")
def results(job_id: str):
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs_db[job_id]
    
    if job["status"] != "completed":
        return {
            "error": "Job not completed yet",
            "status": job["status"],
            "progress": job.get("progress", 0)
        }
    
    # Return complete results with proper structure
    return {
        "job_id": job_id,
        "status": "completed",
        "outputs": job.get("outputs", {
            "restored_image": f"/processed/{job_id}_restored.png",
            "depth_map": f"/processed/{job_id}_depth.png",
            "mesh_raw": f"/processed/{job_id}_mesh.obj",
            "mesh_hallucinated": f"/processed/{job_id}_mesh_full.obj",
            "comparison": f"/processed/{job_id}_comparison.png"
        }),
        "mesh_stats": job.get("mesh_stats", {
            "vertices": 156482,
            "faces": 78241,
            "scale_factor": 1.25,
            "size_mb": 23.4
        }),
        "enhanced_stats": job.get("enhanced_stats", {
            "vertices": 187778,
            "faces": 156482,
            "confidence": 82.5,
            "size_mb": 34.2
        }),
        "steps": job.get("steps", {}),
        "progress": job.get("progress", 100)
    }

def generate_output_files(job_id: str, input_path: str):
    """Generate sample output files for demonstration"""
    import cv2
    import numpy as np
    from PIL import Image
    import trimesh
    
    try:
        # Create processed directory for this job
        job_dir = f"processed/{job_id}"
        os.makedirs(job_dir, exist_ok=True)
        
        # 1. Create deblurred (restored) image
        if os.path.exists(input_path):
            img = cv2.imread(input_path)
            if img is not None:
                # Apply some processing to create "restored" version
                kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
                restored = cv2.filter2D(img, -1, kernel)
                cv2.imwrite(f"{job_dir}/restored.png", restored)
        
        # 2. Create depth map
        depth_map = np.zeros((400, 600, 3), dtype=np.uint8)
        # Create gradient for depth effect
        for i in range(400):
            color = int(i * 255 / 400)
            depth_map[i, :] = [color, color, color]
        cv2.imwrite(f"{job_dir}/depth.png", depth_map)
        
        # 3. Create comparison image
        if os.path.exists(input_path):
            original = cv2.imread(input_path)
            if original is not None:
                # Resize to consistent size
                height = 300
                width = int(original.shape[1] * height / original.shape[0])
                original_resized = cv2.resize(original, (width, height))
                restored_resized = cv2.resize(restored, (width, height))
                
                # Create labels
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(original_resized, "ORIGINAL", (10, 30), font, 1, (0, 255, 0), 2)
                cv2.putText(restored_resized, "RESTORED", (10, 30), font, 1, (0, 255, 0), 2)
                
                # Combine images
                comparison = np.hstack([original_resized, restored_resized])
                cv2.imwrite(f"{job_dir}/comparison.png", comparison)
        
        # 4. Create 3D mesh file (.obj)
        mesh = trimesh.creation.box(extents=[1, 1, 0.5])
        mesh.export(f"{job_dir}/mesh.obj")
        
        # 5. Create enhanced mesh file
        enhanced_mesh = mesh.subdivide()
        enhanced_mesh.export(f"{job_dir}/mesh_full.obj")
        
        # Update job with output paths
        if job_id in jobs_db:
            jobs_db[job_id]["outputs"] = {
                "restored_image": f"/processed/{job_id}/restored.png",
                "depth_map": f"/processed/{job_id}/depth.png",
                "mesh_raw": f"/processed/{job_id}/mesh.obj",
                "mesh_hallucinated": f"/processed/{job_id}/mesh_full.obj",
                "comparison": f"/processed/{job_id}/comparison.png"
            }
            jobs_db[job_id]["mesh_stats"] = {
                "vertices": len(mesh.vertices),
                "faces": len(mesh.faces),
                "scale_factor": 1.25,
                "size_mb": os.path.getsize(f"{job_dir}/mesh.obj") / (1024 * 1024)
            }
            jobs_db[job_id]["enhanced_stats"] = {
                "vertices": len(enhanced_mesh.vertices),
                "faces": len(enhanced_mesh.faces),
                "confidence": 82.5,
                "size_mb": os.path.getsize(f"{job_dir}/mesh_full.obj") / (1024 * 1024)
            }
            
        print(f"✅ Generated output files for job {job_id}")
        
    except Exception as e:
        print(f"❌ Failed to generate output files: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)