"""
02_insights.py
Gera análises prontas para o README e para apresentar na entrevista.
Produz CSVs de ouro (Gold Layer) prontos para o Power BI.

v2 — Adicionado:
  - gold_sazonalidade: coluna regiao + comparativo ano anterior
  - gold_sazonalidade_regiao: sazonalidade por região (nova tabela)
  - Demais tabelas mantidas com mesma estrutura (sem quebrar conexões PBI)
"""

import pandas as pd
import os

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
GOLD_DIR      = os.path.join(os.path.dirname(__file__), "..", "data", "gold")
os.makedirs(GOLD_DIR, exist_ok=True)

def carregar_modelo():
    read = lambda nome: pd.read_parquet(f"{PROCESSED_DIR}/{nome}.parquet")
    return {
        "fato":     read("fato_vendas"),
        "tempo":    read("dim_tempo"),
        "produto":  read("dim_produto"),
        "loja":     read("dim_loja"),
        "vendedor": read("dim_vendedor"),
    }

def analise_sazonalidade(m):
    """Vendas mensais POR REGIÃO com flags de datas especiais + comparativo YoY.
    Granularidade: ano x mes x regiao — permite cruzar tempo com geografia."""
    df = m["fato"].merge(m["tempo"], on="sk_tempo").merge(m["loja"], on="sk_loja")
    mensal = df.groupby(["ano", "mes", "nome_mes", "regiao", "is_pascoa", "is_natal",
                          "is_dias_maes", "is_namorados", "is_data_especial"]).agg(
        total_vendas   = ("valor_total", "sum"),
        total_margem   = ("margem", "sum"),
        qtd_transacoes = ("venda_id", "count"),
    ).reset_index()
    mensal["ticket_medio"] = (mensal["total_vendas"] / mensal["qtd_transacoes"]).round(2)
    mensal["total_vendas"] = mensal["total_vendas"].round(2)
    mensal["total_margem"] = mensal["total_margem"].round(2)

    # Comparativo ano anterior (YoY) por região
    mensal_sorted = mensal.sort_values(["regiao", "mes", "ano"])
    mensal["vendas_ano_anterior"] = mensal_sorted.groupby(["regiao", "mes"])["total_vendas"].shift(1).values
    mensal["variacao_yoy_pct"] = (
        (mensal["total_vendas"] - mensal["vendas_ano_anterior"])
        / mensal["vendas_ano_anterior"] * 100
    ).round(2)

    return mensal.sort_values(["ano", "mes", "regiao"]).reset_index(drop=True)

def analise_por_regiao(m):
    """Performance por região e estado — mantida igual."""
    df = m["fato"].merge(m["loja"], on="sk_loja")
    return df.groupby(["regiao", "estado", "nome_estado"]).agg(
        total_vendas   = ("valor_total", "sum"),
        total_margem   = ("margem", "sum"),
        qtd_transacoes = ("venda_id", "count"),
        ticket_medio   = ("ticket_medio", "mean"),
    ).round(2).reset_index().sort_values("total_vendas", ascending=False)

def analise_mix_produto(m):
    """Ranking de produtos por margem e volume — mantida igual."""
    df = m["fato"].merge(m["produto"], on="sk_produto")
    return df.groupby(["produto_id", "nome", "categoria", "linha", "faixa_preco"]).agg(
        total_vendas   = ("valor_total", "sum"),
        total_margem   = ("margem", "sum"),
        qtd_vendida    = ("quantidade", "sum"),
        qtd_transacoes = ("venda_id", "count"),
        margem_media   = ("margem_pct", "mean"),
    ).round(2).reset_index().sort_values("total_margem", ascending=False)

def analise_por_loja(m):
    """Ranking de lojas + YoY por loja."""
    df = m["fato"].merge(m["loja"], on="sk_loja").merge(m["tempo"], on="sk_tempo")

    # Ranking total — mantida igual para não quebrar conexões
    ranking = df.groupby(["loja_id", "nome_loja", "cidade", "estado", "regiao", "tipo"]).agg(
        total_vendas   = ("valor_total", "sum"),
        total_margem   = ("margem", "sum"),
        qtd_transacoes = ("venda_id", "count"),
        ticket_medio   = ("ticket_medio", "mean"),
    ).round(2).reset_index().sort_values("total_vendas", ascending=False)
    ranking["rank_vendas"] = ranking["total_vendas"].rank(ascending=False).astype(int)

    # YoY por loja
    por_ano = df.groupby(["loja_id", "ano"]).agg(
        vendas_ano = ("valor_total", "sum")
    ).reset_index()
    por_ano_sorted = por_ano.sort_values(["loja_id", "ano"])
    por_ano["vendas_ano_anterior"] = por_ano_sorted.groupby("loja_id")["vendas_ano"].shift(1).values
    por_ano["variacao_yoy_pct"] = (
        (por_ano["vendas_ano"] - por_ano["vendas_ano_anterior"])
        / por_ano["vendas_ano_anterior"] * 100
    ).round(2)

    # Mescla YoY 2024 no ranking principal
    yoy_2024 = por_ano[por_ano["ano"] == 2024][["loja_id", "variacao_yoy_pct"]]
    ranking = ranking.merge(yoy_2024, on="loja_id", how="left")

    return ranking

