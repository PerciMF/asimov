from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Iterable

import pandas as pd

from config import DATA_DIR


@dataclass
class DirectoryEntry:
    caminho: str
    tipo: str
    nome: str


class DirectorySearchTool:
    def __init__(self) -> None:
        self._metric_builders: list[Callable[[list[DirectoryEntry], str], dict]] = [
            self._build_basic_metrics,
            self._build_extension_metrics,
            self._build_depth_metrics,
        ]

    def register_metric_builder(self, builder: Callable[[list[DirectoryEntry], str], dict]) -> None:
        self._metric_builders.append(builder)

    def build_export_path(self, fmt: str) -> str:
        return str(DATA_DIR / f"resultado_diretorio_{Path.cwd().name}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.{fmt}")

    def scan(self, base_path: str, termo: str = "", max_results: int = 500) -> list[DirectoryEntry]:
        base = Path(base_path)
        if not base.exists():
            raise FileNotFoundError(f"Caminho não encontrado: {base_path}")
        if not base.is_dir():
            raise NotADirectoryError(f"O caminho não é uma pasta: {base_path}")

        termo_lower = termo.strip().lower()
        results: list[DirectoryEntry] = []
        for path in base.rglob("*"):
            nome = path.name.lower()
            if termo_lower and termo_lower not in nome:
                continue
            results.append(DirectoryEntry(str(path), "diretório" if path.is_dir() else "arquivo", path.name))
            if len(results) >= max_results:
                break
        return results

    def analyze(self, entries: Iterable[DirectoryEntry], base_path: str) -> dict:
        entries = list(entries)
        metrics: dict = {}
        for builder in self._metric_builders:
            metrics.update(builder(entries, base_path))
        return metrics

    def _build_basic_metrics(self, entries: list[DirectoryEntry], base_path: str) -> dict:
        arquivos = sum(1 for item in entries if item.tipo == "arquivo")
        diretorios = sum(1 for item in entries if item.tipo == "diretório")
        return {"base_path": base_path, "total": len(entries), "arquivos": arquivos, "diretorios": diretorios}

    def _build_extension_metrics(self, entries: list[DirectoryEntry], base_path: str) -> dict:
        counter: Counter[str] = Counter()
        for item in entries:
            if item.tipo != "arquivo":
                continue
            counter[Path(item.nome).suffix.lower() or "(sem extensão)"] += 1
        return {"extensoes": dict(counter.most_common(10))}

    def _build_depth_metrics(self, entries: list[DirectoryEntry], base_path: str) -> dict:
        base = Path(base_path)
        profundidades: list[int] = []
        for item in entries:
            try:
                rel = Path(item.caminho).relative_to(base)
                profundidades.append(len(rel.parts))
            except Exception:
                continue
        if not profundidades:
            return {"profundidade_max": 0, "profundidade_media": 0.0}
        return {
            "profundidade_max": max(profundidades),
            "profundidade_media": round(sum(profundidades) / len(profundidades), 2),
        }

    def summarize(self, entries: Iterable[DirectoryEntry], termo: str, base_path: str) -> str:
        entries = list(entries)
        metrics = self.analyze(entries, base_path=base_path)
        lines = [
            "Busca por diretório concluída.",
            f"Base: {base_path}",
            f"Filtro de nome: {termo or '(sem filtro)'}",
            f"Resultados: {metrics.get('total', 0)} | Arquivos: {metrics.get('arquivos', 0)} | Diretórios: {metrics.get('diretorios', 0)}",
            f"Profundidade máx.: {metrics.get('profundidade_max', 0)} | Profundidade média: {metrics.get('profundidade_media', 0)}",
        ]
        extensoes = metrics.get("extensoes", {})
        if extensoes:
            lines.append("Top extensões: " + ", ".join(f"{ext}:{qtd}" for ext, qtd in extensoes.items()))
        if entries:
            lines.append("Primeiros resultados:")
            for item in entries[:10]:
                lines.append(f"- [{item.tipo}] {item.caminho}")
        return "\n".join(lines)

    def export(
        self,
        entries: Iterable[DirectoryEntry],
        base_path: str,
        termo: str = "",
        fmt: str = "excel",
        output_path: str | None = None,
    ) -> str:
        entries = list(entries)
        metrics = self.analyze(entries, base_path=base_path)
        output = output_path or self.build_export_path("xlsx" if fmt.lower() == "excel" else "json")
        if fmt.lower() == "json":
            payload = {
                "base_path": base_path,
                "termo": termo,
                "metrics": metrics,
                "entries": [asdict(e) for e in entries],
            }
            Path(output).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            return output
        df = pd.DataFrame([asdict(e) for e in entries], columns=["caminho", "tipo", "nome"])
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Diretorio", index=False)
            resumo_df = pd.DataFrame(
                {"Métrica": list(metrics.keys()), "Valor": [str(v) for v in metrics.values()]}
            )
            resumo_df.to_excel(writer, sheet_name="Resumo", index=False)
        return output
