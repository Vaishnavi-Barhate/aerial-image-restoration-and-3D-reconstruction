An AI-powered system for restoring UAV (drone) images, estimating depth, reconstructing 3D meshes, and analyzing AI hallucinations built using FastAPI, PyTorch, OpenCV, MongoDB, and React.

Setup

Clone repository

Create Virtual Environment -
cd backend
python -m venv venv
venv\Scripts\activate   # Windows

Install dependencies -
pip install -r requirements.txt

Run the project
backend - 
uvicorn main:app --reload
frontend - 
cd frontend
npm install
npm start
