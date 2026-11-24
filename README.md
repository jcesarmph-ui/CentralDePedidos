# Central de Pedidos

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/PySide6-41CD52?style=for-the-badge&logo=qt&logoColor=white" alt="PySide6"/>
  <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite"/>
  <img src="https://img.shields.io/badge/pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white" alt="pytest"/>
</p>
<p align="center">
  <img src="https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Windows"/>
  <img src="https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white" alt="Git"/>
  <img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub"/>
  <img src="https://img.shields.io/badge/Claude_Code-D97757?style=for-the-badge&logo=claude&logoColor=white" alt="Claude Code"/>
</p>
<p align="center">
  <img src="https://img.shields.io/badge/área-vendas_e_produção-blue?style=flat-square" alt="Área"/>
  <img src="https://img.shields.io/badge/tipo-aplicação_desktop-orange?style=flat-square" alt="Tipo"/>
  <img src="https://img.shields.io/badge/foco-UX-purple?style=flat-square" alt="Foco"/>
  <img src="https://img.shields.io/badge/testes-82_passando-brightgreen?style=flat-square" alt="Testes"/>
  <img src="https://img.shields.io/badge/idioma-pt--BR-green?style=flat-square" alt="Idioma"/>
  <img src="https://img.shields.io/badge/versão-0.6.1-blue?style=flat-square" alt="Versão"/>
</p>

<p align="center">
  Aplicativo desktop que reúne, num lugar só, os <b>pedidos de clientes</b> e os <b>planos de corte</b>
  de toda a equipe de vendas — com uma <b>agenda visual dos prazos de entrega</b>, saldo a entregar
  calculado sozinho e cores que mostram na hora o que está atrasado, o que vence hoje e o que já foi entregue.
</p>

<p align="center">
  <a href="#-visão-geral">Visão Geral</a> •
  <a href="#-em-números">Números</a> •
  <a href="#-telas">Telas</a> •
  <a href="#-funcionalidades">Funcionalidades</a> •
  <a href="#️-arquitetura">Arquitetura</a> •
  <a href="#️-como-foi-desenvolvido">Desenvolvimento</a> •
  <a href="#-estrutura-do-repositório">Estrutura</a>
</p>

---

## 📌 Visão Geral

Numa empresa de corte e venda de aço (bobinas, rolos e chapas), cada vendedor registrava os
**pedidos** (material já cortado, em estoque) e os **planos de corte** (serviço de cortar uma
bobina para o cliente) em **planilhas separadas**. Ninguém via o que o outro estava fazendo, e o
acompanhamento dos prazos dependia de cada um lembrar de olhar a sua.

| ❌ Problema | 💡 Solução | ✅ Resultado |
|---|---|---|
| Uma planilha por vendedor, sem ligação entre elas | Um programa único numa pasta da rede, usado por todos ao mesmo tempo | Todos veem tudo, com filtro por vendedor |
| Prazos espalhados em linhas de tabela | **Agenda** em forma de calendário, com cores por situação do prazo | Atrasados e entregas do dia saltam aos olhos |
| "Falta entregar" calculado à mão | Entregas lançadas em kg; o saldo é calculado sozinho | Item entregue ganha um ✔ verde e o pedido vira **Atendido** |
| Digitação repetida e nomes escritos de jeitos diferentes | Botão HOJE, cliente com sugestões, "copiar item de cima", pedido com vários itens | Menos digitação e dados padronizados |
| Não se sabia quem registrou cada linha | Nome tirado do usuário do Windows, sem digitar | Cada registro mostra o vendedor |
| Duas pessoas mexendo na mesma linha da planilha | **Trava por pedido/plano**: o colega vê quem está editando | Nada se perde por gravação em cima |
| Linha apagada sem querer sumia para sempre | **Lixeira** com restaurar e excluir de vez | Exclusão segura |

```mermaid
mindmap
  root((Central de Pedidos))
    Agenda
      Calendário do mês
      Cores pelo prazo
      Atrasados e próximos 7 dias
      Total de kg por dia
    Pedidos
      Vários itens por pedido
      Rolo ou chapa com medidas
      Entregas e saldo automático
      Preço do kg por item
    Planos de corte
      Bobina mãe
      Lote e item
      Marcação de crítico
    Equipe
      Nome automático
      Filtro por vendedor
      Trava por registro
      Lixeira
    Para cada pessoa
      Modo claro e escuro
```

**Objetivos:** dar a toda a equipe a mesma visão dos compromissos, reduzir atrasos esquecidos e
tirar trabalho repetitivo de quem vende.

## 📊 Em números

