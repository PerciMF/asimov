import json
from datetime import datetime
from pathlib import Path

from config import HISTORY_FILE
from exceptions import HistoryError
from logger import get_logger

logger = get_logger(__name__)


class HistoryManager:
    def __init__(self, filepath: Path | None = None, max_entries: int = 500):
        self.filepath = filepath or HISTORY_FILE
        self.max_entries = max_entries
        self.data = self._load()

    def _load(self) -> list[dict]:
        if not self.filepath.exists():
            return []

        try:
            with open(self.filepath, "r", encoding="utf-8") as file:
                return json.load(file)
        except (json.JSONDecodeError, OSError) as exc:
            logger.error("Falha ao carregar histórico: %s", exc)
            return []

    def _save(self) -> None:
        try:
            with open(self.filepath, "w", encoding="utf-8") as file:
                json.dump(self.data, file, ensure_ascii=False, indent=4)
        except OSError as exc:
            logger.error("Falha ao salvar histórico: %s", exc)
            raise HistoryError("Não foi possível salvar o histórico.") from exc

    def add_entry(self, source: str, message: str, persist: bool = True) -> None:
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source": source,
            "message": message,
        }
        self.data.append(entry)
        if len(self.data) > self.max_entries:
            self.data = self.data[-self.max_entries:]
        if persist:
            self._save()

    def flush(self) -> None:
        self._save()

    def get_last_entries(self, limit: int = 10) -> list[dict]:
        return self.data[-limit:]

    def clear(self) -> None:
        self.data = []
        self._save()
