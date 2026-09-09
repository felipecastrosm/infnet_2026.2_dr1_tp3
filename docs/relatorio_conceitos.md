# Relatório de conceitos — TP3 (DR1)

Este documento mapeia cada um dos 12 itens do enunciado (e os itens correspondentes da rubrica) para o trecho de código que os implementa em `app_tp3_felipe_castro_sotto_mayor.py`, e explica as decisões tomadas.

## 1. Escolha dos datasets, objetivo e motivação

Ver `secao_sobre()` (linha 157), que exibe o mesmo texto dentro do próprio app, em um `st.expander`. Resumo:

- **Datasets**: duas tabelas oficiais do portal [Data.Rio](https://www.data.rio), seção Turismo — *"Visitação ao Centro Cultural Banco do Brasil, 2015 a 2021"* (Tabela 4018) e *"Número de passagens vendidas para o morro do Corcovado (via estrada de ferro), 1996-2003"* (Tabela 474). Ambas publicadas pela Prefeitura do Rio de Janeiro sob licença CC-BY 4.0.
- **Preparação**: as duas tabelas originais vêm no formato "matriz Mês × Ano" típico dos relatórios estatísticos do Data.Rio (cabeçalho e notas de rodapé do template, dado numérico às vezes com espaço como separador de milhar ou "..." para indisponível). `scripts/preparar_dataset.py` baixa as duas planilhas originais, limpa esses valores e as reorganiza em uma única tabela "arrumada" (uma linha por observação): `Atrativo, Ano, Mes, Mes_Numero, Visitantes`, salva em `data/turismo_visitantes_atrativos.xlsx` (162 linhas). Essa é a planilha usada para testar o upload do dashboard.
- **Motivação**: comparar a visitação entre diferentes atrativos turísticos da cidade e sua evolução ao longo do tempo é uma necessidade real de quem planeja divulgação turística, eventos e investimentos - hoje esses dados ficam espalhados em várias planilhas isoladas do portal.
- **Funcionalidades planejadas**: upload de planilha, filtros (atrativo, ano, colunas), tabela ordenável/pesquisável, download do recorte filtrado, indicadores visuais de carregamento, personalização visual, cache, persistência de filtros, gráficos simples e avançados, métricas-resumo — detalhados nas seções seguintes.

## 2. Upload de arquivo XLS

`secao_upload()` (linha 189) usa `st.file_uploader(..., type=["xls", "xlsx", "csv"])`. O enunciado pede especificamente XLS; a rubrica pede especificamente CSV — o uploader aceita as duas variantes (e XLSX) para atender ambos, com o formato sendo detectado pela extensão do arquivo em `carregar_dados()` (linha 112).

## 3. Filtro de dados e seleção (radio, checkbox, dropdown)

`secao_filtros()` (linha 215) exibe o dataset carregado e implementa os três seletores pedidos, lado a lado em três colunas:

- **radio** (`st.radio`, dentro de `col_radio`): escolhe um valor da coluna categórica principal (`Atrativo`) ou "Todos".
- **checkbox** (`st.checkbox`, um por ano, dentro de `col_checkbox`): cada ano disponível no dataset vira uma caixa de marcação independente; os anos marcados definem quais linhas entram no filtro.
- **dropdown** (`st.multiselect`, dentro de `col_dropdown`): seleciona quais colunas do dataset devem ser exibidas/mantidas no restante do app.

Os três seletores atuam em conjunto sobre `dados_filtrados`, que já sai deste ponto com linhas e colunas reduzidas conforme a escolha do usuário.

## 4. Tabela interativa

`secao_tabela()` (linha 270) exibe `dados_filtrados` em `st.dataframe` (que já permite ordenar clicando no cabeçalho da coluna e tem busca embutida na barra de ferramentas), complementado por controles explícitos na interface:

- caixa de busca (`st.text_input`) que filtra linhas cujo conteúdo (em qualquer coluna) contém o texto digitado;
- `st.selectbox` para escolher a coluna de ordenação, e `st.radio` para a ordem (crescente/decrescente), aplicados via `DataFrame.sort_values`.

## 5. Serviço de download

`secao_download()` (linha 303) gera dois `st.download_button`: um exportando a tabela exibida (já filtrada/ordenada/buscada) como `.xlsx` (via `pd.ExcelWriter` com `openpyxl`, em um buffer `io.BytesIO`), outro como `.csv` (`DataFrame.to_csv`, codificado em `utf-8-sig` para abrir corretamente acentos no Excel).

## 6. Barra de progresso e spinner

`processar_upload()` (linha 127) usa os dois elementos em pontos diferentes e genuínos do carregamento: um `st.progress` com 3 etapas reais (leitura do arquivo, interpretação da planilha, validação/limpeza), e um `st.spinner` envolvendo especificamente a chamada de `carregar_dados()` (a etapa mais custosa, sujeita ao cache).

## 7. Color picker

`secao_personalizacao()` (linha 329), na barra lateral, expõe dois `st.color_picker`: cor de fundo do painel e cor das fontes. `aplicar_tema()` (linha 77) injeta essas cores como CSS customizado (`st.markdown(..., unsafe_allow_html=True)`), afetando o fundo do app, a cor do texto em geral e os cartões de métrica.

## 8. Cache

`carregar_dados()` (linha 111-112) é decorada com `@st.cache_data`. Como o cache é indexado pelo conteúdo do arquivo (bytes) e seu nome, reenviar o mesmo arquivo - ou apenas interagir com os filtros, que disparam um novo *rerun* do script Streamlit - não reprocessa a leitura da planilha; o resultado é reaproveitado da execução anterior.

## 9. Persistência com Session State

`inicializar_session_state()` (linha 53) define, uma única vez, as chaves usadas por todos os widgets de filtro e personalização (`filtro_atrativo`, `filtro_anos`, `colunas_exibidas`, `ordenar_por`, `cor_fundo`, `cor_fonte`, etc.). Cada widget correspondente é criado com `key=` apontando para essa mesma chave (ex.: linha 236, 253, 322-323), o que faz o Streamlit manter o valor escolhido pelo usuário em `st.session_state` entre um *rerun* e outro. O botão "Restaurar filtros e cores padrão" (linha 332-336) demonstra a manipulação explícita do `st.session_state` (limpando todas as chaves e forçando um novo `st.rerun()`).

## 10. Gráficos simples (barras, linhas, pizza)

`secao_graficos_simples()` (linha 349), com Plotly Express, organizados em `st.tabs`:

- **barras**: soma da coluna numérica por categoria (`px.bar`);
- **linhas**: evolução da soma da coluna numérica por `Ano` (`px.line`, com marcadores);
- **pizza**: participação percentual de cada categoria no total (`px.pie`).

## 11. Gráficos avançados (histograma e scatter)

`secao_graficos_avancados()` (linha 378):

- **histograma** (`px.histogram`): distribuição dos valores da coluna numérica, segmentada por cor pela categoria;
- **dispersão** (`px.scatter`): número do mês (`Mes_Numero`) no eixo X contra a coluna numérica no eixo Y, colorido e dimensionado pela categoria - evidencia sazonalidade mensal por atrativo.

## 12. Métricas básicas

`secao_metricas()` (linha 405) exibe, em `st.metric`, quatro indicadores calculados sobre os dados já filtrados: contagem de registros, soma, média e máximo da coluna numérica principal.

## Seleção dinâmica de colunas (generalização)

Para que os filtros/gráficos/métricas funcionem também se o usuário enviar outra planilha de turismo do Data.Rio com colunas diferentes das do dataset de exemplo, `_coluna_padrao()` (linha 208) e `_preparar_colunas_grafico()` (linha 340) escolhem automaticamente uma coluna categórica e uma numérica razoáveis (preferindo `Atrativo`/`Visitantes` quando existem, caindo para a primeira coluna de texto/número disponível caso contrário) - controle de fluxo (`if`/`for` e funções auxiliares) usado para estruturar toda a lógica de exibição do app, conforme pedido pela rubrica.
