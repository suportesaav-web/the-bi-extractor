"""Motor de Extração Inteligente de Matrizes e Tabelas via Google GenAI (Gemini Vision) - Modo Híbrido."""

from __future__ import annotations

import io
import json
import os
import re
from typing import Any, Dict, List, Optional, Union

from google import genai
from google.genai import types
import pandas as pd
from PIL import Image

from pathlib import Path

import time

# Chaves antigas/revogadas que devem ser ignoradas automaticamente
REVOKED_KEYS = {
    "AQ.Ab8RN6LV7L0YNvB5VyjWvileuaJrfeLm5SLmmX8Mn34PCioi7w",
}

def get_available_api_keys() -> List[str]:
    """Retorna a lista de chaves de API disponíveis e válidas (primária e backup)."""
    keys: List[str] = []

    # 1. Tenta obter de st.secrets (Streamlit Community Cloud)
    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            for sec_name in ["GEMINI_API_KEY", "GEMINI_API_KEY_BACKUP"]:
                if sec_name in st.secrets:
                    val = str(st.secrets[sec_name]).strip()
                    if val and val not in REVOKED_KEYS and val not in keys:
                        keys.append(val)
    except Exception:
        pass

    # 2. Prioriza o arquivo .env local
    env_file = Path(__file__).resolve().parent.parent / ".env"
    if env_file.exists():
        try:
            for line in env_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                for prefix in ["GEMINI_API_KEY=", "GEMINI_API_KEY_BACKUP="]:
                    if line.startswith(prefix):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if val and val not in REVOKED_KEYS and val not in keys:
                            keys.append(val)
        except Exception:
            pass

    # 3. Variáveis de ambiente
    for env_var in ["GEMINI_API_KEY", "GEMINI_API_KEY_BACKUP"]:
        val = os.environ.get(env_var, "").strip()
        if val and val not in REVOKED_KEYS and val not in keys:
            keys.append(val)

    return keys


def get_default_api_key() -> str:
    """Obtém a chave de API padrão (ou primeira válida disponível)."""
    keys = get_available_api_keys()
    return keys[0] if keys else ""

HYBRID_EXTRACTION_PROMPT = """
Você é um Engenheiro de Dados especialista em Visão Computacional, Análise de Documentos e Extração Tabular.
Analise a imagem fornecida minuciosamente.

Seu objetivo é:
1. Detectar se a imagem contém alguma tabela, matriz (como Power BI, Excel, grade com linhas e colunas, extrato ou relatório tabular).
2. Se NÃO houver nenhuma tabela ou dados estruturados em linhas/colunas, retorne:
{
  "has_table": false,
  "message": "Nenhuma tabela ou matriz de dados visível foi identificada nesta imagem. Por favor, envie uma captura que contenha uma tabela ou planilha legível."
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
Critérios: Qualquer outra tabela (financeira, estoque, vendas, lista de clientes, notas, faturas, etc.) que não seja a matriz específica Saavedra Power BI.
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


def extract_matrix_with_gemini(
    image_input: Union[bytes, io.BytesIO, str, Image.Image],
    api_key: Optional[str] = None,
) -> pd.DataFrame:
    """Extrai os dados da imagem em Modo Híbrido usando a API multimodal do Google Gemini.
    
    Identifica automaticamente se a imagem possui:
    - Nenhuma tabela (avisa o usuário amigavelmente).
    - Matriz Power BI Saavedra (formato enriquecido com KPIs, BUs e Looker Studio).
    - Tabela genérica (extrai colunas e linhas dinamicamente para exibição e download em Excel/CSV).
    """
    candidate_keys: List[str] = []
    if api_key and api_key.strip() not in REVOKED_KEYS:
        candidate_keys.append(api_key.strip())
    for k in get_available_api_keys():
        if k not in candidate_keys:
            candidate_keys.append(k)

    if not candidate_keys:
        raise ValueError("Chave de API do Gemini não configurada ou inválida.")

    # 1. Carregar imagem no PIL
    if isinstance(image_input, Image.Image):
        pil_img = image_input
    elif isinstance(image_input, (bytes, io.BytesIO)):
        data_bytes = image_input.getvalue() if isinstance(image_input, io.BytesIO) else image_input
        pil_img = Image.open(io.BytesIO(data_bytes))
    elif isinstance(image_input, str):
        pil_img = Image.open(image_input)
    else:
        raise ValueError("Formato de imagem não suportado.")

    # 2. Execução resiliente com fallback de chaves e modelos
    candidate_models = ["gemini-3.6-flash", "gemini-flash-latest", "gemini-flash-lite-latest", "gemini-2.5-flash-lite"]
    response = None
    last_error = None

    for active_key in candidate_keys:
        try:
            client = genai.Client(api_key=active_key)
        except Exception as client_err:
            last_error = client_err
            continue

        for model_name in candidate_models:
            for attempt in range(2):
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=[pil_img, HYBRID_EXTRACTION_PROMPT],
                        config=types.GenerateContentConfig(response_mime_type="application/json"),
                    )
                    if response and response.text:
                        break
                except Exception as err:
                    last_error = err
                    err_str = str(err).lower()
                    # Se for erro temporário de alta demanda (503) ou cota (429), aguarda antes de tentar outro
                    if "503" in err_str or "demand" in err_str or "429" in err_str:
                        time.sleep(1.0)
                    else:
                        break
            if response and response.text:
                break
        if response and response.text:
            break

    if not response or not response.text:
        err_msg = f"Falha ao processar imagem com Gemini Vision: {last_error}" if last_error else "Resposta vazia do modelo."
        raise RuntimeError(err_msg)

    # 3. Decodificar JSON de forma robusta
    raw_text = response.text.strip()
    clean_json = re.sub(r"^```(?:json)?\s*", "", raw_text, flags=re.IGNORECASE)
    clean_json = re.sub(r"\s*```$", "", clean_json.strip())

    try:
        parsed = json.loads(clean_json)
    except Exception:
        # Tenta extrair o bloco JSON mais externo se houver texto ao redor
        match = re.search(r"(\{[\s\S]*\})", raw_text)
        if match:
            try:
                parsed = json.loads(match.group(1))
            except Exception as e:
                raise ValueError(f"A IA não retornou um JSON válido: {e}. Resposta: {raw_text[:200]}")
        else:
            raise ValueError(f"A IA não retornou um JSON válido. Resposta: {raw_text[:200]}")


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
