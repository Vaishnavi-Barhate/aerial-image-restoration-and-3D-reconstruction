import os
import cv2
import time
import numpy as np
import trimesh

from crud import update_job
from reconstruction import (
    deblur_image,
    run_depth,
    pointcloud_to_mesh,
    hallucinate_mesh
)

os.makedirs("processed", exist_ok=True)

def run_pipeline(job_id: str, input_path: str):
    print("PIPELINE STARTED FOR:", input_path)

    update_job(job_id, {"status": "running"})

    # -------- Step 1: Deblur --------
    update_job(job_id, {"steps.deblur": "running"})
    restored_path = deblur_image(input_path, job_id)
    update_job(job_id, {"steps.deblur": "done"})
    time.sleep(1)

    # -------- Step 2: Depth --------
    update_job(job_id, {"steps.depth": "running"})
    depth_array, depth_path = run_depth(restored_path, job_id)
    update_job(job_id, {"steps.depth": "done"})
    time.sleep(1)

    # -------- Step 3: Mesh --------
    update_job(job_id, {"steps.mesh": "running"})
    mesh_path = pointcloud_to_mesh(depth_array, job_id)
    update_job(job_id, {"steps.mesh": "done"})
    time.sleep(1)

    # -------- Step 4: Hallucination --------
    update_job(job_id, {"steps.hallucination": "running"})
    hallucinated_path = hallucinate_mesh(mesh_path, job_id)
    update_job(job_id, {"steps.hallucination": "done"})
    time.sleep(1)

    # -------- Final Outputs --------
    update_job(job_id, {
        "status": "completed",
        "outputs": {
            "restored_image": f"/processed/{job_id}_restored.png",
            "depth_map": f"/processed/{job_id}_depth.png",
            "mesh_raw": f"/processed/{job_id}_mesh.obj",
            "mesh_hallucinated": f"/processed/{job_id}_mesh_full.obj"
        }
    })

    print("PIPELINE COMPLETED FOR:", job_id)