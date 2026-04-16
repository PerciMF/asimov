from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from config import TOOL_HISTORY_DIR


class ToolHistoryManager:
    def __init__(self, base_dir: Path | None = None, max_entries: int = 200):
        self.base_dir = base_dir or TOOL_HISTORY_DIR
        self.max_entries = max_entries
        self.base_dir.mkdir(exist_ok=True)

    def _path_for(self, tool_name: str) -> Path:
        safe_name = tool_name.replace(" ", "_").lower()
        return self.base_dir / f"{safe_name}.json"

    def add_entry(self, tool_name: str, event_type: str, message: str, metadata: dict[str, Any] | None = None) -> None:
        path = self._path_for(tool_name)
        data = []
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                data = []
        data.append(
            {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "event_type": event_type,
                "message": message,
                "metadata": metadata or {},
            }
        )
        if len(data) > self.max_entries:
            data = data[-self.max_entries:]
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def get_last_entries(self, tool_name: str, limit: int = 10) -> list[dict]:
        path = self._path_for(tool_name)
        if not path.exists():
            return []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return []
        return data[-limit:]
