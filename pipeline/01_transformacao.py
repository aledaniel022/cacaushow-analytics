"""
01_transformacao.py
Lê os CSVs brutos (Bronze), aplica limpeza e tipagem (Silver),
e gera as tabelas dimensão + fato do modelo estrela em Parquet.

Simula o que seria feito em Databricks com PySpark:
  spark.read.csv(...)  →  df.withColumn(...)  →  df.write.parquet(...)
Aqui usamos Pandas + PyArrow para rodar localmente.
"""

import pandas as pd
import numpy as np
import os

RAW_DIR       = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)

# ─── Helpers ──────────────────────────────────────────────────────────────────
def log(msg): print(f"  {msg}")

def salvar_parquet(df: pd.DataFrame, nome: str):
    path = os.path.join(PROCESSED_DIR, f"{nome}.parquet")
    df.to_parquet(path, index=False, engine="pyarrow")
    log(f"✅ {nome}.parquet salvo — {len(df):,} linhas, {df.shape[1]} colunas")

# ─── dim_tempo ────────────────────────────────────────────────────────────────
def build_dim_tempo() -> pd.DataFrame:
    log("Construindo dim_tempo...")
    datas = pd.date_range("2023-01-01", "2024-12-31", freq="D")
    df = pd.DataFrame({"data": datas})

    df["sk_tempo"]      = df["data"].dt.strftime("%Y%m%d").astype(int)
    df["data"]          = df["data"].dt.date
    df["ano"]           = pd.DatetimeIndex(pd.to_datetime(df["data"])).year
    df["trimestre"]     = pd.DatetimeIndex(pd.to_datetime(df["data"])).quarter
    df["mes"]           = pd.DatetimeIndex(pd.to_datetime(df["data"])).month
    df["nome_mes"]      = pd.to_datetime(df["data"]).dt.strftime("%B")
    df["semana_ano"]    = pd.DatetimeIndex(pd.to_datetime(df["data"])).isocalendar().week.astype(int)
    df["dia_semana_num"]= pd.DatetimeIndex(pd.to_datetime(df["data"])).dayofweek   # 0=seg
    df["nome_dia"]      = pd.to_datetime(df["data"]).dt.strftime("%A")
    df["is_fim_semana"] = df["dia_semana_num"] >= 5

    # Datas comemorativas — críticas para varejo de chocolate
    dt = pd.to_datetime(df["data"])
    df["is_pascoa"]      = ((dt >= "2023-03-20") & (dt <= "2023-04-09")) | \
                           ((dt >= "2024-03-11") & (dt <= "2024-03-31"))
    df["is_natal"]       = dt.dt.month == 12
    df["is_dias_maes"]   = ((dt >= "2023-05-01") & (dt <= "2023-05-14")) | \
                           ((dt >= "2024-05-01") & (dt <= "2024-05-12"))
    df["is_namorados"]   = (dt.dt.month == 6) & (dt.dt.day <= 12) & (dt.dt.day >= 5)
    df["is_dias_pais"]   = (dt.dt.month == 8) & (dt.dt.day >= 5) & (dt.dt.day <= 13)
    df["is_data_especial"] = (df["is_pascoa"] | df["is_natal"] | df["is_dias_maes"] |
                               df["is_namorados"] | df["is_dias_pais"])

    return df[["sk_tempo","data","ano","trimestre","mes","nome_mes",
               "semana_ano","dia_semana_num","nome_dia","is_fim_semana",
               "is_pascoa","is_natal","is_dias_maes","is_namorados",
               "is_dias_pais","is_data_especial"]]

# ─── dim_produto ──────────────────────────────────────────────────────────────
def build_dim_produto() -> pd.DataFrame:
    log("Construindo dim_produto...")
    df = pd.read_csv(f"{RAW_DIR}/dim_produto_raw.csv")
    df = df.rename(columns={"id": "produto_id"})

    # Surrogate key
    df.insert(0, "sk_produto", range(1, len(df) + 1))

    # Faixa de preço
    df["faixa_preco"] = pd.cut(df["preco_base"],
                               bins=[0, 15, 50, 100, float("inf")],
                               labels=["Econômico", "Médio", "Alto", "Super Premium"])
    df["margem_bruta_pct"] = ((df["preco_base"] - df["custo_base"]) / df["preco_base"] * 100).round(1)

    return df

