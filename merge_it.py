import re
import os

with open("admin/dashboard.html", "r") as f:
    content = f.read()

# 1. Inject CSS
css_to_add = """
        /* --- NEW SIMULATION ENGINE CSS --- */
        .form-grid{display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;margin-bottom:1.5rem;}
        .form-grid.three{grid-template-columns:1fr 1fr 1fr;}
        .form-grid.full{grid-template-columns:1fr;}

        .section-card{background:var(--bg-surface);border:1px solid var(--border-light);border-radius:12px;padding:1.5rem;margin-bottom:1.25rem;backdrop-filter:blur(12px);}
        .section-header{display:flex;align-items:center;gap:0.75rem;margin-bottom:1.25rem;padding-bottom:0.85rem;border-bottom:1px solid var(--border-light);}
        .section-num{width:24px;height:24px;border-radius:6px;background:rgba(56,189,248,0.15);color:var(--brand-primary);font-size:0.72rem;font-weight:600;display:flex;align-items:center;justify-content:center;flex-shrink:0;}
        .section-title{font-family:'Outfit',sans-serif;font-weight:600;font-size:0.95rem;}
        .section-sub{font-size:0.78rem;color:var(--text-secondary);margin-top:0.15rem;}
        .section-badge{margin-left:auto;font-size:0.68rem;padding:0.2rem 0.6rem;border-radius:4px;font-weight:600;}
        .badge-required{background:rgba(248,113,113,0.15);color:var(--brand-danger);}
        .badge-optional{background:rgba(161,161,170,0.15);color:var(--text-secondary);}
        .badge-auto{background:rgba(52,211,153,0.15);color:var(--brand-accent);}

        .field{display:flex;flex-direction:column;gap:0.4rem;}
        .field label{font-size:0.82rem;color:var(--text-secondary);font-weight:500;}
        .field label .req{color:var(--brand-danger);margin-left:2px;}
        .field input,.field select,.field textarea{
            background:rgba(0,0,0,0.3);border:1px solid var(--border-light);border-radius:8px;
            padding:0.75rem 1rem;color:var(--text-primary);font-family:inherit;
            font-size:0.9rem;outline:none;transition:border-color 0.15s;width:100%;
        }
        .field input:focus,.field select:focus,.field textarea:focus{border-color:var(--brand-primary);box-shadow:0 0 0 2px rgba(56,189,248,0.2);}
        .field select option{background:var(--bg-base);color:white;}
        .field textarea{resize:vertical;min-height:90px;line-height:1.6;}

        .check-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:0.75rem;}
        .check-item{display:flex;align-items:center;gap:0.75rem;padding:0.75rem 1rem;background:rgba(0,0,0,0.2);border:1px solid var(--border-light);border-radius:8px;cursor:pointer;transition:all 0.15s;}
        .check-item:hover{border-color:rgba(255,255,255,0.2);}
        .check-item.selected{background:rgba(56,189,248,0.1);border-color:var(--brand-primary);}
        .check-item input[type=checkbox]{accent-color:var(--brand-primary);width:16px;height:16px;flex-shrink:0;cursor:pointer;}
        .check-label{font-size:0.85rem;font-weight:500;}
        .check-sub{font-size:0.75rem;color:var(--text-secondary);margin-top:2px;}

        .agent-preview{background:rgba(0,0,0,0.2);border:1px solid var(--border-light);border-radius:10px;padding:1.25rem;margin-bottom:1.5rem;}
        .ap-title{font-size:0.75rem;color:var(--text-secondary);text-transform:uppercase;letter-spacing:1.5px;margin-bottom:1rem;font-weight:600;}
        .ap-bars{display:flex;flex-direction:column;gap:0.6rem;}
        .ap-row{display:flex;align-items:center;gap:1rem;}
        .ap-name{font-size:0.85rem;width:180px;flex-shrink:0;color:var(--text-secondary);}
        .ap-bar-wrap{flex:1;height:6px;background:rgba(255,255,255,0.05);border-radius:3px;overflow:hidden;}
        .ap-bar-fill{height:100%;border-radius:3px;transition:width 0.5s ease;}
        .ap-count{font-size:0.85rem;color:var(--text-primary);width:50px;text-align:right;flex-shrink:0;font-variant-numeric:tabular-nums;font-weight:600;}

        .priority-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem;}
        .priority-item{background:rgba(0,0,0,0.2);border:1px solid var(--border-light);border-radius:8px;padding:1rem;}
        .priority-label{font-size:0.8rem;color:var(--text-secondary);margin-bottom:1rem;}
        .priority-val{font-family:'Outfit',sans-serif;font-size:1.5rem;font-weight:700;margin-bottom:0.5rem;}
        .priority-item input[type=range]{width:100%;accent-color:var(--brand-primary);cursor:pointer;}

        .output-panel{background:rgba(0,0,0,0.8);border:1px solid var(--border-light);border-radius:10px;padding:1.25rem;font-family:'JetBrains Mono',monospace;font-size:0.85rem;line-height:1.7;max-height:500px;overflow-y:auto;display:none;box-shadow:inset 0 0 20px rgba(0,0,0,0.5);}
        .output-panel.visible{display:block;}
        .out-ceo{color:#c084fc;} .out-cto{color:#60a5fa;} .out-pm{color:#facc15;}
        .out-dev{color:var(--brand-accent);} .out-qa{color:#f87171;} .out-devops{color:#fbbf24;}
        .out-sec{color:#f87171;} .out-data{color:#c084fc;} .out-bpm{color:#38bdf8;}
        .out-comment{color:var(--text-tertiary);}

        .run-bar{display:flex;align-items:center;gap:1rem;padding:1.25rem 1.5rem;background:var(--bg-surface);border:1px solid var(--border-light);border-radius:12px;margin-bottom:1.5rem;box-shadow:var(--shadow-glass);}
        .run-btn{background:linear-gradient(135deg, var(--brand-primary), var(--brand-secondary));color:white;border:none;padding:0.85rem 2rem;border-radius:8px;font-family:inherit;font-weight:600;font-size:1rem;cursor:pointer;transition:all 0.2s;display:flex;align-items:center;gap:0.5rem;}
        .run-btn:hover{box-shadow:0 4px 14px 0 rgba(56,189,248,0.39);transform:translateY(-1px);}
        .run-btn:disabled{opacity:0.5;cursor:not-allowed;transform:none;box-shadow:none;}
        .run-status{font-size:0.9rem;color:var(--text-secondary);font-weight:500;}

        .tag-row{display:flex;flex-wrap:wrap;gap:0.5rem;margin-top:0.75rem;}
        .tag-pill{font-size:0.75rem;padding:0.4rem 0.75rem;border-radius:6px;cursor:pointer;border:1px solid var(--border-light);color:var(--text-secondary);background:rgba(0,0,0,0.3);transition:all 0.15s;}
        .tag-pill:hover{border-color:rgba(255,255,255,0.2);}
        .tag-pill.active{background:rgba(56,189,248,0.15);border-color:var(--brand-primary);color:var(--brand-primary);}

        .compliance-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:0.75rem;}
</style>
"""

