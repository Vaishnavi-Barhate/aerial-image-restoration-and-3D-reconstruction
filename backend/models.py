from pydantic import BaseModel
from typing import Dict, Optional

class JobSteps(BaseModel):
    deblur: str = "pending"
    depth: str = "pending"
    mesh: str = "pending"
    hallucination: str = "pending"

class JobOutputs(BaseModel):
    restored_image: Optional[str] = None
    depth_map: Optional[str] = None
    mesh_raw: Optional[str] = None
    mesh_hallucinated: Optional[str] = None

class Job(BaseModel):
    job_id: str
    input_file: str
    status: str
    steps: JobSteps
    outputs: JobOutputs