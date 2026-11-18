"""Visual azul-marinho, escuro e claro (escolhido por foto em 2026-11-18 — ver CLAUDE.md).

Diferente dos outros programas (preto puro): este é de escritório/vendas, aberto o dia
todo. O significado das cores continua: vermelho = atrasado/erro, amarelo = aviso/hoje,
verde = entregue/certo.
"""

ESCURO = {
    "fundo": "#0f172a", "caixa": "#1e293b", "campo": "#273449", "borda": "#334155",
    "texto": "#e2e8f0", "dica": "#94a3b8", "destaque": "#60a5fa", "hoje": "#1d3a66",
    "mouse": "#334155",
}
CLARO = {
    "fundo": "#f1f5f9", "caixa": "#ffffff", "campo": "#f8fafc", "borda": "#cbd5e1",
    "texto": "#0f172a", "dica": "#64748b", "destaque": "#2563eb", "hoje": "#dbeafe",
    "mouse": "#e2e8f0",
}
TEMAS = {"escuro": ESCURO, "claro": CLARO}

# Cores de prazo: iguais nos dois temas (fundo, letra).
ATRASADO = ("#c62828", "#ffffff")
HOJE = ("#ffd54f", "#000000")
ENTREGUE = ("#2e7d32", "#ffffff")

ESTILO = """
QWidget {{ font-family: "Segoe UI"; font-size: 13pt; color: {texto}; }}
QMainWindow, #central {{ background: {fundo}; }}
QTabWidget::pane {{ border: 1px solid {borda}; border-radius: 10px; background: {caixa};
                    top: -1px; }}
QTabBar::tab {{ background: transparent; padding: 10px 26px; margin-right: 4px; color: {dica};
                border: none; border-bottom: 3px solid transparent; }}
QTabBar::tab:hover:!selected {{ color: {texto}; }}
QTabBar::tab:selected {{ color: {texto}; font-weight: bold;
                         border-bottom: 3px solid {destaque}; }}
QPushButton, QToolButton {{ background: {campo}; border: 1px solid {borda}; border-radius: 8px;
                            padding: 6px 14px; }}
QPushButton:hover, QToolButton:hover {{ background: {mouse}; }}
QToolButton:pressed {{ padding: 7px 13px 5px 15px; }}
#acao {{ background: {destaque}; color: #ffffff; border: none; font-weight: bold; }}
#titulo {{ font-size: 22pt; font-weight: bold; letter-spacing: 3px; }}
#canto {{ color: {dica}; font-size: 10pt; }}
#dica {{ color: {dica}; font-style: italic; }}
QToolTip {{ background: {campo}; color: {texto}; border: 1px solid {borda}; }}
"""


def folha_de_estilo(tema: str) -> str:
    return ESTILO.format(**TEMAS[tema])
