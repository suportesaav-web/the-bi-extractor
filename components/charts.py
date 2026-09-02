"""Gráficos interativos em Plotly para análise visual de performance por BU e Portfólio."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def render_bu_performance_chart(df: pd.DataFrame) -> None:
    """Gráfico de barras comparativo: Total Gross vs Meta FY26 por Business Unit."""
    if df.empty:
        return

    # Agrupar por Business Unit
    bu_summary = df.groupby("Business Unit", as_index=False).agg(
        {
            "Total Gross": "sum",
            "FY26 PPs": "sum",
            "Gross Sales Billed": "sum",
            "Gross Sales Open": "sum",
        }
    )
    bu_summary["% Atingimento"] = (
        bu_summary.apply(lambda r: (r["Total Gross"] / r["FY26 PPs"] * 100.0) if r["FY26 PPs"] > 0 else 0.0, axis=1)
    )
    bu_summary = bu_summary.sort_values(by="Total Gross", ascending=True)

    fig = go.Figure()

    # Barra Meta FY26
    fig.add_trace(
        go.Bar(
            y=bu_summary["Business Unit"],
            x=bu_summary["FY26 PPs"],
            name="Meta (FY26 PPs)",
            orientation="h",
            marker=dict(color="#CBD5E1", line=dict(color="#94A3B8", width=1)),
            hovertemplate="<b>%{y}</b><br>Meta FY26: R$ %{x:,.2f}<extra></extra>",
        )
    )

    # Barra Realizado (Total Gross)
    fig.add_trace(
        go.Bar(
            y=bu_summary["Business Unit"],
            x=bu_summary["Total Gross"],
            name="Total Gross (Realizado)",
            orientation="h",
            marker=dict(color="#1F4E78", line=dict(color="#0F2D4A", width=1)),
            hovertemplate="<b>%{y}</b><br>Total Gross: R$ %{x:,.2f}<extra></extra>",
        )
    )

    fig.update_layout(
        title=dict(text="<b>Performance por Business Unit: Realizado vs Meta</b>", font=dict(size=16, color="#1E293B")),
        barmode="group",
        height=380,
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        xaxis=dict(
            title="Valor (R$)",
            gridcolor="#F1F5F9",
            tickprefix="R$ ",
            separatethousands=True,
        ),
        yaxis=dict(title=None),
    )

    st.plotly_chart(fig, use_container_width=True)


def render_portfolio_achievement_chart(df: pd.DataFrame) -> None:
    """Gráfico de barras de % de Atingimento por Portfólio com linha de 100%."""
    if df.empty:
        return

    # Agrupar por Portfólio
    port_df = df[df["FY26 PPs"] > 0].copy()
    if port_df.empty:
        port_df = df.copy()

    port_summary = port_df.groupby(["Portfolio", "Business Unit"], as_index=False).agg(
        {
            "Total Gross": "sum",
            "FY26 PPs": "sum",
        }
    )
    port_summary["% Atingimento"] = port_summary.apply(
        lambda r: (r["Total Gross"] / r["FY26 PPs"] * 100.0) if r["FY26 PPs"] > 0 else 0.0,
        axis=1,
    )
    port_summary = port_summary.sort_values(by="% Atingimento", ascending=False).head(15)

    # Cores dinâmicas por faixa de atingimento
    colors = [
        "#10B981" if val >= 100 else ("#F59E0B" if val >= 80 else "#EF4444")
        for val in port_summary["% Atingimento"]
    ]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=port_summary["Portfolio"],
            y=port_summary["% Atingimento"],
            marker=dict(color=colors),
            customdata=port_summary[["Business Unit", "Total Gross", "FY26 PPs"]],
            hovertemplate=(
                "<b>%{x}</b> (%{customdata[0]})<br>"
                "Atingimento: %{y:.2f}%<br>"
                "Realizado: R$ %{customdata[1]:,.2f}<br>"
                "Meta: R$ %{customdata[2]:,.2f}<extra></extra>"
            ),
        )
    )

    # Linha de Meta (100%)
    fig.add_shape(
        type="line",
        x0=-0.5,
        x1=len(port_summary) - 0.5,
        y0=100,
        y1=100,
        line=dict(color="#1F4E78", width=2, dash="dash"),
    )
    fig.add_annotation(
        x=len(port_summary) - 1,
        y=100,
        text="Meta (100%)",
        showarrow=False,
        yshift=12,
        font=dict(color="#1F4E78", size=11, family="Segoe UI"),
    )

    fig.update_layout(
        title=dict(text="<b>Top Portfólios por % de Atingimento</b>", font=dict(size=16, color="#1E293B")),
        height=380,
        margin=dict(l=20, r=20, t=50, b=50),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        xaxis=dict(title=None, tickangle=-30),
        yaxis=dict(title="% Atingimento", gridcolor="#F1F5F9", ticksuffix="%"),
    )

    st.plotly_chart(fig, use_container_width=True)


def render_sales_composition_chart(df: pd.DataFrame) -> None:
    """Gráfico de barras empilhadas: Faturamento Realizado (Billed) vs Em Aberto (Open) por BU."""
    if df.empty:
        return

    bu_sales = df.groupby("Business Unit", as_index=False).agg(
        {
            "Gross Sales Billed": "sum",
            "Gross Sales Open": "sum",
        }
    )

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            name="Faturado (Billed)",
            x=bu_sales["Business Unit"],
            y=bu_sales["Gross Sales Billed"],
            marker_color="#1F4E78",
            hovertemplate="<b>%{x}</b><br>Faturado: R$ %{y:,.2f}<extra></extra>",
        )
    )

    fig.add_trace(
        go.Bar(
            name="Em Aberto (Open)",
            x=bu_sales["Business Unit"],
            y=bu_sales["Gross Sales Open"],
            marker_color="#00A896",
            hovertemplate="<b>%{x}</b><br>Em Aberto: R$ %{y:,.2f}<extra></extra>",
        )
    )

    fig.update_layout(
        title=dict(text="<b>Composição de Vendas: Faturado vs Em Aberto</b>", font=dict(size=16, color="#1E293B")),
        barmode="stack",
        height=380,
        margin=dict(l=20, r=20, t=50, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        xaxis=dict(title=None),
        yaxis=dict(title="Valor (R$)", gridcolor="#F1F5F9", tickprefix="R$ "),
    )

    st.plotly_chart(fig, use_container_width=True)
