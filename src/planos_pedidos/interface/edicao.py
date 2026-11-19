"""Abrir um pedido/plano para editar com trava: um de cada vez.

Se outra pessoa está com ele aberto, nem abre: devolve o aviso com o nome. Enquanto a janela
está aberta, manda um sinal de vida a cada 30 s; se o programa fechar de repente, a trava
deixa de valer sozinha depois de 2 min sem sinal.
"""

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QDialog, QMessageBox

from planos_pedidos.dados.repositorio import Repositorio
from planos_pedidos.regras.vendedor import nome_pc

SINAL_MS = 30_000
NOME = {"pedido": "neste pedido", "plano": "neste plano de corte"}


def texto_trava(tipo: str, quem: str, pc: str) -> str:
    onde = f" (no computador {pc})" if pc else ""
    return (f"{quem or 'Outra pessoa'} está mexendo {NOME[tipo]} agora{onde}. "
            "Tente de novo quando terminar.")


def abrir_com_trava(repo: Repositorio, tipo: str, registro: int, quem: str,
                    janela: QDialog) -> tuple[bool, str]:
    """Abre `janela` se conseguir a trava. Devolve (salvou/excluiu, aviso de trava)."""
    pc = nome_pc()
    ocupado = repo.pegar_trava(tipo, registro, quem, pc)
    if ocupado:
        return False, texto_trava(tipo, *ocupado)
    sinal = QTimer(janela)
    sinal.timeout.connect(lambda: repo.renovar_trava(tipo, registro, quem, pc))
    sinal.start(SINAL_MS)
    try:
        return bool(janela.exec()), ""
    finally:
        sinal.stop()
        repo.soltar_trava(tipo, registro, quem, pc)


def confirmar_exclusao(pai, descricao: str) -> bool:
    caixa = QMessageBox(pai)
    caixa.setWindowTitle("Excluir")
    caixa.setText(f"Mandar {descricao} para a Lixeira?")
    caixa.setInformativeText("Dá para restaurar depois pela aba Lixeira.")
    sim = caixa.addButton("Mandar para a Lixeira", QMessageBox.AcceptRole)
    caixa.addButton("Cancelar", QMessageBox.RejectRole)
    caixa.exec()
    return caixa.clickedButton() is sim
