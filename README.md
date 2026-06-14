# 🍫 Cacau Analytics — Plataforma de Dados para Varejo de Chocolate

Projeto de portfólio que simula uma arquitetura moderna de dados para uma rede de franquias de chocolate, cobrindo desde a ingestão de dados brutos até dashboards executivos em Power BI.

---

## 🏗️ Arquitetura

```
Fontes (CSV/Excel)
        │
        ▼
  [Bronze Layer]          → dados brutos, sem transformação
  data/raw/
        │
        ▼
  [Silver Layer]          → dados limpos, tipados, modelados em estrela
  data/processed/
        │
        ▼
  [Gold Layer / BI]       → agregações e métricas prontas para consumo
  Power BI (.pbix)
```

Inspirada na arquitetura **Medallion (Delta Lake / Databricks Lakehouse)**, implementada localmente com **Pandas + Parquet** para fins de portfólio.

---

## 📁 Estrutura do Repositório

```
cacaushow-analytics/
├── data/
│   ├── raw/                    # Dados brutos originais (CSV)
│   └── processed/              # Parquet limpos (Silver layer)
├── pipeline/
│   ├── 01_ingestao.py          # Leitura e validação das fontes
│   ├── 02_transformacao.py     # Limpeza, tipagem e enriquecimento
│   ├── 03_modelagem_estrela.py # Geração das tabelas dimensão e fato
│   └── utils.py                # Funções auxiliares reutilizáveis
├── notebooks/
│   └── eda_vendas_chocolate.ipynb  # Análise exploratória + insights
├── powerbi/
│   └── cacau_analytics.pbix    # Dashboard Power BI
├── docs/
│   └── modelo_dados.md         # Documentação do modelo estrela
├── requirements.txt
└── README.md
```

---

## 📊 Fontes de Dados

| Dataset | Origem | Descrição |
|---|---|---|
| `chocolate_sales_2023_2024.csv` | Kaggle | Vendas sintéticas de chocolate por produto, loja e data |
| `olist_orders.csv` | Kaggle (Olist) | Comportamento de compra e geolocalização BR |
| `olist_geolocation.csv` | Kaggle (Olist) | CEP → latitude/longitude por estado/cidade |

---

## ⭐ Modelo Estrela

```
                    ┌─────────────────┐
                    │   dim_produto   │
                    │─────────────────│
                    │ sk_produto (PK) │
                    │ nome_produto    │
                    │ categoria       │
                    │ linha           │
                    └────────┬────────┘
                             │
┌──────────────┐    ┌────────▼────────┐    ┌─────────────────┐
│  dim_loja    │    │  fato_vendas    │    │   dim_tempo     │
│──────────────│    │─────────────────│    │─────────────────│
│ sk_loja (PK) ├────┤ sk_loja (FK)   ├────┤ sk_tempo (PK)   │
│ nome_loja    │    │ sk_produto (FK) │    │ data            │
│ cidade       │    │ sk_tempo (FK)   │    │ dia_semana      │
│ estado       │    │ sk_vendedor(FK) │    │ mes             │
│ regiao       │    │ qtd_vendida     │    │ trimestre       │
└──────────────┘    │ valor_total     │    │ ano             │
                    │ desconto        │    │ is_pascoa       │
┌──────────────┐    │ custo           │    │ is_natal        │
│ dim_vendedor │    │ margem          │    │ is_dias_maes    │
│──────────────│    └─────────────────┘    └─────────────────┘
│ sk_vendedor  ├────┘
│ nome         │
│ equipe       │
└──────────────┘
```

---

## 🚀 Como Executar

### Pré-requisitos
```bash
pip install -r requirements.txt
```

### Pipeline completo
```bash
python pipeline/01_ingestao.py
python pipeline/02_transformacao.py
python pipeline/03_modelagem_estrela.py
```

### Ou tudo de uma vez
```bash
python pipeline/run_all.py
```

---

## 📈 Principais Insights do Projeto

- 📅 **Sazonalidade**: Páscoa representa pico de vendas ~340% acima da média mensal
- 🗺️ **Regionais**: Sudeste concentra 58% do volume, mas Sul tem maior ticket médio
- 🍫 **Mix de produtos**: Chocolates premium têm margem 2,3x maior que linha básica
- 📦 **Logística**: Tempo médio de entrega afeta diretamente a nota do cliente

---

## 🛠️ Stack Técnica

| Camada | Tecnologia | Equivalente Corporativo |
|---|---|---|
| Ingestão | Python + Pandas | Azure Data Factory |
| Transformação | Pandas + PySpark-like | Databricks (PySpark) |
| Armazenamento | Parquet | Delta Lake / ADLS |
| Modelagem | Star Schema manual | dbt / Synapse |
| Visualização | Power BI Desktop | Power BI Premium |
| Versionamento | Git + GitHub | Azure DevOps |

---

## 👤 Autor

Daniel — Analista de Dados | BI Developer  
Experiência em Power BI, DAX, Power Query, SQL Server e Microsoft 365.
