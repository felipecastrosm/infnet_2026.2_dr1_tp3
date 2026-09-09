"""TP3 (DR1) - Dashboard de Turismo Carioca (Data.Rio)

Disciplina: Desenvolvimento de Dashboards com Streamlit (INFNET)
Autor: Felipe Castro Sotto Mayor

Dashboard em Streamlit para explorar dados de visitação a atrativos
turísticos da cidade do Rio de Janeiro, publicados no portal de dados
abertos Data.Rio (seção Turismo). O usuário faz upload de uma planilha
(XLS/XLSX ou CSV), filtra e ordena os dados pela interface, visualiza
gráficos simples e avançados, métricas-resumo, e exporta o resultado
filtrado de volta em XLS ou CSV.

Dataset de exemplo para teste (gerado por scripts/preparar_dataset.py a
partir de duas tabelas oficiais do Data.Rio - ver docs/relatorio_conceitos.md):
    data/turismo_visitantes_atrativos.xlsx
    colunas: Atrativo, Ano, Mes, Mes_Numero, Visitantes

Execução: `streamlit run app_tp3_felipe_castro_sotto_mayor.py`
"""

from __future__ import annotations

import io
import time

import pandas as pd
import plotly.express as px
import streamlit as st

# --------------------------------------------------------------------------
# Configuração geral da página e valores padrão
# --------------------------------------------------------------------------

COR_FUNDO_PADRAO = "#0E1117"
COR_FONTE_PADRAO = "#FAFAFA"
COR_DESTAQUE = "#00C2CB"

MESES_ORDEM = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]


