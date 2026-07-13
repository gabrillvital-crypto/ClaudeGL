#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import csv
from pathlib import Path

DIR_ANT = Path(r"C:\Users\gabriel.evangelista\Documents\ClaudeGL\clientes\NPS")
DIR_ATU = Path(r"C:\Users\gabriel.evangelista\Documents\ClaudeGL\Documentos")

def campo(row, *keywords):
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

def processar_cliente(arq, nome_cliente):
    rows = ler_csv(arq)
    rows = [r for r in rows if "efcaz.com.br" not in campo(r, "email").lower()]

    respondentes, nao_respondentes = [], []
    for r in rows:
        nota_raw  = campo(r, "nota")
        nome      = campo(r, "nome")
        email     = campo(r, "email")
        motivo    = campo(r, "motivo")
        views_raw = campo(r, "exibicao", "qtdd")
        views     = int(views_raw) if views_raw else 0

        if nota_raw:
            respondentes.append({"nota": int(nota_raw), "nome": nome, "email": email,
                                  "motivo": motivo, "views": views})
        else:
            nao_respondentes.append({"nome": nome, "email": email, "views": views})

    promoters  = [r for r in respondentes if r["nota"] >= 9]
    passivos   = [r for r in respondentes if 7 <= r["nota"] <= 8]
    detratores = [r for r in respondentes if r["nota"] <= 6]
    n = len(respondentes)
    nps = round((len(promoters) - len(detratores)) / n * 100) if n else None

    return {
        "cliente": nome_cliente,
        "total_exibicoes": len(rows),
        "n_resp": n,
        "promoters": len(promoters),
        "passivos": len(passivos),
        "detratores": len(detratores),
        "nps": nps,
        "respondentes": respondentes,
        "nao_resp": nao_respondentes,
    }

def processar_pasta(pasta, sufixo_data):
    arquivos = sorted(pasta.glob(f"nps___*{sufixo_data}*.csv"))
    resultado = {}
    for arq in arquivos:
        # extrai nome do cliente do nome do arquivo
        nome = arq.name.replace("nps___", "").split(sufixo_data)[0].rstrip("_").replace("_", " ").title()
        resultado[nome] = processar_cliente(arq, nome)
    return resultado

# Processar as duas bases
ant = processar_pasta(DIR_ANT,  "2026-06-19")
atu = processar_pasta(DIR_ATU,  "2026-07-07")

# Union de todos os clientes
todos_clientes = sorted(set(list(ant.keys()) + list(atu.keys())))

# ─── SUMÁRIOS ────────────────────────────────────────────────────────────────
def sumario(dados):
    vals = list(dados.values())
    total_resp  = sum(v["n_resp"]          for v in vals)
    total_exib  = sum(v["total_exibicoes"] for v in vals)
    all_p       = sum(v["promoters"]       for v in vals)
    all_pa      = sum(v["passivos"]        for v in vals)
    all_d       = sum(v["detratores"]      for v in vals)
    nps_g       = round((all_p - all_d) / total_resp * 100) if total_resp else 0
    taxa        = round(total_resp / total_exib * 100, 1) if total_exib else 0
    com_resp    = sum(1 for v in vals if v["n_resp"] > 0)
    sem_resp    = sum(1 for v in vals if v["n_resp"] == 0 and v["total_exibicoes"] > 0)
    sem_acesso  = sum(1 for v in vals if v["total_exibicoes"] == 0)
    return {"clientes": len(vals), "com_resp": com_resp, "sem_resp": sem_resp,
            "sem_acesso": sem_acesso, "total_exib": total_exib, "total_resp": total_resp,
            "taxa": taxa, "promoters": all_p, "passivos": all_pa, "detratores": all_d,
            "nps": nps_g}

sa = sumario(ant)
su = sumario(atu)

def delta(a, b, fmt="+d"):
    d = b - a
    return f"{d:+d}" if fmt == "+d" else f"{d:+.1f}"

