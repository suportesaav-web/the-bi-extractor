# The BI Extractor ⚡

**The BI Extractor** é uma aplicação web desenvolvida em **Python** e **Streamlit** criada para solucionar problemas recorrentes de ingestão de dados brutos exportados do Power BI (matrizes hierárquicas com símbolos `└`, números formatados como texto, inconsistências de separadores decimais e células mescladas).

O sistema processa esses dados, normaliza-os no formato tabular **Tidy Data**, disponibiliza um **Mini-BI interativo** executivo na tela e permite a exportação em **Excel (.xlsx)** estilizado profissionalmente com fórmulas nativas e **CSV** pronto para ingestão direta no **Google Looker Studio**.

---

## 🛠️ Stack Tecnológico

- **Python 3.10+**
- **Streamlit**: Interface web interativa e gerenciamento de estado reativo.
- **Pandas**: Motor de higienização, desmembramento hierárquico e tipagem de dados.
- **Openpyxl**: Renderização e estilização corporativa de planilhas Excel (`.xlsx`) com paleta Navy Blue, efeitos zebrados e fórmulas dinâmicas (`=SUM(...)`).
- **Plotly Express & Graph Objects**: Visualizações gráficas analíticas de alta performance.

---

## 📂 Arquitetura do Projeto

```
the-bi-extractor/
├── .gitignore
├── README.md
├── requirements.txt
├── app.py                      # Ponto de entrada Streamlit (UI, upload e orquestração)
├── core/
│   ├── __init__.py
│   ├── parser.py               # Motor de higienização, desmembramento hierárquico e tipagem
│   └── excel_exporter.py       # Renderizador de arquivo Excel (.xlsx) com estilos e fórmulas
└── components/
    ├── __init__.py
    ├── metrics_cards.py        # KPIs executivos (Total Gross, Atingimento, Gap de Meta)
    └── charts.py               # Gráficos interativos em Plotly (Performance por BU e Portfólio)
```

---

## ⚡ Principais Funcionalidades

1. **Ingestão Flexível**:
   - Suporte a uploads em `.xlsx`, `.xls` e `.csv`.
   - Limpeza automática de caracteres de árvore como `└`, `├`, `─`, recuos e espaços em branco.
   - Detecção em cascata dos níveis: `Customer Group`, `Business Unit` e `Portfolio`.
   - Recálculo dinâmico de `Total Gross`, `Ating PPs` e `% PPs`.

2. **Mini-BI Executivo Integrado**:
   - Cards de métricas com indicadores visuais de atingimento de meta.
   - Gráfico de barras comparativo: Realizado vs Meta FY26 por Business Unit.
   - Ranking de Top Portfólios por % de Atingimento com linha de meta de 100%.
   - Gráfico de barras empilhadas: Composição de Faturado (*Billed*) vs Em Aberto (*Open*).

3. **Central de Exportação**:
   - **Excel (.xlsx)**: Aba `Consolidado Looker Studio`, cabeçalho `#1F4E78` (Navy Blue), efeito zebrado `#F2F4F8`, formatação contábil `R$ #,##0.00` e linha final de `TOTAL GERAL` com fórmulas nativas do Excel.
   - **CSV (Google Looker Studio Ready)**: UTF-8 com BOM, delimitado e normalizado sem inconsistências.

---

## 🚀 Como Executar Localmente

### 1. Clonar o Repositório
```bash
git clone https://github.com/suportesaav-web/the-bi-extractor.git
cd the-bi-extractor
```

### 2. Criar e Ativar o Ambiente Virtual (Opcional, mas recomendado)
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

### 4. Executar a Aplicação Streamlit
```bash
streamlit run app.py
```
A aplicação abrirá automaticamente no seu navegador padrão no endereço `http://localhost:8501`.

---

## ☁️ Como Configurar o Deploy no Streamlit Cloud

1. Faça o push do código para o repositório no GitHub: `https://github.com/suportesaav-web/the-bi-extractor`.
2. Acesse [share.streamlit.io](https://share.streamlit.io/) e conecte sua conta do GitHub.
3. Clique em **"New app"**.
4. Selecione o repositório `suportesaav-web/the-bi-extractor`, a branch `main` (ou `master`) e defina o **Main file path** como `app.py`.
5. Clique em **"Deploy!"**. O Streamlit Cloud instalará automaticamente as dependências do `requirements.txt` e disponibilizará a aplicação online.

---

## 📝 Licença e Créditos
Desenvolvido para **Saavedra** como ferramenta de automação e engenharia de dados.
