"""Componentes de exibição dos KPIs executivos (Total Gross, Atingimento, Gap de Meta, etc.)."""

from __future__ import annotations

import pandas as pd
import streamlit as st


def format_currency_br(val: float) -> str:
    """Formata valor em moeda brasileira (R$)."""
    if pd.isna(val):
        return "R$ 0,00"
    is_neg = val < 0
    val_abs = abs(val)
    formatted = f"{val_abs:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"-R$ {formatted}" if is_neg else f"R$ {formatted}"


def render_metrics(df: pd.DataFrame) -> None:
    """Renderiza cards com os principais KPIs executivos formatados sem truncamento de valores."""
    if df.empty:
        st.warning("Nenhum dado disponível para cálculo de métricas.")
        return

    # Cálculos Consolidados
    total_billed = df["Gross Sales Billed"].sum()
    total_open = df["Gross Sales Open"].sum()
    total_gross = df["Total Gross"].sum()
    total_meta = df["FY26 PPs"].sum()
    gap_meta = total_gross - total_meta
    ating_percent = (total_gross / total_meta * 100.0) if total_meta > 0 else 0.0

    # Determinar status e cores de atingimento
    if ating_percent >= 100.0:
        badge_bg = "#ECFDF5"
        badge_color = "#059669"
        status_text = f"✓ Meta Atingida (+{ating_percent - 100.0:.2f}%)"
    elif ating_percent >= 80.0:
        badge_bg = "#FFFBEB"
        badge_color = "#D97706"
        status_text = f"⚠ Atenção ({ating_percent - 100.0:.2f}%)"
    else:
        badge_bg = "#FEF2F2"
        badge_color = "#DC2626"
        status_text = f"↓ Abaixo da Meta ({ating_percent - 100.0:.2f}%)"

    gap_color = "#DC2626" if gap_meta < 0 else "#059669"
    gap_badge_bg = "#FEF2F2" if gap_meta < 0 else "#ECFDF5"

    # Layout de 5 Colunas com HTML/CSS de Alta Densidade e Legibilidade Total
    c1, c2, c3, c4, c5 = st.columns(5)

    card_style = """
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 14px 16px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        min-height: 110px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    """

    with c1:
        st.markdown(
            f"""
            <div style="{card_style}">
                <div style="font-size: 13px; color: #64748B; font-weight: 600;">💼 Total Faturado</div>
                <div style="font-size: 19px; color: #0F172A; font-weight: 700; margin: 4px 0;">{format_currency_br(total_billed)}</div>
                <div style="font-size: 11px; color: #94A3B8;">Gross Sales Billed</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            f"""
            <div style="{card_style}">
                <div style="font-size: 13px; color: #64748B; font-weight: 600;">⏳ Vendas em Aberto</div>
                <div style="font-size: 19px; color: #0F172A; font-weight: 700; margin: 4px 0;">{format_currency_br(total_open)}</div>
                <div style="font-size: 11px; color: #94A3B8;">Gross Sales Open</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            f"""
            <div style="{card_style}">
                <div style="font-size: 13px; color: #64748B; font-weight: 600;">📊 Total Geral (Gross)</div>
                <div style="font-size: 19px; color: #1F4E78; font-weight: 700; margin: 4px 0;">{format_currency_br(total_gross)}</div>
                <div style="font-size: 11px; color: #94A3B8;">Billed + Open</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c4:
        st.markdown(
            f"""
            <div style="{card_style}">
                <div style="font-size: 13px; color: #64748B; font-weight: 600;">🎯 Meta FY26 PPs</div>
                <div style="font-size: 19px; color: #0F172A; font-weight: 700; margin: 4px 0;">{format_currency_br(total_meta)}</div>
                <div style="font-size: 11px; color: {gap_color}; font-weight: 600; background: {gap_badge_bg}; padding: 2px 6px; border-radius: 4px; display: inline-block;">
                    Gap: {format_currency_br(gap_meta)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c5:
        st.markdown(
            f"""
            <div style="{card_style}">
                <div style="font-size: 13px; color: #64748B; font-weight: 600;">📈 % Atingimento</div>
                <div style="font-size: 22px; color: {badge_color}; font-weight: 800; margin: 2px 0;">{ating_percent:.2f}%</div>
                <div style="font-size: 11px; color: {badge_color}; font-weight: 600; background: {badge_bg}; padding: 2px 6px; border-radius: 4px; display: inline-block;">
                    {status_text}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
