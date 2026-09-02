"""Motor de higienização, desmembramento hierárquico e tipagem de dados do Power BI."""

from __future__ import annotations

import io
import re
from typing import Any, BinaryIO, Dict, List, Optional, Tuple, Union

import pandas as pd

from core.gemini_vision_parser import extract_matrix_with_gemini
from core.image_parser import parse_image_matrix


def clean_hierarchy_string(val: Any) -> str:
    """Remove símbolos visuais de matriz do Power BI (└, ├, ─, etc.), recuos e espaços extras."""
    if pd.isna(val) or val is None:
        return ""
    text = str(val).strip()
    # Remove caracteres de árvore/hierarquia do Power BI e caracteres unicode especiais
    text = re.sub(r"^[└├─\s\-\|\+\>\•\*]+", "", text)
    text = re.sub(r"[\t\r\n]+", " ", text)
    # Remove espaços duplos
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_numeric_value(val: Any) -> float:
    """Converte valores brutos (strings formatadas, moedas, percentuais) para float de forma defensiva."""
    if pd.isna(val) or val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)

    text = str(val).strip()
    if not text or text.lower() in ("nan", "none", "null", "-", "—", "n/a", ""):
        return 0.0

    # Identifica se é negativo com parênteses ex: (1,234.56) ou com sinal -
    is_negative = False
    if text.startswith("(") and text.endswith(")"):
        is_negative = True
        text = text[1:-1].strip()
    elif text.startswith("-"):
        is_negative = True
        text = text[1:].strip()

    # Trata porcentagem
    is_percent = "%" in text

    # Remove símbolos de moeda e caracteres não numéricos exceto separadores
    text = re.sub(r"[^\d.,]", "", text)
    if not text:
        return 0.0

    # Trata separadores decimais e de milhar
    # Casos:
    # 1.234.567,89 (BR) -> 1234567.89
    # 1,234,567.89 (US) -> 1234567.89
    # 1234,56 (BR) -> 1234.56
    # 1234.56 (US) -> 1234.56
    if "," in text and "." in text:
        last_comma = text.rfind(",")
        last_dot = text.rfind(".")
        if last_comma > last_dot:
            # Formato Brasileiro / Europeu: 1.234,56
            text = text.replace(".", "").replace(",", ".")
        else:
            # Formato Americano: 1,234.56
            text = text.replace(",", "")
    elif "," in text:
        # Apenas vírgula: se tiver múltiplos dígitos após a vírgula (ex: 2 dígitos decimais)
        parts = text.split(",")
        if len(parts) == 2 and len(parts[1]) <= 2:
            text = text.replace(",", ".")
        elif len(parts) == 2 and len(parts[1]) == 3 and int(parts[0]) > 0:
            # Pode ser milhar sem decimal ex: 1,234 -> 1234
            # Porém em matrizes BR geralmente vírgula é decimal
            text = text.replace(",", ".")
        else:
            text = text.replace(",", "")
    elif "." in text:
        # Apenas ponto
        parts = text.split(".")
        if len(parts) == 2 and len(parts[1]) <= 2:
            # Decimal padrão americano
            pass
        elif len(parts) > 2:
            # Múltiplos pontos = separador de milhar BR: 1.234.567
            text = text.replace(".", "")

    try:
        num = float(text)
        if is_percent:
            num = num / 100.0 if num > 1.0 else num
        return -num if is_negative else num
    except (ValueError, TypeError):
        return 0.0


