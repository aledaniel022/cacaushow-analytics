"""
02_insights.py
Gera análises prontas para o README e para apresentar na entrevista.
Produz CSVs de ouro (Gold Layer) prontos para o Power BI.
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
    """Vendas mensais com flag de datas especiais."""
    df = m["fato"].merge(m["tempo"], on="sk_tempo")
    mensal = df.groupby(["ano", "mes", "nome_mes", "is_pascoa", "is_natal",
                          "is_dias_maes", "is_namorados", "is_data_especial"]).agg(
        total_vendas   = ("valor_total", "sum"),
        total_margem   = ("margem", "sum"),
        qtd_transacoes = ("venda_id", "count"),
    ).reset_index()
    mensal["ticket_medio"] = (mensal["total_vendas"] / mensal["qtd_transacoes"]).round(2)
    mensal["total_vendas"]  = mensal["total_vendas"].round(2)
    mensal["total_margem"]  = mensal["total_margem"].round(2)
    return mensal

def analise_por_regiao(m):
    """Performance por região e estado."""
    df = m["fato"].merge(m["loja"], on="sk_loja")
    return df.groupby(["regiao", "estado", "nome_estado"]).agg(
        total_vendas   = ("valor_total", "sum"),
        total_margem   = ("margem", "sum"),
        qtd_transacoes = ("venda_id", "count"),
        ticket_medio   = ("ticket_medio", "mean"),
    ).round(2).reset_index().sort_values("total_vendas", ascending=False)

def analise_mix_produto(m):
    """Ranking de produtos por margem e volume."""
    df = m["fato"].merge(m["produto"], on="sk_produto")
    return df.groupby(["produto_id", "nome", "categoria", "linha", "faixa_preco"]).agg(
        total_vendas   = ("valor_total", "sum"),
        total_margem   = ("margem", "sum"),
        qtd_vendida    = ("quantidade", "sum"),
        qtd_transacoes = ("venda_id", "count"),
        margem_media   = ("margem_pct", "mean"),
    ).round(2).reset_index().sort_values("total_margem", ascending=False)

def analise_por_loja(m):
    """Ranking de lojas — útil para gestão de franquias."""
    df = m["fato"].merge(m["loja"], on="sk_loja")
    ranking = df.groupby(["loja_id", "nome_loja", "cidade", "estado", "regiao", "tipo"]).agg(
        total_vendas   = ("valor_total", "sum"),
        total_margem   = ("margem", "sum"),
        qtd_transacoes = ("venda_id", "count"),
        ticket_medio   = ("ticket_medio", "mean"),
    ).round(2).reset_index().sort_values("total_vendas", ascending=False)
    ranking["rank_vendas"] = ranking["total_vendas"].rank(ascending=False).astype(int)
    return ranking

def analise_pascoa(m):
    """Análise específica do período de Páscoa — o pico da Cacau Show."""
    df = m["fato"].merge(m["tempo"], on="sk_tempo") \
                  .merge(m["produto"], on="sk_produto")
    pascoa = df[df["is_pascoa"]].groupby(["ano", "nome", "categoria"]).agg(
        total_vendas = ("valor_total", "sum"),
        qtd_vendida  = ("quantidade", "sum"),
        margem_media = ("margem_pct", "mean"),
    ).round(2).reset_index().sort_values(["ano", "total_vendas"], ascending=[True, False])
    return pascoa

if __name__ == "__main__":
    print("\n🍫 Cacau Analytics — Geração de Insights (Gold Layer)\n")
    m = carregar_modelo()

    sazonalidade = analise_sazonalidade(m)
    regiao       = analise_por_regiao(m)
    mix_produto  = analise_mix_produto(m)
    lojas        = analise_por_loja(m)
    pascoa       = analise_pascoa(m)

    # Salvar Gold Layer (prontos para Power BI)
    sazonalidade.to_csv(f"{GOLD_DIR}/gold_sazonalidade.csv",   index=False)
    regiao.to_csv(      f"{GOLD_DIR}/gold_regiao.csv",         index=False)
    mix_produto.to_csv( f"{GOLD_DIR}/gold_mix_produto.csv",    index=False)
    lojas.to_csv(       f"{GOLD_DIR}/gold_ranking_lojas.csv",  index=False)
    pascoa.to_csv(      f"{GOLD_DIR}/gold_analise_pascoa.csv", index=False)

    # Print dos principais insights
    print("📊 TOP INSIGHTS\n")
    print("── Sazonalidade ──────────────────────────────")
    media_normal = sazonalidade[~sazonalidade["is_data_especial"]]["total_vendas"].mean()
    media_pascoa = sazonalidade[sazonalidade["is_pascoa"]]["total_vendas"].mean()
    print(f"   Venda média dias normais : R$ {media_normal:,.0f}")
    print(f"   Venda média período Páscoa: R$ {media_pascoa:,.0f}")
    print(f"   Fator Páscoa             : {media_pascoa/media_normal:.1f}x\n")

    print("── Top 3 regiões por faturamento ────────────")
    for _, r in regiao.head(3).iterrows():
        print(f"   {r['regiao']:15} R$ {r['total_vendas']:>12,.0f}")
    print()

    print("── Top 3 produtos por margem ────────────────")
    for _, p in mix_produto.head(3).iterrows():
        print(f"   {p['nome'][:30]:30} margem: {p['margem_media']:.1f}%")
    print()

    print("✅ Gold Layer salvo em data/gold/\n")
