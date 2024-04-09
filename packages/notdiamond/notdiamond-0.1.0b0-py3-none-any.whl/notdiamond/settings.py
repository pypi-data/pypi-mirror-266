import os

from dotenv import load_dotenv

load_dotenv(os.getcwd() + "/.env")

NOTDIAMOND_API_KEY = os.getenv("NOTDIAMOND_API_KEY", default="")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", default="")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", default="")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", default="")
COHERE_API_KEY = os.getenv("COHERE_API_KEY", default="")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", default="")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY", default="")


ND_BASE_URL = "https://not-diamond-server.onrender.com"

PROVIDERS = {
    "openai": {
        "models": [
            "gpt-3.5-turbo",
            "gpt-4",
            "gpt-4-1106-preview",
            "gpt-4-turbo-preview",
        ],
        "api_key": OPENAI_API_KEY,
    },
    "anthropic": {
        "models": [
            "claude-2.1",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
        ],
        "api_key": ANTHROPIC_API_KEY,
    },
    "google": {"models": ["gemini-pro"], "api_key": GOOGLE_API_KEY},
    "cohere": {"models": ["command"], "api_key": COHERE_API_KEY},
    "mistral": {
        "models": [
            "mistral-large-latest",
            "mistral-medium-latest",
            "mistral-small-latest",
            "open-mistral-7b",
            "open-mixtral-8x7b",
        ],
        "api_key": MISTRAL_API_KEY,
    },
    "togetherai": {
        "models": [
            "CodeLlama-34b-Instruct-hf",
            "Phind-CodeLlama-34B-v2",
            "Mistral-7B-Instruct-v0.2",
            "Mixtral-8x7B-Instruct-v0.1",
        ],
        "api_key": TOGETHER_API_KEY,
        "model_prefix": {
            "CodeLlama-34b-Instruct-hf": "codellama",
            "Phind-CodeLlama-34B-v2": "Phind",
            "Mistral-7B-Instruct-v0.2": "mistralai",
            "Mixtral-8x7B-Instruct-v0.1": "mistralai",
        },
    },
}