def identify_columns(df: pd.DataFrame) -> Dict[str, Optional[str]]:
    """Identifica dinamicamente as colunas no DataFrame exportado."""
    mapping: Dict[str, Optional[str]] = {
        "customer_group": None,
        "business_unit": None,
        "portfolio": None,
        "hierarchy_col": None,
        "fy26_pps": None,
        "gross_sales_billed": None,
        "gross_sales_open": None,
        "total_gross": None,
        "ating_pps": None,
        "perc_pps": None,
    }

    cols = list(df.columns)
    for col in cols:
        col_clean = str(col).strip().lower()
        col_clean_norm = re.sub(r"[\s_\-\.]+", " ", col_clean)

        # Hierarquias
        if "customer group" in col_clean_norm or "grupo" in col_clean_norm or "cliente" in col_clean_norm:
            mapping["customer_group"] = str(col)
        elif "business unit" in col_clean_norm or col_clean_norm in ("bu", "unidade de negócio", "unidade de negocio"):
            mapping["business_unit"] = str(col)
        elif "portfolio" in col_clean_norm or "portfólio" in col_clean_norm or "produto" in col_clean_norm:
            mapping["portfolio"] = str(col)
        elif any(term in col_clean_norm for term in ["hierarquia", "estrutura", "segmento", "linha"]):
            mapping["hierarchy_col"] = str(col)

        # Métricas
        if any(term in col_clean_norm for term in ["fy26", "fy 26", "meta pps", "meta", "target"]):
            if "ating" not in col_clean_norm and "%" not in col_clean_norm:
                mapping["fy26_pps"] = str(col)
        elif any(term in col_clean_norm for term in ["billed", "faturado", "faturamento", "gross sales billed"]):
            mapping["gross_sales_billed"] = str(col)
        elif any(term in col_clean_norm for term in ["open", "aberto", "em aberto", "gross sales open", "carteira"]):
            mapping["gross_sales_open"] = str(col)
        elif any(term in col_clean_norm for term in ["total gross", "gross total", "venda total", "total faturado + aberto"]):
            mapping["total_gross"] = str(col)
        elif any(term in col_clean_norm for term in ["ating pps", "atingimento pps", "ating.", "gap pps", "gap meta", "atingimento r$"]):
            mapping["ating_pps"] = str(col)
        elif any(term in col_clean_norm for term in ["% pps", "% ating", "% atingimento", "% meta", "atingimento %"]):
            mapping["perc_pps"] = str(col)

    # Se não encontrou coluna de hierarquia específica, verifica a primeira coluna de texto
    if not mapping["customer_group"] and not mapping["business_unit"] and not mapping["portfolio"]:
        if len(cols) > 0:
            mapping["hierarchy_col"] = str(cols[0])

    return mapping


def unpack_hierarchy(df: pd.DataFrame, col_name: str) -> pd.DataFrame:
    """Desmembra uma coluna hierárquica do Power BI em Customer Group, Business Unit e Portfolio.
    
    Analisa os recuos e prefixos de hierarquia como '└' para rastrear níveis em cascata:
    Nível 0: Customer Group (ex: SAAVEDRA)
    Nível 1: Business Unit (ex: MDS, PI, UCC)
    Nível 2: Portfolio (ex: Bone, Ports, Chronic Dialysis, AAD)
    """
    records: List[Dict[str, Any]] = []
    current_customer_group = "SAAVEDRA"
    current_bu = "Geral"

    for idx, row in df.iterrows():
        raw_val = row[col_name]
        if pd.isna(raw_val):
            continue

        raw_str = str(raw_val)
        clean_text = clean_hierarchy_string(raw_str)
        if not clean_text:
            continue

        # Ignorar linhas de Total / Subtotal gerais
        lower_clean = clean_text.lower()
        if lower_clean in ("total", "total geral", "grand total", "subtotal"):
            continue

        # Detectar nível de indentação e símbolos
        has_symbol = bool(re.search(r"[└├─\-\>\•]", raw_str))
        leading_spaces = len(raw_str) - len(raw_str.lstrip())

        # Análise do nível
        # Nível 0: Sem símbolos e sem espaços (ex: SAAVEDRA)
        if not has_symbol and leading_spaces < 2:
            current_customer_group = clean_text
            continue

        # Nível 1: Business Unit (ex: MDS, PI, UCC ou 1 símbolo)
        # Se o texto for curto ou se for uma sigla conhecida ou primeiro nível de indentação
        if (has_symbol and leading_spaces < 4) or (clean_text in ["MDS", "PI", "UCC", "DIABETES", "VASCULAR", "CIRURGICO"]):
            current_bu = clean_text
            # Se for linha de consolidado da BU com valores
            portfolio_item = f"Consolidado {current_bu}"
        else:
            # Nível 2: Portfolio específico
            portfolio_item = clean_text

        row_dict = row.to_dict()
        row_dict["Customer Group"] = current_customer_group
        row_dict["Business Unit"] = current_bu
        row_dict["Portfolio"] = portfolio_item
        records.append(row_dict)

    return pd.DataFrame(records)


