"""
gerador_dados.py
Gera dados sintéticos realistas de vendas de uma rede de franquias de chocolate.
Simula sazonalidade brasileira: Páscoa, Natal, Dia das Mães, etc.
"""

import pandas as pd
import numpy as np
from datetime import date, timedelta
import random
import os

random.seed(42)
np.random.seed(42)

# ─── Configurações ────────────────────────────────────────────────────────────
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─── Dados mestres ────────────────────────────────────────────────────────────
PRODUTOS = [
    {"id": "P001", "nome": "Trufa Belga Dark 200g",       "categoria": "Trufas",     "linha": "Premium", "preco_base": 45.90, "custo_base": 18.00},
    {"id": "P002", "nome": "Trufa Avelã ao Leite 200g",   "categoria": "Trufas",     "linha": "Premium", "preco_base": 42.90, "custo_base": 17.00},
    {"id": "P003", "nome": "Ovo de Páscoa 500g",          "categoria": "Ovos",       "linha": "Premium", "preco_base": 89.90, "custo_base": 32.00},
    {"id": "P004", "nome": "Ovo de Páscoa 250g",          "categoria": "Ovos",       "linha": "Classic", "preco_base": 49.90, "custo_base": 18.00},
    {"id": "P005", "nome": "Tablete Dark 70% 100g",       "categoria": "Tabletes",   "linha": "Classic", "preco_base": 12.90, "custo_base": 4.50},
    {"id": "P006", "nome": "Tablete Ao Leite 100g",       "categoria": "Tabletes",   "linha": "Classic", "preco_base": 10.90, "custo_base": 3.80},
    {"id": "P007", "nome": "Bombom Sortido Cx 300g",      "categoria": "Bombons",    "linha": "Premium", "preco_base": 38.90, "custo_base": 14.00},
    {"id": "P008", "nome": "Bombom Individual",           "categoria": "Bombons",    "linha": "Classic", "preco_base": 3.90,  "custo_base": 1.20},
    {"id": "P009", "nome": "Kit Presente Namorados",      "categoria": "Kits",       "linha": "Premium", "preco_base": 120.00,"custo_base": 45.00},
    {"id": "P010", "nome": "Panetone Recheado 400g",      "categoria": "Sazonais",   "linha": "Classic", "preco_base": 35.90, "custo_base": 13.00},
]

LOJAS = [
    {"id": "L001", "nome": "Shopping Ibirapuera",  "cidade": "São Paulo",      "estado": "SP", "regiao": "Sudeste", "tipo": "Shopping"},
    {"id": "L002", "nome": "Rua Oscar Freire",     "cidade": "São Paulo",      "estado": "SP", "regiao": "Sudeste", "tipo": "Rua"},
    {"id": "L003", "nome": "Shopping Eldorado",    "cidade": "São Paulo",      "estado": "SP", "regiao": "Sudeste", "tipo": "Shopping"},
    {"id": "L004", "nome": "Barra Shopping",       "cidade": "Rio de Janeiro", "estado": "RJ", "regiao": "Sudeste", "tipo": "Shopping"},
    {"id": "L005", "nome": "Shopping Tijuca",      "cidade": "Rio de Janeiro", "estado": "RJ", "regiao": "Sudeste", "tipo": "Shopping"},
    {"id": "L006", "nome": "Shopping Mueller",     "cidade": "Curitiba",       "estado": "PR", "regiao": "Sul",     "tipo": "Shopping"},
    {"id": "L007", "nome": "Rua XV de Novembro",   "cidade": "Curitiba",       "estado": "PR", "regiao": "Sul",     "tipo": "Rua"},
    {"id": "L008", "nome": "Shopping Iguatemi POA","cidade": "Porto Alegre",   "estado": "RS", "regiao": "Sul",     "tipo": "Shopping"},
    {"id": "L009", "nome": "Shopping Recife",      "cidade": "Recife",         "estado": "PE", "regiao": "Nordeste","tipo": "Shopping"},
    {"id": "L010", "nome": "Shopping Bela Vista",  "cidade": "Salvador",       "estado": "BA", "regiao": "Nordeste","tipo": "Shopping"},
    {"id": "L011", "nome": "Conjunto Nacional BSB","cidade": "Brasília",       "estado": "DF", "regiao": "Centro-Oeste","tipo": "Shopping"},
    {"id": "L012", "nome": "Shopping Manaus",      "cidade": "Manaus",         "estado": "AM", "regiao": "Norte",   "tipo": "Shopping"},
]

VENDEDORES = [
    {"id": "V001", "nome": "Ana Paula Silva",    "equipe": "A"},
    {"id": "V002", "nome": "Carlos Mendes",      "equipe": "A"},
    {"id": "V003", "nome": "Fernanda Costa",     "equipe": "B"},
    {"id": "V004", "nome": "Ricardo Oliveira",   "equipe": "B"},
    {"id": "V005", "nome": "Juliana Martins",    "equipe": "C"},
    {"id": "V006", "nome": "Marcos Souza",       "equipe": "C"},
]

