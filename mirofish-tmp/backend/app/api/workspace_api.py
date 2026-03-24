from flask import Blueprint, jsonify
import json, os, sys

workspace_bp = Blueprint('workspace', __name__)

# Path to workspace output from workspace.py
WORKSPACE_FILE = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    '../../workspace_output.json'
))

@workspace_bp.route('/api/workspace/state', methods=['GET'])
def get_workspace_state():
    """Returns full workspace state for the Vue frontend"""
    try:
        with open(WORKSPACE_FILE) as f:
            return jsonify(json.load(f))
    except FileNotFoundError:
        return jsonify({
            "phase": "waiting",
            "project": "No simulation running",
            "files": {},
            "debate_board": [],
            "decisions": [],
            "bugs": [],
            "review_queue": [],
            "agent_logs": [],
            "test_results": {},
            "documents": {}
        })

@workspace_bp.route('/api/workspace/agents', methods=['GET'])
def get_agents():
    """Returns all 1000 agents with roles, models, status"""
    agents = []
    
    # C-Suite (5)
    csuite = [
        {"id":"CEO-001","role":"CEO","dept":"Executive","model":"nemotron-super","status":"active","task":"Reviewing project scope"},
        {"id":"CTO-001","role":"CTO","dept":"Executive","model":"nemotron-super","status":"active","task":"Finalizing tech stack"},
        {"id":"COO-001","role":"COO","dept":"Executive","model":"nemotron-super","status":"idle","task":"Waiting"},
        {"id":"ARCH-001","role":"Solution Architect","dept":"Executive","model":"step-flash","status":"active","task":"Designing microservices"},
        {"id":"BA-001","role":"Business Analyst","dept":"Executive","model":"step-flash","status":"active","task":"Writing BRD"},
    ]
    
    # Department Heads (6)
    heads = [
        {"id":"HEAD-BE","role":"Head of Backend","dept":"Management","model":"nemotron-super","status":"active","task":"Reviewing backend files"},
        {"id":"HEAD-FE","role":"Head of Frontend","dept":"Management","model":"nemotron-super","status":"active","task":"Reviewing UI components"},
        {"id":"HEAD-QA","role":"Head of QA","dept":"Management","model":"nemotron-super","status":"busy","task":"Coordinating test suites"},
        {"id":"HEAD-OPS","role":"Head of DevOps","dept":"Management","model":"nemotron-super","status":"idle","task":"Waiting for code"},
        {"id":"HEAD-SEC","role":"Head of Security","dept":"Management","model":"nemotron-super","status":"active","task":"Security audit"},
        {"id":"HEAD-DATA","role":"Head of Data","dept":"Management","model":"nemotron-super","status":"active","task":"ML pipeline review"},
    ]
    
    # PM Team (2)
    pms = [
        {"id":f"PM-{i:03d}","role":"Project Manager","dept":"Delivery","model":"nemotron-super","status":"active","task":f"Sprint {i} planning"}
        for i in range(1,3)
    ]
    
    # Backend devs (200 — show 5 representative + count)
    be_devs = [
        {"id":f"BE-{i:03d}","role":"Backend Developer","dept":"Backend","model":"qwen-coder","status":"busy","task":["Writing FastAPI routes","Building auth service","Creating DB models","Writing Kafka producer","Building payment API"][i%5]}
        for i in range(1,6)
    ]
    
    # Frontend devs (200)
    fe_devs = [
        {"id":f"FE-{i:03d}","role":"Frontend Developer","dept":"Frontend","model":"qwen-coder","status":"busy","task":["Building Dashboard","Writing Auth pages","Creating UI components","Building mobile nav","Writing API service"][i%5]}
        for i in range(1,6)
    ]
    
    # Mobile devs (50)
    mob_devs = [
        {"id":f"MOB-{i:03d}","role":"Mobile Developer","dept":"Mobile","model":"qwen-coder","status":"active","task":["React Native setup","iOS navigation","Android push notifications"][i%3]}
        for i in range(1,3)
    ]
    
    # DB engineers (100)
    db_engs = [
        {"id":f"DB-{i:03d}","role":"Database Engineer","dept":"Database","model":"qwen-coder","status":"active","task":["Schema design","Writing migrations","Query optimization"][i%3]}
        for i in range(1,3)
    ]
    
    # ML engineers (50)
    ml_engs = [
        {"id":f"ML-{i:03d}","role":"ML Engineer","dept":"AI","model":"step-flash","status":"active","task":["Training fraud model","Building RAG pipeline"][i%2]}
        for i in range(1,3)
    ]
    
    # QA agents (100)
    qa_agents = [
        {"id":f"QA-{i:03d}","role":"QA Engineer","dept":"Quality","model":"step-flash","status":"busy","task":["Writing unit tests","Running E2E tests","Load testing"][i%3]}
        for i in range(1,4)
    ]
    
    # Security (50)
    sec_agents = [
        {"id":f"SEC-{i:03d}","role":"Security Agent","dept":"Security","model":"step-flash","status":"active","task":["OWASP scan","PCI-DSS audit"][i%2]}
        for i in range(1,3)
    ]
    
    # DevOps (40)
    ops_agents = [
        {"id":f"OPS-{i:03d}","role":"DevOps Engineer","dept":"DevOps","model":"qwen-coder","status":"idle","task":"Waiting for code"}
        for i in range(1,3)
    ]
    
    # Code Review (1)
    reviewers = [
        {"id":"REV-001","role":"Code Review Agent","dept":"Quality","model":"nemotron-super","status":"busy","task":"Reviewing 3 files"},
    ]
    
    # Bug Hunter (1)
    bug_hunter = [
        {"id":"BUG-001","role":"Bug Hunter","dept":"Quality","model":"step-flash","status":"busy","task":"Scanning codebase"},
    ]
    
    # Client layer (5)
    client = [
        {"id":"CLIENT-001","role":"Client Manager","dept":"Client","model":"sarvam-ai","status":"active","task":"Calling HDFC client"},
        {"id":"SALES-001","role":"Sales Agent","dept":"Client","model":"nemotron-super","status":"idle","task":"Waiting"},
    ]
    
    all_agents = csuite + heads + pms + be_devs + fe_devs + mob_devs + db_engs + ml_engs + qa_agents + sec_agents + ops_agents + reviewers + bug_hunter + client
    
    # Add department totals
    dept_totals = {
        "Backend":   200,
        "Frontend":  200,
        "Mobile":    50,
        "Database":  100,
        "AI":        50,
        "Quality":   100,
        "Security":  50,
        "DevOps":    40,
        "Executive": 5,
        "Management":6,
        "Delivery":  2,
        "Client":    5,
    }
    
    return jsonify({
        "agents": all_agents,
        "dept_totals": dept_totals,
        "total": 1000,
        "active": sum(1 for a in all_agents if a["status"] in ["active","busy"]),
    })

