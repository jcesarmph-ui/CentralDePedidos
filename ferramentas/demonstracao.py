"""Demonstração: abre o programa já cheio de pedidos e planos FICTÍCIOS.

Serve para mostrar às vendedoras como vai ficar, como se a Ana e a Carlos já tivessem
começado a lançar. O banco é criado do zero numa pasta temporária a cada vez (nunca mexe nos
dados de verdade). Todos os nomes de clientes e números são inventados.

    python ferramentas/demonstracao.py            # abre como ANA
    python ferramentas/demonstracao.py CARLOS      # abre como CARLOS
"""

import datetime
import os
import random
import sys
import tempfile
from pathlib import Path

PASTA = Path(tempfile.gettempdir()) / "planos_pedidos_demonstracao"

CLIENTES = ["Alfa Chapas", "Beta Aços", "Gama Estruturas", "Delta Implementos",
            "Ômega Metalúrgica", "Sigma Telhas", "Vetor Perfis", "Prisma Caldeiraria"]


def criar_banco(pasta: Path, hoje: datetime.date | None = None) -> Path:
    from planos_pedidos.dados.caminhos import NOME_BANCO
    from planos_pedidos.dados.repositorio import Repositorio
    from planos_pedidos.regras.pedidos import Item, Pedido, Tipo
    from planos_pedidos.regras.planos import Plano

    hoje = hoje or datetime.date.today()
    sorteio = random.Random(42)  # sempre os mesmos dados

    def dia(n: int) -> datetime.date:
        return hoje + datetime.timedelta(days=n)

    pasta.mkdir(parents=True, exist_ok=True)
    arquivo = pasta / NOME_BANCO
    arquivo.unlink(missing_ok=True)
    repo = Repositorio(arquivo)
    for c in CLIENTES:
        repo.adicionar_cliente(c)

    # ---------------------------------------------------------- pedidos
    # (vendedora, dias do pedido, cliente, itens: (tipo, esp, larg, comp, kg, prazo, 1ª, 2ª, R$))
    pedidos = [
        ("ANA", -20, 0, [("Rolo", 0.75, 653, None, 5000, -6, 3000, None, 6.20)]),
        ("CARLOS", -15, 1, [("Chapa", 2.00, 1200, 3000, 8000, -2, 8000, None, 5.80),
                           ("Chapa", 3.00, 1200, 3000, 4000, -2, 1500, None, 5.70)]),
        ("ANA", -12, 2, [("Rolo", 1.50, 300, None, 2500, 0, None, None, 6.05)]),
        ("CARLOS", -10, 3, [("Rolo", 0.50, 1000, None, 6000, 1, 2000, 2000, 6.40)]),
        ("ANA", -9, 4, [("Chapa", 4.75, 1500, 6000, 12000, 3, None, None, 5.55),
                             ("Chapa", 6.30, 1500, 6000, 9000, 3, None, None, 5.50)]),
        ("CARLOS", -8, 5, [("Rolo", 0.43, 1200, None, 3000, -9, 3000, None, 6.90)]),
        ("ANA", -6, 6, [("Rolo", 1.20, 150, None, 1800, 5, None, None, 6.10)]),
        ("CARLOS", -5, 7, [("Chapa", 1.90, 1000, 2000, 3500, 6, None, None, 5.95)]),
        ("ANA", -4, 1, [("Rolo", 2.25, 400, None, 4000, 8, None, None, 5.85),
                             ("Rolo", 2.65, 400, None, 4000, 12, None, None, 5.85)]),
        ("CARLOS", -3, 0, [("Chapa", 3.75, 1200, 2500, 7000, 10, None, None, 5.65)]),
        ("ANA", -2, 3, [("Rolo", 0.95, 500, None, 2200, 14, None, None, 6.25)]),
        ("CARLOS", -1, 2, [("Rolo", 1.06, 250, None, 1600, 2, None, None, 6.15)]),
        ("ANA", 0, 5, [("Chapa", 2.65, 1200, 3000, 5000, 18, None, None, 5.75)]),
        ("CARLOS", 0, 4, [("Rolo", 0.65, 800, None, 3300, 21, None, None, 6.35)]),
        ("ANA", -25, 7, [("Rolo", 3.00, 600, None, 2000, -16, 2000, None, 5.90)]),
    ]
    for n, (vend, d, cli, itens) in enumerate(pedidos):
        lista = []
        for k, (tipo, esp, larg, comp, qtd, prazo, e1, e2, preco) in enumerate(itens):
            lista.append(Item(codigo=f"{sorteio.randint(10, 49)}-{sorteio.randint(100, 999)}",
                              tipo=Tipo(tipo), espessura=esp, largura=larg, comprimento=comp,
                              quantidade=qtd, prazo=dia(prazo), entrega1=e1, entrega2=e2,
                              preco_kg=preco, observacoes="Retira no local" if k == 1 else ""))
        repo.salvar_pedido(Pedido(data=dia(d), cliente=CLIENTES[cli], numero=str(48210 + n),
                                  vendedor=vend, itens=lista))

    # ---------------------------------------------------------- planos de corte
    # (vendedora, dias do plano, cliente, descrição, bobina mãe, kg, entrega, crítico)
    planos = [
        ("CARLOS", -9, 1, "BLQ 2,00 X 1200 X 3000", "BQ 2,00 X 1200 - LOTE 77120", "8.000", -3,
         False),
        ("ANA", -7, 0, "BF 0,75 X 653", "BF 0,75 X 1200 - LOTE 77455", "5.000", -1, False),
        ("CARLOS", -6, 6, "FITA 1,20 X 150", "BF 1,20 X 1200 - LOTE 77501", "1.800", 0, True),
        ("ANA", -5, 3, "BZ 0,50 X 1000", "BZ 0,50 X 1200 - LOTE 77610", "6.000", 1, False),
        ("CARLOS", -4, 4, "BQ 4,75 X 1500 X 6000", "BQ 4,75 X 1500 - LOTE 77702", "12.000", 2,
         True),
        ("ANA", -3, 2, "FITA 1,50 X 300", "BF 1,50 X 1200 - LOTE 77711", "2.500", 4, False),
        ("CARLOS", -3, 5, "BG 0,43 X 1200", "BG 0,43 X 1200 - LOTE 77730", "saldo total", 5,
         False),
        ("ANA", -2, 7, "BLQ 1,90 X 1000 X 2000", "BF 1,90 X 1200 - LOTE 77802", "3.500",
         7, False),
        ("CARLOS", -2, 1, "FITA 2,25 X 400", "BQ 2,25 X 1200 - LOTE 77815", "4.000", 9, False),
        ("ANA", -1, 0, "BQ 3,75 X 1200 X 2500", "BQ 3,75 X 1200 - LOTE 77840", "7.000", 11,
         True),
        ("CARLOS", -1, 3, "FITA 0,95 X 500", "BF 0,95 X 1200 - LOTE 77861", "2.200", 13, False),
        ("ANA", 0, 2, "FITA 1,06 X 250", "BF 1,06 X 1250 - LOTE 77870", "1.600", 15,
         False),
        ("CARLOS", 0, 5, "BLQ 2,65 X 1200 X 3000", "BQ 2,65 X 1200 - LOTE 77888", "5.000", 19,
         False),
    ]
    for n, (vend, d, cli, desc, bobina, qtd, entrega, critico) in enumerate(planos):
        repo.salvar_plano(Plano(data=dia(d), cliente=CLIENTES[cli],
                                item=f"{sorteio.randint(10, 49)}-{sorteio.randint(100, 999)}",
                                lote=f"V{3100 + n}", descricao=desc, bobina_mae=bobina,
                                quantidade=qtd, entrega=dia(entrega), critico=critico,
                                vendedor=vend,
                                observacoes="Embalar em pallet" if n % 4 == 0 else ""))

    # Um de cada na Lixeira, para mostrar como funciona.
    lixo_pedido = repo.salvar_pedido(Pedido(
        data=dia(-3), cliente=CLIENTES[6], numero="48299", vendedor="CARLOS",
        itens=[Item(tipo=Tipo.ROLO, espessura=1.5, largura=200, quantidade=900,
                    prazo=dia(4), preco_kg=6.0)]))
    repo.excluir("pedido", lixo_pedido, quem="CARLOS")
    lixo_plano = repo.salvar_plano(Plano(
        data=dia(-2), cliente=CLIENTES[4], lote="V3199", descricao="FITA 0,75 X 120",
        bobina_mae="BF 0,75 X 1200", quantidade="700", entrega=dia(6), vendedor="ANA"))
    repo.excluir("plano", lixo_plano, quem="ANA")
    return arquivo


def main() -> int:
    raiz = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(raiz / "src"))
    os.environ["PLANOS_PEDIDOS_DADOS"] = str(PASTA)
    os.environ["PLANOS_PEDIDOS_USUARIO"] = sys.argv[1] if len(sys.argv) > 1 else "ANA"
    criar_banco(PASTA)
    from planos_pedidos.app import main as abrir

    return abrir()


if __name__ == "__main__":
    sys.exit(main())
