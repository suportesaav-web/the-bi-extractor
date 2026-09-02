"""Motor de Extração Inteligente de Matrizes Power BI via Google GenAI (Gemini Vision)."""

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

DEFAULT_API_KEY = os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6LV7L0YNvB5VyjWvileuaJrfeLm5SLmmX8Mn34PCioi7w")

EXTRACTION_PROMPT = """
Você é um Engenheiro de Dados especialista em extrair e normalizar matrizes hierárquicas e tabelas financeiras do Power BI.
Analise a imagem da matriz fornecida com precisão cirúrgica.

Regras de Extração:
1. Extraia cada linha de detalhe de produto / portfólio.
2. Identifique a hierarquia de cada linha:
   - "Customer Group": Grupo cliente de nível superior (ex: "SAAVEDRA").
   - "Business Unit": Sigla da unidade de negócio correspondente (ex: "MDS", "PI", "UCC", etc.).
   - "Portfolio": Nome exato do portfólio / produto (ex: "AAD", "Bone", "Chronic CVC Catheters", "Ports", "Dignishield", etc.).
3. Extraia todos os valores numéricos como números decimais puros (float):
   - "FY26 PPs": Meta financeira (ex: 12000.00). Se vazio/traço, retorne 0.0.
   - "Gross Sales Billed": Faturamento Realizado (ex: 2880.24). Se vazio, retorne 0.0.
   - "Gross Sales Open": Vendas em Carteira/Aberto (ex: 9086.82). Se vazio, retorne 0.0.
   - "Total Gross": Total Faturado + Aberto (ex: 1466331.17).
   - "Ating PPs": Gap em relação à meta (ex: 170224.99).
   - "% PPs": Percentual de atingimento em decimal (ex: 1.1313 para 113.13%, 0.24 para 24.00%).

4. Não inclua as linhas de Subtotal intermediárias de BU ou a linha de "Total Geral" nos records (elas serão recalculadas programaticamente).

Retorne APENAS um JSON estrito no seguinte formato:
{
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
"""


def extract_matrix_with_gemini(
    image_input: Union[bytes, io.BytesIO, str, Image.Image],
    api_key: Optional[str] = None,
) -> pd.DataFrame:
    """Extrai os dados da matriz do Power BI usando a API multimodal do Google Gemini com o SDK oficial google-genai."""
    key = api_key or DEFAULT_API_KEY
    if not key:
        raise ValueError("Chave de API do Gemini não configurada.")

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

    # 2. Inicializar cliente oficial do Google GenAI
    client = genai.Client(api_key=key)

    response = None
    for model_name in ["gemini-3.6-flash", "gemini-flash-latest", "gemini-2.5-flash"]:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=[pil_img, EXTRACTION_PROMPT],
                config=types.GenerateContentConfig(response_mime_type="application/json"),
            )
            if response and response.text:
                break
        except Exception:
            continue

    if not response or not response.text:
        raise RuntimeError("Não foi possível obter resposta estruturada do Gemini Vision.")

    # 3. Decodificar JSON
    clean_json = re.sub(r"^```json\s*", "", response.text.strip())
    clean_json = re.sub(r"\s*```$", "", clean_json.strip())

    parsed = json.loads(clean_json)
    records = parsed.get("records", parsed) if isinstance(parsed, dict) else parsed

    if not isinstance(records, list) or len(records) == 0:
        raise ValueError("Nenhum registro foi encontrado na resposta do Gemini.")

    # 4. Converter em DataFrame e garantir integridade
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
        lambda r: (r["Total Gross"] / r["FY26 PPs"]) if r["FY26 PPs"] > 0 else 0.0, axis=1
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
    return df[target_columns].reset_index(drop=True)