# ─── Datas comemorativas brasileiras ─────────────────────────────────────────
def get_fator_sazonalidade(data: date) -> float:
    """Retorna multiplicador de volume para datas especiais."""
    mes, dia = data.month, data.day

    # Páscoa 2023: 9 abr | Páscoa 2024: 31 mar (aprox 3 semanas antes)
    pascoa_2023 = (date(2023, 3, 20) <= data <= date(2023, 4, 9))
    pascoa_2024 = (date(2024, 3, 11) <= data <= date(2024, 3, 31))

    # Dia das Mães (2º domingo de maio) — semana anterior
    maes_2023 = (date(2023, 5, 1) <= data <= date(2023, 5, 14))
    maes_2024 = (date(2024, 5, 1) <= data <= date(2024, 5, 12))

    # Namorados — 12 de junho
    namorados = (mes == 6 and 5 <= dia <= 12)

    # Natal — dezembro todo
    natal = (mes == 12)

    # Dia dos Pais — 2º domingo de agosto
    pais = (mes == 8 and 5 <= dia <= 13)

    if pascoa_2023 or pascoa_2024:
        return np.random.uniform(3.0, 4.5)   # pico altíssimo
    elif maes_2023 or maes_2024:
        return np.random.uniform(2.0, 3.0)
    elif natal:
        return np.random.uniform(1.8, 2.8)
    elif namorados:
        return np.random.uniform(1.5, 2.2)
    elif pais:
        return np.random.uniform(1.3, 1.8)
    else:
        # Variação semanal: fim de semana vende mais
        if data.weekday() >= 5:
            return np.random.uniform(1.1, 1.4)
        return np.random.uniform(0.7, 1.1)

def produto_ativo_na_data(produto: dict, data: date) -> bool:
    """Ovos e Panetone só aparecem nas épocas corretas."""
    if produto["categoria"] == "Ovos":
        mes = data.month
        return mes in [2, 3, 4]  # fev-abr = Páscoa
    if produto["nome"].startswith("Panetone"):
        return data.month in [11, 12]
    if produto["id"] == "P009":  # Kit Namorados
        return data.month in [5, 6]
    return True

# ─── Geração das vendas ───────────────────────────────────────────────────────
def gerar_vendas():
    print("⚙️  Gerando dados de vendas...")
    registros = []
    venda_id = 1

    start = date(2023, 1, 1)
    end   = date(2024, 12, 31)
    delta = timedelta(days=1)
    current = start

    while current <= end:
        fator_global = get_fator_sazonalidade(current)

        for loja in LOJAS:
            # Lojas de shopping vendem mais
            fator_loja = 1.3 if loja["tipo"] == "Shopping" else 1.0
            # Sudeste tem mais volume
            fator_regiao = {"Sudeste": 1.4, "Sul": 1.1, "Nordeste": 0.9,
                            "Centro-Oeste": 0.85, "Norte": 0.7}.get(loja["regiao"], 1.0)

            n_transacoes = int(np.random.poisson(8 * fator_global * fator_loja * fator_regiao))

            for _ in range(n_transacoes):
                produto = random.choice([p for p in PRODUTOS if produto_ativo_na_data(p, current)])
                vendedor = random.choice(VENDEDORES)
                qtd = max(1, int(np.random.poisson(2.5)))

                # Desconto maior em datas sazonais (promoções)
                desconto_pct = 0.0
                if fator_global > 2.0:
                    desconto_pct = round(random.choice([0, 5, 10, 15]) / 100, 2)

                preco_unit = round(produto["preco_base"] * (1 - desconto_pct), 2)
                custo_unit = produto["custo_base"]
                valor_total = round(preco_unit * qtd, 2)
                custo_total = round(custo_unit * qtd, 2)
                margem = round(valor_total - custo_total, 2)

                registros.append({
                    "venda_id":      venda_id,
                    "data":          current.isoformat(),
                    "loja_id":       loja["id"],
                    "produto_id":    produto["id"],
                    "vendedor_id":   vendedor["id"],
                    "quantidade":    qtd,
                    "preco_unitario":preco_unit,
                    "desconto_pct":  desconto_pct,
                    "valor_total":   valor_total,
                    "custo_total":   custo_total,
                    "margem":        margem,
                })
                venda_id += 1

        current += delta

    df = pd.DataFrame(registros)
    print(f"   ✅ {len(df):,} registros gerados")
    return df

# ─── Exportação ───────────────────────────────────────────────────────────────
def exportar_masters():
    pd.DataFrame(PRODUTOS).to_csv(f"{OUTPUT_DIR}/dim_produto_raw.csv", index=False)
    pd.DataFrame(LOJAS).to_csv(f"{OUTPUT_DIR}/dim_loja_raw.csv", index=False)
    pd.DataFrame(VENDEDORES).to_csv(f"{OUTPUT_DIR}/dim_vendedor_raw.csv", index=False)
    print("   ✅ Tabelas mestres exportadas")

if __name__ == "__main__":
    print("\n🍫 Cacau Analytics — Gerador de Dados\n")
    exportar_masters()
    df_vendas = gerar_vendas()
    df_vendas.to_csv(f"{OUTPUT_DIR}/fato_vendas_raw.csv", index=False)
    print(f"\n📁 Arquivos gerados em: {OUTPUT_DIR}")
    print(f"   - fato_vendas_raw.csv    ({len(df_vendas):,} linhas)")
    print(f"   - dim_produto_raw.csv    ({len(PRODUTOS)} produtos)")
    print(f"   - dim_loja_raw.csv       ({len(LOJAS)} lojas)")
    print(f"   - dim_vendedor_raw.csv   ({len(VENDEDORES)} vendedores)")
