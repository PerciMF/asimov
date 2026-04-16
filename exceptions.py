class AsimovError(Exception):
    """Exceção base do projeto."""


class ValidationError(AsimovError):
    """Erro de validação."""


class HistoryError(AsimovError):
    """Erro no gerenciamento do histórico."""


class CommandError(AsimovError):
    """Erro no processamento de comandos."""