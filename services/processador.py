from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from logger import get_logger
from services.historico import HistoryManager
from tools.catalog import ToolCatalog
from tools.directory_search_tool import DirectorySearchTool
from tools.file_search_tool import FileSearchTool, SearchConfig, build_output_path
from utils.system_integrity import build_integrity_report
from utils.system_status import format_log_status, format_required_libs_status, read_last_log_lines

logger = get_logger(__name__)


@dataclass
class CommandResult:
    response: str
    state: str
    action: str | None = None
    payload: dict = field(default_factory=dict)


class CommandProcessor:
    def __init__(self, history_manager: HistoryManager):
        self.history_manager = history_manager
        self.file_search_tool = FileSearchTool()
        self.directory_search_tool = DirectorySearchTool()
        self.tool_catalog = ToolCatalog()

    def _parse_pipe_command(self, text: str) -> list[str]:
        return [part.strip() for part in text.split("|") if part.strip()]

    def _build_inline_search_config(self, text: str) -> SearchConfig | None:
        if "|" not in text:
            return None
        parts = self._parse_pipe_command(text)
        if not parts:
            return None
        head = parts[0]
        lowered = head.lower()
        prefixes = ("buscar ", "buscador ", "buscar arquivos ", "tool buscador ")
        prefix = next((item for item in prefixes if lowered.startswith(item)), None)
        if prefix is None:
            return None
        termo = head[len(prefix):].strip()
        if not termo or len(parts) < 2:
            return None
        pasta = parts[1]
        saida = parts[2] if len(parts) >= 3 else build_output_path()
        return SearchConfig(termo=termo, pasta=pasta, saida=saida)

    def _parse_directory_command(self, text: str) -> tuple[str, str, str | None, str | None] | None:
        lowered = text.lower().strip()
        aliases = ("buscar-dir", "buscar_dir", "diretorio", "diretório")
        alias = next((item for item in aliases if lowered.startswith(item)), None)
        if alias is None:
            return None
        raw = text.strip()[len(alias):].strip()
        if not raw:
            return None
        parts = self._parse_pipe_command(raw)
        if not parts:
            return None
        pasta = parts[0]
        termo = parts[1] if len(parts) > 1 else ""
        fmt = None
        output_path = None
        if len(parts) > 2:
            last = parts[2].lower()
            if last in {"excel", "json"}:
                fmt = last
            else:
                output_path = parts[2]
        if len(parts) > 3:
            fmt = parts[3].lower()
        return pasta, termo, fmt, output_path

    def process(self, text: str) -> CommandResult:
        command = text.strip()
        lowered = command.lower()
        logger.info("Processando comando: %s", lowered)

        inline_search = self._build_inline_search_config(command)
        if inline_search is not None:
            return CommandResult(
                response=(
                    "Executando busca inline em thread.\n"
                    "Modo: terminal\n"
                    f"Termo: {inline_search.termo}\n"
                    f"Pasta: {inline_search.pasta}\n"
                    f"Saída: {inline_search.saida}"
                ),
                state="PROCESSANDO",
                action="run_file_search_inline",
                payload={"config": inline_search},
            )

        dir_command = self._parse_directory_command(command)
        if dir_command is not None:
            pasta, termo, fmt, output_path = dir_command
            action = "run_directory_search_export" if fmt or output_path else "run_directory_search_inline"
            return CommandResult(
                response=(
                    "Executando busca por diretório.\n"
                    "Ferramenta preparada para contexto de LLM futura.\n"
                    f"Pasta: {pasta}\n"
                    f"Filtro: {termo or '(sem filtro)'}\n"
                    f"Exportação: {fmt or output_path or 'não'}"
                ),
                state="PROCESSANDO",
                action=action,
                payload={"pasta": pasta, "termo": termo, "fmt": fmt, "output_path": output_path},
            )

        if lowered == "ajuda":
            return CommandResult(
                response=(
                    "Comandos disponíveis: ajuda, status, integridade, integridade profunda, log, limpar, hora, data, historico, buscador, cancelar, catalogo, reset, sair\n\n"
                    "Busca inline:\n"
                    "- buscar termo | C:/pasta/origem | C:/saida/resultado.xlsx\n"
                    "- buscar termo | C:/pasta/origem\n\n"
                    "Busca por diretório:\n"
                    "- buscar-dir C:/pasta/base | termo_opcional\n"
                    "- buscar-dir C:/pasta/base | termo_opcional | excel\n"
                    "- buscar-dir C:/pasta/base | termo_opcional | json"
                ),
                state="AJUDA",
            )

        if lowered == "status":
            response = (
                "Sistema operacional. Interface, terminal e núcleo estão ativos.\n\n"
                f"{format_required_libs_status()}\n\n{format_log_status()}\n\n"
                "A interface de tools usa abas compactas estilo TabStrip.\n"
                "Execução pesada do buscador agora usa worker thread com cancelamento.\n"
                "Base preparada para catálogo central, histórico por tool e camada de contexto para LLM."
            )
            return CommandResult(response=response, state="ONLINE")

        if lowered in {"integridade", "diagnostico", "diagnóstico", "check"}:
            return CommandResult(response=build_integrity_report(deep=False), state="PROCESSANDO")
        if lowered in {"integridade profunda", "check profundo", "diagnostico profundo", "diagnóstico profundo"}:
            return CommandResult(response=build_integrity_report(deep=True), state="PROCESSANDO")
        if lowered in {"log", "logs", "logger"}:
            return CommandResult(response=read_last_log_lines(), state="PROCESSANDO")
        if lowered in {"catalogo", "catálogo", "tools", "menu tools"}:
            return CommandResult(response=self.tool_catalog.describe(), state="PROCESSANDO")
        if lowered == "limpar":
            return CommandResult(response="Terminal limpo com sucesso.", state="OCIOSA", action="clear_terminal")
        if lowered == "hora":
            return CommandResult(response=f"Hora atual: {datetime.now().strftime('%H:%M:%S')}", state="PROCESSANDO")
        if lowered == "data":
            return CommandResult(response=f"Data atual: {datetime.now().strftime('%d/%m/%Y')}", state="PROCESSANDO")
        if lowered == "historico":
            entries = self.history_manager.get_last_entries(5)
            if not entries:
                return CommandResult(response="Nenhum histórico encontrado.", state="OCIOSA")
            linhas = ["Últimas entradas do histórico:"]
            for item in entries:
                linhas.append(f"{item['timestamp']} | {item['source']}: {item['message']}")
            return CommandResult(response="\n".join(linhas), state="PROCESSANDO")
        if lowered in {"buscador", "buscar", "buscar arquivos", "tool buscador"}:
            return CommandResult(
                response=(
                    "Abrindo ferramenta de busca de arquivos.\n"
                    "Dica: também aceita modo inline com 'buscar termo | pasta | saida'."
                ),
                state="PROCESSANDO",
                action="open_file_search_tool",
            )
        if lowered in {"cancelar", "parar busca", "stop"}:
            return CommandResult(response="Solicitando cancelamento da execução ativa.", state="PROCESSANDO", action="cancel_active_job")
        if lowered == "reset":
            return CommandResult(response="Sistema reiniciado logicamente.", state="RESET", action="reset_system")
        if lowered == "sair":
            return CommandResult(response="Encerrando aplicação.", state="ERRO", action="exit_app")
        return CommandResult(response=f"Comando não reconhecido: '{text}'", state="ERRO")
