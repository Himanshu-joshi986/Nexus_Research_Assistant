import os
from dotenv import load_dotenv

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
ADMIN_NAME = os.getenv("ADMIN_NAME", "Research Admin")

USERS_FILE = os.path.join(os.path.dirname(__file__), "data", "users.json")
REPORTS_FILE = os.path.join(os.path.dirname(__file__), "data", "reports.json")
CHROMA_DIR = os.path.join(os.path.dirname(__file__), "data", "chroma_db")

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
OPENROUTER_MODEL = "meta-llama/llama-3.1-8b-instruct"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")
HUGGINGFACE_MODEL = "meta-llama/Llama-3.1-8B-Instruct"
HUGGINGFACE_BASE_URL = "https://router.huggingface.co/v1"

DEPTH_CONFIG = {
    "Basic": {"max_results": 5, "max_chunks": 10},
    "Medium": {"max_results": 10, "max_chunks": 20},
    "Advanced": {"max_results": 15, "max_chunks": 30},
}

RECENCY_DAYS = {
    "1 Month": 30,
    "6 Months": 180,
    "1 Year": 365,
}
