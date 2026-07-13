#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import csv
from pathlib import Path

DOC = Path(r"C:\Users\gabriel.evangelista\Documents\ClaudeGL\Documentos")

def campo(row, *keywords):
    """Retorna o valor da primeira coluna cujo nome contenha todas as keywords."""
    for kws in keywords:
        kws_list = kws if isinstance(kws, (list, tuple)) else [kws]
        for k, v in row.items():
            if all(kw in k for kw in kws_list) and v.strip():
                return v.strip()
    return ""

def ler_csv(arq):
    rows = []
    with open(arq, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            norm = {k.lower(): v.strip() for k, v in row.items()}
            rows.append(norm)
    return rows

def processar_cliente(arq):
    nome_cliente = arq.name.replace("nps___", "").split("_2026-07-07")[0].replace("_", " ").title()
    rows = ler_csv(arq)

    # Filtrar contas internas da Efcaz
    rows = [r for r in rows if "efcaz.com.br" not in campo(r, "email").lower()]

    respondentes, nao_respondentes = [], []

    for r in rows:
        nota_raw = campo(r, "nota")
        nome     = campo(r, "nome")
        email    = campo(r, "email")
        motivo   = campo(r, "motivo")
        views_raw = campo(r, "exibicao", "qtdd")
        views    = int(views_raw) if views_raw else 0

        if nota_raw:
            respondentes.append({"nota": int(nota_raw), "nome": nome, "email": email,
                                  "motivo": motivo, "views": views})
        else:
            nao_respondentes.append({"nome": nome, "email": email, "views": views})

    promoters  = [r for r in respondentes if r["nota"] >= 9]
    passivos   = [r for r in respondentes if 7 <= r["nota"] <= 8]
    detratores = [r for r in respondentes if r["nota"] <= 6]

    nao_resp_sorted = sorted(nao_respondentes, key=lambda x: -x["views"])
    heavy = [x for x in nao_resp_sorted if x["views"] >= 3]

    n = len(respondentes)
    nps = round((len(promoters) - len(detratores)) / n * 100) if n else None

    return {
        "cliente": nome_cliente,
        "total_exibicoes": len(rows),
        "respondentes": respondentes,
        "nao_resp": nao_resp_sorted,
        "heavy": heavy,
        "promoters": promoters,
        "passivos": passivos,
        "detratores": detratores,
        "nps": nps,
    }

# ─── PROCESSAR TODOS ─────────────────────────────────────────────────────────
arquivos = sorted(DOC.glob("nps___*_2026-07-07*.csv"))
resultados = [processar_cliente(a) for a in arquivos]

com_resposta  = [r for r in resultados if r["respondentes"]]
sem_resposta  = [r for r in resultados if not r["respondentes"] and r["total_exibicoes"] > 0]
sem_acesso    = [r for r in resultados if r["total_exibicoes"] == 0]

total_resp     = sum(len(r["respondentes"])  for r in resultados)
total_exib     = sum(r["total_exibicoes"]    for r in resultados)
all_promoters  = sum(len(r["promoters"])     for r in resultados)
all_passivos   = sum(len(r["passivos"])      for r in resultados)
all_detratores = sum(len(r["detratores"])    for r in resultados)

nps_geral     = round((all_promoters - all_detratores) / total_resp * 100) if total_resp else 0
taxa_resposta = round(total_resp / total_exib * 100, 1) if total_exib else 0

print("=" * 72)
print("  NPS CARTEIRA EFCAZ — BASE 07/07/2026")
print("=" * 72)
print(f"  Total de clientes:      {len(resultados)}")
print(f"  Com resposta:           {len(com_resposta)}")
print(f"  Acessam, sem resposta:  {len(sem_resposta)}")
print(f"  Sem acesso algum:       {len(sem_acesso)}")
print(f"  Total exibições:        {total_exib}")
print(f"  Total respondentes:     {total_resp}")
print(f"  Taxa de resposta:       {taxa_resposta}%")
print(f"  Promoters:              {all_promoters}")
print(f"  Passivos:               {all_passivos}")
print(f"  Detratores:             {all_detratores}")
print(f"  NPS GERAL:              {nps_geral:+d}")

print()
print("─" * 72)
print("  DETRATORES E PASSIVOS")
print("─" * 72)
for r in resultados:
    for p in r["detratores"] + r["passivos"]:
        cat = "DETRATOR" if p["nota"] <= 6 else "PASSIVO "
        mot = f"\n    '{p['motivo']}'" if p["motivo"] else ""
        print(f"  [{cat} {p['nota']}] {r['cliente']:30s} — {p['nome']}{mot}")

print()
print("─" * 72)
print("  SEM ACESSO")
print("─" * 72)
print("  Nenhum" if not sem_acesso else "\n".join(f"  {r['cliente']}" for r in sem_acesso))

print()
print("─" * 72)
print("  ACESSAM MAS NÃO RESPONDERAM")
print("─" * 72)
for r in sorted(sem_resposta, key=lambda x: -x["total_exibicoes"]):
    heavy_str = ", ".join(f"{x['nome']} ({x['views']}v)" for x in r["heavy"][:3])
    print(f"  {r['cliente']:35s} | {r['total_exibicoes']} exib | {heavy_str}")

print()
print("─" * 72)
print("  CLIENTES COM RESPOSTA (por NPS)")
print("─" * 72)
for r in sorted(com_resposta, key=lambda x: -(x["nps"] or 0)):
    nps_str = f"NPS {r['nps']:+d}" if r["nps"] is not None else "sem NPS"
    p  = len(r["promoters"]); pa = len(r["passivos"]); d = len(r["detratores"])
    n  = len(r["respondentes"])
    print(f"  {r['cliente']:35s} | {n:2d} resp | {nps_str:10s} | P:{p} Pa:{pa} D:{d}")

print()
print("─" * 72)
print("  PROMOTERS COM COMENTÁRIO")
print("─" * 72)
for r in resultados:
    for p in r["promoters"]:
        if p["motivo"]:
            print(f"  [{p['nota']}] {r['cliente']:30s} / {p['nome']}: '{p['motivo']}'")

# ─── DEBUG: verificar campos por cliente (comentar quando OK) ─────────────────
# print("\n\n=== DEBUG CAMPOS ===")
# for a in arquivos[:3]:
#     rows = ler_csv(a)
#     if rows:
#         print(f"\n{a.name}:")
#         print(list(rows[0].keys()))
