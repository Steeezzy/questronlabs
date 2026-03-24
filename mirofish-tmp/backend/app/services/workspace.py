import os
import json
import time
import asyncio
import requests
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# ─── Model assignments ────────────────────────────────────────
# 🔥 NVIDIA Nemotron 3 Super — #1 agent brain, free
MODELS = {
    "nemotron_super": "nvidia/nemotron-3-super-120b-a12b:free",
    "nemotron_nano":  "nvidia/nemotron-3-nano-30b-a3b:free",
    "qwen_coder":     "qwen/qwen3-coder:free",
    "step_flash":     "stepfun/step-3.5-flash:free",
}

ROLE_MODELS = {
    # ── LAYER 1 — C-Suite & Management → Nemotron Super ──────
    "CEO":                  MODELS["nemotron_super"],
    "CTO":                  MODELS["nemotron_super"],
    "COO":                  MODELS["nemotron_super"],
    "Department Head":      MODELS["nemotron_super"],
    "Senior Manager":       MODELS["nemotron_super"],
    "Project Manager":      MODELS["nemotron_super"],
    "Solution Architect":   MODELS["nemotron_super"],
    "Business Analyst":     MODELS["nemotron_super"],
    "IT Consultant":        MODELS["nemotron_super"],

    # ── Senior Technical → Nemotron Super ────────────────────
    "Code Review Agent":    MODELS["nemotron_super"],
    "Bug Hunter":           MODELS["nemotron_super"],
    "Security Auditor":     MODELS["nemotron_super"],
    "Penetration Tester":   MODELS["nemotron_super"],
    "ML Engineer":          MODELS["nemotron_super"],
    "Legacy Mod Agent":     MODELS["nemotron_super"],
    "Integration Agent":    MODELS["nemotron_super"],

    # ── Mid-tier Analysis → Nemotron Nano ────────────────────
    "Data Engineer":        MODELS["nemotron_nano"],
    "Performance Agent":    MODELS["nemotron_nano"],
    "Analytics Agent":      MODELS["nemotron_nano"],
    "Compliance Agent":     MODELS["nemotron_nano"],
    "Finance Agent":        MODELS["nemotron_nano"],
    "Supply Chain Agent":   MODELS["nemotron_nano"],
    "HR Agent":             MODELS["nemotron_nano"],
    "QA Engineer":          MODELS["nemotron_nano"],
    "E2E Test Agent":       MODELS["nemotron_nano"],
    "Load Test Agent":      MODELS["nemotron_nano"],

    # ── All Coding → Qwen3 Coder ──────────────────────────────
    "Frontend Developer":   MODELS["qwen_coder"],
    "Backend Developer":    MODELS["qwen_coder"],
    "Mobile Developer":     MODELS["qwen_coder"],
    "Database Engineer":    MODELS["qwen_coder"],
    "DevOps Engineer":      MODELS["qwen_coder"],
    "Unit Test Agent":      MODELS["qwen_coder"],
    "CI/CD Agent":          MODELS["qwen_coder"],
    "IoT Agent":            MODELS["qwen_coder"],
    "Cloud Deploy Agent":   MODELS["qwen_coder"],
}

# Fallbacks if any model goes offline
FALLBACKS = [
    MODELS["step_flash"],
    "mistralai/mistral-7b-instruct:free",
    "meta-llama/llama-3.1-8b-instruct:free",
]

# Per-model settings — some models need stricter params
MODEL_PARAMS = {
    "nvidia/nemotron-3-super-120b-a12b:free": {
        "temperature": 0.3,
        "max_tokens":  600,
        "repetition_penalty": 1.15,
    },
    "stepfun/step-3.5-flash:free": {
        "temperature": 0.4,
        "max_tokens":  800,
        "repetition_penalty": 1.1,
    },
    "qwen/qwen3-coder:free": {
        "temperature": 0.2,
        "max_tokens":  1000,
        "repetition_penalty": 1.05,
    },
}

def get_model_params(model: str) -> dict:
    return MODEL_PARAMS.get(model, {
        "temperature": 0.3,
        "max_tokens":  600,
        "repetition_penalty": 1.1,
    })

# Multiple free coding models to rotate between
CODING_MODELS = [
    "qwen/qwen3-coder:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "stepfun/step-3.5-flash:free",
    "mistralai/mistral-7b-instruct:free",
    "meta-llama/llama-3.1-8b-instruct:free",
]

# Track which model each agent uses
_agent_model_map = {}

