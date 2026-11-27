"""Importação do estoque de bobinas (dados fictícios, no formato da exportação do ERP)."""

import datetime

import openpyxl
import pytest

from planos_pedidos.regras.bobinas import PlanilhaInvalida, importar_planilha, ler_linhas

CABECALHO = (
    "Ori.", "Dt. Emissão", "Núm. Lote", "Liber./Util.", "Cód.Ref.", "Espessura (mm)",
    "Largura (mm)", "Compr./B.Maior (mm)", "Entrada", "Reserva/OF (T)", "Baixa/Saída (R)",
    "Disponíbilidade", "Saldo (R)", "Acabamento de Superfície", "Classificação",
    "Preço Unit.", "Local", "Nome Fantasia",
)  # fmt: skip


def linha(ori="LOT", lote="L-001", liber="S", disp=5000, compr=0):
    return (
        ori, datetime.datetime(2026, 11, 2), lote, liber, "20-01-999", 2.0, 1200, compr,
        8000, 0, 3000, disp, 5000, "Decapado", "NORMA-FICT", 9.99, "A-01", "Fornecedor X",
    )  # fmt: skip


def test_le_bobina_lot_com_disponibilidade():
    (b,) = ler_linhas([CABECALHO, linha()])
    assert b.lote == "L-001" and b.codigo == "20-01-999"
    assert (b.espessura, b.largura, b.comprimento) == (2.0, 1200, None)
    assert b.disponivel == 5000 and b.saldo == 5000 and b.liberado
    assert b.emissao == datetime.date(2026, 11, 2)
    assert (b.acabamento, b.classificacao, b.local) == ("Decapado", "NORMA-FICT", "A-01")
    assert not hasattr(b, "preco")


def test_ignora_ord_e_disponibilidade_zerada():
    linhas = [CABECALHO, linha(ori="ORD"), linha(disp=0), linha(disp=None), linha(lote="ok")]
    assert [b.lote for b in ler_linhas(linhas)] == ["ok"]


def test_liberado_n_e_lote_numerico():
    (b,) = ler_linhas([CABECALHO, linha(liber="N", lote=123456.0)])
    assert not b.liberado and b.lote == "123456"


def test_colunas_em_outra_ordem():
    cab = tuple(reversed(CABECALHO))
    (b,) = ler_linhas([cab, tuple(reversed(linha()))])
    assert b.lote == "L-001" and b.disponivel == 5000


def test_falta_coluna_obrigatoria():
    cab = tuple(c for c in CABECALHO if c != "Núm. Lote")
    with pytest.raises(PlanilhaInvalida, match="Lote"):
        ler_linhas([cab])


def test_importa_arquivo_xlsx(tmp_path):
    livro = openpyxl.Workbook()
    livro.active.append(CABECALHO)
    livro.active.append(linha())
    livro.active.append(linha(ori="ORD"))
    caminho = tmp_path / "estoque.xlsx"
    livro.save(caminho)
    assert len(importar_planilha(caminho)) == 1


def test_arquivo_que_nao_abre(tmp_path):
    caminho = tmp_path / "nao_e_excel.xlsx"
    caminho.write_text("texto")
    with pytest.raises(PlanilhaInvalida):
        importar_planilha(caminho)