content = content.replace("</style>", css_to_add)

# 2. Inject HTML for View: Simulate
html_simulate = """
        <!-- View: Simulate -->
        <div id="view-simulate" class="view-section">
            <div class="page-header">
                <div>
                    <h1>Simulation Engine</h1>
                    <p style="color:var(--text-secondary); margin-top: 8px;">Configure and initialize the 1000-agent swarm for any IT delivery project</p>
                </div>
                <div>
                    <button class="btn-outline" onclick="loadTemplate('saas')" style="margin-right:10px;">Load Template</button>
                    <button class="btn-outline" onclick="clearForm()">Clear</button>
                </div>
            </div>
            
            <!-- SECTION 1 -->
            <div class="section-card">
              <div class="section-header">
                <div class="section-num">1</div>
                <div><div class="section-title">Client & Project Basics</div><div class="section-sub">Core project identification and client details</div></div>
                <div class="section-badge badge-required">Required</div>
              </div>
              <div class="form-grid three">
                <div class="field"><label>Client Name <span class="req">*</span></label><input type="text" id="clientName" placeholder="e.g. Global Bank Corp"></div>
                <div class="field"><label>Contact Person</label><input type="text" id="contactPerson" placeholder="e.g. Ravi Menon, CTO"></div>
                <div class="field"><label>Industry Vertical <span class="req">*</span></label>
                  <select id="industry">
                    <option value="">Select industry...</option>
                    <option>Banking & Finance</option>
                    <option>Healthcare & Pharma</option>
                    <option>Retail & Ecommerce</option>
                    <option>Manufacturing & IoT</option>
                    <option>Government & Public Sector</option>
                    <option>Telecom & Media</option>
                    <option>Logistics & Supply Chain</option>
                    <option>Education & EdTech</option>
                    <option>Real Estate & PropTech</option>
                    <option>SaaS / Tech Startup</option>
                  </select>
                </div>
              </div>
              <div class="form-grid three">
                <div class="field"><label>Project Name <span class="req">*</span></label><input type="text" id="projectName" placeholder="e.g. CoreBanking Modernization 2026"></div>
                <div class="field"><label>Priority Level</label>
                  <select id="priority">
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="critical">Critical — All agents on standby</option>
                    <option value="low">Low</option>
                  </select>
                </div>
                <div class="field"><label>Expected Delivery</label>
                  <select id="delivery">
                    <option>As fast as possible</option>
                    <option>Within 2 hours</option>
                    <option>Within 24 hours</option>
                    <option>Within 1 week</option>
                    <option>Custom timeline</option>
                  </select>
                </div>
              </div>
              <div class="form-grid full">
                <div class="field"><label>Project Description <span class="req">*</span></label>
                  <textarea id="projectDesc" rows="4" placeholder="Describe exactly what the client needs. Be specific — the AI agents will use this to allocate themselves and decide architecture, tech stack, and delivery plan."></textarea>
                </div>
              </div>
            </div>

            <!-- SECTION 2 -->
            <div class="section-card">
              <div class="section-header">
                <div class="section-num">2</div>
                <div><div class="section-title">Service Layer Selection</div><div class="section-sub">Which Qestron Labs service layers does this project need?</div></div>
                <div class="section-badge badge-required">Required</div>
              </div>
              <div class="check-grid" id="serviceGrid">
                <label class="check-item selected" onclick="toggleCheck(this);updateAgentPreview()"><input type="checkbox" value="app_dev" checked><div><div class="check-label">Application Development</div><div class="check-sub">Web, mobile, backend</div></div></label>
                <label class="check-item selected" onclick="toggleCheck(this);updateAgentPreview()"><input type="checkbox" value="cloud_infra" checked><div><div class="check-label">Cloud Infrastructure</div><div class="check-sub">AWS, Azure, GCP setup</div></div></label>
                <label class="check-item" onclick="toggleCheck(this);updateAgentPreview()"><input type="checkbox" value="data_ai"><div><div class="check-label">Data & AI / LLMs</div><div class="check-sub">Pipelines, RAG, agents</div></div></label>
                <label class="check-item" onclick="toggleCheck(this);updateAgentPreview()"><input type="checkbox" value="cybersecurity"><div><div class="check-label">Cybersecurity</div><div class="check-sub">IAM, pentest, zero trust</div></div></label>
                <label class="check-item" onclick="toggleCheck(this);updateAgentPreview()"><input type="checkbox" value="legacy_mod"><div><div class="check-label">Legacy Modernization</div><div class="check-sub">COBOL → Python/Go</div></div></label>
                <label class="check-item" onclick="toggleCheck(this);updateAgentPreview()"><input type="checkbox" value="bpm"><div><div class="check-label">BPM / Outsourcing</div><div class="check-sub">Finance, HR, supply chain</div></div></label>
                <label class="check-item" onclick="toggleCheck(this);updateAgentPreview()"><input type="checkbox" value="iot"><div><div class="check-label">IoT & Edge Computing</div><div class="check-sub">Sensors, factories</div></div></label>
                <label class="check-item" onclick="toggleCheck(this);updateAgentPreview()"><input type="checkbox" value="saas_impl"><div><div class="check-label">SaaS Implementation</div><div class="check-sub">Salesforce, SAP, ServiceNow</div></div></label>
                <label class="check-item" onclick="toggleCheck(this);updateAgentPreview()"><input type="checkbox" value="devops"><div><div class="check-label">DevOps & CI/CD</div><div class="check-sub">Pipelines, deployment</div></div></label>
                <label class="check-item" onclick="toggleCheck(this);updateAgentPreview()"><input type="checkbox" value="qa"><div><div class="check-label">QA & Testing</div><div class="check-sub">Unit, E2E, load, security</div></div></label>
              </div>
            </div>

            <!-- SECTION 3 -->
            <div class="section-card">
              <div class="section-header">
                <div class="section-num">3</div>
                <div><div class="section-title">Tech Stack Preferences</div><div class="section-sub">Let agents know your preferred technologies (or leave to CTO Agent to decide)</div></div>
                <div class="section-badge badge-optional">Optional</div>
              </div>
              <div class="form-grid">
                <div class="field"><label>Frontend</label><select id="frontend"><option value="auto">Let CTO Agent decide</option><option>React + Next.js</option><option>Vue.js + Nuxt</option><option>Angular</option><option>React Native (Mobile)</option><option>Flutter</option><option>No frontend needed</option></select></div>
                <div class="field"><label>Backend</label><select id="backend"><option value="auto">Let CTO Agent decide</option><option>Python + FastAPI</option><option>Node.js + Express</option><option>Java + Spring Boot</option><option>Go</option><option>Ruby on Rails</option><option>.NET Core</option></select></div>
              </div>
              <div class="form-grid three">
                <div class="field"><label>Database</label><select id="database"><option value="auto">Let CTO Agent decide</option><option>PostgreSQL</option><option>MySQL</option><option>MongoDB</option><option>Redis + PostgreSQL</option><option>Supabase</option><option>Firebase</option></select></div>
                <div class="field"><label>Cloud Provider</label><select id="cloud"><option value="auto">Let DevOps Agent decide</option><option>AWS</option><option>Google Cloud</option><option>Azure</option><option>Multi-cloud (AWS + GCP)</option><option>Vercel + Railway</option></select></div>
                <div class="field"><label>AI / LLM Model</label><select id="llmChoice"><option value="auto">Auto-assign per agent role</option><option>Claude Opus (all agents)</option><option>Claude Sonnet (all agents)</option><option>Qwen3-Coder (coding only)</option><option>Mixed: Opus+Sonnet+Qwen</option></select></div>
              </div>
              <div class="field">
                <label>Additional Tech Requirements</label>
                <div class="tag-row" id="techTags">
                  <span class="tag-pill" onclick="toggleTag(this)">Stripe Payments</span>
                  <span class="tag-pill" onclick="toggleTag(this)">Twilio SMS/Calls</span>
                  <span class="tag-pill" onclick="toggleTag(this)">Sarvam AI (Indian languages)</span>
                  <span class="tag-pill" onclick="toggleTag(this)">Kafka Streaming</span>
                  <span class="tag-pill" onclick="toggleTag(this)">Docker + Kubernetes</span>
                  <span class="tag-pill" onclick="toggleTag(this)">GraphQL API</span>
                  <span class="tag-pill" onclick="toggleTag(this)">WebSockets (Real-time)</span>
                  <span class="tag-pill" onclick="toggleTag(this)">OAuth2 / SSO</span>
                  <span class="tag-pill" onclick="toggleTag(this)">Multi-tenant SaaS</span>
                  <span class="tag-pill" onclick="toggleTag(this)">Razorpay</span>
                  <span class="tag-pill" onclick="toggleTag(this)">WhatsApp API</span>
                  <span class="tag-pill" onclick="toggleTag(this)">OpenAI Integration</span>
                </div>
              </div>
            </div>

            <!-- SECTION 4 -->
            <div class="section-card">
              <div class="section-header">
                <div class="section-num">4</div>
                <div><div class="section-title">Compliance & Security Requirements</div><div class="section-sub">Security agents will audit and enforce these standards</div></div>
                <div class="section-badge badge-optional">Optional</div>
              </div>
              <div class="compliance-grid">
                <label class="check-item" onclick="toggleCheck(this)"><input type="checkbox" value="gdpr"><div><div class="check-label">GDPR</div><div class="check-sub">EU data privacy</div></div></label>
                <label class="check-item" onclick="toggleCheck(this)"><input type="checkbox" value="hipaa"><div><div class="check-label">HIPAA</div><div class="check-sub">Healthcare</div></div></label>
                <label class="check-item" onclick="toggleCheck(this)"><input type="checkbox" value="pci_dss"><div><div class="check-label">PCI-DSS</div><div class="check-sub">Payment security</div></div></label>
                <label class="check-item" onclick="toggleCheck(this)"><input type="checkbox" value="soc2"><div><div class="check-label">SOC 2</div><div class="check-sub">Trust & security</div></div></label>
                <label class="check-item" onclick="toggleCheck(this)"><input type="checkbox" value="iso27001"><div><div class="check-label">ISO 27001</div><div class="check-sub">Info security</div></div></label>
                <label class="check-item" onclick="toggleCheck(this)"><input type="checkbox" value="owasp"><div><div class="check-label">OWASP Top 10</div><div class="check-sub">Web security</div></div></label>
                <label class="check-item" onclick="toggleCheck(this)"><input type="checkbox" value="zero_trust"><div><div class="check-label">Zero Trust</div><div class="check-sub">Network</div></div></label>
                <label class="check-item" onclick="toggleCheck(this)"><input type="checkbox" value="rbi"><div><div class="check-label">RBI Guidelines</div><div class="check-sub">Indian banking</div></div></label>
              </div>
            </div>

            <!-- SECTION 5 -->
            <div class="section-card">
              <div class="section-header">
                <div class="section-num">5</div>
                <div><div class="section-title">Agent Swarm Configuration</div><div class="section-sub">Fine-tune how the 1000 agents are distributed across this project</div></div>
                <div class="section-badge badge-auto">Auto</div>
              </div>
              <div class="agent-preview">
                <div class="ap-title">Live Agent Allocation Preview</div>
                <div class="ap-bars" id="agentBars"></div>
              </div>
              <div class="form-grid three">
                <div class="field"><label>Simulation Mode</label>
                  <select id="simMode"><option value="it_company">Standard IT Delivery</option><option value="rapid">Rapid Prototype (2hrs)</option><option value="enterprise">Enterprise Grade</option><option value="legacy">Legacy Modernization</option><option value="security">Security-First Delivery</option></select>
                </div>
                <div class="field"><label>Quality vs Speed</label>
                  <select id="qualityMode"><option value="balanced">Balanced</option><option value="quality">Max Quality (slower)</option><option value="speed">Max Speed (faster)</option></select>
                </div>
                <div class="field"><label>Total Agents</label>
                  <select id="agentCount" onchange="updateAgentPreview()"><option value="1000">1000 (Full Swarm)</option><option value="500">500 (Half Swarm)</option><option value="200">200 (Lean Team)</option><option value="50">50 (Prototype)</option></select>
                </div>
              </div>
              <div class="priority-grid">
                <div class="priority-item">
                  <div class="priority-label">Development Focus</div>
                  <div class="priority-val" id="devFocusVal">60%</div>
                  <input type="range" min="20" max="80" value="60" oninput="document.getElementById('devFocusVal').textContent=this.value+'%';updateAgentPreview()">
                </div>
                <div class="priority-item">
                  <div class="priority-label">QA & Security Focus</div>
                  <div class="priority-val" id="qaFocusVal">25%</div>
                  <input type="range" min="10" max="60" value="25" oninput="document.getElementById('qaFocusVal').textContent=this.value+'%';updateAgentPreview()">
                </div>
                <div class="priority-item">
                  <div class="priority-label">DevOps Focus</div>
                  <div class="priority-val" id="devopsFocusVal">15%</div>
                  <input type="range" min="5" max="40" value="15" oninput="document.getElementById('devopsFocusVal').textContent=this.value+'%';updateAgentPreview()">
                </div>
              </div>
            </div>

            <!-- SECTION 6 -->
            <div class="section-card">
              <div class="section-header">
                <div class="section-num">6</div>
                <div><div class="section-title">Expected Deliverables</div><div class="section-sub">What documents and outputs should agents produce?</div></div>
                <div class="section-badge badge-optional">Optional</div>
              </div>
              <div class="check-grid">
                <label class="check-item selected" onclick="toggleCheck(this)"><input type="checkbox" value="brd" checked><div><div class="check-label">BRD Document</div></div></label>
                <label class="check-item selected" onclick="toggleCheck(this)"><input type="checkbox" value="architecture" checked><div><div class="check-label">System Architecture</div></div></label>
                <label class="check-item selected" onclick="toggleCheck(this)"><input type="checkbox" value="code" checked><div><div class="check-label">Working Code</div></div></label>
                <label class="check-item selected" onclick="toggleCheck(this)"><input type="checkbox" value="test_report" checked><div><div class="check-label">Test Report</div></div></label>
                <label class="check-item" onclick="toggleCheck(this)"><input type="checkbox" value="api_docs"><div><div class="check-label">API Documentation</div></div></label>
                <label class="check-item" onclick="toggleCheck(this)"><input type="checkbox" value="deployment_config"><div><div class="check-label">Deployment Config</div></div></label>
                <label class="check-item" onclick="toggleCheck(this)"><input type="checkbox" value="security_report"><div><div class="check-label">Security Audit Report</div></div></label>
                <label class="check-item" onclick="toggleCheck(this)"><input type="checkbox" value="user_manual"><div><div class="check-label">User Manual</div></div></label>
              </div>
            </div>

            <!-- RUN BAR -->
            <div class="run-bar">
              <button class="run-btn" id="runBtn" onclick="runSimulate()">
                ⚡ Initialize 1000-Agent Swarm
              </button>
              <div class="run-status" id="runStatus">Fill in sections above and click to initialize the swarm.</div>
            </div>

            <!-- OUTPUT -->
            <div class="section-card" id="sim-output-box" style="display:none;">
              <div class="section-header">
                <div class="section-num">✓</div>
                <div><div class="section-title">Simulation Output</div><div class="section-sub">Raw MiroFish agent response</div></div>
                <div class="section-badge badge-auto">Live</div>
              </div>
              <div class="output-panel visible" id="sim-terminal"></div>
            </div>
            
            <div id="agent-allocation" style="display:none;"></div> <!-- Keep placeholder for existing logic backwards compatibility -->

        </div>
"""