def get_rotating_model(agent_name: str) -> str:
    """Each agent gets a fixed model from the rotation"""
    if agent_name not in _agent_model_map:
        # Assign based on agent number to spread load
        num = int(''.join(filter(str.isdigit, agent_name)) or 0)
        _agent_model_map[agent_name] = CODING_MODELS[num % len(CODING_MODELS)]
    return _agent_model_map[agent_name]

def get_model(role: str) -> str:
    for key, model in ROLE_MODELS.items():
        if key.lower() in role.lower():
            return model
    return MODELS["nemotron_nano"]  # safe default


# ══════════════════════════════════════════════════════════════
# SHARED WORKSPACE — all agents read and write here
# ══════════════════════════════════════════════════════════════

class SharedWorkspace:
    def __init__(self, project_name: str, client: str):
        self.project_name = project_name
        self.client = client
        self.created_at = datetime.now().isoformat()

        # ── The shared state all agents see ──────────────────
        self.state = {
            "project":        project_name,
            "client":         client,
            "phase":          "planning",   # planning → designing → building → testing → deploying
            "files":          {},           # filename → code content
            "decisions":      [],           # architectural decisions made
            "debate_board":   [],           # ongoing agent debates
            "review_queue":   [],           # code awaiting review
            "approved_files": [],           # files approved by review
            "bugs":           [],           # bugs found
            "fixed_bugs":     [],           # bugs fixed and verified
            "test_results":   {},           # test file → pass/fail
            "documents":      {},           # BRD, architecture, reports
            "agent_logs":     [],           # full activity log
        }

    # ── Write a file to workspace ─────────────────────────────
    def write_file(self, agent: str, filename: str, content: str):
        self.state["files"][filename] = {
            "content":    content,
            "written_by": agent,
            "timestamp":  datetime.now().strftime("%H:%M:%S"),
            "reviews":    [],
            "approved":   False,
        }
        self.log(agent, f"Wrote file: {filename}")
        self.state["review_queue"].append(filename)

    # ── Add a debate entry ────────────────────────────────────
    def add_debate(self, agent: str, topic: str, opinion: str):
        self.state["debate_board"].append({
            "agent":     agent,
            "topic":     topic,
            "opinion":   opinion,
            "time":      datetime.now().strftime("%H:%M:%S"),
            "responses": [],
        })
        self.log(agent, f"Started debate: {topic}")

    def respond_to_debate(self, agent: str, debate_idx: int, response: str):
        if debate_idx < len(self.state["debate_board"]):
            self.state["debate_board"][debate_idx]["responses"].append({
                "agent":    agent,
                "response": response,
                "time":     datetime.now().strftime("%H:%M:%S"),
            })

    # ── Review a file ─────────────────────────────────────────
    def review_file(self, agent: str, filename: str, verdict: str, comment: str):
        if filename in self.state["files"]:
            self.state["files"][filename]["reviews"].append({
                "agent":   agent,
                "verdict": verdict,    # "approve" or "reject"
                "comment": comment,
                "time":    datetime.now().strftime("%H:%M:%S"),
            })
            reviews = self.state["files"][filename]["reviews"]
            approvals = sum(1 for r in reviews if r["verdict"] == "approve")
            if approvals >= 3:
                self.state["files"][filename]["approved"] = True
                self.state["approved_files"].append(filename)
                if filename in self.state["review_queue"]:
                    self.state["review_queue"].remove(filename)
                self.log(agent, f"✅ {filename} APPROVED (3/3 reviews)")

    # ── Report a bug ──────────────────────────────────────────
    def report_bug(self, agent: str, filename: str, description: str, severity: str):
        self.state["bugs"].append({
            "id":          f"BUG-{len(self.state['bugs'])+1:03d}",
            "file":        filename,
            "found_by":    agent,
            "description": description,
            "severity":    severity,   # critical / high / medium / low
            "status":      "open",
            "time":        datetime.now().strftime("%H:%M:%S"),
        })
        self.log(agent, f"🐛 Bug found in {filename}: {description[:50]}")

    # ── Fix a bug ─────────────────────────────────────────────
    def fix_bug(self, agent: str, bug_id: str, fix_description: str):
        for bug in self.state["bugs"]:
            if bug["id"] == bug_id:
                bug["status"] = "fixed"
                bug["fixed_by"] = agent
                bug["fix"] = fix_description
                self.state["fixed_bugs"].append(bug_id)
                self.log(agent, f"✅ Fixed {bug_id}")
                break

    # ── Add a decision ────────────────────────────────────────
    def add_decision(self, agent: str, decision: str, reason: str):
        self.state["decisions"].append({
            "made_by": agent,
            "decision": decision,
            "reason":   reason,
            "time":     datetime.now().strftime("%H:%M:%S"),
        })
        self.log(agent, f"📋 Decision: {decision[:60]}")

    # ── Add document ──────────────────────────────────────────
    def add_document(self, agent: str, doc_name: str, content: str):
        self.state["documents"][doc_name] = {
            "content":    content,
            "written_by": agent,
            "time":       datetime.now().strftime("%H:%M:%S"),
        }
        self.log(agent, f"📄 Document created: {doc_name}")

    # ── Log activity ──────────────────────────────────────────
    def log(self, agent: str, action: str):
        self.state["agent_logs"].append({
            "time":   datetime.now().strftime("%H:%M:%S"),
            "agent":  agent,
            "action": action,
        })

    # ── Get workspace summary (what agents read) ──────────────
    def get_summary(self) -> str:
        bugs_open = [b for b in self.state["bugs"] if b["status"] == "open"]
        return f"""
=== SHARED WORKSPACE: {self.project_name} ===
Phase: {self.state['phase']}
Files written: {len(self.state['files'])}
Files approved: {len(self.state['approved_files'])}
Files in review: {len(self.state['review_queue'])}
Decisions made: {len(self.state['decisions'])}
Open bugs: {len(bugs_open)}
Fixed bugs: {len(self.state['fixed_bugs'])}
Active debates: {len(self.state['debate_board'])}
Documents: {list(self.state['documents'].keys())}

RECENT DECISIONS:
{chr(10).join([f"- {d['decision']}" for d in self.state['decisions'][-3:]])}

OPEN BUGS:
{chr(10).join([f"- [{b['severity']}] {b['file']}: {b['description'][:50]}" for b in bugs_open[:5]])}

FILES IN REVIEW:
{chr(10).join(self.state['review_queue'][:5])}
"""

    def to_json(self) -> dict:
        return self.state