def configurar_pagina() -> None:
    st.set_page_config(
        page_title="Turismo Carioca | Data.Rio",
        page_icon="🏖️",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def inicializar_session_state() -> None:
    """Define, uma única vez, os valores padrão persistidos entre interações.

    Os widgets abaixo são todos ligados a chaves de `st.session_state` (via
    o argumento `key=`), então qualquer seleção do usuário - filtros, cores
    escolhidas, colunas exibidas - permanece a mesma enquanto a aplicação
    roda, mesmo que o usuário interaja com outro widget e a página seja
    re-executada (comportamento padrão do Streamlit a cada interação).
    """
    valores_padrao = {
        "cor_fundo": COR_FUNDO_PADRAO,
        "cor_fonte": COR_FONTE_PADRAO,
        "filtro_atrativo": "Todos",
        "filtro_anos": [],
        "colunas_exibidas": [],
        "ordenar_por": None,
        "ordem_crescente": True,
        "busca_texto": "",
    }
    for chave, valor in valores_padrao.items():
        if chave not in st.session_state:
            st.session_state[chave] = valor


def aplicar_tema(cor_fundo: str, cor_fonte: str) -> None:
    """Injeta CSS customizado para aplicar as cores escolhidas no color picker."""
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {cor_fundo};
            color: {cor_fonte};
        }}
        .stApp, .stApp p, .stApp span, .stApp label, .stApp li,
        .stApp h1, .stApp h2, .stApp h3, .stApp h4 {{
            color: {cor_fonte};
        }}
        section[data-testid="stSidebar"] {{
            background-color: {cor_fundo};
            border-right: 1px solid {COR_DESTAQUE}40;
        }}
        div[data-testid="stMetric"] {{
            background-color: {cor_fonte}0d;
            border: 1px solid {COR_DESTAQUE}40;
            border-radius: 10px;
            padding: 12px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------------------
# Carregamento dos dados (upload + cache)
# --------------------------------------------------------------------------


@st.cache_data(show_spinner=False)
def carregar_dados(conteudo_arquivo: bytes, nome_arquivo: str) -> pd.DataFrame:
    """Lê o arquivo enviado pelo usuário (CSV ou XLS/XLSX) e devolve um DataFrame.

    Decorado com `st.cache_data`: enquanto o mesmo arquivo (mesmos bytes)
    for reenviado, o Streamlit reaproveita o resultado já calculado em vez
    de reprocessar a planilha a cada interação do usuário com os filtros.
    """
    buffer = io.BytesIO(conteudo_arquivo)
    if nome_arquivo.lower().endswith(".csv"):
        dados = pd.read_csv(buffer)
    else:
        dados = pd.read_excel(buffer)
    return dados


def processar_upload(arquivo_carregado) -> pd.DataFrame | None:
    """Processa o arquivo enviado, exibindo barra de progresso e spinner
    durante as etapas de leitura e validação dos dados."""
    if arquivo_carregado is None:
        return None

    etapas = ("Lendo arquivo...", "Interpretando planilha...", "Validando colunas...")
    barra_progresso = st.progress(0, text=etapas[0])

    conteudo = arquivo_carregado.getvalue()
    barra_progresso.progress(33, text=etapas[1])

    with st.spinner("Processando dados carregados..."):
        dados = carregar_dados(conteudo, arquivo_carregado.name)
        time.sleep(0.3)  # torna a etapa perceptível para o usuário

    barra_progresso.progress(66, text=etapas[2])
    dados = dados.dropna(how="all")
    barra_progresso.progress(100, text="Concluído!")
    time.sleep(0.2)
    barra_progresso.empty()

    return dados


# --------------------------------------------------------------------------
# Seções da interface
# --------------------------------------------------------------------------


def secao_sobre() -> None:
    with st.expander("📌 Sobre este projeto - dataset, objetivo e motivação", expanded=False):
        st.markdown(
            """
            **Datasets escolhidos (portal [Data.Rio](https://www.data.rio), seção Turismo):**

            - *Visitação ao Centro Cultural Banco do Brasil, 2015 a 2021* (Tabela 4018)
            - *Número de passagens vendidas para o morro do Corcovado — visita ao
              Cristo Redentor pela estrada de ferro, 1996-2003* (Tabela 474)

            As duas tabelas foram combinadas (ver `scripts/preparar_dataset.py`) em uma
            única planilha "arrumada" (uma linha por observação mensal), disponível em
            `data/turismo_visitantes_atrativos.xlsx`, com as colunas **Atrativo, Ano,
            Mes, Mes_Numero e Visitantes**.

            **Objetivo e motivação:** o time de turismo da cidade frequentemente precisa
            comparar a visitação entre diferentes atrativos e ao longo do tempo, para
            apoiar decisões de investimento, sazonalidade de eventos e promoção turística.
            Este dashboard permite carregar esse tipo de planilha, filtrar por atrativo e
            ano, visualizar tabelas e gráficos (evolução mensal, distribuição de
            visitantes, participação de cada atrativo) e exportar o recorte de interesse.

            **Funcionalidades implementadas:** upload de XLS/CSV, filtros por radio button,
            checkboxes e dropdowns, tabela interativa (ordenação e busca), download dos
            dados filtrados (XLS e CSV), barra de progresso e spinner no carregamento,
            personalização de cores (color picker), cache dos dados carregados,
            persistência de filtros via Session State, gráficos simples (barras, linhas,
            pizza), gráficos avançados (histograma, dispersão) e métricas-resumo.
            """
        )


def secao_upload() -> pd.DataFrame | None:
    st.subheader("1. Upload dos dados")
    arquivo_carregado = st.file_uploader(
        "Envie um arquivo de turismo do Data.Rio (XLS, XLSX ou CSV)",
        type=["xls", "xlsx", "csv"],
        help="Ex.: data/turismo_visitantes_atrativos.xlsx, gerado a partir de tabelas do Data.Rio.",
    )
    if arquivo_carregado is None:
        st.info(
            "Nenhum arquivo enviado ainda. Utilize o arquivo de exemplo em "
            "`data/turismo_visitantes_atrativos.xlsx` para testar a aplicação."
        )
        return None

    dados = processar_upload(arquivo_carregado)
    st.success(f"Arquivo **{arquivo_carregado.name}** carregado com {len(dados)} linhas.")
    return dados


def _coluna_padrao(colunas: list[str], candidatas: list[str], indice_fallback: int = 0) -> str:
    for candidata in candidatas:
        if candidata in colunas:
            return candidata
    return colunas[indice_fallback]


def secao_filtros(dados: pd.DataFrame) -> pd.DataFrame:
    st.subheader("2. Filtros e seleção de dados")

    colunas_categoricas = [c for c in dados.columns if dados[c].dtype == object]
    coluna_categoria = _coluna_padrao(list(dados.columns), ["Atrativo"] + colunas_categoricas)

    col_radio, col_checkbox, col_dropdown = st.columns(3)

    # --- Seletor 1: radio -------------------------------------------------
    with col_radio:
        opcoes_categoria = ["Todos"] + sorted(dados[coluna_categoria].dropna().unique().tolist())
        st.radio(
            f"Filtrar por '{coluna_categoria}'",
            options=opcoes_categoria,
            key="filtro_atrativo",
        )

    # --- Seletor 2: checkbox ------------------------------------------------
    with col_checkbox:
        st.markdown("Filtrar por ano" if "Ano" in dados.columns else "Anos disponíveis")
        if "Ano" in dados.columns:
            anos_disponiveis = sorted(dados["Ano"].dropna().unique().tolist())
            if not st.session_state["filtro_anos"]:
                st.session_state["filtro_anos"] = anos_disponiveis
            anos_selecionados = []
            for ano in anos_disponiveis:
                marcado = st.checkbox(
                    str(int(ano)), value=ano in st.session_state["filtro_anos"], key=f"ano_{ano}"
                )
                if marcado:
                    anos_selecionados.append(ano)
            st.session_state["filtro_anos"] = anos_selecionados
        else:
            st.caption("Este dataset não possui coluna 'Ano'.")

    # --- Seletor 3: dropdown (multiselect) ---------------------------------
    with col_dropdown:
        if not st.session_state["colunas_exibidas"]:
            st.session_state["colunas_exibidas"] = list(dados.columns)
        st.multiselect(
            "Selecionar colunas a exibir",
            options=list(dados.columns),
            key="colunas_exibidas",
        )

    dados_filtrados = dados.copy()
    if st.session_state["filtro_atrativo"] != "Todos":
        dados_filtrados = dados_filtrados[dados_filtrados[coluna_categoria] == st.session_state["filtro_atrativo"]]
    if "Ano" in dados.columns and st.session_state["filtro_anos"]:
        dados_filtrados = dados_filtrados[dados_filtrados["Ano"].isin(st.session_state["filtro_anos"])]

    colunas_para_exibir = st.session_state["colunas_exibidas"] or list(dados.columns)
    return dados_filtrados[colunas_para_exibir]


def secao_tabela(dados_filtrados: pd.DataFrame) -> pd.DataFrame:
    st.subheader("3. Tabela interativa")

    col_busca, col_ordenar, col_ordem = st.columns([2, 1, 1])
    with col_busca:
        st.text_input(
            "Buscar (filtra linhas que contenham o texto em qualquer coluna)",
            key="busca_texto",
        )
    with col_ordenar:
        st.selectbox("Ordenar por", options=list(dados_filtrados.columns), key="ordenar_por")
    with col_ordem:
        st.radio("Ordem", options=["Crescente", "Decrescente"], key="ordem_texto", horizontal=True)

    tabela = dados_filtrados.copy()
    if st.session_state["busca_texto"]:
        mascara = tabela.apply(
            lambda linha: linha.astype(str).str.contains(st.session_state["busca_texto"], case=False).any(),
            axis=1,
        )
        tabela = tabela[mascara]

    coluna_ordenacao = st.session_state.get("ordenar_por")
    if coluna_ordenacao in tabela.columns:
        tabela = tabela.sort_values(
            coluna_ordenacao, ascending=(st.session_state.get("ordem_texto", "Crescente") == "Crescente")
        )

    st.dataframe(tabela, use_container_width=True, height=360)
    st.caption(f"{len(tabela)} linha(s) exibida(s) de {len(dados_filtrados)} após os filtros.")
    return tabela


def secao_download(dados_para_download: pd.DataFrame) -> None:
    st.subheader("4. Download dos dados filtrados")

    buffer_xlsx = io.BytesIO()
    with pd.ExcelWriter(buffer_xlsx, engine="openpyxl") as escritor:
        dados_para_download.to_excel(escritor, index=False, sheet_name="Dados filtrados")

    col_xlsx, col_csv = st.columns(2)
    with col_xlsx:
        st.download_button(
            "⬇️ Baixar como XLSX",
            data=buffer_xlsx.getvalue(),
            file_name="turismo_dados_filtrados.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    with col_csv:
        st.download_button(
            "⬇️ Baixar como CSV",
            data=dados_para_download.to_csv(index=False).encode("utf-8-sig"),
            file_name="turismo_dados_filtrados.csv",
            mime="text/csv",
            use_container_width=True,
        )


def secao_personalizacao() -> None:
    with st.sidebar:
        st.markdown("### 🎨 Personalização")
        st.color_picker("Cor de fundo do painel", key="cor_fundo")
        st.color_picker("Cor das fontes", key="cor_fonte")
        if st.button("Restaurar filtros e cores padrão"):
            for chave in list(st.session_state.keys()):
                del st.session_state[chave]
            st.rerun()


def _preparar_colunas_grafico(dados: pd.DataFrame) -> tuple[str, str]:
    colunas_numericas = dados.select_dtypes("number").columns.tolist()
    colunas_categoricas = [c for c in dados.columns if c not in colunas_numericas]

    coluna_numerica = _coluna_padrao(colunas_numericas or list(dados.columns), ["Visitantes"])
    coluna_categorica = _coluna_padrao(colunas_categoricas or list(dados.columns), ["Atrativo", "Mes"])
    return coluna_categorica, coluna_numerica


def secao_graficos_simples(dados: pd.DataFrame) -> None:
    st.subheader("5. Gráficos simples")
    if dados.empty:
        st.warning("Não há dados para plotar com os filtros atuais.")
        return

    coluna_categorica, coluna_numerica = _preparar_colunas_grafico(dados)

    aba_barras, aba_linhas, aba_pizza = st.tabs(["📊 Barras", "📈 Linhas", "🥧 Pizza"])

    with aba_barras:
        resumo = dados.groupby(coluna_categorica, as_index=False)[coluna_numerica].sum()
        fig = px.bar(resumo, x=coluna_categorica, y=coluna_numerica, color=coluna_categorica)
        st.plotly_chart(fig, use_container_width=True)

    with aba_linhas:
        if "Ano" in dados.columns:
            evolucao = dados.groupby("Ano", as_index=False)[coluna_numerica].sum()
            fig = px.line(evolucao, x="Ano", y=coluna_numerica, markers=True)
        else:
            fig = px.line(dados.reset_index(), x="index", y=coluna_numerica)
        st.plotly_chart(fig, use_container_width=True)

    with aba_pizza:
        resumo = dados.groupby(coluna_categorica, as_index=False)[coluna_numerica].sum()
        fig = px.pie(resumo, names=coluna_categorica, values=coluna_numerica)
        st.plotly_chart(fig, use_container_width=True)


def secao_graficos_avancados(dados: pd.DataFrame) -> None:
    st.subheader("6. Gráficos avançados")
    if dados.empty:
        st.warning("Não há dados para plotar com os filtros atuais.")
        return

    coluna_categorica, coluna_numerica = _preparar_colunas_grafico(dados)
    coluna_eixo_x = "Mes_Numero" if "Mes_Numero" in dados.columns else coluna_numerica

    aba_histograma, aba_dispersao = st.tabs(["📐 Histograma", "✨ Dispersão"])

    with aba_histograma:
        fig = px.histogram(dados, x=coluna_numerica, color=coluna_categorica, nbins=20)
        st.plotly_chart(fig, use_container_width=True)

    with aba_dispersao:
        fig = px.scatter(
            dados,
            x=coluna_eixo_x,
            y=coluna_numerica,
            color=coluna_categorica,
            size=coluna_numerica,
            hover_data=dados.columns,
        )
        st.plotly_chart(fig, use_container_width=True)


def secao_metricas(dados: pd.DataFrame) -> None:
    st.subheader("7. Métricas-resumo")
    if dados.empty:
        st.warning("Não há dados para resumir com os filtros atuais.")
        return

    _, coluna_numerica = _preparar_colunas_grafico(dados)
    coluna_valores = dados[coluna_numerica]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Registros", f"{len(dados):,}".replace(",", "."))
    col2.metric(f"Soma de {coluna_numerica}", f"{coluna_valores.sum():,.0f}".replace(",", "."))
    col3.metric(f"Média de {coluna_numerica}", f"{coluna_valores.mean():,.0f}".replace(",", "."))
    col4.metric(f"Máximo de {coluna_numerica}", f"{coluna_valores.max():,.0f}".replace(",", "."))


# --------------------------------------------------------------------------
# Orquestração
# --------------------------------------------------------------------------


def main() -> None:
    configurar_pagina()
    inicializar_session_state()
    secao_personalizacao()
    aplicar_tema(st.session_state["cor_fundo"], st.session_state["cor_fonte"])

    st.title("🏖️ Dashboard de Turismo Carioca")
    st.caption("Dados abertos do portal Data.Rio - seção Turismo")

    secao_sobre()

    dados = secao_upload()
    if dados is None:
        st.stop()

    dados_filtrados = secao_filtros(dados)
    tabela_exibida = secao_tabela(dados_filtrados)
    secao_download(tabela_exibida)
    secao_graficos_simples(dados_filtrados)
    secao_graficos_avancados(dados_filtrados)
    secao_metricas(dados_filtrados)


if __name__ == "__main__":
    main()