print("=" * 80)
print("  COMPARATIVO NPS — 19/06/2026  →  07/07/2026")
print("=" * 80)
linha = f"  {'MÉTRICA':<30} {'19/06':>8} {'07/07':>8} {'Δ':>8}"
print(linha)
print("─" * 80)

metricas = [
    ("Total de clientes",       sa["clientes"],    su["clientes"],    "+d"),
    ("Com resposta",            sa["com_resp"],    su["com_resp"],    "+d"),
    ("Acessam, sem resposta",   sa["sem_resp"],    su["sem_resp"],    "+d"),
    ("Sem acesso",              sa["sem_acesso"],  su["sem_acesso"],  "+d"),
    ("Total exibições",         sa["total_exib"],  su["total_exib"],  "+d"),
    ("Total respondentes",      sa["total_resp"],  su["total_resp"],  "+d"),
    ("Taxa de resposta (%)",    sa["taxa"],        su["taxa"],        "+f"),
    ("Promoters",               sa["promoters"],   su["promoters"],   "+d"),
    ("Passivos",                sa["passivos"],    su["passivos"],    "+d"),
    ("Detratores",              sa["detratores"],  su["detratores"],  "+d"),
    ("NPS GERAL",               sa["nps"],         su["nps"],         "+d"),
]

for label, va, vu, fmt in metricas:
    d = vu - va
    if fmt == "+f":
        d_str = f"{d:+.1f}"
        va_str = f"{va:.1f}"
        vu_str = f"{vu:.1f}"
    else:
        d_str = f"{d:+d}"
        va_str = str(va)
        vu_str = str(vu)
    print(f"  {label:<30} {va_str:>8} {vu_str:>8} {d_str:>8}")

# ─── POR CLIENTE ──────────────────────────────────────────────────────────────
print()
print("=" * 80)
print("  DETALHAMENTO POR CLIENTE")
print("=" * 80)
print(f"  {'CLIENTE':<32} {'NPS ant':>7} {'NPS atu':>7} {'Δ NPS':>7} {'Resp ant':>8} {'Resp atu':>8} {'STATUS'}")
print("─" * 80)

for cli in todos_clientes:
    a = ant.get(cli)
    u = atu.get(cli)

    nps_a   = f"{a['nps']:+d}"  if a and a["nps"] is not None else "—"
    nps_u   = f"{u['nps']:+d}"  if u and u["nps"] is not None else "—"
    resp_a  = str(a["n_resp"])  if a else "—"
    resp_u  = str(u["n_resp"])  if u else "—"

    if a and u and a["nps"] is not None and u["nps"] is not None:
        d = u["nps"] - a["nps"]
        d_str = f"{d:+d}"
        if d > 0:   status = "↑ melhora"
        elif d < 0: status = "↓ piora"
        else:        status = "= estável"
    elif u and u["n_resp"] > 0 and (not a or a["n_resp"] == 0):
        d_str = "novo"; status = "★ nova resposta"
    elif a and a["n_resp"] > 0 and (not u or u["n_resp"] == 0):
        d_str = "perdeu"; status = "✗ sem resposta agora"
    else:
        d_str = "—"; status = ""

    print(f"  {cli:<32} {nps_a:>7} {nps_u:>7} {d_str:>7} {resp_a:>8} {resp_u:>8}  {status}")

# ─── NOVOS DETRATORES/PASSIVOS ────────────────────────────────────────────────
print()
print("=" * 80)
print("  DETRATORES E PASSIVOS — AMBAS AS BASES")
print("=" * 80)
for cli in todos_clientes:
    for base_label, dados in [("19/06", ant.get(cli)), ("07/07", atu.get(cli))]:
        if not dados:
            continue
        for p in dados["respondentes"]:
            if p["nota"] <= 8:
                cat = "DETRATOR" if p["nota"] <= 6 else "PASSIVO "
                mot = f" | '{p['motivo']}'" if p["motivo"] else ""
                print(f"  [{base_label}] [{cat} {p['nota']}] {cli:28s} — {p['nome']}{mot}")
