"""
run_all.py
Orquestrador do pipeline completo.
  Passo 1: Gera dados sintéticos (Bronze)
  Passo 2: Transforma e modela em estrela (Silver / Parquet)
  Passo 3: Gera Gold Layer com insights prontos para BI
"""

import subprocess
import sys
import os

BASE = os.path.dirname(__file__)

passos = [
    ("Bronze — Geração de dados",         os.path.join(BASE, "00_gerador_dados.py")),
    ("Silver — Transformação e modelagem", os.path.join(BASE, "01_transformacao.py")),
    ("Gold   — Insights e agregações",    os.path.join(BASE, "02_insights.py")),
]

print("\n" + "="*55)
print("  🍫 Cacau Analytics — Pipeline Completo")
print("="*55)

for titulo, script in passos:
    print(f"\n▶ {titulo}")
    resultado = subprocess.run([sys.executable, script], capture_output=False)
    if resultado.returncode != 0:
        print(f"\n❌ Erro no passo: {titulo}")
        sys.exit(1)

print("\n" + "="*55)
print("  ✅ Pipeline finalizado com sucesso!")
print("  📁 Conecte o Power BI em: data/gold/")
print("="*55 + "\n")
