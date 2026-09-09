"""Prepara o dataset de turismo (Data.Rio) usado para testar o dashboard Streamlit.

Este script é executado UMA VEZ, fora do app, para baixar dois conjuntos de
dados originais do portal Data.Rio (seção Turismo) e transformá-los em uma
única planilha "arrumada" (tidy: uma linha por observação), que é o arquivo
efetivamente carregado na interface via upload (`data/turismo_visitantes_atrativos.xlsx`).

Datasets originais (Data.Rio, licença CC-BY 4.0, Prefeitura do Rio de Janeiro):

1. "Visitação ao Centro Cultural Banco do Brasil, 2015 a 2021" (Tabela 4018)
   https://www.arcgis.com/home/item.html?id=614ad116a32746fc8d85e93f70df568d
2. "Número de passagens vendidas para o morro do Corcovado - visitação ao
   Cristo Redentor, pela estrada de ferro, entre 1996-2003" (Tabela 474)
   https://www.arcgis.com/home/item.html?id=a664d2a908b04be4bb1c21ce7be05b19

Ambos vêm no mesmo formato de tabela estatística (uma matriz Mês x Ano, com
cabeçalho e notas de rodapé do template padrão do Data.Rio), o que permite
reshape com a mesma lógica. O resultado é uma tabela única, no formato longo,
com uma linha por (atrativo, ano, mês):

    Atrativo | Ano | Mes | Mes_Numero | Visitantes

Uso: `python scripts/preparar_dataset.py` (a partir da raiz do projeto).
"""

from __future__ import annotations

import pandas as pd
import requests

MESES_PT = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]

FONTES = {
    "Centro Cultural Banco do Brasil": {
        "item_id": "614ad116a32746fc8d85e93f70df568d",
        "sheet_name": "Corcovado Rodoviário",  # nome da aba no arquivo original (sic)
        "linha_cabecalho_anos": 4,
        "linha_primeiro_mes": 6,
    },
    "Corcovado (trem ao Cristo Redentor)": {
        "item_id": "a664d2a908b04be4bb1c21ce7be05b19",
        "sheet_name": "T 474",
        "linha_cabecalho_anos": 5,
        "linha_primeiro_mes": 9,
    },
}

URL_TEMPLATE = "https://www.arcgis.com/sharing/rest/content/items/{item_id}/data"


def _baixar_planilha_original(item_id: str) -> bytes:
    resposta = requests.get(URL_TEMPLATE.format(item_id=item_id), timeout=30)
    resposta.raise_for_status()
    return resposta.content


def _limpar_valor(valor) -> float | None:
    """Converte um valor numérico "sujo" (com espaço como separador, texto
    "..." indicando dado indisponível, floats de células mescladas) em float."""
    if isinstance(valor, str):
        valor = valor.replace(" ", "").strip()
        if valor in {"...", "--", "", "-"}:
            return None
        valor = valor.replace(",", ".")
    try:
        return float(valor)
    except (TypeError, ValueError):
        return None


def _extrair_atrativo(nome_atrativo: str, config: dict) -> pd.DataFrame:
    conteudo = _baixar_planilha_original(config["item_id"])
    bruto = pd.read_excel(pd.io.common.BytesIO(conteudo), sheet_name=config["sheet_name"], header=None)

    linha_anos = bruto.iloc[config["linha_cabecalho_anos"]]
    anos = [int(a) for a in linha_anos[1:] if pd.notna(a)]

    registros = []
    for offset, mes in enumerate(MESES_PT):
        linha = bruto.iloc[config["linha_primeiro_mes"] + offset]
        assert str(linha[0]).strip() == mes, f"Linha inesperada para {mes}: {linha[0]!r}"
        for coluna_idx, ano in enumerate(anos, start=1):
            visitantes = _limpar_valor(linha[coluna_idx])
            if visitantes is None:
                continue
            registros.append(
                {
                    "Atrativo": nome_atrativo,
                    "Ano": ano,
                    "Mes": mes,
                    "Mes_Numero": offset + 1,
                    "Visitantes": int(visitantes),
                }
            )

    return pd.DataFrame(registros)


def preparar_dataset() -> pd.DataFrame:
    partes = [_extrair_atrativo(nome, config) for nome, config in FONTES.items()]
    dados = pd.concat(partes, ignore_index=True)
    dados = dados.sort_values(["Atrativo", "Ano", "Mes_Numero"]).reset_index(drop=True)
    return dados


if __name__ == "__main__":
    dados = preparar_dataset()
    caminho_saida = "data/turismo_visitantes_atrativos.xlsx"
    dados.to_excel(caminho_saida, index=False, sheet_name="Visitantes")
    print(f"{len(dados)} registros gravados em {caminho_saida}")
    print(dados.head(10).to_string())
