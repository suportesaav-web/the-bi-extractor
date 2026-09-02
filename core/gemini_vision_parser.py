"""Motor de Extração Inteligente de Matrizes e Tabelas via Google GenAI (Gemini Vision) - Modo Híbrido."""

from __future__ import annotations

import io
import json
import os
import re
import time
from typing import Any, Dict, List, Optional, Union

from google import genai
from google.genai import types
import pandas as pd
from PIL import Image

from pathlib import Path

# Chaves antigas/revogadas que devem ser ignoradas automaticamente
REVOKED_KEYS = {
    "AQ.Ab8RN6LV7L0YNvB5VyjWvileuaJrfeLm5SLmmX8Mn34PCioi7w",
}

def get_default_api_key() -> str:
    """Obtém a chave de API ativa do Streamlit Secrets (Cloud), arquivo .env local ou variáveis de ambiente."""
    # 1. Tenta obter de st.secrets (Streamlit Community Cloud)
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            sec_val = str(st.secrets["GEMINI_API_KEY"]).strip()
            if sec_val and sec_val not in REVOKED_KEYS:
                return sec_val
    except Exception:
        pass

    # 2. Prioriza o arquivo .env local
    env_file = Path(__file__).resolve().parent.parent / ".env"
    if env_file.exists():
        try:
            for line in env_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("GEMINI_API_KEY="):
                    val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if val and val not in REVOKED_KEYS:
                        return val
        except Exception:
            pass

    # 3. Variável de ambiente (se válida e não revogada)
    key = os.environ.get("GEMINI_API_KEY", "")
    if key and key not in REVOKED_KEYS:
        return key

    return ""

HYBRID_EXTRACTION_PROMPT = """
Você é um Engenheiro de Dados especialista em Visão Computacional, Análise de Documentos e Extração Tabular.
Analise a imagem ou documento PDF fornecido minuciosamente.

Seu objetivo é:
1. Detectar se o arquivo contém alguma tabela, matriz (como Power BI, Excel, grade com linhas e colunas, extrato ou relatório tabular).
2. Se NÃO houver nenhuma tabela ou dados estruturados em linhas/colunas, retorne:
{
  "has_table": false,
  "message": "Nenhuma tabela ou matriz de dados visível foi identificada neste arquivo. Por favor, envie uma captura ou documento que contenha uma tabela ou planilha legível."
}

3. Se HOUVER tabela, identifique se ela é uma matriz do Power BI / Saavedra ou uma tabela genérica:

CENÁRIO A - Matriz Power BI (Saavedra / Vendas / Metas):
Critérios: Contém hierarquias como Customer Group (SAAVEDRA), Business Unit / BU (ex: MDS, PI, UCC), Portfólio / Produtos, e métricas como Metas (FY26 PPs), Faturamento (Gross Sales Billed), Carteira (Gross Sales Open), Total Gross, Atingimento, etc.
Para este caso, extraia APENAS as linhas de detalhe de portfólio (sem linhas de subtotais ou total geral):
{
  "has_table": true,
  "table_type": "powerbi_matrix",
  "records": [
    {
      "Customer Group": "SAAVEDRA",
      "Business Unit": "MDS",
      "Portfolio": "AAD",
      "FY26 PPs": 1296106.18,
      "Gross Sales Billed": 1457244.35,
      "Gross Sales Open": 9086.82,
      "Total Gross": 1466331.17,
      "Ating PPs": 170224.99,
      "% PPs": 1.1313
    }
  ]
}

CENÁRIO B - Qualquer Outra Tabela (Tabela Genérica):
Critérios: Qualquer outra tabela (financeira, estoque, vendas, lista de clientes, notas, faturas, relatórios) que não seja a matriz específica Saavedra Power BI.
Para este caso, extraia TODOS os cabeçalhos de colunas e TODAS as linhas visíveis:
{
  "has_table": true,
  "table_type": "generic_table",
  "table_title": "Título descritivo da tabela (se houver)",
  "columns": ["Coluna 1", "Coluna 2", "Coluna 3"],
  "records": [
    {
      "Coluna 1": "Valor Linha 1",
      "Coluna 2": 150.00,
      "Coluna 3": "Ativo"
    }
  ]
}

IMPORTANTE:
- Converta valores numéricos e monetários para float numérico puro (ex: 1500.50 em vez de "R$ 1.500,50").
- Preserve acentuação e nomes exatos.
- Retorne APENAS um JSON válido estrito, sem textos explicativos fora do bloco JSON.
"""


