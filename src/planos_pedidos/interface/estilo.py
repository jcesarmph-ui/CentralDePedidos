"""Visual azul-marinho, escuro e claro (escolhido por foto em 2026-11-18 — ver CLAUDE.md).

Diferente dos outros programas (preto puro): este é de escritório/vendas, aberto o dia
todo. O significado das cores continua: vermelho = atrasado/erro, amarelo = aviso/hoje,
verde = entregue/certo.
"""

ESCURO = {
    "fundo": "#0f172a", "caixa": "#1e293b", "campo": "#273449", "borda": "#334155",
    "texto": "#e2e8f0", "dica": "#94a3b8", "destaque": "#60a5fa", "hoje": "#1d3a66",
    "mouse": "#334155", "selecao": "#1d3a66", "erro": "#ef5350", "aviso": "#ffd54f",
    "certo": "#66bb6a", "foco": "#60a5fa",
    "listra": "#243247",
}
CLARO = {
    "fundo": "#f1f5f9", "caixa": "#ffffff", "campo": "#f8fafc", "borda": "#cbd5e1",
    "texto": "#0f172a", "dica": "#64748b", "destaque": "#2563eb", "hoje": "#dbeafe",
    "mouse": "#e2e8f0", "selecao": "#dbeafe", "erro": "#c62828", "aviso": "#8d6e00",
    "certo": "#2e7d32", "foco": "#2563eb",
    "listra": "#f4f7fb",
}
TEMAS = {"escuro": ESCURO, "claro": CLARO}

# As telas leem daqui; `aplicar_tema` troca o conteúdo (o mesmo dicionário).
CORES = dict(ESCURO)

# Cores de prazo: iguais nos dois temas (fundo, letra).
ATRASADO = ("#c62828", "#ffffff")
HOJE = ("#ffd54f", "#000000")
ENTREGUE = ("#2e7d32", "#ffffff")