def parse_raw_data(
    file_input: Union[BinaryIO, io.BytesIO, str, pd.DataFrame],
    api_key: Optional[str] = None,
) -> pd.DataFrame:
    """Realiza o parsing, higienização, tipagem e normalização completa dos dados do Power BI.
    
    Suporta DataFrames, arquivos Excel (.xlsx, .xls), CSV (.csv) e imagens com OCR (.png, .jpg, .jpeg).
    """
    # 1. Se for DataFrame
    if isinstance(file_input, pd.DataFrame):
        df_raw = file_input.copy()
    else:
        # Verificar se é arquivo de imagem
        file_name = getattr(file_input, "name", "")
        if isinstance(file_input, str):
            file_name = file_input

        file_name_lower = str(file_name).lower()
        if any(file_name_lower.endswith(ext) for ext in [".png", ".jpg", ".jpeg"]):
            try:
                return extract_matrix_with_gemini(file_input, api_key=api_key)
            except Exception as e:
                try:
                    from core.image_parser import WINSDK_AVAILABLE
                    if WINSDK_AVAILABLE and "Nenhuma tabela" not in str(e):
                        if hasattr(file_input, "seek"):
                            file_input.seek(0)
                        return parse_image_matrix(file_input)
                except Exception:
                    pass
                raise e

        # Determinar se é CSV ou Excel
        try:
            if file_name_lower.endswith(".csv"):
                try:
                    df_raw = pd.read_csv(file_input, sep=None, engine="python", encoding="utf-8")
                except Exception:
                    if hasattr(file_input, "seek"):
                        file_input.seek(0)
                    df_raw = pd.read_csv(file_input, sep=";", encoding="latin1")
            else:
                df_raw = pd.read_excel(file_input)
        except Exception:
            if hasattr(file_input, "seek"):
                file_input.seek(0)
            df_raw = pd.read_csv(file_input, sep=";", encoding="utf-8-sig")

    if df_raw.empty:
        raise ValueError("O arquivo fornecido está vazio ou não possui registros válidos.")

    # 2. Identificar Colunas
    mapping = identify_columns(df_raw)

    # 3. Desmembrar Hierarquia se necessário
    if mapping["hierarchy_col"] and (not mapping["business_unit"] or not mapping["portfolio"]):
        df_processed = unpack_hierarchy(df_raw, mapping["hierarchy_col"])
    else:
        df_processed = df_raw.copy()
        if "Customer Group" not in df_processed.columns:
            if mapping["customer_group"]:
                df_processed["Customer Group"] = df_processed[mapping["customer_group"]].apply(clean_hierarchy_string)
            else:
                df_processed["Customer Group"] = "SAAVEDRA"

        if "Business Unit" not in df_processed.columns:
            if mapping["business_unit"]:
                df_processed["Business Unit"] = df_processed[mapping["business_unit"]].apply(clean_hierarchy_string)
            else:
                df_processed["Business Unit"] = "Geral"

        if "Portfolio" not in df_processed.columns:
            if mapping["portfolio"]:
                df_processed["Portfolio"] = df_processed[mapping["portfolio"]].apply(clean_hierarchy_string)
            else:
                df_processed["Portfolio"] = "Consolidado"

    if df_processed.empty:
        raise ValueError("Não foi possível extrair linhas de dados válidas da matriz hierárquica.")

    # 4. Extrair e Tratar Campos Numéricos
    fy26_col = mapping["fy26_pps"]
    billed_col = mapping["gross_sales_billed"]
    open_col = mapping["gross_sales_open"]
    total_col = mapping["total_gross"]
    ating_col = mapping["ating_pps"]

    df_clean = pd.DataFrame()
    df_clean["Customer Group"] = df_processed["Customer Group"].astype(str).replace("", "SAAVEDRA")
    df_clean["Business Unit"] = df_processed["Business Unit"].astype(str).replace("", "Geral")
    df_clean["Portfolio"] = df_processed["Portfolio"].astype(str).replace("", "Geral")

    # Higienizar e extrair números
    df_clean["FY26 PPs"] = df_processed[fy26_col].apply(parse_numeric_value) if fy26_col and fy26_col in df_processed.columns else 0.0
    df_clean["Gross Sales Billed"] = df_processed[billed_col].apply(parse_numeric_value) if billed_col and billed_col in df_processed.columns else 0.0
    df_clean["Gross Sales Open"] = df_processed[open_col].apply(parse_numeric_value) if open_col and open_col in df_processed.columns else 0.0

    # 5. Cálculos Dinâmicos de Negócio Garantidos
    # Total Gross = Billed + Open
    df_clean["Total Gross"] = df_clean["Gross Sales Billed"] + df_clean["Gross Sales Open"]

    # Se Billed e Open eram 0 mas Total Gross veio no arquivo, usa o total bruto existente
    if (df_clean["Total Gross"] == 0).all() and total_col and total_col in df_processed.columns:
        df_clean["Total Gross"] = df_processed[total_col].apply(parse_numeric_value)

    # Ating PPs = Total Gross - FY26 PPs
    df_clean["Ating PPs"] = df_clean["Total Gross"] - df_clean["FY26 PPs"]

    # % PPs = Total Gross / FY26 PPs (onde FY26 PPs > 0)
    df_clean["% PPs"] = df_clean.apply(
        lambda r: (r["Total Gross"] / r["FY26 PPs"]) if r["FY26 PPs"] > 0 else 0.0,
        axis=1,
    )

    # 6. Limpeza final de registros inconsistentes
    # Remove linhas onde todos os valores monetários são zero ou vazios
    df_clean = df_clean[
        ~((df_clean["FY26 PPs"] == 0) & (df_clean["Gross Sales Billed"] == 0) & (df_clean["Gross Sales Open"] == 0) & (df_clean["Total Gross"] == 0))
    ].copy()

    # Remove possíveis linhas duplicadas
    df_clean = df_clean.drop_duplicates(subset=["Customer Group", "Business Unit", "Portfolio"])
    df_clean = df_clean.reset_index(drop=True)

    # Reordenar colunas finais para o padrão Tidy Data
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

    return df_clean[target_columns]