def fato_detalhada(m):
    """NOVA — Fato detalhada por dia/produto/loja para drill-through.
    Granularidade fina para detalhar, leve para o Power BI."""
    df = m["fato"].merge(m["tempo"][["sk_tempo","data","ano","mes","nome_mes"]], on="sk_tempo") \
                  .merge(m["produto"][["sk_produto","nome","categoria"]], on="sk_produto") \
                  .merge(m["loja"][["sk_loja","nome_loja","cidade","estado","regiao"]], on="sk_loja")
    det = df.groupby(["data","ano","mes","nome_mes","regiao","estado","cidade",
                      "nome_loja","nome","categoria"]).agg(
        valor_total = ("valor_total","sum"),
        margem      = ("margem","sum"),
        quantidade  = ("quantidade","sum"),
        qtd_vendas  = ("venda_id","count"),
    ).round(2).reset_index()
    return det

def analise_pascoa(m):
    """Análise específica do período de Páscoa — mantida igual."""
    df = m["fato"].merge(m["tempo"], on="sk_tempo") \
                  .merge(m["produto"], on="sk_produto")
    pascoa = df[df["is_pascoa"]].groupby(["ano", "nome", "categoria"]).agg(
        total_vendas = ("valor_total", "sum"),
        qtd_vendida  = ("quantidade", "sum"),
        margem_media = ("margem_pct", "mean"),
    ).round(2).reset_index().sort_values(["ano", "total_vendas"], ascending=[True, False])
    return pascoa

if __name__ == "__main__":
    print("\n🍫 Cacau Analytics — Geração de Insights (Gold Layer) v2\n")
    m = carregar_modelo()

    sazonalidade         = analise_sazonalidade(m)
    regiao               = analise_por_regiao(m)
    mix_produto          = analise_mix_produto(m)
    lojas                = analise_por_loja(m)
    pascoa               = analise_pascoa(m)
    detalhada            = fato_detalhada(m)

    # Gold Layer — nomes mantidos para não quebrar conexões Power BI
    sazonalidade.to_csv(        f"{GOLD_DIR}/gold_sazonalidade.csv",        index=False)
    regiao.to_csv(              f"{GOLD_DIR}/gold_regiao.csv",              index=False)
    mix_produto.to_csv(         f"{GOLD_DIR}/gold_mix_produto.csv",         index=False)
    lojas.to_csv(               f"{GOLD_DIR}/gold_ranking_lojas.csv",       index=False)
    pascoa.to_csv(              f"{GOLD_DIR}/gold_analise_pascoa.csv",       index=False)
    detalhada.to_csv(           f"{GOLD_DIR}/gold_vendas_detalhada.csv",    index=False)

    print("📊 TOP INSIGHTS\n")
    print("── Sazonalidade ──────────────────────────────")
    media_normal = sazonalidade[~sazonalidade["is_data_especial"]]["total_vendas"].mean()
    media_pascoa = sazonalidade[sazonalidade["is_pascoa"]]["total_vendas"].mean()
    print(f"   Venda média dias normais  : R$ {media_normal:,.0f}")
    print(f"   Venda média período Páscoa: R$ {media_pascoa:,.0f}")
    print(f"   Fator Páscoa              : {media_pascoa/media_normal:.1f}x\n")

    print("── YoY Sazonalidade ─────────────────────────")
    yoy = sazonalidade[sazonalidade["ano"] == 2024][["nome_mes", "total_vendas", "variacao_yoy_pct"]].head(6)
    for _, r in yoy.iterrows():
        sinal = "▲" if (r["variacao_yoy_pct"] or 0) > 0 else "▼"
        print(f"   {r['nome_mes']:10} R$ {r['total_vendas']:>12,.0f}  {sinal} {abs(r['variacao_yoy_pct'] or 0):.1f}%")

    print("\n── Top 3 regiões por faturamento ────────────")
    for _, r in regiao.head(3).iterrows():
        print(f"   {r['regiao']:15} R$ {r['total_vendas']:>12,.0f}")

    print("\n── Sazonalidade agora por região ──────────────")
    print(f"   {len(sazonalidade)} linhas (ano x mês x região)")

    print("\n── Fato detalhada (drill-through) ─────────────")
    print(f"   {len(detalhada):,} linhas (dia x loja x produto)")

    print("\n✅ Gold Layer v2 salvo em data/gold/\n")
