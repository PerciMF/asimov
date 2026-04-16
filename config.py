from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

HISTORY_FILE = DATA_DIR / "historico_ia.json"
LOG_FILE = DATA_DIR / "app.log"
INTEGRITY_DIR = DATA_DIR / "integrity"
INTEGRITY_DIR.mkdir(exist_ok=True)
TOOL_HISTORY_DIR = DATA_DIR / "tool_history"
TOOL_HISTORY_DIR.mkdir(exist_ok=True)
TOOLS_CATALOG_FILE = DATA_DIR / "tools_catalog.json"
CONTEXT_DIR = DATA_DIR / "context"
CONTEXT_DIR.mkdir(exist_ok=True)

APP_NAME = "Asimov Interface v3.1.4 otimizada"
WINDOW_WIDTH = 1180
WINDOW_HEIGHT = 690
WINDOW_MIN_WIDTH = 930
WINDOW_MIN_HEIGHT = 580

VALID_STATES = {
    "ONLINE",
    "OCIOSA",
    "PROCESSANDO",
    "AJUDA",
    "ERRO",
    "RESET",
}
