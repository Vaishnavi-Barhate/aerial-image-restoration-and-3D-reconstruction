from database import jobs

def create_job(job: dict):
    jobs.insert_one(job)

def update_job(job_id: str, data: dict):
    jobs.update_one(
        {"job_id": job_id},
        {"$set": data}
    )

def get_job(job_id: str):
    return jobs.find_one(
        {"job_id": job_id},
        {"_id": 0}
    )

def delete_job(job_id: str):
    jobs.delete_one({"job_id": job_id})

def list_jobs():
    return list(jobs.find({}, {"_id": 0}))