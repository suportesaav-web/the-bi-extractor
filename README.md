<div align="center">

# ⚡ The BI Extractor
### *Engine de Ingestão Inteligente de Dados, Visão Computacional e Normalização Tidy Data*

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-Vision_AI-8E75C2?style=for-the-badge&logo=googlegemini&logoColor=white)](https://ai.google.dev/)
[![Looker Studio](https://img.shields.io/badge/Looker_Studio-Ready-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://lookerstudio.google.com/)
[![Excel](https://img.shields.io/badge/Microsoft_Excel-OpenPyXL-217346?style=for-the-badge&logo=microsoftexcel&logoColor=white)](https://openpyxl.readthedocs.io/)

<p align="center">
  <b>Transforme exportações brutas do Power BI, faturas em PDF e capturas de tela em bases Tidy Data perfeitamente estruturadas para o Looker Studio e planilhas corporativas com fórmulas ativas.</b>
</p>

---

</div>

## 📌 Visão Geral

O **The BI Extractor** é uma solução de engenharia de dados e Business Intelligence corporativo que elimina o gargalo manual de higienização de matrizes do **Power BI** (árvores hierárquicas desestruturadas com caracteres `└`, números formatados como texto e células mescladas) e relatórios em **PDF/Imagens**.

Equipado com **IA Multimodal (Google Gemini Vision)** e motor de cálculo defensivo em **Pandas**, o pipeline reconcilia valores monetários, detecta níveis hierárquicos e entrega saídas executivas imediatas.

---

## 🔄 Fluxo de Transformação (Antes vs Depois)

```
[ Entrada: Dados Brutos & Hierarquias ]               [ Motor de Processamento ]             [ Saídas Corporativas Prontas ]
┌──────────────────────────────────────┐             ┌─────────────────────────┐            ┌─────────────────────────────────────────┐
│ Exportação Power BI / Print / PDF    │             │  The BI Extractor       │            │ 1. Mini-BI Interativo (Web Dashboard)   │
│                                      │             │                         │            │    ├─ Cards de KPIs e Gap de Meta       │
│ └ SAAVEDRA (Customer Group)          │  ─────────► │  • Gemini Vision AI     │  ────────► │    └─ Gráficos de Metas e Portfólios    │
│   ├── MDS (Business Unit)            │             │  • Parser Hierárquico   │            │ 2. Excel Corporativo (.xlsx)            │
│   │   └── AAD (Portfolio)            │             │  • Reconciliação Tidy   │            │    └─ Estilo Navy Blue + Fórmulas SUM   │
│   └── PI (Business Unit)             │             │                         │            │ 3. CSV Google Looker Studio (.csv)      │
│       └── Ports (Portfolio)          │             │                         │            │    └─ UTF-8 BOM Tidy Data Normalizado   │
└──────────────────────────────────────┘             └─────────────────────────┘            └─────────────────────────────────────────┘
```

---

## 📥 Entradas & 📤 Saídas Suportadas

<table width="100%">
<tr>
<td width="50%" valign="top">

### 📥 Entradas Suportadas

* **📄 Documentos & Relatórios (`.pdf`)**
  * Relatórios contábeis, faturas e relatórios multipáginas analisados diretamente por IA multimodal.
* **🖼️ Capturas de Tela (`.png`, `.jpg`, `.jpeg`)**
  * Prints de matrizes do Power BI ou ERPs com tabelas na tela.
* **📊 Planilhas & Arquivos de Dados (`.xlsx`, `.xls`, `.csv`)**
  * Matrizes hierárquicas brutas e exportações com separadores `,` ou `;`.

</td>
<td width="50%" valign="top">

### 📤 Saídas Geradas

* **📊 Mini-BI Executivo Integrado**
  * Visualização reativa em tela: cards de atingimento, gap financeiro e gráficos Plotly.
* **📑 Excel Corporativo (`.xlsx`)**
  * Cabeçalho executivo `#1F4E78` (*Navy Blue*), linhas zebradas, formatação `R$ #,##0.00` e fórmulas dinâmicas (`=SUM(...)`).
* **📈 CSV Google Looker Studio Ready (`.csv`)**
  * Granularidade 1 linha por portfólio (Tidy Data), codificação UTF-8 com BOM para upload imediato sem retrabalho de ETL.

</td>
</tr>
</table>

---

## 📸 Demonstração Visual da Aplicação

<div align="center">

<table width="100%">
<tr>
<td width="50%" align="center">
  <b>📊 1. Mini-BI Executivo Integrado</b><br>
  <img src="docs/screenshots/mini_bi_dashboard.png" alt="Mini-BI Dashboard" width="100%" style="border-radius: 8px; border: 1px solid #E2E8F0;" /><br>
  <sub><i>KPIs de Meta, Gap Financeiro, Performance por BU e Top Portfólios</i></sub>
</td>
<td width="50%" align="center">
  <b>📑 2. Planilha Excel Estilizada (.xlsx)</b><br>
  <img src="docs/screenshots/excel_corporate.png" alt="Planilha Excel Formatada" width="100%" style="border-radius: 8px; border: 1px solid #E2E8F0;" /><br>
  <sub><i>Cabeçalho Navy Blue corporativo, efeito zebrado e fórmulas nativas</i></sub>
</td>
</tr>
<tr>
<td width="50%" align="center">
  <b>📥 3. Arquivo / Documento de Entrada</b><br>
  <img src="docs/screenshots/input_preview.png" alt="Documento Original" width="100%" style="border-radius: 8px; border: 1px solid #E2E8F0;" /><br>
  <sub><i>Relatório em PDF ou captura de tela bruta com nós hierárquicos</i></sub>
</td>
<td width="50%" align="center">
  <b>📋 4. Matriz Tidy Data Normalizada</b><br>
  <img src="docs/screenshots/tidy_table.png" alt="Tabela Tidy Data" width="100%" style="border-radius: 8px; border: 1px solid #E2E8F0;" /><br>
  <sub><i>Dados desacoplados e higienizados prontos para ingestão e auditoria</i></sub>
</td>
</tr>
</table>

</div>

---

## 🛠️ Stack Tecnológico

| Camada | Tecnologia | Função Principal |
| :--- | :--- | :--- |
| **Frontend & UI** | `Streamlit 1.30+` | Interface executiva reativa, filtros dinâmicos e controle de visualizações |
| **Visão Computacional & IA** | `Google GenAI SDK (Gemini Vision)` | Extração multimodal inteligente em Modo Híbrido de imagens e PDFs |
| **Renderização de Documentos**| `Pypdfium2` & `Pillow` | Renderização ultrarrápida de páginas PDF e tratamento de imagens |
| **Engenharia de Dados** | `Pandas` | Desmembramento hierárquico em cascata e normalização Tidy Data |
| **Exportação Corporativa** | `Openpyxl` | Geração de planilhas Excel formatadas com fórmulas analíticas nativas |
| **Visualizações Analíticas** | `Plotly Express / Graph Objects` | Gráficos interativos com tooltips e comparativos de metas |

---

## 📂 Arquitetura do Projeto

```
the-bi-extractor/
├── .gitignore
├── README.md
├── requirements.txt
├── app.py                         # Aplicação Streamlit (UI, upload multimodal e orquestração)
├── core/
│   ├── __init__.py
│   ├── parser.py                  # Roteamento de ingestão, higienização e cálculos de negócio
│   ├── gemini_vision_parser.py    # Motor multimodal Gemini (visão computacional para imagens e PDFs)
│   ├── image_parser.py            # OCR local de contingência (Windows Media OCR)
│   └── excel_exporter.py          # Renderizador de arquivo Excel (.xlsx) com estilos e fórmulas
├── components/
│   ├── __init__.py
│   ├── metrics_cards.py           # KPIs executivos (Total Gross, Atingimento, Gap de Meta)
│   └── charts.py                  # Gráficos interativos em Plotly (Performance por BU e Portfólio)
└── docs/
    └── screenshots/               # Imagens e capturas de tela de demonstração do README
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

### 4. Configurar a Chave do Gemini (Opcional)
Crie um arquivo `.env` na raiz do projeto ou insira diretamente na barra lateral da aplicação:
```env
GEMINI_API_KEY=sua_chave_aqui
```

### 5. Iniciar a Aplicação
```bash
streamlit run app.py
```
Acesse no seu navegador: `http://localhost:8501`.

</details>

<details>
<summary><b>☁️ Clique aqui para ver o Passo a Passo de Deploy no Streamlit Cloud</b></summary>

<br>

1. Faça o push do projeto para o seu repositório no GitHub: `https://github.com/suportesaav-web/the-bi-extractor`.
2. Acesse [share.streamlit.io](https://share.streamlit.io/) e realize login com seu GitHub.
3. Clique em **"New app"**.
4. Selecione o repositório `suportesaav-web/the-bi-extractor`, branch `main` e defina **Main file path** como `app.py`.
5. Em **Advanced Settings > Secrets**, declare sua chave de IA:
   ```toml
   GEMINI_API_KEY = "sua_chave_aqui"
   ```
6. Clique em **"Deploy!"**. O ambiente instalará os pacotes de `requirements.txt` e publicará o app online.

</details>

---

## 📝 Licença e Créditos
Desenvolvido para **Saavedra** como ferramenta corporativa de automação, visão computacional e engenharia de dados.
