"""
配置管理
统一从项目根目录的 .env 文件加载配置
"""

import os
from dotenv import load_dotenv

#  .env 
# : MiroFish/.env ( backend/app/config.py)
project_root_env = os.path.join(os.path.dirname(__file__), '../../.env')

if os.path.exists(project_root_env):
    load_dotenv(project_root_env, override=True)
else:
    #  .env
    load_dotenv(override=True)


class Config:
    """Flask配置类"""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'mirofish-secret-key')
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # JSON - ASCII \uXXXX 
    JSON_AS_ASCII = False
    
    # ─── Model per agent type (Qestron Labs IT Company) ───────────
    AGENT_MODELS = {
        "ceo":        os.environ.get("MODEL_CEO",       "claude-opus-4-6"),
        "cto":        os.environ.get("MODEL_CTO",       "claude-sonnet-4-6"),
        "pm":         os.environ.get("MODEL_PM",        "claude-sonnet-4-6"),
        "developer":  os.environ.get("MODEL_DEV",       "qwen/qwen3-coder:free"),
        "qa":         os.environ.get("MODEL_QA",        "claude-sonnet-4-6"),
        "devops":     os.environ.get("MODEL_DEVOPS",    "qwen/qwen3-coder:free"),
        "client":     os.environ.get("MODEL_CLIENT",    "claude-sonnet-4-6"),
        "default":    os.environ.get("LLM_MODEL_NAME",  "claude-sonnet-4-6"),
    }

    AGENT_TOOLS = {
        # ─── C-Suite (4 agents) ────────────────────────────────
        "CEO": [
            "read_requirement",    # reads client input
            "approve_project",     # signs off scope
            "create_brd",          # generates BRD document
            "notify_pm",           # triggers PM agent
        ],
        "CTO": [
            "analyze_requirement", # understands technical needs
            "choose_tech_stack",   # picks React/FastAPI etc
            "create_architecture", # generates architecture doc
            "assign_to_pm",        # hands off to PM
        ],
        "Project Manager": [
            "create_sprint_plan",  # breaks into tasks
            "assign_tasks",        # sends to dev agents
            "track_progress",      # monitors all stages
            "github_create_issues",# creates GitHub issues
            "update_status",       # updates client portal
        ],

        # ─── Developers (200-270 agents) ──────────────────────
        "Frontend Developer": [
            "write_code",          # writes React/Next.js
            "read_design_spec",    # reads architecture doc
            "github_commit",       # commits to repo
            "github_create_pr",    # opens pull request
            "run_linter",          # checks code quality
        ],
        "Backend Developer": [
            "write_code",          # writes FastAPI/Node
            "create_api_schema",   # defines endpoints
            "write_db_queries",    # database operations
            "github_commit",
            "github_create_pr",
            "run_linter",
        ],
        "Database Engineer": [
            "create_schema",       # designs DB structure
            "write_migrations",    # database migrations
            "optimize_queries",    # performance tuning
            "seed_test_data",      # creates test data
        ],

        # ─── QA Layer (200 agents) ────────────────────────────
        "QA Engineer": [
            "write_unit_tests",    # pytest/jest
            "run_tests",           # executes test suite
            "check_coverage",      # ensures 80%+ coverage
            "bug_hunter",          # tries to break the app
            "sql_injection_test",  # security testing
            "load_test",           # 100 concurrent users
            "playwright_e2e",      # end-to-end user flows
            "create_bug_report",   # documents found bugs
            "verify_bug_fix",      # confirms fixes work
            "generate_test_report",# final test document
        ],

        # ─── DevOps (150 agents) ──────────────────────────────
        "DevOps Engineer": [
            "setup_cicd",          # GitHub Actions config
            "deploy_vercel",       # frontend deployment
            "deploy_aws",          # backend deployment
            "setup_monitoring",    # error tracking
            "setup_alerts",        # uptime notifications
            "configure_env",       # environment variables
            "ssl_setup",           # HTTPS config
        ],

        # ─── Client Layer (1 agent) ───────────────────────────
        "Client Manager": [
            "qestron_call",        # voice call via Twilio
            "qestron_chat",        # chat via Qestron
            "send_documents",      # shares BRD, reports
            "collect_feedback",    # gets client approval
            "send_invoice",        # Stripe billing
        ],

        # ─── Flexible (145 agents — project specific) ─────────
        "ML Engineer": [
            "write_code",
            "train_model",
            "evaluate_model",
            "create_api_wrapper",  # wraps model as API
            "github_commit",
        ],
        "Security Auditor": [
            "owasp_scan",          # top 10 vulnerabilities
            "penetration_test",    # tries to hack it
            "auth_review",         # checks login security
            "create_security_report",
        ],
        "Payment Engineer": [
            "stripe_integration",
            "razorpay_integration",
            "payment_security_test",
            "write_code",
            "github_commit",
        ],
        "React Native Dev": [
            "write_code",
            "github_commit",
            "github_create_pr",
            "run_linter"
        ],
        "iOS Developer": [
            "write_code",
            "github_commit",
            "github_create_pr",
            "run_linter"
        ],
        "Mobile QA": [
            "run_tests",
            "playwright_e2e",
            "create_bug_report",
            "verify_bug_fix"
        ],
        "Data Engineer": [
            "write_code",
            "github_commit"
        ],
        "AI QA Engineer": [
            "run_tests",
            "create_bug_report",
            "evaluate_model"
        ],
        "Compliance Agent": [
            "create_security_report",
            "auth_review"
        ],
        "Performance Eng": [
            "load_test",
            "optimize_queries"
        ]
    }

    @classmethod
    def get_model_for_agent(cls, agent_role: str) -> str:
        role = agent_role.lower()
        for key in cls.AGENT_MODELS:
            if key in role:
                return cls.AGENT_MODELS[key]
        return cls.AGENT_MODELS["default"]

    @classmethod
    def get_tools_for_agent(cls, agent_role: str) -> list:
        for key in cls.AGENT_TOOLS:
            if key.lower() in agent_role.lower():
                return cls.AGENT_TOOLS[key]
        return ["write_code", "github_commit"]  # safe default

    # LLMOpenAI
    LLM_API_KEY = os.environ.get('LLM_API_KEY')
    LLM_BASE_URL = os.environ.get('LLM_BASE_URL', 'https://api.openai.com/v1')
    LLM_MODEL_NAME = AGENT_MODELS["default"]

    
    # Zep
    ZEP_API_KEY = os.environ.get('ZEP_API_KEY')
    
    # 
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '../uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'md', 'txt', 'markdown'}
    
    # 
    DEFAULT_CHUNK_SIZE = 500  # 
    DEFAULT_CHUNK_OVERLAP = 50  # 
    
    # OASIS
    OASIS_DEFAULT_MAX_ROUNDS = int(os.environ.get('OASIS_DEFAULT_MAX_ROUNDS', '10'))
    OASIS_SIMULATION_DATA_DIR = os.path.join(os.path.dirname(__file__), '../uploads/simulations')
    
    # OASIS
    OASIS_TWITTER_ACTIONS = [
        'CREATE_POST', 'LIKE_POST', 'REPOST', 'FOLLOW', 'DO_NOTHING', 'QUOTE_POST'
    ]
    OASIS_REDDIT_ACTIONS = [
        'LIKE_POST', 'DISLIKE_POST', 'CREATE_POST', 'CREATE_COMMENT',
        'LIKE_COMMENT', 'DISLIKE_COMMENT', 'SEARCH_POSTS', 'SEARCH_USER',
        'TREND', 'REFRESH', 'DO_NOTHING', 'FOLLOW', 'MUTE'
    ]
    
    # Report Agent
    REPORT_AGENT_MAX_TOOL_CALLS = int(os.environ.get('REPORT_AGENT_MAX_TOOL_CALLS', '5'))
    REPORT_AGENT_MAX_REFLECTION_ROUNDS = int(os.environ.get('REPORT_AGENT_MAX_REFLECTION_ROUNDS', '2'))
    REPORT_AGENT_TEMPERATURE = float(os.environ.get('REPORT_AGENT_TEMPERATURE', '0.5'))
    
    @classmethod
    def validate(cls):
        """验证必要配置"""
        errors = []
        if not cls.LLM_API_KEY:
            errors.append("LLM_API_KEY 未配置")
        if not cls.ZEP_API_KEY:
            errors.append("ZEP_API_KEY 未配置")
        return errors