| Indicador | Valor |
|---|---|
| ✅ Testes automáticos | **82** (regras, banco e janela) |
| 🧾 Linhas de código | **~2.900** no programa + **~750** de testes |
| 🔀 Pull requests | **8** |
| 🧭 Fases entregues | **6** (0.1 a 0.6) |
| 🏷️ Versão atual | **0.6.1** |
| 🖼️ Ícones | Material Symbols, todos escolhidos por foto |

## 📸 Telas

> Todas as telas usam **dados fictícios** (clientes, vendedores, números e lotes inventados).

<p align="center">
  <img src="docs/telas/01_agenda.png" alt="Agenda dos prazos" width="100%"/><br/>
  <i>Agenda: o mês inteiro com cores por prazo, atrasados e próximos 7 dias ao lado</i>
</p>

| | |
|---|---|
| <img src="docs/telas/02_pedidos.png" alt="Lista de pedidos"/><br/><i>Pedidos: falta, próximo prazo e situação de cada um</i> | <img src="docs/telas/03_pedido.png" alt="Pedido com vários itens"/><br/><i>Pedido com vários itens e saldo calculado sozinho</i> |
| <img src="docs/telas/04_planos.png" alt="Planos de corte"/><br/><i>Planos de corte com bobina mãe, lote e críticos</i> | <img src="docs/telas/05_agenda_claro.png" alt="Agenda no modo claro"/><br/><i>Modo claro, escolhido por cada pessoa</i> |

<p align="center">
  <img src="docs/telas/07_plano_claro.png" alt="Plano de corte" width="70%"/><br/>
  <i>Cadastro do plano de corte</i>
</p>

## ✨ Funcionalidades

- [x] **Agenda** do mês com etiquetas por dia (pedido e plano), total de kg do dia e coluna de
      **atrasados** e **próximos 7 dias**; clicar abre o registro
- [x] Cores pelo prazo: 🔴 atrasado · 🟡 hoje/amanhã · neutro no prazo · 🟢 entregue
- [x] **Pedidos com vários itens**: código, rolo ou chapa, espessura, largura, comprimento (some no
      rolo), quantidade, em estoque, prazo, 1ª e 2ª entrega, **falta automática** e preço do kg por item
- [x] **Planos de corte**: cliente, item, lote, descrição, bobina mãe, quantidade, entrega, crítico e em estoque
- [x] Situação **Atendido / Em aberto** (o pedido com tudo entregue fica atendido sozinho)
- [x] **Cliente com sugestões** enquanto digita e confirmação antes de criar um cliente novo
- [x] Botão **HOJE**, calendário em todo campo de data e "copiar item de cima"
- [x] **Nome do vendedor automático** a partir do usuário do Windows (`joao.silva` → **JOAO**)
- [x] **Filtro "Registrado por"** valendo para todas as abas
- [x] **Trava por pedido/plano**: quem tenta abrir o que outro edita vê um aviso com o nome
- [x] **Lixeira** com restaurar e excluir de vez
- [x] Tema **azul-marinho** em modo **claro e escuro**, escolhido e lembrado por pessoa
- [x] Pesquisa por cliente, número, código, medida, lote ou bobina

## 🧭 UX: o programa é para outras pessoas

Diferente dos meus outros programas, que eu mesmo uso, este foi **pedido pelos vendedores** e é
usado **100% por eles**. Por isso o desenvolvimento seguiu práticas de UX:

- **Entrevista com quem usa** antes de desenhar qualquer tela (o que fazem, o que irrita, o que falta).
- **Protótipo rápido**: começar com a primeira entrevista e melhorar com a opinião dos demais.
- **Escolha visual por foto**: três propostas de tema, cada uma em modo claro e escuro, comparadas
  lado a lado antes de virar código.
- **Nunca passar informação só pela cor** e ícones apenas onde explicam algo.

### Como a agenda decide a cor

```mermaid
flowchart TD
    A[Registro com prazo] --> B{Tudo entregue<br/>ou atendido?}
    B -- sim --> V[🟢 Verde: entregue]
    B -- não --> C{Prazo já passou?}
    C -- sim --> R[🔴 Vermelho: atrasado]
    C -- não --> D{Vence hoje<br/>ou amanhã?}
    D -- sim --> Y[🟡 Amarelo: atenção]
    D -- não --> N[Neutro: no prazo]
```

## 🏗️ Arquitetura

```mermaid
flowchart LR
    A[Interface<br/>PySide6] --> B[Regras<br/>prazos, saldo, agenda, vendedor]
    B --> C[Dados<br/>repositório SQLite]
    C --> D[(Banco na<br/>pasta da rede)]
```

