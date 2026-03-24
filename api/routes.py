import os
import json
import uuid
import asyncio
import httpx
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Header, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

load_dotenv()

app = FastAPI(title="Qestron Labs API Bridge")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ADMIN_SECRET = os.getenv("ADMIN_SECRET", "your-secret-password-here")
MIROFISH_URL = os.getenv("MIROFISH_URL", "http://localhost:8000")
DATA_FILE = "projects.json"

def load_projects() -> dict:
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_projects(data: dict):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

projects = load_projects()

class ProjectSubmit(BaseModel):
    client_name: str
    client_phone: str
    requirements: str

# ─────────────────────────────────────────────
# PUBLIC ROUTES (Client Facing)
# ─────────────────────────────────────────────
@app.post("/api/project")
async def submit_project(payload: ProjectSubmit, background_tasks: BackgroundTasks):
    project_id = f"proj_{uuid.uuid4().hex[:8]}"
    
    projects[project_id] = {
        "id": project_id,
        "client_name": payload.client_name,
        "client_phone": payload.client_phone,
        "requirements": payload.requirements,
        "created_at": datetime.now().isoformat(),
        "current_stage": 1,
        "stages": {
            "1": {"name": "Requirements Received", "status": "done", "progress": 100},
            "2": {"name": "Design & Architecture", "status": "active", "progress": 10},
            "3": {"name": "Development", "status": "pending", "progress": 0},
            "4": {"name": "Testing & QA", "status": "pending", "progress": 0},
            "5": {"name": "Deployment", "status": "pending", "progress": 0},
            "6": {"name": "Delivery", "status": "pending", "progress": 0},
        },
        "mirofish_raw": None,
        "documents": [],
        "estimated_delivery": "2 hours"
    }
    save_projects(projects)
    
    # Trigger background simulation
    background_tasks.add_task(run_mirofish_simulation, project_id, payload.requirements)
    
    return {
        "project_id": project_id,
        "message": "Project received!",
        "estimated_delivery": "2 hours"
    }

@app.get("/api/project/status")
async def get_project_status(id: str):
    proj = projects.get(id)
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
        
    return {
        "project_id": id,
        "client_name": proj["client_name"],
        "current_stage": proj["current_stage"],
        "estimated_delivery": proj.get("estimated_delivery", "Calculating..."),
        "stages": proj["stages"],
        "documents": proj.get("documents", [])
    }

# ─────────────────────────────────────────────
# BACKGROUND SIMULATION LOGIC
# ─────────────────────────────────────────────
async def run_mirofish_simulation(project_id: str, requirements: str):
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{MIROFISH_URL}/api/simulation/simulate",
                json={
                    "mode": "it_company",
                    "input": requirements
                }
            )
            if response.status_code == 200:
                data = response.json()
                proj = projects.get(project_id)
                if proj:
                    proj["mirofish_raw"] = data
                    proj["documents"] = data.get("documents", [])
                    proj["current_stage"] = 6
                    
                    # Complete all stages
                    for s in proj["stages"].values():
                        s["status"] = "done"
                        s["progress"] = 100
                        
                    save_projects(projects)
    except Exception as e:
        print(f"Failed to run MiroFish simulation for {project_id}: {e}")

# ─────────────────────────────────────────────
# LIVE BUILD LOGS STORAGE
# ─────────────────────────────────────────────
build_logs = []  # stores all agent actions

@app.get("/api/admin/logs")
async def get_logs(x_admin_key: str = Header(None)):
    verify_admin(x_admin_key)
    return {"logs": build_logs}

@app.post("/api/admin/log")  
async def add_log(entry: dict, x_admin_key: str = Header(None)):
    verify_admin(x_admin_key)
    build_logs.append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "agent": entry.get("agent"),
        "action": entry.get("action"),
        "layer": entry.get("layer"),
        "file": entry.get("file"),
    })
    return {"ok": True}

# ─────────────────────────────────────────────
# ADMIN ROUTES (Internal Facing)
# ─────────────────────────────────────────────
def verify_admin(x_admin_key: str):
    if not x_admin_key or x_admin_key != ADMIN_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Admin Key")

@app.get("/api/admin/projects")
async def admin_get_projects(x_admin_key: str = Header(None)):
    verify_admin(x_admin_key)
    return {"success": True, "projects": list(projects.values())}

@app.get("/api/admin/projects/{project_id}")
async def admin_get_project_detail(project_id: str, x_admin_key: str = Header(None)):
    verify_admin(x_admin_key)
    proj = projects.get(project_id)
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"success": True, "project": proj}

@app.post("/api/admin/simulate")
async def admin_simulate(request: Request, x_admin_key: str = Header(None)):
    """Directly trigger simulation from admin dashboard and return raw output"""
    verify_admin(x_admin_key)
    data = await request.json()
    req_input = data.get("input", "")
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{MIROFISH_URL}/api/simulation/simulate",
                json={
                    "mode": "it_company",
                    "input": req_input
                }
            )
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MiroFish connection error: {str(e)}")

@app.get("/api/admin/workspace-logs")
async def get_workspace_logs(x_admin_key: str = Header(None)):
    """Fetch live tail from workspace.log so dashboard can display standalone scripts running"""
    verify_admin(x_admin_key)
    log_path = "mirofish-tmp/backend/workspace.log"
    if os.path.exists(log_path):
        try:
            with open(log_path, "r") as f:
                content = f.read()
                # Return last 50 lines to prevent overloading
                lines = content.split("\n")[-50:]
                return {"success": True, "logs": "\n".join(lines)}
        except Exception as e:
            return {"success": False, "message": f"Error reading log: {str(e)}"}
    return {"success": False, "message": "No active workspace.log found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("routes:app", host="0.0.0.0", port=5001, reload=True)