ESTILO = """
QWidget {{ font-family: "Segoe UI"; font-size: 13pt; color: {texto}; }}
QMainWindow, #central, QDialog {{ background: {fundo}; }}
QScrollArea, #rolagem {{ background: transparent; border: none; }}
QGroupBox {{ font-weight: bold; background: {caixa}; border: 1px solid {borda};
             border-radius: 10px; margin-top: 14px; padding: 12px 10px 10px 10px; }}
QGroupBox::title {{ subcontrol-origin: margin; left: 12px; padding: 0 6px; color: {texto}; }}
QGroupBox QLabel {{ font-weight: normal; }}
QTabWidget::pane {{ border: 1px solid {borda}; border-radius: 10px; background: {caixa};
                    top: -1px; }}
QTabBar::tab {{ background: transparent; padding: 10px 26px; margin-right: 4px; color: {dica};
                border: none; border-bottom: 3px solid transparent; }}
QTabBar::tab:hover:!selected {{ color: {texto}; }}
QTabBar::tab:selected {{ color: {texto}; font-weight: bold;
                         border-bottom: 3px solid {destaque}; }}
QLineEdit, QComboBox {{ background: {campo}; border: 1px solid {borda}; border-radius: 6px;
                        padding: 5px 8px; selection-background-color: {selecao};
                        selection-color: {texto}; }}
QLineEdit:focus, QComboBox:focus {{ border: 1px solid {foco}; }}
QLineEdit[erro="true"] {{ border: 2px solid {erro}; }}
QComboBox:hover {{ background: {mouse}; }}
/* Seta moderna (ícone expand_more do Google), sem a caixinha separada do Windows. */
QComboBox::drop-down {{ subcontrol-origin: padding; subcontrol-position: center right;
                        width: 30px; border: none; background: transparent; }}
QComboBox::down-arrow {{ image: url({seta}); width: 22px; height: 22px; }}
QComboBox::down-arrow:on {{ image: url({seta_aberta}); }}
QComboBox QAbstractItemView {{ background: {campo}; color: {texto}; border: 1px solid {borda};
    selection-background-color: {selecao}; selection-color: {texto}; outline: none; }}
QListView#sugestoes {{ background: {campo}; color: {texto}; border: 1px solid {borda};
    selection-background-color: {selecao}; selection-color: {texto}; outline: none; }}
QListView#sugestoes::item {{ padding: 4px 8px; }}
QListView#sugestoes::item:hover {{ background: {mouse}; }}
QPushButton, QToolButton {{ background: {campo}; border: 1px solid {borda}; border-radius: 8px;
                            padding: 6px 14px; }}
QPushButton:hover, QToolButton:hover {{ background: {mouse}; }}
QToolButton:pressed, QPushButton:pressed {{ padding-top: 7px; padding-bottom: 5px; }}
QToolButton#calendario, QToolButton#remover {{ padding: 4px; }}
#acao {{ background: {destaque}; color: #ffffff; border: none; font-weight: bold;
         padding: 8px 18px; }}
#acao:hover {{ background: {foco}; }}
QCalendarWidget QWidget {{ alternate-background-color: {campo}; }}
QCalendarWidget QAbstractItemView {{ background: {campo}; color: {texto};
    selection-background-color: {destaque}; selection-color: #ffffff; outline: none; }}
QCalendarWidget QAbstractItemView:disabled {{ color: {dica}; }}
QCalendarWidget #qt_calendar_navigationbar {{ background: {caixa};
                                              border-bottom: 1px solid {borda}; }}
QCalendarWidget QToolButton {{ color: {texto}; background: transparent; border: none;
                               font-weight: bold; padding: 4px 10px; }}
QCalendarWidget QToolButton:hover {{ background: {mouse}; }}
QCalendarWidget QMenu {{ background: {campo}; color: {texto}; }}
QCalendarWidget QSpinBox {{ background: {campo}; color: {texto}; border: 1px solid {borda}; }}
QTableWidget {{ background: {caixa}; alternate-background-color: {listra};
                border: none; gridline-color: {borda};
                selection-background-color: {selecao}; selection-color: {texto}; }}
QTableWidget::item {{ padding: 4px; }}
QTableWidget::item:hover {{ background: {mouse}; }}
QHeaderView::section {{ background: {campo}; color: {dica}; font-weight: bold; padding: 6px;
                        border: none; border-bottom: 1px solid {borda}; }}
QScrollBar:vertical {{ background: transparent; width: 12px; }}
QScrollBar::handle:vertical {{ background: {borda}; border-radius: 5px; min-height: 30px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: transparent; }}
QMessageBox {{ background: {caixa}; }}
#titulo {{ font-size: 22pt; font-weight: bold; letter-spacing: 3px; }}
#canto {{ color: {dica}; font-size: 10pt; }}
#dica {{ color: {dica}; font-style: italic; }}
#rotulo {{ color: {dica}; font-size: 11pt; }}
#cabecalho_itens {{ color: {dica}; font-size: 11pt; font-weight: bold; }}
#vendedor {{ font-weight: bold; }}
#aviso {{ color: {aviso}; }}
#erro {{ color: {erro}; }}
QLineEdit#falta {{ font-weight: bold; background: {caixa}; }}
QLineEdit#falta[estado="ok"] {{ color: {certo}; }}
QLineEdit#falta[estado="falta"] {{ color: {erro}; }}
/* Agenda */
#painel_lado {{ background: {campo}; border: 1px solid {borda}; border-radius: 10px; }}
#dia {{ background: {caixa}; border: 1px solid {borda}; border-radius: 8px; }}
#dia:hover {{ border: 1px solid {foco}; }}
#dia_fora {{ background: {fundo}; border: 1px solid {borda}; border-radius: 8px; }}
#diahoje {{ background: {hoje}; border: 2px solid {destaque}; border-radius: 8px; }}
#num_dia {{ font-weight: bold; font-size: 11pt; }}
#dia_fora QLabel#num_dia {{ color: {dica}; }}
#num_hoje {{ font-weight: bold; font-size: 11pt; color: {destaque}; }}
#kg_dia {{ color: {dica}; font-size: 9pt; }}
#mes {{ font-size: 17pt; font-weight: bold; padding-left: 10px; }}
#semana {{ color: {dica}; font-weight: bold; font-size: 10pt; }}
#legenda {{ color: {dica}; font-size: 10pt; }}
QPushButton#etiqueta {{ text-align: left; padding: 2px 6px; border-radius: 4px;
                        font-size: 10pt; }}
QPushButton#mais {{ background: transparent; border: none; color: {destaque};
                    font-size: 10pt; padding: 0 6px; }}
QPushButton#mais:hover {{ text-decoration: underline; }}
QLabel#secao {{ font-weight: bold; font-size: 11pt; padding: 6px 0 2px 0; }}
QToolButton#nav {{ padding: 3px; }}
QCheckBox {{ spacing: 8px; }}
QCheckBox::indicator {{ width: 18px; height: 18px; border: 1px solid {borda};
                       border-radius: 4px; background: {campo}; }}
QCheckBox::indicator:hover {{ border: 1px solid {foco}; }}
QCheckBox::indicator:checked {{ background: {destaque}; border: 1px solid {destaque};
                               image: url({check_branco}); }}
QToolTip {{ background: {campo}; color: {texto}; border: 1px solid {borda}; }}
"""


def _arquivo_seta(cor: str, aberta: bool) -> str:
    """O estilo do Qt só aceita imagem por arquivo: grava a seta na cor do tema numa pasta
    temporária (aberta = virada para cima)."""
    import tempfile
    from pathlib import Path

    from planos_pedidos.interface.icones import svg_colorido

    svg = svg_colorido("expand_more", cor)
    if aberta:
        svg = svg.replace("<path ", '<path transform="rotate(180 480 -480)" ', 1)
    pasta = Path(tempfile.gettempdir()) / "planos_pedidos_icones"
    pasta.mkdir(exist_ok=True)
    arquivo = pasta / f"seta_{'cima' if aberta else 'baixo'}_{cor.lstrip('#')}.svg"
    arquivo.write_text(svg, encoding="utf-8")
    return arquivo.as_posix()


def _arquivo_icone(nome: str, cor: str) -> str:
    """Ícone na cor pedida gravado num arquivo (o estilo do Qt só aceita imagem por arquivo)."""
    import tempfile
    from pathlib import Path

    from planos_pedidos.interface.icones import svg_colorido

    pasta = Path(tempfile.gettempdir()) / "planos_pedidos_icones"
    pasta.mkdir(exist_ok=True)
    arquivo = pasta / f"{nome}_{cor.lstrip('#')}.svg"
    arquivo.write_text(svg_colorido(nome, cor), encoding="utf-8")
    return arquivo.as_posix()


def aplicar_tema(nome: str) -> str:
    """Troca as cores de CORES e devolve a folha de estilo pronta."""
    CORES.clear()
    CORES.update(TEMAS[nome])
    return ESTILO.format(**CORES, check_branco=_arquivo_icone("check", "#ffffff"),
                         seta=_arquivo_seta(CORES["dica"], False),
                         seta_aberta=_arquivo_seta(CORES["dica"], True))
