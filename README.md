# TP3 (DR1) — Dashboard de Turismo Carioca (Streamlit + Data.Rio)

Repositório: https://github.com/felipecastrosm/infnet_2026.2_dr1_tp3

Disciplina: Desenvolvimento de Dashboards com Streamlit (INFNET)
Autor: Felipe Castro Sotto Mayor

## O que é

Dashboard Streamlit para explorar dados de visitação a atrativos turísticos do Rio de Janeiro, publicados no portal de dados abertos [Data.Rio](https://www.data.rio) (seção Turismo). Implementa, em um único arquivo, os 12 itens pedidos pelo TP: upload de planilha, filtros (radio/checkbox/dropdown), tabela interativa, download dos dados filtrados, barra de progresso e spinner, color picker, cache, Session State, gráficos simples e avançados, e métricas-resumo.

Ver `docs/relatorio_conceitos.md` para o mapeamento item a item entre o enunciado/rubrica e o código.

## Estrutura do projeto

```
Felipe_Castro_Sotto_Mayor_DR1_TP3/
├── app_tp3_felipe_castro_sotto_mayor.py  # aplicação Streamlit (arquivo único, conforme entrega)
├── scripts/
│   └── preparar_dataset.py             # baixa e limpa 2 tabelas do Data.Rio -> data/*.xlsx
├── data/
│   └── turismo_visitantes_atrativos.xlsx  # dataset de exemplo para testar o upload
├── docs/
│   └── relatorio_conceitos.md          # mapeamento item a item da rubrica -> código
├── requirements.txt
├── .gitignore
└── README.md
```

## Dataset de exemplo

`data/turismo_visitantes_atrativos.xlsx` combina duas tabelas oficiais do Data.Rio (visitação ao Centro Cultural Banco do Brasil, 2015-2021, e passagens vendidas para o Corcovado via estrada de ferro, 1996-2003), reorganizadas em formato "arrumado":

| Coluna | Descrição |
|---|---|
| `Atrativo` | nome do ponto turístico |
| `Ano` | ano da observação |
| `Mes` / `Mes_Numero` | mês da observação (nome e número) |
| `Visitantes` | número de visitantes/passagens no mês |

Para regenerar esse arquivo a partir dos dados originais do Data.Rio: `python scripts/preparar_dataset.py`.

## Como rodar

```bash
cd Felipe_Castro_Sotto_Mayor_DR1_TP3
python3 -m venv .venv

# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app_tp3_felipe_castro_sotto_mayor.py
```

Com o app aberto no navegador, faça upload de `data/turismo_visitantes_atrativos.xlsx` (ou de outra planilha de turismo do Data.Rio com estrutura semelhante) para explorar os filtros, tabela, gráficos, métricas e downloads.

## Ambiente de desenvolvimento

- Python 3.9+
- Dependências: `streamlit`, `pandas`, `plotly`, `openpyxl`, `xlrd`, `requests`