# ─── dim_loja ─────────────────────────────────────────────────────────────────
def build_dim_loja() -> pd.DataFrame:
    log("Construindo dim_loja...")
    df = pd.read_csv(f"{RAW_DIR}/dim_loja_raw.csv")
    df = df.rename(columns={"id": "loja_id", "nome": "nome_loja"})
    df.insert(0, "sk_loja", range(1, len(df) + 1))

    # Mapeamento de macrorregião
    macro = {"SP": "São Paulo", "RJ": "Rio de Janeiro", "PR": "Paraná",
             "RS": "Rio Grande do Sul", "SC": "Santa Catarina",
             "MG": "Minas Gerais", "BA": "Bahia", "PE": "Pernambuco",
             "CE": "Ceará", "DF": "Distrito Federal", "AM": "Amazonas"}
    df["nome_estado"] = df["estado"].map(macro).fillna(df["estado"])
    return df

# ─── dim_vendedor ─────────────────────────────────────────────────────────────
def build_dim_vendedor() -> pd.DataFrame:
    log("Construindo dim_vendedor...")
    df = pd.read_csv(f"{RAW_DIR}/dim_vendedor_raw.csv")
    df = df.rename(columns={"id": "vendedor_id", "nome": "nome_vendedor"})
    df.insert(0, "sk_vendedor", range(1, len(df) + 1))
    return df

# ─── fato_vendas ──────────────────────────────────────────────────────────────
def build_fato_vendas(dim_tempo, dim_produto, dim_loja, dim_vendedor) -> pd.DataFrame:
    log("Construindo fato_vendas...")
    df = pd.read_csv(f"{RAW_DIR}/fato_vendas_raw.csv", parse_dates=["data"])

    # Lookup de surrogate keys
    sk_tempo     = dim_tempo[["sk_tempo","data"]].copy()
    sk_tempo["data"] = pd.to_datetime(sk_tempo["data"])

    sk_produto   = dim_produto[["sk_produto","produto_id"]]
    sk_loja      = dim_loja[["sk_loja","loja_id"]]
    sk_vendedor  = dim_vendedor[["sk_vendedor","vendedor_id"]]

    df["data_join"] = df["data"].dt.normalize()
    sk_tempo["data_join"] = pd.to_datetime(sk_tempo["data"])

    df = df.merge(sk_tempo[["sk_tempo","data_join"]],    on="data_join",     how="left")
    df = df.merge(sk_produto,  on="produto_id",  how="left")
    df = df.merge(sk_loja,     on="loja_id",     how="left")
    df = df.merge(sk_vendedor, on="vendedor_id", how="left")

    # Métricas derivadas
    df["margem_pct"] = (df["margem"] / df["valor_total"] * 100).round(2)
    df["ticket_medio"] = (df["valor_total"] / df["quantidade"]).round(2)

    fato = df[["venda_id", "sk_tempo", "sk_produto", "sk_loja", "sk_vendedor",
               "quantidade", "preco_unitario", "desconto_pct",
               "valor_total", "custo_total", "margem", "margem_pct", "ticket_medio"]]

    # Checagem de integridade
    nulls = fato[["sk_tempo","sk_produto","sk_loja","sk_vendedor"]].isnull().sum()
    if nulls.sum() > 0:
        print(f"\n⚠️  ATENÇÃO — chaves sem match:\n{nulls[nulls > 0]}")

    return fato

# ─── Execução ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n🍫 Cacau Analytics — Pipeline de Transformação (Bronze → Silver)\n")

    dim_tempo    = build_dim_tempo()
    dim_produto  = build_dim_produto()
    dim_loja     = build_dim_loja()
    dim_vendedor = build_dim_vendedor()
    fato_vendas  = build_fato_vendas(dim_tempo, dim_produto, dim_loja, dim_vendedor)

    print("\n📦 Salvando em Parquet (Silver Layer)...")
    salvar_parquet(dim_tempo,    "dim_tempo")
    salvar_parquet(dim_produto,  "dim_produto")
    salvar_parquet(dim_loja,     "dim_loja")
    salvar_parquet(dim_vendedor, "dim_vendedor")
    salvar_parquet(fato_vendas,  "fato_vendas")

    print("\n📊 Resumo da fato_vendas:")
    print(f"   Total de vendas   : {len(fato_vendas):,}")
    print(f"   Período           : 2023-01-01 a 2024-12-31")
    print(f"   Valor total (R$)  : {fato_vendas['valor_total'].sum():,.2f}")
    print(f"   Margem média      : {fato_vendas['margem_pct'].mean():.1f}%")
    print(f"   Ticket médio      : R$ {fato_vendas['ticket_medio'].mean():.2f}")
    print("\n✅ Pipeline concluído com sucesso!\n")
