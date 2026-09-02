"""The BI Extractor - Aplicação Web em Streamlit.

Motor de extração inteligente via OCR (PNG/JPG) e arquivos (Excel/CSV), normalização Tidy Data e exportação para Excel/Looker Studio.
"""

from __future__ import annotations

import io
import os
from typing import Optional

from PIL import Image
import pandas as pd
import streamlit as st

from components.charts import (
    render_bu_performance_chart,
    render_portfolio_achievement_chart,
    render_sales_composition_chart,
)
from components.metrics_cards import format_currency_br, render_metrics
from core.excel_exporter import generate_excel_workbook
from core.parser import parse_raw_data

# Configuração da Página
st.set_page_config(
    page_title="The BI Extractor | Saavedra",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilização CSS Customizada e Responsiva
st.markdown(
    """
    <style>
    /* Estilos Gerais */
    .main {
        background-color: #F8FAFC;
    }
    h1, h2, h3, h4 {
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
        color: #0F172A;
    }
    
    /* Header Customizado */
    .app-header {
        background: linear-gradient(135deg, #1F4E78 0%, #0F2D4A 100%);
        padding: 20px 28px;
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .app-header h1 {
        color: #FFFFFF !important;
        margin: 0;
        font-size: 26px;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    .app-header p {
        color: #93C5FD !important;
        margin: 4px 0 0 0;
        font-size: 14px;
    }

    /* Caixa de Instrução Inicial */
    .welcome-card {
        background: #FFFFFF;
        border: 2px dashed #CBD5E1;
        border-radius: 12px;
        padding: 48px 24px;
        text-align: center;
        margin-top: 20px;
    }
    .welcome-card h3 {
        color: #1F4E78;
        margin-bottom: 8px;
    }
    .welcome-card p {
        color: #64748B;
        font-size: 15px;
        max-width: 600px;
        margin: 0 auto;
    }

    /* Total Summary Box */
    .total-summary-card {
        background: #1F4E78;
        color: white;
        padding: 16px 20px;
        border-radius: 8px;
        margin-top: 14px;
        margin-bottom: 14px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
    }
    .total-summary-item {
        display: flex;
        flex-direction: column;
    }
    .total-summary-label {
        font-size: 12px;
        color: #93C5FD;
        font-weight: 500;
    }
    .total-summary-val {
        font-size: 17px;
        font-weight: 700;
        color: #FFFFFF;
    }

    /* Botões de Download */
    .stDownloadButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        padding: 12px 16px;
        transition: all 0.2s ease;
    }
    .stDownloadButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(31, 78, 120, 0.25);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def process_uploaded_file(file_bytes: bytes, filename: str) -> pd.DataFrame:
    """Processa e normaliza a imagem (PNG/JPG com OCR) ou arquivo (Excel/CSV) em memória."""
    buffer = io.BytesIO(file_bytes)
    buffer.name = filename
    return parse_raw_data(buffer)


def build_dataframe_with_total(df: pd.DataFrame) -> pd.DataFrame:
    """Insere a linha de TOTAL GERAL no final do DataFrame."""
    if df.empty:
        return df

    total_billed = df["Gross Sales Billed"].sum()
    total_open = df["Gross Sales Open"].sum()
    total_gross = df["Total Gross"].sum()
    total_meta = df["FY26 PPs"].sum()
    ating_pps = total_gross - total_meta
    perc_pps = (total_gross / total_meta) if total_meta > 0 else 0.0

    total_row = pd.DataFrame(
        [
            {
                "Customer Group": "TOTAL GERAL",
                "Business Unit": "CONSOLIDADO",
                "Portfolio": "TOTAL GERAL",
                "FY26 PPs": total_meta,
                "Gross Sales Billed": total_billed,
                "Gross Sales Open": total_open,
                "Total Gross": total_gross,
                "Ating PPs": ating_pps,
                "% PPs": perc_pps,
            }
        ]
    )
    return pd.concat([df, total_row], ignore_index=True)


def main() -> None:
    """Função principal que orquestra a interface e as regras de negócio."""
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚡ The BI Extractor")
        st.caption("Extrator OCR de Imagens & Normalizador Power BI")
        st.divider()

        # Upload de Imagens (PNG, JPG) ou Planilhas (Excel, CSV)
        st.markdown("#### 📷 Ingestão de Imagem / Arquivo")
        uploaded_file = st.file_uploader(
            "Faça o upload do print (PNG, JPG) ou arquivo:",
            type=["png", "jpg", "jpeg", "xlsx", "xls", "csv"],
            help="Faça o upload do print de tela da matriz para iniciar a extração com IA Gemini Vision.",
        )

        with st.expander("⚙️ Configurações de IA (Gemini)", expanded=False):
            gemini_key = st.text_input(
                "Chave API do Google GenAI:",
                value="AQ.Ab8RN6LV7L0YNvB5VyjWvileuaJrfeLm5SLmmX8Mn34PCioi7w",
                type="password",
                help="Chave utilizada para extração visual com Gemini 3.6 Flash / Flash Latest.",
            )
            if gemini_key:
                os.environ["GEMINI_API_KEY"] = gemini_key

        st.divider()

        view_mode = "📋 Dados Normalizados (Tidy Data)"
        if uploaded_file is not None:
            st.markdown("#### 🧭 Modo de Exibição")
            view_mode = st.radio(
                "Visualizar:",
                options=["📋 Dados Normalizados (Tidy Data)", "📊 Mini-BI & Gráficos Executivos"],
                index=0,
            )
            st.divider()

    # Cabeçalho Principal
    st.markdown(
        """
        <div class="app-header">
            <h1>⚡ The BI Extractor</h1>
            <p>Extração automática de matrizes Power BI via OCR e normalização para o Google Looker Studio.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. TELA INICIAL LIMPA (SE NENHUM ARQUIVO FOR CARREGADO)
    if uploaded_file is None:
        st.markdown(
            """
            <div class="welcome-card">
                <h3>📷 Aguardando Upload de Imagem ou Arquivo</h3>
                <p>
                    Nenhum dado foi carregado ainda.<br>
                    Utilize a <b>barra lateral à esquerda</b> para anexar o print de tela (PNG / JPG) da matriz do Power BI ou a planilha exportada.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # 2. PROCESSAMENTO DO ARQUIVO ANEXADO
    df_raw_tidy: Optional[pd.DataFrame] = None
    image_preview: Optional[Image.Image] = None

    try:
        filename_lower = uploaded_file.name.lower()
        is_image = any(filename_lower.endswith(ext) for ext in [".png", ".jpg", ".jpeg"])

        if is_image:
            image_preview = Image.open(uploaded_file)
            uploaded_file.seek(0)
            with st.spinner("🤖 Analisando matriz com IA Vision do Google Gemini e calculando totais..."):
                file_bytes = uploaded_file.getvalue()
                df_raw_tidy = process_uploaded_file(file_bytes, uploaded_file.name)
        else:
            with st.spinner("Processando e normalizando arquivo tabular..."):
                file_bytes = uploaded_file.getvalue()
                df_raw_tidy = process_uploaded_file(file_bytes, uploaded_file.name)

        st.sidebar.success(f"✓ {len(df_raw_tidy)} itens extraídos e integrados!")
    except Exception as e:
        st.error(f"❌ Erro ao extrair dados do arquivo: {str(e)}")
        return

    if df_raw_tidy is None or df_raw_tidy.empty:
        st.warning("Nenhum dado tabular foi identificado na imagem enviada.")
        return

    # Filtros na Sidebar
    with st.sidebar:
        st.markdown("#### 🔍 Filtros")
        available_bus = sorted(df_raw_tidy["Business Unit"].dropna().unique().tolist())
        selected_bus = st.multiselect(
            "Business Unit (BU):",
            options=available_bus,
            default=available_bus,
        )

        search_query = st.text_input("Buscar Portfólio / Grupo:", placeholder="Ex: AAD, Bone, MDS...").strip().lower()

        include_total_in_table = st.checkbox("Exibir Linha de TOTAL GERAL na Tabela", value=True)
        st.divider()
        st.caption("Desenvolvido para Saavedra • The BI Extractor v2.2")

    # Aplicação dos Filtros
    df_filtered = df_raw_tidy.copy()
    if selected_bus:
        df_filtered = df_filtered[df_filtered["Business Unit"].isin(selected_bus)]

    if search_query:
        df_filtered = df_filtered[
            df_filtered["Portfolio"].str.lower().str.contains(search_query)
            | df_filtered["Business Unit"].str.lower().str.contains(search_query)
            | df_filtered["Customer Group"].str.lower().str.contains(search_query)
        ]

    # Imagem Original Opcional
    if image_preview is not None:
        with st.expander("🖼️ Visualizar Imagem Original Enviada", expanded=False):
            st.image(image_preview, caption="Imagem do Power BI", use_container_width=True)

    # VISÃO 1: DADOS NORMALIZADOS (TIDY DATA)
    if view_mode == "📋 Dados Normalizados (Tidy Data)":
        st.markdown("### 📋 Dados Normalizados (Tidy Data)")

        # Barra de Totais Executivos em Destaque
        t_meta = df_filtered["FY26 PPs"].sum()
        t_billed = df_filtered["Gross Sales Billed"].sum()
        t_open = df_filtered["Gross Sales Open"].sum()
        t_gross = df_filtered["Total Gross"].sum()
        t_gap = t_gross - t_meta
        t_perc = (t_gross / t_meta * 100.0) if t_meta > 0 else 0.0

        st.markdown(
            f"""
            <div class="total-summary-card">
                <div class="total-summary-item">
                    <span class="total-summary-label">TOTAL FATURADO (BILLED)</span>
                    <span class="total-summary-val">{format_currency_br(t_billed)}</span>
                </div>
                <div class="total-summary-item">
                    <span class="total-summary-label">VENDAS EM ABERTO (OPEN)</span>
                    <span class="total-summary-val">{format_currency_br(t_open)}</span>
                </div>
                <div class="total-summary-item">
                    <span class="total-summary-label">TOTAL GERAL (GROSS)</span>
                    <span class="total-summary-val" style="color: #6EE7B7;">{format_currency_br(t_gross)}</span>
                </div>
                <div class="total-summary-item">
                    <span class="total-summary-label">META FY26 PPS</span>
                    <span class="total-summary-val">{format_currency_br(t_meta)}</span>
                </div>
                <div class="total-summary-item">
                    <span class="total-summary-label">GAP DE META</span>
                    <span class="total-summary-val" style="color: {'#FCA5A5' if t_gap < 0 else '#6EE7B7'};">{format_currency_br(t_gap)}</span>
                </div>
                <div class="total-summary-item">
                    <span class="total-summary-label">% ATINGIMENTO</span>
                    <span class="total-summary-val" style="color: {'#6EE7B7' if t_perc >= 100 else '#FCD34D'};">{t_perc:.2f}%</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Preparação do DataFrame de exibição (com ou sem linha de Total Geral)
        df_display = build_dataframe_with_total(df_filtered) if include_total_in_table else df_filtered

        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Customer Group": st.column_config.TextColumn("Grupo Cliente", width="medium"),
                "Business Unit": st.column_config.TextColumn("Business Unit", width="small"),
                "Portfolio": st.column_config.TextColumn("Portfólio", width="large"),
                "FY26 PPs": st.column_config.NumberColumn("Meta FY26 PPs", format="R$ %.2f"),
                "Gross Sales Billed": st.column_config.NumberColumn("Gross Sales Billed", format="R$ %.2f"),
                "Gross Sales Open": st.column_config.NumberColumn("Gross Sales Open", format="R$ %.2f"),
                "Total Gross": st.column_config.NumberColumn("Total Gross", format="R$ %.2f"),
                "Ating PPs": st.column_config.NumberColumn("Ating PPs (Gap)", format="R$ %.2f"),
                "% PPs": st.column_config.NumberColumn("% PPs (Atingimento)", format="%.2f%%"),
            },
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # Central de Exportação
        st.markdown("### 🚀 Central de Exportação")
        col_exp1, col_exp2 = st.columns(2)

        with col_exp1:
            st.markdown("#### 📑 Planilha Excel Formatada (.xlsx)")
            st.caption("Inclui formatação contábil em Navy Blue e linha de TOTAL GERAL com fórmulas nativas.")
            try:
                excel_bytes = generate_excel_workbook(df_filtered)
                st.download_button(
                    label="📥 Baixar Planilha Formatada (.xlsx)",
                    data=excel_bytes,
                    file_name="the_bi_extractor_tidy_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_excel_main",
                )
            except Exception as e:
                st.error(f"Erro ao gerar planilha Excel: {e}")

        with col_exp2:
            st.markdown("#### 🌐 Google Looker Studio Ready (.csv)")
            st.caption("Arquivo UTF-8 com BOM pronto para conexão direta como fonte de dados no Looker Studio.")
            try:
                csv_data = df_filtered.to_csv(index=False, sep=";", encoding="utf-8-sig")
                st.download_button(
                    label="📥 Baixar CSV para Looker Studio (.csv)",
                    data=csv_data,
                    file_name="the_bi_extractor_looker_studio.csv",
                    mime="text/csv",
                    key="download_csv_main",
                )
            except Exception as e:
                st.error(f"Erro ao gerar CSV: {e}")

    # VISÃO 2: MINI-BI & GRÁFICOS EXECUTIVOS
    else:
        st.markdown("### 📌 Indicadores Consolidados (KPIs)")
        render_metrics(df_filtered)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("### 📊 Mini-BI Executivo")
        tab_bu, tab_portfolio, tab_sales = st.tabs(
            ["🏢 Desempenho por Business Unit", "🎯 Top Portfólios por Atingimento", "📦 Composição de Faturamento"]
        )

        with tab_bu:
            render_bu_performance_chart(df_filtered)

        with tab_portfolio:
            render_portfolio_achievement_chart(df_filtered)

        with tab_sales:
            render_sales_composition_chart(df_filtered)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("### 🚀 Exportação dos Dados Filtrados")
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            excel_bytes = generate_excel_workbook(df_filtered)
            st.download_button(
                label="📥 Baixar Excel Formatado (.xlsx)",
                data=excel_bytes,
                file_name="the_bi_extractor_tidy_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_excel_bi",
            )
        with col_b2:
            csv_data = df_filtered.to_csv(index=False, sep=";", encoding="utf-8-sig")
            st.download_button(
                label="📥 Baixar CSV para Looker Studio (.csv)",
                data=csv_data,
                file_name="the_bi_extractor_looker_studio.csv",
                mime="text/csv",
                key="download_csv_bi",
            )


if __name__ == "__main__":
    main()