def get_sample_data() -> pd.DataFrame:
    """Gera um conjunto de dados simulado fiel à matriz do Power BI de exemplo da Saavedra."""
    raw_sample = [
        {"Hierarquia": "SAAVEDRA", "FY26 PPs": "", "Gross Sales Billed": "", "Gross Sales Open": "", "Total Gross": ""},
        {"Hierarquia": "  └ SAAVEDRA", "FY26 PPs": "6,348,232.58", "Gross Sales Billed": "5,131,675.73", "Gross Sales Open": "235,095.31", "Total Gross": "5,366,771"},
        # MDS
        {"Hierarquia": "    └ MDS", "FY26 PPs": "1,296,106.18", "Gross Sales Billed": "1,457,244.35", "Gross Sales Open": "9,086.82", "Total Gross": "1,466,331"},
        {"Hierarquia": "      └ AAD", "FY26 PPs": "1,296,106.18", "Gross Sales Billed": "1,457,244.35", "Gross Sales Open": "9,086.82", "Total Gross": "1,466,331"},
        # PI
        {"Hierarquia": "    └ PI", "FY26 PPs": "4,872,000.00", "Gross Sales Billed": "3,609,529.25", "Gross Sales Open": "226,008.49", "Total Gross": "3,835,538"},
        {"Hierarquia": "      └ Bone", "FY26 PPs": "12,000.00", "Gross Sales Billed": "2,880.24", "Gross Sales Open": "0.00", "Total Gross": "2,880"},
        {"Hierarquia": "      └ Chronic CVC Catheters", "FY26 PPs": "70,000.00", "Gross Sales Billed": "86,908.81", "Gross Sales Open": "0.00", "Total Gross": "86,909"},
        {"Hierarquia": "      └ Chronic Dialysis", "FY26 PPs": "430,000.00", "Gross Sales Billed": "595,980.20", "Gross Sales Open": "3,764.04", "Total Gross": "599,744"},
        {"Hierarquia": "      └ Core Needle Biopsy", "FY26 PPs": "1,320,000.00", "Gross Sales Billed": "878,059.82", "Gross Sales Open": "6,692.14", "Total Gross": "884,752"},
        {"Hierarquia": "      └ EleVation", "FY26 PPs": "210,000.00", "Gross Sales Billed": "5,063.50", "Gross Sales Open": "0.00", "Total Gross": "5,063"},
        {"Hierarquia": "      └ Encor Capital", "FY26 PPs": "80,000.00", "Gross Sales Billed": "0.00", "Gross Sales Open": "0.00", "Total Gross": "0"},
        {"Hierarquia": "      └ Encor Probes", "FY26 PPs": "670,000.00", "Gross Sales Billed": "592,165.57", "Gross Sales Open": "52,874.25", "Total Gross": "645,040"},
        {"Hierarquia": "      └ Localization Wire", "FY26 PPs": "5,000.00", "Gross Sales Billed": "5,345.68", "Gross Sales Open": "1,436.80", "Total Gross": "6,782"},
        {"Hierarquia": "      └ Mission Needles", "FY26 PPs": "60,000.00", "Gross Sales Billed": "239,166.56", "Gross Sales Open": "0.00", "Total Gross": "239,167"},
        {"Hierarquia": "      └ Ports", "FY26 PPs": "1,555,000.00", "Gross Sales Billed": "802,025.97", "Gross Sales Open": "142,664.96", "Total Gross": "944,691"},
        {"Hierarquia": "      └ Senomark Markers", "FY26 PPs": "45,000.00", "Gross Sales Billed": "21,755.37", "Gross Sales Open": "0.00", "Total Gross": "21,755"},
        {"Hierarquia": "      └ UltraClip Markers", "FY26 PPs": "415,000.00", "Gross Sales Billed": "380,177.53", "Gross Sales Open": "18,576.30", "Total Gross": "398,754"},
        # UCC
        {"Hierarquia": "    └ UCC", "FY26 PPs": "180,126.40", "Gross Sales Billed": "64,902.13", "Gross Sales Open": "0.00", "Total Gross": "64,902"},
        {"Hierarquia": "      └ Dignicare Accessories", "FY26 PPs": "23,484.00", "Gross Sales Billed": "10,800.00", "Gross Sales Open": "0.00", "Total Gross": "10,800"},
        {"Hierarquia": "      └ Dignishield", "FY26 PPs": "76,302.40", "Gross Sales Billed": "37,830.00", "Gross Sales Open": "0.00", "Total Gross": "37,830"},
        {"Hierarquia": "      └ Hydrophilic Urethral Catheters", "FY26 PPs": "80,340.00", "Gross Sales Billed": "16,272.13", "Gross Sales Open": "0.00", "Total Gross": "16,272"},
        # Total
        {"Hierarquia": "Total Geral", "FY26 PPs": "6,348,232.58", "Gross Sales Billed": "5,131,675.73", "Gross Sales Open": "235,095.31", "Total Gross": "5,366,771"},
    ]
    return pd.DataFrame(raw_sample)