# Replace the inner part of #view-simulate
start_tag = '<!-- View: Simulate -->'
end_tag = '<!-- View: Projects -->'

import re
content = re.sub(r'<!-- View: Simulate -->.*?<!-- View: Projects -->', html_simulate + "\n        " + end_tag, content, flags=re.DOTALL)


# 3. Inject JS
js_logic = """

        // --- NEW UI HELPER FUNCTIONS ---
        function toggleCheck(el) {
          el.classList.toggle('selected');
        }
        function toggleTag(el) {
          el.classList.toggle('active');
        }

        const BASE_ALLOCATION = [
          { name: "C-Suite (CEO/CTO/PM)",  base: 5,   color: "#a78bfa" },
          { name: "Frontend Devs",          base: 150, color: "#34d399" },
          { name: "Backend Devs",           base: 150, color: "#34d399" },
          { name: "Database Engineers",     base: 80,  color: "#34d399" },
          { name: "QA Engineers",           base: 150, color: "#f87171" },
          { name: "DevOps Engineers",       base: 100, color: "#fbbf24" },
          { name: "Security Agents",        base: 80,  color: "#f87171" },
          { name: "Data / AI Agents",       base: 50,  color: "#a78bfa" },
          { name: "BPM Agents",             base: 50,  color: "#38bdf8" },
          { name: "Flexible / Specialist",  base: 145, color: "#818cf8" },
          { name: "Client Manager",         base: 1,   color: "#fbbf24" },
        ];

        function updateAgentPreview() {
          const totalEl = document.getElementById('agentCount');
          if(!totalEl) return;
          const total = parseInt(totalEl.value) || 1000;
          const bars = document.getElementById('agentBars');
          if(!bars) return;
          bars.innerHTML = BASE_ALLOCATION.map(a => {
            const count = Math.round((a.base / 1000) * total);
            const pct = (count / total) * 100;
            return `
              <div class="ap-row">
                <div class="ap-name">${a.name}</div>
                <div class="ap-bar-wrap">
                  <div class="ap-bar-fill" style="width:${pct}%;background:${a.color};"></div>
                </div>
                <div class="ap-count">${count}</div>
              </div>`;
          }).join('');
        }

        function loadTemplate(type) {
          document.getElementById('clientName').value = 'Demo Client Corp';
          document.getElementById('projectName').value = 'SaaS Platform v2.0';
          document.getElementById('industry').value = 'SaaS / Tech Startup';
          document.getElementById('projectDesc').value = 'Build a multi-tenant SaaS platform for HR management. Features: employee onboarding, leave management, payroll integration, role-based access control, React dashboard, FastAPI backend, PostgreSQL database, Stripe billing, deployed on AWS with Docker + GitHub Actions CI/CD.';
          document.getElementById('frontend').value = 'React + Next.js';
          document.getElementById('backend').value = 'Python + FastAPI';
          document.getElementById('database').value = 'PostgreSQL';
          document.getElementById('cloud').value = 'AWS';
        }

        function clearForm() {
          document.querySelectorAll('input[type=text], textarea, select').forEach(el => {
            if (el.tagName === 'SELECT') el.selectedIndex = 0;
            else el.value = '';
          });
          document.querySelectorAll('.check-item').forEach(el => el.classList.remove('selected'));
          document.querySelectorAll('.tag-pill').forEach(el => el.classList.remove('active'));
          document.getElementById('sim-output-box').style.display = 'none';
        }
        
        // Ensure preview is generated when page loads
        document.addEventListener('DOMContentLoaded', updateAgentPreview);
        
        // --- OVERRIDE runSimulate to use the form blocks ---
        async function runSimulate() {
            const clientName   = document.getElementById('clientName').value;
            const projectDesc  = document.getElementById('projectDesc').value;
            const industry     = document.getElementById('industry').value;
            const simMode      = document.getElementById('simMode').value;
            const agentCount   = document.getElementById('agentCount').value;

            if (!clientName || !projectDesc || !industry) {
                alert('Please fill in Client Name, Industry, and Project Description at minimum.');
                return;
            }

            const btn = document.getElementById("runBtn");
            const box = document.getElementById("sim-output-box");
            const term = document.getElementById("sim-terminal");
            const status = document.getElementById('runStatus');
            
            btn.textContent = "Booting Agent Cluster...";
            btn.disabled = true;
            status.textContent = `Initializing agents for ${clientName}...`;
            
            box.style.display = "block";
            term.innerHTML = `<span class="out-comment">// Connecting to MiroFish simulation engine (port 5001)...</span>\\n<span class="out-comment">// Allocating swarm topologies...</span>\\n`;

            try {
                // Post to our proper API back-end
                const res = await fetch(`${API_BASE}/admin/simulate`, {
                    method: 'POST',
                    headers: {
                        "Content-Type": "application/json",
                        "x-admin-key": ADMIN_KEY
                    },
                    body: JSON.stringify({ input: projectDesc, mode: simMode }) // using projectDesc as main input
                });

                const data = await res.json();
                
                term.innerHTML += `<span class="out-comment">// ✅ TOPOLOGY RECEIVED. STREAMING RESULTS:</span>\\n\\n`;
                
                let html = `<span class="out-comment">// Client: ${clientName} | Agents allocated out of 1000 pool</span>\\n\\n`;
                if(data.output) {
                    for(const [key, msg] of Object.entries(data.output)) {
                        const isCsuite = key.includes("CEO") || key.includes("CTO") || key.includes("PM") || key.includes("Manager");
                        const isDev = key.includes("Developer") || key.includes("Engineer");
                        const cls = isCsuite ? 'out-ceo' : (key.includes("QA") ? 'out-qa' : (key.includes("DevOps") ? "out-devops" : "out-dev"));
                        html += `<span class="${cls}">${key.padEnd(25, ' ')}</span> <span class="out-comment">→</span> ${msg}\\n`;
                    }
                } else {
                    html += JSON.stringify(data, null, 2);
                }
                
                term.innerHTML += html;
                status.textContent = `✅ Simulation complete — Architecture pipeline resolved successfully.`;

            } catch(e) {
                term.innerHTML += "\\n<span class=\\"out-qa\\">[CRITICAL FAULT] Connection failed: " + e.message + "</span>";
                status.textContent = "Fatal exception occurred.";
            } finally {
                btn.textContent = "⚡ Initialize 1000-Agent Swarm";
                btn.disabled = false;
                refreshData(); 
            }
        }
"""

content = content.replace("function logout()", js_logic + "\n        function logout()")
# We also need to remove the old function runSimulate() completely to prevent duplication
content = re.sub(r'async function runSimulate\(\) \{.*?(?=</script>)', '', content, flags=re.DOTALL)
content = content.replace("</script>", "\n</script>")


with open("admin/dashboard.html", "w") as f:
    f.write(content)

print("Merged dashboard.html successfully.")