def pdf_to_preview_images(
    pdf_input: Union[bytes, io.BytesIO, str, Any],
    max_pages: int = 3,
) -> List[Image.Image]:
    """Renderiza as primeiras páginas de um arquivo PDF como imagens PIL para exibição na interface."""
    try:
        import pypdfium2 as pdfium

        if isinstance(pdf_input, io.BytesIO):
            data = pdf_input.getvalue()
        elif isinstance(pdf_input, bytes):
            data = pdf_input
        elif isinstance(pdf_input, str):
            with open(pdf_input, "rb") as f:
                data = f.read()
        elif hasattr(pdf_input, "getvalue"):
            data = pdf_input.getvalue()
        elif hasattr(pdf_input, "read"):
            pos = pdf_input.tell() if hasattr(pdf_input, "tell") else 0
            data = pdf_input.read()
            if hasattr(pdf_input, "seek"):
                pdf_input.seek(pos)
        else:
            return []

        doc = pdfium.PdfDocument(data)
        num_pages = min(len(doc), max_pages)
        images: List[Image.Image] = []
        for i in range(num_pages):
            page = doc[i]
            pil_image = page.render(scale=2).to_pil()
            images.append(pil_image)
        return images
    except Exception:
        return []


def extract_matrix_with_gemini(
    file_input: Union[bytes, io.BytesIO, str, Image.Image, Any],
    api_key: Optional[str] = None,
    filename: Optional[str] = None,
) -> pd.DataFrame:
    """Extrai os dados da imagem ou PDF em Modo Híbrido usando a API multimodal do Google Gemini.
    
    Identifica automaticamente se o arquivo possui:
    - Nenhuma tabela (avisa o usuário amigavelmente).
    - Matriz Power BI Saavedra (formato enriquecido com KPIs, BUs e Looker Studio).
    - Tabela genérica (extrai colunas e linhas dinamicamente para exibição e download em Excel/CSV).
    """
    key = api_key if (api_key and api_key not in REVOKED_KEYS) else None
    if not key:
        key = get_default_api_key()
    if not key:
        raise ValueError("Chave de API do Gemini não configurada ou inválida.")

    # 1. Identificar formato (PDF vs Imagem) e preparar conteúdo multimodal
    contents_to_send = []

    name_hint = (filename or getattr(file_input, "name", "") or (file_input if isinstance(file_input, str) else "")).lower()

    if isinstance(file_input, Image.Image):
        contents_to_send = [file_input, HYBRID_EXTRACTION_PROMPT]
    else:
        # Obter bytes
        if isinstance(file_input, (bytes, io.BytesIO)):
            raw_bytes = file_input.getvalue() if isinstance(file_input, io.BytesIO) else file_input
        elif isinstance(file_input, str):
            with open(file_input, "rb") as f:
                raw_bytes = f.read()
        elif hasattr(file_input, "getvalue"):
            raw_bytes = file_input.getvalue()
        elif hasattr(file_input, "read"):
            pos = file_input.tell() if hasattr(file_input, "tell") else 0
            raw_bytes = file_input.read()
            if hasattr(file_input, "seek"):
                file_input.seek(pos)
        else:
            raise ValueError("Formato de arquivo de entrada não suportado.")

        # Verificar se é PDF (assinatura mágica %PDF ou extensão)
        is_pdf = raw_bytes.startswith(b"%PDF") or name_hint.endswith(".pdf")

        if is_pdf:
            pdf_part = types.Part.from_bytes(data=raw_bytes, mime_type="application/pdf")
            contents_to_send = [pdf_part, HYBRID_EXTRACTION_PROMPT]
        else:
            # Imagem normal (PNG, JPG, etc.)
            pil_img = Image.open(io.BytesIO(raw_bytes))
            contents_to_send = [pil_img, HYBRID_EXTRACTION_PROMPT]

    # 2. Inicializar cliente oficial do Google GenAI
    client = genai.Client(api_key=key)

    response = None
    last_error = None

    # Modelos oficiais em ordem de resiliência e performance
    CANDIDATE_MODELS = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-2.5-pro",
        "gemini-1.5-pro",
        "gemini-flash-latest",
    ]

    for model_name in CANDIDATE_MODELS:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=contents_to_send,
                    config=types.GenerateContentConfig(response_mime_type="application/json"),
                )
                if response and response.text:
                    break
            except Exception as err:
                last_error = err
                err_str = str(err).lower()
                # Em caso de pico de demanda (503) ou rate limit (429), pausa brevemente antes do próximo teste
                if any(code in err_str for code in ["503", "unavailable", "high demand", "429", "resource_exhausted"]):
                    time.sleep(1.5)
                    continue
                # Se o modelo não estiver disponível no endpoint (404/not found), passa para o próximo candidato
                if "not_found" in err_str or "not found" in err_str or "404" in err_str:
                    break
        if response and response.text:
            break

    if not response or not response.text:
        err_str = str(last_error) if last_error else ""
        if "503" in err_str or "high demand" in err_str.lower() or "unavailable" in err_str.lower():
            raise RuntimeError(
                "Os servidores do Google Gemini estão enfrentando alta demanda temporária (Erro 503). "
                "O sistema tentou os modelos de contingência automaticamente. Por favor, aguarde alguns segundos e tente novamente."
            )
        err_msg = f"Falha ao processar arquivo com Gemini Vision: {last_error}" if last_error else "Resposta vazia do modelo."
        raise RuntimeError(err_msg)

    # 3. Decodificar JSON
    clean_json = re.sub(r"^```json\s*", "", response.text.strip())
    clean_json = re.sub(r"\s*```$", "", clean_json.strip())

    try:
        parsed = json.loads(clean_json)
    except Exception as e:
        raise ValueError(f"A IA não retornou um JSON válido: {e}. Resposta: {clean_json[:200]}")

    # Verificar se foi identificada tabela
    has_table = parsed.get("has_table", True)
    if not has_table:
        msg = parsed.get(
            "message",
            "Nenhuma tabela foi identificada nesta imagem. Certifique-se de que a imagem contém uma tabela ou planilha legível.",
        )
        raise ValueError(msg)

    table_type = parsed.get("table_type", "powerbi_matrix")
    records = parsed.get("records", [])

    if not isinstance(records, list) or len(records) == 0:
        raise ValueError("Nenhum registro tabular foi encontrado na imagem.")

    # CASO A: Matriz Power BI Saavedra
    if table_type == "powerbi_matrix":
        df = pd.DataFrame(records)

        for col in ["Customer Group", "Business Unit", "Portfolio"]:
            if col not in df.columns:
                df[col] = "Geral"

        for col in ["FY26 PPs", "Gross Sales Billed", "Gross Sales Open"]:
            if col not in df.columns:
                df[col] = 0.0
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

        # Reconciliação Matemática
        df["Total Gross"] = df["Gross Sales Billed"] + df["Gross Sales Open"]
        df["Ating PPs"] = df["Total Gross"] - df["FY26 PPs"]
        df["% PPs"] = df.apply(
            lambda r: (r["Total Gross"] / r["FY26 PPs"]) if r["FY26 PPs"] > 0 else 0.0,
            axis=1,
        )

        target_columns = [
            "Customer Group",
            "Business Unit",
            "Portfolio",
            "FY26 PPs",
            "Gross Sales Billed",
            "Gross Sales Open",
            "Total Gross",
            "Ating PPs",
            "% PPs",
        ]
        final_df = df[target_columns].reset_index(drop=True)
        final_df.attrs["is_powerbi"] = True
        final_df.attrs["table_type"] = "powerbi_matrix"
        final_df.attrs["table_title"] = "Matriz Power BI Saavedra"
        return final_df

    # CASO B: Tabela Genérica
    df_generic = pd.DataFrame(records)
    # Ordenar colunas conforme especificado pelo Gemini se fornecido
    columns_order = parsed.get("columns")
    if columns_order and isinstance(columns_order, list):
        existing_cols = [c for c in columns_order if c in df_generic.columns]
        other_cols = [c for c in df_generic.columns if c not in existing_cols]
        df_generic = df_generic[existing_cols + other_cols]

    # Converter colunas numéricas de strings para float quando possível
    for col in df_generic.columns:
        try:
            df_generic[col] = pd.to_numeric(df_generic[col])
        except (ValueError, TypeError):
            pass

    df_generic.attrs["is_powerbi"] = False
    df_generic.attrs["table_type"] = "generic_table"
    df_generic.attrs["table_title"] = parsed.get("table_title", "Tabela Genérica Extraída")
    return df_generic
