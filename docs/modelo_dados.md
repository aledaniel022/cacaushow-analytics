# Modelo de Dados — Cacau Analytics

## Arquitetura Medallion

```
Bronze  →  Silver  →  Gold
  CSV       Parquet    CSV agregado
(bruto)   (limpo)    (BI-ready)
```

## Tabelas

### fato_vendas
Granularidade: **1 linha = 1 transação de venda**

| Coluna | Tipo | Descrição |
|---|---|---|
| venda_id | INT | Chave natural da venda |
| sk_tempo | INT | FK → dim_tempo |
| sk_produto | INT | FK → dim_produto |
| sk_loja | INT | FK → dim_loja |
| sk_vendedor | INT | FK → dim_vendedor |
| quantidade | INT | Qtd de itens vendidos |
| preco_unitario | FLOAT | Preço após desconto |
| desconto_pct | FLOAT | % de desconto aplicado |
| valor_total | FLOAT | Receita bruta |
| custo_total | FLOAT | Custo dos produtos |
| margem | FLOAT | Lucro bruto |
| margem_pct | FLOAT | % de margem |
| ticket_medio | FLOAT | Valor por unidade |

### dim_tempo
| Coluna | Tipo | Descrição |
|---|---|---|
| sk_tempo | INT (PK) | YYYYMMDD |
| data | DATE | Data completa |
| ano | INT | |
| trimestre | INT | 1–4 |
| mes | INT | 1–12 |
| nome_mes | STRING | |
| semana_ano | INT | ISO week |
| dia_semana_num | INT | 0=Seg, 6=Dom |
| nome_dia | STRING | |
| is_fim_semana | BOOL | |
| is_pascoa | BOOL | ⭐ crítico para chocolate |
| is_natal | BOOL | |
| is_dias_maes | BOOL | |
| is_namorados | BOOL | |
| is_dias_pais | BOOL | |
| is_data_especial | BOOL | OR de todos acima |

### dim_produto
| Coluna | Tipo | Descrição |
|---|---|---|
| sk_produto | INT (PK) | Surrogate key |
| produto_id | STRING | Chave natural |
| nome | STRING | Nome do produto |
| categoria | STRING | Trufas, Ovos, Tabletes... |
| linha | STRING | Premium / Classic |
| preco_base | FLOAT | |
| custo_base | FLOAT | |
| faixa_preco | STRING | Econômico → Super Premium |
| margem_bruta_pct | FLOAT | % margem do produto |

### dim_loja
| Coluna | Tipo | Descrição |
|---|---|---|
| sk_loja | INT (PK) | Surrogate key |
| loja_id | STRING | Chave natural |
| nome_loja | STRING | |
| cidade | STRING | |
| estado | STRING | UF |
| nome_estado | STRING | |
| regiao | STRING | Sudeste, Sul... |
| tipo | STRING | Shopping / Rua |

### dim_vendedor
| Coluna | Tipo | Descrição |
|---|---|---|
| sk_vendedor | INT (PK) | Surrogate key |
| vendedor_id | STRING | Chave natural |
| nome_vendedor | STRING | |
| equipe | STRING | A / B / C |

## Decisões de Modelagem

**Por que Star Schema e não Snowflake?**
Power BI performa melhor com Star Schema. Evita JOINs em cascata e simplifica DAX.

**Por que Surrogate Keys inteiras?**
Joins inteiros são mais rápidos que string. Padrão Kimball.

**Por que `is_pascoa` na dim_tempo e não na fato?**
Atributo da data, não da venda. Permite filtrar períodos sem alterar a fato.
