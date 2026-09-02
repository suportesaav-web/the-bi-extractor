# The BI Extractor ⚡

**The BI Extractor** é uma aplicação web corporativa desenvolvida em **Python** e **Streamlit** equipada com **IA Multimodal (Google Gemini Vision)** e motor de engenharia de dados.

Criada para solucionar o desafio crítico de ingestão de relatórios e exportações brutas do Power BI (matrizes hierárquicas colapsadas com nós `└`, números formatados como texto, inconsistências decimais e células mescladas), além de capturas de tela e documentos PDF contendo tabelas.

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

## 📥 Entradas Suportadas

O sistema opera em **Modo Híbrido** e aceita:

* **Documentos & Relatórios (`.pdf`)**: Relatórios contábeis, faturas e páginas exportadas processadas diretamente pela IA multimodal com renderização de alta fidelidade.
* **Capturas de Tela & Imagens (`.png`, `.jpg`, `.jpeg`)**: Prints diretos da tela do Power BI ou de sistemas ERP legados, extraídos instantaneamente por visão computacional.
* **Planilhas & Dados Tabulares (`.xlsx`, `.xls`, `.csv`)**: Extração direta de matrizes nativas do Excel com detecção automática de separadores (`;` ou `,`) e encoding UTF-8 / Latin-1.

---

## 📤 Saídas Geradas

* **📊 Mini-BI Executivo Integrado**: Visualização instantânea no navegador com indicadores de meta (Realizado vs FY26), atingimento financeiro e gráficos interativos em Plotly.
* **📑 Excel Corporativo (`.xlsx`)**: Aba *Consolidado Looker Studio*, cabeçalho executivo `#1F4E78` (*Navy Blue*), linhas zebradas `#F2F4F8`, formatação de moeda contábil `R$ #,##0.00` e linha de `TOTAL GERAL` com fórmulas nativas dinâmicas (`=SUM(...)`).
* **📈 CSV Looker Studio Ready (`.csv`)**: Formato normalizado *Tidy Data* (uma observação por linha, sem símbolos de árvore ou quebras), codificado em UTF-8 com BOM, pronto para ingestão direta no Looker Studio sem retrabalho de ETL.

---

## 📸 Demonstração Visual

| 📊 Mini-BI Executivo (Streamlit + Plotly) | 📑 Planilha Formatada (.xlsx) |
| :---: | :---: |
| ![Mini-BI Dashboard](docs/screenshots/mini_bi_dashboard.png) | ![Excel Corporativo](docs/screenshots/excel_corporate.png) |
| *Visualização de KPIs, Gap de Metas e Composição de Vendas* | *Cabeçalho Navy Blue, Fórmulas Nativas e Estilo Zebrado* |

| 🖼️ Documento / Print de Entrada (Original) | 📋 Tabela Tidy Data Normalizada |
| :---: | :---: |
| ![Entrada Original](docs/screenshots/input_preview.png) | ![Dados Tidy](docs/screenshots/tidy_table.png) |
| *Matriz hierárquica colapsada com símbolos de árvore* | *Granularidade tratada por Cliente, BU e Portfólio* |

> *Dica: As imagens de demonstração podem ser armazenadas no diretório `docs/screenshots/` utilizando dados anonimizados.*

---

## 🛠️ Stack Tecnológico

- **Python 3.10+**
- **Streamlit**: Interface web executiva e reatividade em tempo real.
- **Google GenAI SDK (`google-genai`)**: Motor multimodal Gemini Vision para leitura visual de imagens e relatórios em PDF.
- **Pypdfium2 & Pillow**: Renderização e processamento de páginas de documentos e imagens.
- **Pandas**: Motor de higienização de strings, desmembramento hierárquico em cascata e tipagem numérica defensiva.
- **Openpyxl**: Geração e estilização corporativa de planilhas Excel (`.xlsx`) com paleta Navy Blue e fórmulas analíticas.
- **Plotly Express & Graph Objects**: Gráficos analíticos interativos de alta performance.

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
└── components/
    ├── __init__.py
    ├── metrics_cards.py           # KPIs executivos (Total Gross, Atingimento, Gap de Meta)
    └── charts.py                  # Gráficos interativos em Plotly (Performance por BU e Portfólio)
```

---

## ⚡ Principais Capacidades

1. **Ingestão Universal e Inteligente**:
   - Upload de imagens (`.png`, `.jpg`), documentos (`.pdf`) e planilhas (`.xlsx`, `.xls`, `.csv`).
   - Pré-visualização integrada de imagens e documentos no Streamlit.
   - Remoção inteligente de caracteres como `└`, `├`, `─`, tabulações e recuos.
   - Desmembramento de níveis em cascata: `Customer Group`, `Business Unit` e `Portfolio`.
   - Reconciliação matemática garantida: `Total Gross = Faturado + Aberto`, `Atingimento = Total Gross - Meta`.

2. **Mini-BI Executivo Integrado**:
   - Cards de métricas com indicadores visuais de atingimento de meta.
   - Comparativo Realizado vs Meta por Unidade de Negócio (BU).
   - Ranking de Top Portfólios por percentual de atingimento.
   - Composição de Vendas: Faturado (*Billed*) vs Carteira em Aberto (*Open*).

3. **Exportação Profissional**:
   - **Excel (.xlsx)**: Modelo corporativo pronto para apresentação executiva.
   - **CSV Looker Studio**: Ingestão automática em pipelines de Business Intelligence.

---

## 🚀 Como Executar Localmente

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

### 4. Configurar a Chave do Gemini (Opcional para extração via IA)
Crie um arquivo `.env` na raiz ou informe diretamente na interface web:
```env
GEMINI_API_KEY=sua_chave_aqui
```

### 5. Executar a Aplicação Streamlit
```bash
streamlit run app.py
```
Acesse no seu navegador: `http://localhost:8501`.

---

## ☁️ Como Configurar o Deploy no Streamlit Cloud

1. Faça o push do código para o repositório no GitHub: `https://github.com/suportesaav-web/the-bi-extractor`.
2. Acesse [share.streamlit.io](https://share.streamlit.io/) e conecte sua conta do GitHub.
3. Clique em **"New app"**.
4. Selecione o repositório `suportesaav-web/the-bi-extractor`, branch `main` e defina o arquivo principal como `app.py`.
5. Em **Advanced Settings > Secrets**, adicione sua chave de API (opcional):
   ```toml
   GEMINI_API_KEY = "sua_chave_aqui"
   ```
6. Clique em **"Deploy!"**.

---

## 📝 Licença e Créditos
Desenvolvido para **Saavedra** como ferramenta de automação e engenharia de dados.