Camadas independentes: a regra de negócio não conhece a tela. O programa fica numa **pasta comum
da rede**, sem servidor, e os vendedores gravam ao mesmo tempo — com uma trava **por pedido**:
se alguém está editando um pedido, o colega vê quem é e espera. A trava solta sozinha se o
programa de quem editava fechar ou parar de responder.

```mermaid
flowchart TB
    subgraph Rede[Pasta comum da rede]
      EXE[Programa] --- DB[(Banco SQLite<br/>journal tradicional + busy_timeout)]
    end
    V1[Vendedor 1] --> EXE
    V2[Vendedor 2] --> EXE
    V3[Vendedor 3] --> EXE
```

| Tecnologia | Aplicação no projeto |
|---|---|
| **Python 3.12+** | Linguagem de todo o programa |
| **PySide6 (Qt)** | Janelas, abas, agenda, calendário e tema claro/escuro |
| **SQLite** | Banco de dados num arquivo, na pasta da rede, com transações curtas |
| **Material Symbols** | Ícones (licença Apache 2.0, arquivo `LICENSE` junto) |
| **pytest** | Testes automáticos, inclusive da janela sem abrir na tela |
| **Ruff** | Padronização do código |
| **Claude Code** | Desenvolvimento assistido por IA, passo a passo |

## 🗃️ Modelo de dados

```mermaid
erDiagram
    CLIENTES ||--o{ PEDIDOS : "faz"
    CLIENTES ||--o{ PLANOS : "pede"
    PEDIDOS ||--|{ ITENS_PEDIDO : "tem"
    TRAVAS }o--|| PEDIDOS : "protege"
    TRAVAS }o--|| PLANOS : "protege"
    PEDIDOS {
        date data
        text cliente
        text numero
        text vendedor
        bool atendido
        datetime excluido_em
    }
    ITENS_PEDIDO {
        text codigo
        text tipo
        real espessura
        real largura
        real comprimento
        real quantidade
        real estoque
        date prazo
        real entrega1
        real entrega2
        real preco_kg
    }
    PLANOS {
        date data
        text cliente
        text item
        text lote
        text descricao
        text bobina_mae
        text quantidade
        date entrega
        bool critico
        bool atendido
    }
    TRAVAS {
        text tipo
        int registro
        text quem
        text pc
        datetime sinal_em
    }
```

Exclusão é **lógica**: o registro ganha a data de exclusão e vai para a Lixeira.

## 🛠️ Como foi desenvolvido

- Desenvolvimento **assistido por IA (Claude Code)**, uma etapa por vez, com branch e pull request.
- **Testes automáticos** desde o primeiro dia; os testes nunca mexem nas preferências reais de quem roda.
- **Versionamento semântico**: `0.x` a cada fase, tag Git por versão.
- **Cada ícone e cada tela aprovados por foto** antes de entrar.
- Dados reais da empresa ficam **fora do repositório**; exemplos e fotos usam nomes fictícios.

<details>
<summary><b>🗺️ Roteiro</b></summary>

- [x] **0.1** — Base: janela, abas, tema claro/escuro, nome do vendedor
- [x] **0.2** — Pedidos com itens, entregas e saldo
- [x] **0.3** — Planos de corte
- [x] **0.4** — Agenda visual dos prazos
- [x] **0.5** — Filtro por vendedor, Lixeira e trava por pedido
- [x] **0.6** — Situação Atendido / Em aberto e campo Em estoque

</details>

<details>
<summary><b>📜 História das fases</b></summary>

| Fase | O que entrou |
|---|---|
| 0.1 | Janela com abas, tema azul-marinho claro/escuro, nome automático do vendedor |
| 0.2 | Pedido com vários itens, rolo/chapa, entregas, falta automática, cliente com sugestões |
| 0.3 | Plano de corte com bobina mãe, lote, crítico |
| 0.4 | Agenda do mês, cores pelo prazo, atrasados e próximos 7 dias |
| 0.5 | Lixeira, trava por pedido/plano, filtro "Registrado por" |
| 0.6 | Atendido / Em aberto (automático quando tudo é entregue), Em estoque (kg) |

</details>

## 📁 Estrutura do repositório

```
src/planos_pedidos/
├── interface/   telas (agenda, pedidos, planos, lixeira), tema e ícones
├── regras/      regras de negócio (prazos, saldo, agenda, nome do vendedor)
└── dados/       repositório do banco SQLite
tests/           testes automáticos (regras, banco e janela)
docs/telas/      fotos com dados fictícios
```

## 💼 Competências

UX com usuários reais · Python · Interfaces desktop com Qt · SQLite em rede · Testes automáticos ·
Git e GitHub · Desenvolvimento com IA

---

<p align="center"><b>Um programa feito a partir de quem vai usar: menos planilhas espalhadas, mais prazos cumpridos.</b></p>