@workspace_bp.route('/api/workspace/graph', methods=['GET'])
def get_graph():
    """Returns D3 graph data — nodes and links between agents"""
    print("\n[DEBUG] Serving /api/workspace/graph - 1000 agent layout triggered")
    nodes = [
        # Core nodes
        {"id":"CEO-001",    "label":"CEO",         "group":"executive", "size":30},
        {"id":"CTO-001",    "label":"CTO",         "group":"executive", "size":25},
        {"id":"ARCH-001",   "label":"Architect",   "group":"executive", "size":20},
        {"id":"PM-001",     "label":"PM-1",        "group":"management","size":18},
        {"id":"PM-002",     "label":"PM-2",        "group":"management","size":18},
        {"id":"HEAD-BE",    "label":"Head BE",     "group":"management","size":18},
        {"id":"HEAD-FE",    "label":"Head FE",     "group":"management","size":18},
        {"id":"HEAD-QA",    "label":"Head QA",     "group":"management","size":18},
        {"id":"HEAD-SEC",   "label":"Head SEC",    "group":"management","size":16},
        {"id":"HEAD-OPS",   "label":"Head Ops",    "group":"management","size":16},
        {"id":"HEAD-DATA",  "label":"Head Data",   "group":"management","size":16},
        
        # Department Heads (already listed up top if needed)
    ]
    
    links = [
        # CEO controls everything
        {"source":"CEO-001",    "target":"CTO-001",    "type":"reports"},
        {"source":"CEO-001",    "target":"PM-001",     "type":"reports"},
        {"source":"CEO-001",    "target":"PM-002",     "type":"reports"},
        {"source":"CEO-001",    "target":"CLIENT-001", "type":"reports"},
        
        # CTO controls tech
        {"source":"CTO-001",   "target":"ARCH-001",   "type":"reports"},
        {"source":"CTO-001",   "target":"HEAD-BE",    "type":"reports"},
        {"source":"CTO-001",   "target":"HEAD-FE",    "type":"reports"},
        {"source":"CTO-001",   "target":"HEAD-OPS",   "type":"reports"},
        {"source":"CTO-001",   "target":"HEAD-DATA",  "type":"reports"},
        {"source":"CTO-001",   "target":"HEAD-QA",    "type":"reports"},
        {"source":"CTO-001",   "target":"HEAD-SEC",   "type":"reports"},
    ]

    # Dynamically generate 1000+ nodes based on department totals
    dept_configs = [
        ("Backend",   "HEAD-BE",   "backend",   180, "BE"),
        ("Frontend",  "HEAD-FE",   "frontend",  180, "FE"),
        ("Mobile",    "HEAD-FE",   "mobile",    60,  "MOB"),
        ("Database",  "HEAD-BE",   "database",  80,  "DB"),
        ("AI",        "HEAD-DATA", "ai",        60,  "ML"),
        ("Quality",   "HEAD-QA",   "qa",        100, "QA"),
        ("Security",  "HEAD-SEC",  "security",  50,  "SEC"),
        ("DevOps",    "HEAD-OPS",  "devops",    50,  "OPS"),
        # ── Corporate Operations ────────────────────────────
        ("HR",        "CEO-001",   "hr",        60,  "HR"),
        ("Legal",     "CEO-001",   "legal",     40,  "LEGAL"),
        ("Finance",   "CEO-001",   "finance",   60,  "FIN"),
        ("Sales",     "CEO-001",   "sales",     100, "SALES"),
        ("Marketing", "CEO-001",   "marketing", 100, "MKT"),
        ("Support",   "HEAD-OPS",  "support",   100, "SUP"),
    ]

    for dept_name, head_id, group_name, count, prefix in dept_configs:
        for i in range(1, count + 1):
            node_id = f"{prefix}-{i:03d}"
            # Add node
            nodes.append({
                "id": node_id, 
                "label": f"{prefix}-{i}", 
                "group": group_name, 
                "size": 11
            })
            # Link to Head Node (Hierarchy)
            links.append({"source": head_id, "target": node_id, "type": "manages"})
            # Link to Workspace (Shared drive)
            if group_name in ["backend", "frontend", "mobile", "database", "ai"]:
                links.append({"source": node_id, "target": "WORKSPACE", "type": "writes"})
            elif group_name in ["qa", "security"]:
                links.append({"source": node_id, "target": "WORKSPACE", "type": "reads"})

    # Workspace node (center)
    nodes.append({"id":"WORKSPACE",  "label":"SHARED\nWORKSPACE","group":"workspace","size":40})
    
    # Extra Core Nodes / Links (C-Suite and Special)
    nodes.extend([
        {"id":"REV-001",    "label":"Code Review",  "group":"qa",        "size":15},
        {"id":"BUG-001",    "label":"Bug Hunter",   "group":"qa",        "size":15},
        {"id":"CLIENT-001", "label":"Client Mgr",  "group":"client",    "size":18},
    ])

    links.extend([
        {"source":"HEAD-QA",   "target":"REV-001",    "type":"manages"},
        {"source":"HEAD-QA",   "target":"BUG-001",    "type":"manages"},
        {"source":"REV-001",   "target":"WORKSPACE",   "type":"reads"},
        {"source":"BUG-001",   "target":"WORKSPACE",   "type":"reads"},
        {"source":"WORKSPACE", "target":"HEAD-OPS",    "type":"deploys"},
    ])
    
    try:
        return jsonify({"nodes": nodes, "links": links})
    except Exception as e:
        with open("/tmp/api_error.log", "w") as f:
            f.write(f"JSONIFY ERROR: {str(e)}")
        return jsonify({"error": str(e)}), 500
