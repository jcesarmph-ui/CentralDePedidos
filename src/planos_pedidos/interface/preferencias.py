"""Preferências de cada pessoa (no registro do Windows de quem usa, não no banco)."""

from PySide6.QtCore import QSettings

EMPRESA, PROGRAMA = "CentralDePedidos", "PlanosPedidos"


def _configuracoes() -> QSettings:
    # Formato explícito: assim os testes conseguem trocar o registro por um arquivo temporário
    # (QSettings.setDefaultFormat) e nunca mexem nas preferências de verdade de quem roda.
    return QSettings(QSettings.defaultFormat(), QSettings.UserScope, EMPRESA, PROGRAMA)


def ler_tema() -> str:
    """"escuro" (padrão) ou "claro"."""
    valor = _configuracoes().value("tema", "escuro")
    return valor if valor in ("escuro", "claro") else "escuro"


def gravar_tema(tema: str) -> None:
    _configuracoes().setValue("tema", tema)