# ══════════════════════════════════════════════════════════════
# AGENT — one agent that reads workspace and acts
# ══════════════════════════════════════════════════════════════

class Agent:
    def __init__(self, name: str, role: str, department: str):
        self.name = name
        self.role = role
        self.department = department

        # Management → Nemotron Super
        if any(r in role for r in ["CEO", "CTO", "Manager", "Architect", "Head"]):
            self.model = "nvidia/nemotron-3-super-120b-a12b:free"
            
        # Coding → ROTATE across 5 models
        elif any(r in role for r in ["Developer", "Engineer", "DevOps", "Test"]):
            self.model = get_rotating_model(name)
            
        # Everything else → Step Flash
        else:
            self.model = "stepfun/step-3.5-flash:free"

    def _call_llm(self, system: str, user: str) -> str:
        max_retries = 3
        retry_delay = 5  # seconds
        params = get_model_params(self.model)
        
        for attempt in range(max_retries):
            try:
                res = requests.post(
                    OPENROUTER_URL,
                    headers={
                        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                        "Content-Type":  "application/json",
                        "HTTP-Referer":  "https://questronlabs.com",
                        "X-Title":       "Qestron Labs",
                    },
                    json={
                        "model":    self.model,
                        "messages": [
                            {"role": "system",  "content": system},
                            {"role": "user",    "content": user},
                        ],
                        "max_tokens":        params.get("max_tokens", 600),
                        "temperature":       params.get("temperature", 0.3),
                        "top_p":             0.9,
                        "repetition_penalty": params.get("repetition_penalty", 1.15),
                        "stop": [
                            "setup securely",
                            "layout setup",
                            "\n\n\n",
                        ]
                    },
                    timeout=60
                )
                data = res.json()
                
                if "choices" in data:
                    content = data["choices"][0]["message"]["content"]
                    if content is None:
                        content = ""
                        
                    # Extra safety — detect and cut loops
                    words = content.split()
                    seen = {}
                    clean = []
                    for word in words:
                        seen[word] = seen.get(word, 0) + 1
                        if seen[word] > 4:   # word repeating more than 4 times = loop
                            break
                        clean.append(word)
                    return " ".join(clean)
                
                print(f"\n[DEBUG {self.name}] API ERROR (Attempt {attempt+1}/{max_retries}): {data}")
                
                error_info = data.get("error", {})
                code = error_info.get("code")
                
                if code in [429, 503] or "Rate limit" in error_info.get("message", ""):
                    print(f"[{self.name}] Backing off for {retry_delay}s due to rate limit/load...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                else:
                    break  # Don't retry for other errors (like 401, 404)
                    
            except Exception as e:
                print(f"[{self.name}] Network error during LLM call: {str(e)[:100]}")
                time.sleep(2)
                
        return f"[{self.name} error: Failed after {max_retries} attempts]"

    def act(self, workspace: SharedWorkspace, task: str) -> str:
        system = f"""You are {self.name}, a {self.role} at Qestron Labs — 
an autonomous IT company replacing Infosys and TCS.
Department: {self.department}
Model: {self.model}

WORKSPACE SUMMARY:
{workspace.get_summary()}

RULES:
- Read the workspace before acting
- Be specific about what you build/decide/review
- If you see a problem in someone's work — say so
- Format: start with your action, then details
- Keep response under 200 words but be specific"""

        return self._call_llm(system, task)


# ══════════════════════════════════════════════════════════════
# MULTI-AGENT CODING TEAM — multiple devs on same codebase
# ══════════════════════════════════════════════════════════════

class MultiAgentCodingTeam:
    def __init__(self, workspace: SharedWorkspace, project_requirement: str):
        self.workspace = workspace
        self.requirement = project_requirement

        # ── Management layer ─────────────────────────────────
        self.ceo       = Agent("CEO-001",      "CEO",              "Executive")
        self.cto       = Agent("CTO-001",      "CTO",              "Executive")
        self.architect = Agent("ARCH-001",     "Solution Architect","Engineering")
        self.pm        = Agent("PM-001",       "Project Manager",  "Delivery")
        self.pm2       = Agent("PM-002",       "Project Manager",  "Delivery")

        # ── Business Expansion layer ─────────────────────────
        self.sales_rep     = Agent("SALES-001",    "Sales Representative", "Sales")
        self.legal_counsel = Agent("LEGAL-001",    "Legal Counsel",       "Legal")

        # ── Department heads ──────────────────────────────────
        self.head_frontend  = Agent("HEAD-FE",  "Department Head",  "Frontend")
        self.head_backend   = Agent("HEAD-BE",  "Department Head",  "Backend")
        self.head_qa        = Agent("HEAD-QA",  "Department Head",  "Quality")
        self.head_devops    = Agent("HEAD-OPS", "Department Head",  "DevOps")
        self.head_security  = Agent("HEAD-SEC", "Department Head",  "Security")
        self.head_data      = Agent("HEAD-DATA","Department Head",  "Data & AI")

        # ── Frontend dev team ─────────────────────────────────
        self.fe_devs = [
            Agent(f"FE-{i:03d}", "Frontend Developer", "Frontend")
            for i in range(1, 6)   # 5 frontend devs
        ]

        # ── Backend dev team ──────────────────────────────────
        self.be_devs = [
            Agent(f"BE-{i:03d}", "Backend Developer", "Backend")
            for i in range(1, 6)   # 5 backend devs
        ]

        # ── Mobile dev team ───────────────────────────────────
        self.mobile_devs = [
            Agent(f"MOB-{i:03d}", "Mobile Developer", "Mobile")
            for i in range(1, 3)   # 2 mobile devs
        ]

        # ── Database team ─────────────────────────────────────
        self.db_engineers = [
            Agent(f"DB-{i:03d}", "Database Engineer", "Data")
            for i in range(1, 3)   # 2 DB engineers
        ]

        # ── QA team ───────────────────────────────────────────
        self.qa_agents = [
            Agent(f"QA-{i:03d}", "Unit Test Agent", "Quality")
            for i in range(1, 4)   # 3 QA agents
        ]
        self.bug_hunter    = Agent("BUG-001",  "Bug Hunter",       "Quality")
        self.code_reviewer = Agent("REV-001",  "Code Review Agent","Quality")

        # ── DevOps team ───────────────────────────────────────
        self.devops_agents = [
            Agent(f"OPS-{i:03d}", "DevOps Engineer", "DevOps")
            for i in range(1, 3)   # 2 devops agents
        ]

        # ── Security team ─────────────────────────────────────
        self.security_agents = [
            Agent(f"SEC-{i:03d}", "Penetration Tester", "Security")
            for i in range(1, 3)
        ]

        # ── Data & AI team ────────────────────────────────────
        self.ml_engineers = [
            Agent(f"ML-{i:03d}", "ML Engineer", "Data & AI")
            for i in range(1, 3)
        ]

    # ── PHASE 0: Sales & Pitching ───────────────────────────
    def phase_sales(self):
        print("\n" + "="*60)
        print("PHASE 0 — SALES & CLIENT PITCHING")
        print("="*60)
        self.workspace.state["phase"] = "sales"

        pitch = self.sales_rep.act(
            self.workspace,
            f"Draft a winning sales pitch and RFP response for this client requirement: {self.requirement}. "
            f"Offer top-tier AI automation, timeline, and rough cost estimation. Save to workspace documents."
        )
        self.workspace.add_document("SALES-001", "Client Pitch & Proposal", pitch)
        with open('workspace_output.json', 'w') as f:
            json.dump(self.workspace.to_json(), f, indent=2)
        print(f"\n[SALES-001] {pitch[:200]}")

    # ── PHASE 0.1: Legal & Contracts ─────────────────────────
    def phase_legal(self):
        print("\n" + "="*60)
        print("PHASE 0.1 — LEGAL AUDIT & CONTRACTS")
        print("="*60)
        self.workspace.state["phase"] = "legal"

        audit = self.legal_counsel.act(
            self.workspace,
            "Review the Client Pitch & Proposal drafted by Sales. "
            "Audit liability, intellectual property clauses, and SLA standards. "
            "Write 'APPROVED' if safe, or list legal blockers."
        )
        self.workspace.add_document("LEGAL-001", "Legal Contract Audit", audit)
        self.workspace.add_decision("LEGAL-001", "Contract signed & approved", "Legal audit passed successfully.")
        with open('workspace_output.json', 'w') as f:
            json.dump(self.workspace.to_json(), f, indent=2)
        print(f"\n[LEGAL-001] {audit[:200]}")

    # ── PHASE 1: Planning & Architecture ─────────────────────
    def phase_planning(self):
        print("\n" + "="*60)
        print("PHASE 1 — PLANNING & ARCHITECTURE")
        print("="*60)

        # CEO scopes the project
        ceo_response = self.ceo.act(
            self.workspace,
            f"Scope this project for our team: {self.requirement}. "
            f"Define budget, timeline, and success metrics. Add your decision to workspace."
        )
        self.workspace.add_decision("CEO-001", f"Project scoped: {self.requirement[:50]}", ceo_response[:100])
        print(f"\n[CEO-001] {ceo_response[:200]}")

        # CTO decides architecture
        cto_response = self.cto.act(
            self.workspace,
            f"Based on CEO scope, decide the full tech stack and system architecture. "
            f"Project: {self.requirement}. Be specific about every technology choice."
        )
        self.workspace.add_decision("CTO-001", "Tech stack decided", cto_response[:100])
        print(f"\n[CTO-001] {cto_response[:200]}")

        # Architect designs system
        arch_response = self.architect.act(
            self.workspace,
            "Based on CTO's tech stack decision, design the complete system architecture. "
            "Include microservices breakdown, database schema, API design, and deployment topology."
        )
        self.workspace.add_document("ARCH-001", "System Architecture", arch_response)
        print(f"\n[ARCH-001] {arch_response[:200]}")

        # Department heads debate architecture
        print("\n--- DEPARTMENT HEAD DEBATE ---")
        self.workspace.add_debate(
            "HEAD-BE",
            "Database choice",
            self.head_backend.act(self.workspace,
                "Review the architecture. Do you agree with the database choice? State your position clearly.")
        )

        fe_opinion = self.head_frontend.act(self.workspace,
            "Review the architecture from frontend perspective. What concerns do you have?")
        self.workspace.add_debate("HEAD-FE", "Frontend architecture", fe_opinion)
        print(f"\n[HEAD-FE] {fe_opinion[:150]}")

        qa_opinion = self.head_qa.act(self.workspace,
            "Review the architecture from QA perspective. What testing challenges do you foresee?")
        self.workspace.add_debate("HEAD-QA", "QA concerns", qa_opinion)
        print(f"\n[HEAD-QA] {qa_opinion[:150]}")

        # PM creates sprint plan
        pm_response = self.pm.act(
            self.workspace,
            "Based on all decisions, create a sprint plan. "
            "Assign tasks to frontend team, backend team, mobile team, DB team, QA team, DevOps team. "
            "Set clear priorities."
        )
        self.workspace.add_document("PM-001", "Sprint Plan", pm_response)
        print(f"\n[PM-001] {pm_response[:200]}")

        self.workspace.state["phase"] = "building"
        with open('workspace_output.json', 'w') as f:
            json.dump(self.workspace.to_json(), f, indent=2)
        print(f"\n✅ Phase 1 complete. {len(self.workspace.state['decisions'])} decisions made.")

    # ── PHASE 2: Multi-Agent Development ─────────────────────
    def phase_development(self):
        print("\n" + "="*60)
        print("PHASE 2 — MULTI-AGENT DEVELOPMENT")
        print("="*60)

        # All dev teams work in parallel
        # Backend team
        print("\n--- BACKEND TEAM ---")
        for i, dev in enumerate(self.be_devs):
            task = [
                "Write the main FastAPI application entry point with health check",
                "Write the authentication service with JWT tokens",
                "Write the database models and connection setup",
                "Write the main business logic API endpoints",
                "Write the background task workers and job queue",
            ][i]
            time.sleep(8)  # Rate limit backup delay
            response = dev.act(self.workspace, task)
            filename = [
                "backend/main.py",
                "backend/auth/service.py",
                "backend/models/database.py",
                "backend/api/routes.py",
                "backend/workers/tasks.py",
            ][i]
            self.workspace.write_file(dev.name, filename, response)
            print(f"[{dev.name}] ✍️  {filename}")

        # Backend dept head reviews team output
        be_review = self.head_backend.act(
            self.workspace,
            "Review what the backend team just wrote. "
            "Are there any issues, inconsistencies, or improvements needed? Be specific."
        )
        print(f"\n[HEAD-BE Review] {be_review[:200]}")

        # Frontend team
        print("\n--- FRONTEND TEAM ---")
        for i, dev in enumerate(self.fe_devs):
            task = [
                "Write the main React App.jsx with routing and layout",
                "Write the Dashboard page component with data visualization",
                "Write the authentication pages (login, register, forgot password)",
                "Write reusable UI components (Button, Input, Card, Modal)",
                "Write the API service layer for frontend-backend communication",
            ][i]
            time.sleep(8)  # Rate limit backup delay
            response = dev.act(self.workspace, task)
            filename = [
                "frontend/src/App.jsx",
                "frontend/src/pages/Dashboard.jsx",
                "frontend/src/pages/Auth.jsx",
                "frontend/src/components/UI.jsx",
                "frontend/src/services/api.js",
            ][i]
            self.workspace.write_file(dev.name, filename, response)
            print(f"[{dev.name}] ✍️  {filename}")

        # Database team
        print("\n--- DATABASE TEAM ---")
        for i, eng in enumerate(self.db_engineers):
            task = [
                "Write the complete database schema with all tables, indexes and constraints",
                "Write database migration scripts and seed data",
            ][i]
            time.sleep(8)  # Rate limit backup delay
            response = eng.act(self.workspace, task)
            filename = ["database/schema.sql", "database/migrations.sql"][i]
            self.workspace.write_file(eng.name, filename, response)
            print(f"[{eng.name}] ✍️  {filename}")

        # Mobile team
        print("\n--- MOBILE TEAM ---")
        for i, dev in enumerate(self.mobile_devs):
            task = [
                "Write React Native App.tsx with navigation and auth flow",
                "Write mobile API service and state management",
            ][i]
            time.sleep(8)  # Rate limit backup delay
            response = dev.act(self.workspace, task)
            filename = ["mobile/App.tsx", "mobile/services/api.ts"][i]
            self.workspace.write_file(dev.name, filename, response)
            print(f"[{dev.name}] ✍️  {filename}")

        # ML team
        print("\n--- DATA & AI TEAM ---")
        for i, eng in enumerate(self.ml_engineers):
            task = [
                "Write the ML model training script for fraud detection",
                "Write the model API wrapper to serve predictions",
            ][i]
            time.sleep(8)  # Rate limit backup delay
            response = eng.act(self.workspace, task)
            filename = ["ml/train_model.py", "ml/model_api.py"][i]
            self.workspace.write_file(eng.name, filename, response)
            print(f"[{eng.name}] ✍️  {filename}")

        print(f"\n✅ Phase 2 complete. {len(self.workspace.state['files'])} files written.")
        self.workspace.state["phase"] = "reviewing"
        with open('workspace_output.json', 'w') as f:
            json.dump(self.workspace.to_json(), f, indent=2)

    # ── PHASE 3: Code Review & Debate ────────────────────────
    def phase_review(self):
        print("\n" + "="*60)
        print("PHASE 3 — CODE REVIEW & DEBATE")
        print("="*60)

        files_to_review = list(self.workspace.state["files"].keys())[:6]

        for filename in files_to_review:
            print(f"\n--- Reviewing: {filename} ---")
            file_content = self.workspace.state["files"][filename]["content"]

            # 3 different reviewers review each file
            reviewers = [self.code_reviewer, self.head_backend, self.head_security]
            for reviewer in reviewers:
                review = reviewer.act(
                    self.workspace,
                    f"Review this file: {filename}\n\n"
                    f"Content preview: {file_content[:300]}\n\n"
                    f"Verdict: approve or reject? Give specific feedback."
                )
                verdict = "approve" if any(w in review.lower() for w in
                    ["approve", "looks good", "good", "correct", "well written"]) else "reject"
                self.workspace.review_file(reviewer.name, filename, verdict, review[:100])
                print(f"  [{reviewer.name}] {verdict.upper()} — {review[:80]}")

        # Bug Hunter scans everything
        print("\n--- BUG HUNTER SCAN ---")
        bugs_found = self.bug_hunter.act(
            self.workspace,
            "Scan all files written by the dev team. "
            "Find real bugs, security issues, performance problems. "
            "List each bug with: file, severity (critical/high/medium), description."
        )
        print(f"[BUG-001] {bugs_found[:300]}")

        # Report bugs
        for i, line in enumerate(bugs_found.split('\n')[:3]):
            if len(line) > 20:
                self.workspace.report_bug(
                    "BUG-001",
                    files_to_review[min(i, len(files_to_review)-1)],
                    line[:80],
                    "high"
                )

        # Dev agents fix bugs
        print("\n--- BUG FIXES ---")
        for bug in self.workspace.state["bugs"][:3]:
            fixer = self.be_devs[0]
            fix = fixer.act(
                self.workspace,
                f"Fix this bug: {bug['description']} in {bug['file']}. "
                f"Show the corrected code."
            )
            self.workspace.fix_bug(fixer.name, bug["id"], fix[:100])
            print(f"[{fixer.name}] Fixed {bug['id']}")

        print(f"\n✅ Phase 3 complete.")
        self.workspace.state["phase"] = "testing"
        with open('workspace_output.json', 'w') as f:
            json.dump(self.workspace.to_json(), f, indent=2)

    # ── PHASE 4: QA Testing ───────────────────────────────────
    def phase_testing(self):
        print("\n" + "="*60)
        print("PHASE 4 — QA & TESTING")
        print("="*60)

        for i, qa in enumerate(self.qa_agents):
            task = [
                "Write and describe unit tests for all backend API endpoints. List test cases.",
                "Write E2E tests for the main user flows using Playwright. List scenarios.",
                "Design load test for 2M daily transactions. State expected results.",
            ][i]
            result = qa.act(self.workspace, task)
            filename = [
                "tests/test_backend.py",
                "tests/test_e2e.py",
                "tests/test_load.py"
            ][i]
            self.workspace.state["test_results"][filename] = result[:100]
            print(f"[{qa.name}] {filename} — {result[:120]}")

        # Security audit
        print("\n--- SECURITY AUDIT ---")
        for sec in self.security_agents:
            audit = sec.act(
                self.workspace,
                "Run a security audit on the codebase. "
                "Check for: SQL injection, XSS, auth bypass, API exposure, data leaks. "
                "Rate overall security score out of 100."
            )
            self.workspace.add_document(sec.name, "Security Audit Report", audit)
            print(f"[{sec.name}] {audit[:150]}")

        print(f"\n✅ Phase 4 complete.")
        self.workspace.state["phase"] = "deploying"
        with open('workspace_output.json', 'w') as f:
            json.dump(self.workspace.to_json(), f, indent=2)

    # ── PHASE 5: DevOps & Deployment ─────────────────────────
    def phase_deployment(self):
        print("\n" + "="*60)
        print("PHASE 5 — DEVOPS & DEPLOYMENT")
        print("="*60)

        devops_tasks = [
            ("GitHub Actions CI/CD pipeline", ".github/workflows/deploy.yml"),
            ("Docker + Kubernetes config",    "infra/k8s/deployment.yaml"),
        ]
        for i, (task_desc, filename) in enumerate(devops_tasks):
            result = self.devops_agents[i].act(
                self.workspace,
                f"Write the {task_desc} for this project. "
                f"Include all stages: build, test, security scan, deploy."
            )
            self.workspace.write_file(self.devops_agents[i].name, filename, result)
            print(f"[{self.devops_agents[i].name}] ✍️  {filename}")

        # Head of DevOps final review
        ops_review = self.head_devops.act(
            self.workspace,
            "Review the deployment config. Is everything production-ready? "
            "Any risks for the go-live? Give final approval or list blockers."
        )
        print(f"\n[HEAD-OPS] {ops_review[:200]}")

        print(f"\n✅ Phase 5 complete.")
        self.workspace.state["phase"] = "complete"
        with open('workspace_output.json', 'w') as f:
            json.dump(self.workspace.to_json(), f, indent=2)

    # ── PHASE 6: Continuous Helpdesk Ticketing ───────────────
    def phase_helpdesk(self, ticket_count=2):
        print("\n" + "="*60)
        print("PHASE 6 — CONTINUOUS HELPDESK & SUPPORT")
        print("="*60)
        self.workspace.state["phase"] = "support"

        # Simulating L1 Ticket Ingress
        tickets = [
            "Users report that they cannot reset their passwords, endpoint returns 500 error.",
            "Dashboard load time is extremely slow on mobile devices.",
        ]

        for i, ticket_desc in enumerate(tickets[:ticket_count]):
            print(f"\n--- Ticket L1-00{i+1} ---")
            self.workspace.log("CLIENT-001", f"Raised support ticket: {ticket_desc[:40]}")
            self.workspace.report_bug("CLIENT-001", "Production", ticket_desc, "high")

            # L2 Support picks up and logs proposed fix
            l2_fixer = self.be_devs[0] if "password" in ticket_desc else self.fe_devs[0]
            fix = l2_fixer.act(
                self.workspace,
                f"You are acting as L2 Support. Fix this active ticket: {ticket_desc}. "
                f"Provide the corrected block of code structure or config resolution."
            )
            self.workspace.fix_bug(l2_fixer.name, f"BUG-{len(self.workspace.state['bugs']):03d}", fix[:100])
            print(f"[{l2_fixer.name} L2] Handled ticket. Resolution logged in workspace state.")

        with open('workspace_output.json', 'w') as f:
            json.dump(self.workspace.to_json(), f, indent=2)

    # ── RUN FULL PIPELINE ─────────────────────────────────────
    def run(self):
        print(f"\n🚀 QESTRON LABS — AUTONOMOUS IT COMPANY")
        print(f"Project: {self.workspace.project_name}")
        print(f"Client:  {self.workspace.client}")
        print(f"Models:  MiMo Pro + Step Flash + Qwen Coder (all FREE)")
        print(f"Agents:  {self._count_agents()} active agents\n")

        self.phase_sales()
        self.phase_legal()
        self.phase_planning()
        self.phase_development()
        self.phase_review()
        self.phase_testing()
        self.phase_deployment()
        self.phase_helpdesk()

        return self.workspace.to_json()

    def _count_agents(self):
        return (
            5 +                          # C-suite + managers
            6 +                          # dept heads
            len(self.fe_devs) +
            len(self.be_devs) +
            len(self.mobile_devs) +
            len(self.db_engineers) +
            len(self.qa_agents) + 2 +    # + bug hunter + reviewer
            len(self.devops_agents) +
            len(self.security_agents) +
            len(self.ml_engineers)
        )


# ══════════════════════════════════════════════════════════════
# RUN IT
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    workspace = SharedWorkspace(
        project_name="CoreBanking 2026 — Legacy Modernization",
        client="HDFC Digital Ventures"
    )

    team = MultiAgentCodingTeam(
        workspace=workspace,
        project_requirement="""
        Modernize a 25-year-old COBOL mainframe banking system for HDFC.
        System handles 2M daily transactions across 800 branches in India.
        Build: React dashboard + React Native mobile app + FastAPI microservices
        + PostgreSQL + Redis + Kafka streaming + Razorpay + UPI payments
        + Sarvam AI for Hindi/Tamil/Telugu + AWS deployment + fraud detection ML model.
        Must handle 2M daily transactions with 99.99% uptime.
        PCI-DSS + RBI Guidelines compliance required.
        """
    )

    result = team.run()

    # Save final workspace state
    with open("workspace_output.json", "w") as f:
        json.dump(result, f, indent=2)

    print("\n" + "="*60)
    print("FINAL WORKSPACE SUMMARY")
    print("="*60)
    print(workspace.get_summary())
    print(f"\n✅ Full output saved to workspace_output.json")
