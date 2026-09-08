<div align="center">

# ⚡ The BI Extractor
### *Engine de Ingestão Inteligente de Dados, Visão Computacional e Normalização Tidy Data*

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Acesse Online](https://img.shields.io/badge/🚀_Acesse_Online-Streamlit_Cloud-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://the-bi-extractor-saavedra.streamlit.app/)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-Vision_AI-8E75C2?style=for-the-badge&logo=googlegemini&logoColor=white)](https://ai.google.dev/)
[![Looker Studio](https://img.shields.io/badge/Looker_Studio-Ready-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://lookerstudio.google.com/)
[![Excel](https://img.shields.io/badge/Microsoft_Excel-OpenPyXL-217346?style=for-the-badge&logo=microsoftexcel&logoColor=white)](https://openpyxl.readthedocs.io/)

<p align="center">
  <b>Transforme capturas de tela e exportações brutas em bases Tidy Data perfeitamente estruturadas para o Looker Studio e planilhas corporativas com fórmulas ativas via IA Multimodal em Modo Híbrido.</b>
</p>

<p align="center">
  <a href="https://the-bi-extractor-saavedra.streamlit.app/" target="_blank">
    <img src="https://static.streamlit.io/badges/streamlit_badge_black_white.svg" alt="Open in Streamlit" />
  </a>
  <br>
  🔗 <b>URL de Acesso:</b> <a href="https://the-bi-extractor-saavedra.streamlit.app/" target="_blank"><code>https://the-bi-extractor-saavedra.streamlit.app/</code></a>
</p>

---

</div>

## 📌 Visão Geral

O **The BI Extractor** é uma solução de engenharia de dados e Business Intelligence corporativo que elimina o retrabalho manual de higienização de matrizes do **Power BI** (árvores hierárquicas desestruturadas com caracteres `└`, números formatados como texto e células mescladas), prints de tela e planilhas genéricas.

Equipado com **IA Multimodal (Google Gemini Vision 3.6 Flash / Flash Latest)** com fallback automático e motor de cálculo defensivo em **Pandas**, o pipeline reconcilia valores monetários, detecta níveis hierárquicos e entrega saídas executivas imediatas em **Modo Híbrido**:
1. **Matriz Power BI Saavedra**: Desmembramento de Customer Group, Business Unit e Portfólio, reconciliação monetária, cálculo dinâmico de metas/gaps, dashboard de KPIs e gráficos analíticos.
2. **Tabela Genérica**: Extração dinâmica de qualquer tabela (produtos, finanças, estoque ou clientes) a partir de imagens ou arquivos CSV/Excel, preservando integralmente suas colunas e dados.

---

## 🔄 Fluxo de Transformação (Antes vs Depois)

```
[ Entrada: Dados Brutos & Hierarquias ]               [ Motor de Processamento ]             [ Saídas Corporativas Prontas ]
┌──────────────────────────────────────┐             ┌─────────────────────────┐            ┌─────────────────────────────────────────┐
│ Captura de Tela (PNG/JPG) ou Planilha │             │  The BI Extractor       │            │ 1. Mini-BI Interativo (Web Dashboard)   │
│                                      │             │                         │            │    ├─ Cards de KPIs e Gap de Meta       │
│ └ SAAVEDRA (Customer Group)          │  ─────────► │  • Gemini Vision AI     │  ────────► │    └─ Gráficos de Metas e Portfólios    │
│   ├── MDS (Business Unit)            │             │  • Parser Hierárquico   │            │ 2. Excel Corporativo (.xlsx)            │
│   │   └── AAD (Portfolio)            │             │  • Reconciliação Tidy   │            │    └─ Estilo Navy Blue + Fórmulas SUM   │
│   └── PI (Business Unit)             │             │  • Modo Híbrido Ativo   │            │ 3. CSV Google Looker Studio (.csv)      │
│       └── Ports (Portfolio)          │             │                         │            │    └─ UTF-8 BOM Tidy Data Normalizado   │
└──────────────────────────────────────┘             └─────────────────────────┘            └─────────────────────────────────────────┘
```

---

## 📥 Entradas & 📤 Saídas Suportadas

<table width="100%">
<tr>
<td width="50%" valign="top">

### 📥 Entradas Suportadas

* **🖼️ Capturas de Tela & Imagens (`.png`, `.jpg`, `.jpeg`)**
  * Prints de matrizes do Power BI, dashboards, sistemas ERP ou fotos de tabelas impressas analisadas via visão computacional do Gemini.
* **📊 Planilhas & Arquivos Tabulares (`.xlsx`, `.xls`, `.csv`)**
  * Matrizes hierárquicas brutas e exportações com delimitadores `,` ou `;`, com detecção inteligente de formato.

</td>
<td width="50%" valign="top">

### 📤 Saídas Geradas

* **📊 Mini-BI Executivo Integrado**
  * Visualização reativa: cards de faturamento, metas, gap financeiro e gráficos Plotly comparativos.
* **📑 Excel Corporativo (`.xlsx`)**
  * Cabeçalho executivo `#1F4E78` (*Navy Blue*), linhas zebradas, formatação de moeda e fórmulas dinâmicas (`=SUM(...)`).
* **📈 CSV Pronto para Looker Studio (`.csv`)**
  * Granularidade 1 linha por portfólio (Tidy Data), codificação **UTF-8 com BOM** para abertura perfeita no Microsoft Excel e Looker Studio sem corrupção de acentuação.

</td>
</tr>
</table>

---

## 🤖 Modo Híbrido Inteligente

O extrator detecta automaticamente o conteúdo fornecido:

| Modo | Identificação | Tratamento Aplicado | Saídas e Recursos |
| :--- | :--- | :--- | :--- |
| **Matriz Power BI Saavedra** | Contém hierarquias (*Customer Group*, *BU*, *Portfólio*) e métricas de vendas (*FY26 PPs*, *Billed*, *Open*, *Total Gross*). | Normalização estrita Tidy Data, eliminação de duplicações de subtotais e reconciliação matemática. | Dashboard de KPIs, Gráficos por BU/Portfólio, Filtros, Excel com Fórmulas e CSV Looker Studio. |
| **Tabela Genérica** | Qualquer tabela comercial, contábil ou cadastral (produtos, estoque, faturamento genérico). | Identificação dinâmica de colunas, tipagem numérica automática e preservação integral dos registros. | Tabela interativa com busca rápida, contadores de linhas/colunas e exportação em Excel e CSV padronizado. |

---

## 🛠️ Stack Tecnológico

| Camada | Tecnologia | Função Principal |
| :--- | :--- | :--- |
| **Frontend & UI** | `Streamlit 1.30+` | Interface executiva reativa, filtros dinâmicos e controle de visualizações |
| **Visão Computacional & IA** | `Google GenAI SDK (Gemini Vision)` | Extração multimodal inteligente via modelos `gemini-3.6-flash` e `gemini-flash-latest` |
| **Resiliência e Alta Disponibilidade** | `Multi-Key Pool & Exponential Backoff` | Contingência automática entre `GEMINI_API_KEY` e `GEMINI_API_KEY_BACKUP` e proteção contra 503/429 |
| **Processamento de Imagens** | `Pillow (PIL)` | Ingestão, conversão e manipulação de imagens pré-inferência |
| **Engenharia de Dados** | `Pandas` | Desmembramento hierárquico em cascata, normalização Tidy Data e higienização numérica |
| **Exportação Corporativa** | `Openpyxl` | Geração de planilhas Excel formatadas em Navy Blue com fórmulas analíticas nativas |
| **Visualizações Analíticas** | `Plotly Express / Graph Objects` | Gráficos interativos com tooltips e comparativos de metas |

---

## 📂 Arquitetura do Projeto

```
the-bi-extractor/
├── .gitignore
├── .env.example
├── README.md
├── requirements.txt
├── app.py                         # Aplicação Streamlit (UI, filtros, Modo Híbrido e orquestração)
├── core/
│   ├── __init__.py
│   ├── parser.py                  # Roteamento de ingestão, higienização, Modo Híbrido e Tidy Data
│   ├── gemini_vision_parser.py    # Motor multimodal Gemini (resiliência, pool de chaves e retentativas)
│   ├── image_parser.py            # OCR local de contingência (Windows Media OCR)
│   └── excel_exporter.py          # Renderizador de arquivo Excel (.xlsx) com estilos e fórmulas
├── components/
│   ├── __init__.py
│   ├── metrics_cards.py           # KPIs executivos (Total Gross, Atingimento, Gap de Meta)
│   └── charts.py                  # Gráficos interativos em Plotly (Performance por BU e Portfólio)
└── docs/
    └── screenshots/               # Ativos de documentação
```

---

<details>
<summary><b>🚀 Clique aqui para ver o Guia de Instalação e Execução Local</b></summary>

<br>

### 1. Clonar o Repositório
```bash
git clone https://github.com/suportesaav-web/the-bi-extractor.git
cd the-bi-extractor
```

### 2. Criar e Ativar o Ambiente Virtual
```bash
# No Windows (PowerShell):
python -m venv .venv
.venv\Scripts\Activate.ps1

# No Linux/macOS:
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 4. Configurar as Chaves do Gemini (Alta Disponibilidade)
Crie um arquivo `.env` na raiz do projeto ou configure na barra lateral da aplicação:
```env
GEMINI_API_KEY="sua_chave_primaria"
GEMINI_API_KEY_BACKUP="sua_chave_secundaria_opcional"
```
> O sistema utiliza a chave primária e, caso ela sofra limite de cota ou instabilidade, comuta de forma transparente para a chave backup.

### 5. Iniciar a Aplicação
```bash
streamlit run app.py
```
Acesse no seu navegador: `http://localhost:8501`.

</details>

<details>
<summary><b>☁️ Clique aqui para ver o Passo a Passo de Deploy no Streamlit Cloud</b></summary>

<br>

1. Faça o push do projeto para o repositório GitHub: `https://github.com/suportesaav-web/the-bi-extractor`.
2. Acesse [share.streamlit.io](https://share.streamlit.io/) e realize login.
3. Clique em **"New app"**.
4. Selecione o repositório `suportesaav-web/the-bi-extractor`, branch `main` e defina **Main file path** como `app.py`.
5. Em **Advanced Settings > Secrets**, declare suas credenciais com suporte a backup:
   ```toml
   GEMINI_API_KEY = "sua_chave_primaria"
   GEMINI_API_KEY_BACKUP = "sua_chave_secundaria_opcional"
   ```
6. Clique em **"Deploy!"**. O ambiente instalará as dependências e publicará o app.

> 🌐 **Ambiente de Produção Ativo:**  
> A aplicação oficial já está em execução no Streamlit Cloud: [https://the-bi-extractor-saavedra.streamlit.app/](https://the-bi-extractor-saavedra.streamlit.app/)

</details>

---

## 📝 Licença e Créditos
Desenvolvido para **Saavedra** como ferramenta corporativa de automação, visão computacional e engenharia de dados.
