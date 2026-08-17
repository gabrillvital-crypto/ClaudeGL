"""
email_semanal_zurich.py
Gera e-mail HTML semanal do Dashboard Zurich Airport (circulação interna).
Inclui comparativo geral (KPIs) + evolução de competência R3 e R4.

Uso: python email_semanal_zurich.py
Saída: email_semanal_zurich.html
       → abrir no browser, Ctrl+A, Ctrl+C, colar no Outlook/Gmail
"""
import os
from datetime import datetime
from zurich_core import (
    calcular_kpis, calcular_comp_r4, calcular_comp_r3,
    LABELS_R4, LABELS_R3,
)

# ── Config ────────────────────────────────────────────────────────────────────
DOC = r"C:\Users\gabriel.evangelista\Documents\ClaudeGL\Documentos"
DST = r"C:\Users\gabriel.evangelista\Documents\ClaudeGL\Dashboard\data"

DATA_ANT = "14/08/2026"
DATA_ATU = "17/08/2026"

ANT_FILES = {
    "pendencias":     DOC + r"\zurich_airport___pendencias_por_solicitacao_com_documento___dados_2026-08-14T13_13_23.123008-04_00.csv",
    "terceiros":      DOC + r"\relatorio_de_terceiros_cadastrados_2026-08-14T13_12_28.371437-04_00.csv",
    "sit_terceiro":   DOC + r"\situacao_de_preenchimento_documental_do_terceiro_na_ultima_solicitacao_do_fornecedor___dados_2026-08-14T13_12_41.895377-04_00.csv",
    "sit_fornecedor": DOC + r"\situacao_de_preenchimento_documental_na_ultima_solicitacao_do_fornecedor___dados_2026-08-14T13_12_54.682709-04_00.csv",
    "busca_auto":     DOC + r"\situacao_dos_documentos_de_busca_automatica___dados_2026-08-14T13_13_09.615155-04_00.csv",
    "contratos":      DOC + r"\relatorio_de_codigos_de_contrato_dos_fornecedores___dados_2026-08-14T13_11_27.030514-04_00.csv",
}

ATU_FILES = {
    "pendencias":     DST + r"\pendencias_zurich.csv",
    "terceiros":      DST + r"\terceiros_zurich.csv",
    "sit_terceiro":   DST + r"\situacao_terceiro_zurich.csv",
    "sit_fornecedor": DST + r"\situacao_fornecedor_zurich.csv",
    "busca_auto":     DST + r"\busca_automatica_zurich.csv",
    "contratos":      DST + r"\codigos_contrato_fornecedores_zurich.csv",
}

OUT = r"C:\Users\gabriel.evangelista\Documents\ClaudeGL\Dashboard\email_semanal_zurich.html"

# ── Helpers HTML ──────────────────────────────────────────────────────────────
C_VERDE  = "#1a7a4a"
C_VERM   = "#c0392b"
C_CINZA  = "#555555"
C_BG_VD  = "#e8f5ee"
C_BG_VR  = "#fdecea"
C_BG_CZ  = "#f4f4f4"
C_TEAL   = "#0E8FA3"
C_NAVY   = "#153C5C"
C_LIGHTB = "#e8f6f8"

def seta(ant, atu, inverso=False, pct=False):
    """Retorna (símbolo, cor, bg, texto_var)"""
    try:
        a, b = float(ant), float(atu)
    except Exception:
        return ("→", C_CINZA, C_BG_CZ, "—")
    d = b - a
    if abs(d) < 0.01:
        return ("→", C_CINZA, C_BG_CZ, "sem alt.")
    sobe = d > 0
    bom  = (not sobe) if not inverso else sobe
    cor  = C_VERDE if bom else C_VERM
    bg   = C_BG_VD if bom else C_BG_VR
    sym  = "▲" if sobe else "▼"
    if pct:
        txt = f"{sym} {abs(d):.1f}pp"
    else:
        txt = f"{sym} {abs(int(d)):,}".replace(",", ".")
    return (sym, cor, bg, txt)

def td(val, bold=False, align="center", color=None, bg=None, small=False):
    style = f"padding:6px 10px;border:1px solid #dde;text-align:{align};"
    if bold:  style += "font-weight:600;"
    if color: style += f"color:{color};"
    if bg:    style += f"background:{bg};"
    if small: style += "font-size:12px;"
    return f'<td style="{style}">{val}</td>'

def th(val, align="center", bg=None, color="white", colspan=1):
    bg = bg or C_NAVY
    extra = f'colspan="{colspan}"' if colspan > 1 else ""
    return (f'<th {extra} style="padding:8px 10px;background:{bg};color:{color};'
            f'text-align:{align};font-weight:600;font-size:13px;">{val}</th>')

def secao(titulo, emoji=""):
    return (f'<tr><td colspan="5" style="background:{C_TEAL};color:white;'
            f'padding:8px 12px;font-weight:700;font-size:13px;">'
            f'{emoji} {titulo}</td></tr>')

def linha_kpi(metrica, ant, atu, inverso=False, pct=False, sub=False):
    sym, cor, bg, txt = seta(ant, atu, inverso=inverso, pct=pct)
    ant_s = f"{ant:.1f}%" if pct else f"{int(ant):,}".replace(",",".")
    atu_s = f"{atu:.1f}%" if pct else f"{int(atu):,}".replace(",",".")
    nome  = f"&nbsp;&nbsp;{metrica}" if sub else metrica
    return (f'<tr>'
            f'{td(nome, align="left", small=sub)}'
            f'{td(ant_s)}'
            f'{td(atu_s, bold=True)}'
            f'{td(txt, color=cor, bg=bg, bold=True)}'
            f'</tr>')

# ── Calcular dados ────────────────────────────────────────────────────────────
print("Calculando KPIs gerais...")
kpi_ant = calcular_kpis(
    ANT_FILES["pendencias"], ANT_FILES["terceiros"], ANT_FILES["sit_terceiro"],
    ANT_FILES["sit_fornecedor"], ANT_FILES["busca_auto"], ANT_FILES["contratos"],
)
kpi_atu = calcular_kpis(
    ATU_FILES["pendencias"], ATU_FILES["terceiros"], ATU_FILES["sit_terceiro"],
    ATU_FILES["sit_fornecedor"], ATU_FILES["busca_auto"], ATU_FILES["contratos"],
)

print("Calculando competência R4...")
comp_r4_ant = calcular_comp_r4(ANT_FILES["sit_fornecedor"])
comp_r4_atu = calcular_comp_r4(ATU_FILES["sit_fornecedor"])

print("Calculando competência R3...")
comp_r3_ant = calcular_comp_r3(ANT_FILES["sit_terceiro"])
comp_r3_atu = calcular_comp_r3(ATU_FILES["sit_terceiro"])


# ── Montar tabela comparativo geral ──────────────────────────────────────────
def tabela_geral():
    linhas = []
    linhas.append(f'<tr style="background:#f0f6f8;">'
                  f'{th("Métrica", align="left", bg="#f0f6f8", color=C_NAVY)}'
                  f'{th(DATA_ANT)}{th(DATA_ATU)}'
                  f'{th("Variação")}</tr>')
    linhas.append(secao("Visão Geral", "📋"))
    linhas.append(linha_kpi("Fornecedores cadastrados",   kpi_ant["forn_cadastro"],  kpi_atu["forn_cadastro"],  inverso=True))
    linhas.append(linha_kpi("Fornecedores c/ pendências", kpi_ant["forn_com_pend"],  kpi_atu["forn_com_pend"]))
    linhas.append(linha_kpi("Total de pendências",        kpi_ant["total_pendencias"], kpi_atu["total_pendencias"]))
    linhas.append(secao("Trabalhadores (R3)", "👷"))
    linhas.append(linha_kpi("Ativos",   kpi_ant["trab_ativo"],   kpi_atu["trab_ativo"],   inverso=True))
    linhas.append(linha_kpi("Inativos", kpi_ant["trab_inativo"], kpi_atu["trab_inativo"]))
    linhas.append(secao("Docs Terceiros (R3)", "📄"))
    linhas.append(linha_kpi("Total R3",                kpi_ant["r3_total"],    kpi_atu["r3_total"],    inverso=True))
    linhas.append(linha_kpi("✅ Aprovados",            kpi_ant["r3_aprovado"], kpi_atu["r3_aprovado"], inverso=True, sub=True))
    linhas.append(linha_kpi("❌ Reprovados",           kpi_ant["r3_reprovado"],kpi_atu["r3_reprovado"], sub=True))
    linhas.append(linha_kpi("📭 Não enviados",         kpi_ant["r3_nao_anex"], kpi_atu["r3_nao_anex"],  sub=True))
    linhas.append(linha_kpi("⏳ Aguard. submissão",    kpi_ant["r3_aguard_sub"],kpi_atu["r3_aguard_sub"], sub=True))
    linhas.append(linha_kpi("🔍 Em análise",           kpi_ant["r3_em_analise"],kpi_atu["r3_em_analise"], inverso=True, sub=True))
    linhas.append(secao("Docs Empresa (R4)", "🏢"))
    linhas.append(linha_kpi("Total R4",        kpi_ant["r4_total"],     kpi_atu["r4_total"],     inverso=True))
    linhas.append(linha_kpi("✅ Aprovados",    kpi_ant["r4_aprovado"],  kpi_atu["r4_aprovado"],  inverso=True, sub=True))
    linhas.append(linha_kpi("❌ Reprovados",   kpi_ant["r4_reprovado"], kpi_atu["r4_reprovado"],  sub=True))
    linhas.append(linha_kpi("📭 Não enviados", kpi_ant["r4_nao_anex"],  kpi_atu["r4_nao_anex"],   sub=True))
    linhas.append(linha_kpi("🔍 Em análise",   kpi_ant["r4_em_analise"],kpi_atu["r4_em_analise"], inverso=True, sub=True))
    linhas.append(linha_kpi("📅 Vencidos",     kpi_ant["r4_vencido"],   kpi_atu["r4_vencido"],    sub=True))
    linhas.append(secao("Consolidado R3 + R4", "📊"))
    linhas.append(linha_kpi("Total de docs",       kpi_ant["total_docs"],     kpi_atu["total_docs"],     inverso=True))
    linhas.append(linha_kpi("Total aprovados",     kpi_ant["total_aprovado"], kpi_atu["total_aprovado"], inverso=True))
    linhas.append(linha_kpi("Total reprovados",    kpi_ant["total_reprovado"],kpi_atu["total_reprovado"]))
    linhas.append(linha_kpi("% Conformidade",      kpi_ant["pct_conf"],       kpi_atu["pct_conf"],       inverso=True, pct=True))
    linhas.append(linha_kpi("% Não conformidade",  kpi_ant["pct_nc"],         kpi_atu["pct_nc"],         pct=True))
    return "\n".join(linhas)


# ── Montar tabela competência R4 ──────────────────────────────────────────────
def tabela_comp_r4():
    linhas = []
    linhas.append(f'<tr style="background:#f0f6f8;">'
                  f'{th("Documento", align="left", bg="#f0f6f8", color=C_NAVY)}'
                  f'{th(f"Preenchidos {DATA_ANT}")}'
                  f'{th(f"Preenchidos {DATA_ATU}")}'
                  f'{th("Faltando")}'
                  f'{th("Variação")}'
                  f'</tr>')

    for doc in LABELS_R4:
        label = LABELS_R4[doc]
        d_ant = comp_r4_ant["por_doc"].get(doc, {"preenchidos": 0, "faltando": 0, "total": 0})
        d_atu = comp_r4_atu["por_doc"].get(doc, {"preenchidos": 0, "faltando": 0, "total": 0})
        p_ant = d_ant["preenchidos"]
        p_atu = d_atu["preenchidos"]
        falt  = d_atu["faltando"]
        sym, cor, bg, txt = seta(p_ant, p_atu, inverso=True)
        falt_cor = C_VERM if falt > 0 else C_VERDE
        linhas.append(
            f'<tr>'
            f'{td(label, align="left")}'
            f'{td(p_ant)}'
            f'{td(p_atu, bold=True)}'
            f'{td(falt, color=falt_cor, bold=(falt > 0))}'
            f'{td(txt, color=cor, bg=bg, bold=True)}'
            f'</tr>'
        )

    # Totais
    tp_ant = comp_r4_ant["total_preenchidos"]
    tp_atu = comp_r4_atu["total_preenchidos"]
    tf_atu = comp_r4_atu["total_faltando"]
    sym, cor, bg, txt = seta(tp_ant, tp_atu, inverso=True)
    linhas.append(
        f'<tr style="background:#f0f6f8;font-weight:700;">'
        f'{td("TOTAL", align="left", bold=True, bg="#f0f6f8")}'
        f'{td(tp_ant, bold=True, bg="#f0f6f8")}'
        f'{td(tp_atu, bold=True, bg="#f0f6f8")}'
        f'{td(tf_atu, bold=True, color=C_VERM if tf_atu else C_VERDE, bg="#f0f6f8")}'
        f'{td(txt, color=cor, bg=bg, bold=True)}'
        f'</tr>'
    )

    # Última competência
    uc = comp_r4_atu["ultima_comp"]
    linhas.append(
        f'<tr><td colspan="5" style="padding:8px 12px;background:#f9f9f9;'
        f'font-size:12px;color:#555;border:1px solid #dde;">'
        f'📅 <strong>Última competência registrada (R4):</strong> {uc}</td></tr>'
    )

    return "\n".join(linhas)


# ── Montar tabela competência R3 ──────────────────────────────────────────────
def tabela_comp_r3():
    linhas = []
    linhas.append(f'<tr style="background:#f0f6f8;">'
                  f'{th("Documento", align="left", bg="#f0f6f8", color=C_NAVY)}'
                  f'{th(f"Preenchidos {DATA_ANT}")}'
                  f'{th(f"Preenchidos {DATA_ATU}")}'
                  f'{th("Faltando")}'
                  f'{th("Variação")}'
                  f'</tr>')

    for doc in LABELS_R3:
        label = LABELS_R3[doc]
        d_ant = comp_r3_ant["por_doc"].get(doc, {"preenchidos": 0, "faltando": 0, "total": 0})
        d_atu = comp_r3_atu["por_doc"].get(doc, {"preenchidos": 0, "faltando": 0, "total": 0})
        p_ant = d_ant["preenchidos"]
        p_atu = d_atu["preenchidos"]
        falt  = d_atu["faltando"]
        sym, cor, bg, txt = seta(p_ant, p_atu, inverso=True)
        falt_cor = C_VERM if falt > 0 else C_VERDE
        linhas.append(
            f'<tr>'
            f'{td(label, align="left")}'
            f'{td(p_ant)}'
            f'{td(p_atu, bold=True)}'
            f'{td(falt, color=falt_cor, bold=(falt > 0))}'
            f'{td(txt, color=cor, bg=bg, bold=True)}'
            f'</tr>'
        )

    # Totais
    tp_ant = comp_r3_ant["total_preenchidos"]
    tp_atu = comp_r3_atu["total_preenchidos"]
    tf_atu = comp_r3_atu["total_faltando"]
    sym, cor, bg, txt = seta(tp_ant, tp_atu, inverso=True)
    linhas.append(
        f'<tr style="background:#f0f6f8;font-weight:700;">'
        f'{td("TOTAL", align="left", bold=True, bg="#f0f6f8")}'
        f'{td(tp_ant, bold=True, bg="#f0f6f8")}'
        f'{td(tp_atu, bold=True, bg="#f0f6f8")}'
        f'{td(tf_atu, bold=True, color=C_VERM if tf_atu else C_VERDE, bg="#f0f6f8")}'
        f'{td(txt, color=cor, bg=bg, bold=True)}'
        f'</tr>'
    )

    uc = comp_r3_atu["ultima_comp"]
    linhas.append(
        f'<tr><td colspan="5" style="padding:8px 12px;background:#f9f9f9;'
        f'font-size:12px;color:#555;border:1px solid #dde;">'
        f'📅 <strong>Última competência registrada (R3):</strong> {uc}</td></tr>'
    )

    return "\n".join(linhas)


# ── Distribuição por mês (R3 + R4 combinados) ────────────────────────────────
def tabela_dist_comp():
    # Mescla distribuição R3 e R4
    from collections import defaultdict
    dist_merge: dict = defaultdict(lambda: {"r3": 0, "r4": 0})

    for label, count in comp_r4_atu["dist_por_comp"]:
        dist_merge[label]["r4"] += count
    for label, count in comp_r3_atu["dist_por_comp"]:
        dist_merge[label]["r3"] += count

    # Ordena por competência (MM/YY)
    def sort_key(lbl):
        import re
        m = re.match(r'(\d{2})/(\d{2})', lbl)
        return (2000 + int(m.group(2)), int(m.group(1))) if m else (0, 0)

    top = sorted(dist_merge.items(), key=lambda x: sort_key(x[0]), reverse=True)[:5]

    linhas = []
    linhas.append(f'<tr style="background:#f0f6f8;">'
                  f'{th("Competência", bg="#f0f6f8", color=C_NAVY)}'
                  f'{th("R3 (Terceiros)", bg="#f0f6f8", color=C_NAVY)}'
                  f'{th("R4 (Empresa)", bg="#f0f6f8", color=C_NAVY)}'
                  f'{th("Total", bg="#f0f6f8", color=C_NAVY)}'
                  f'</tr>')

    for lbl, counts in top:
        r3 = counts["r3"]
        r4 = counts["r4"]
        tot = r3 + r4
        linhas.append(
            f'<tr>'
            f'{td(f"<strong>{lbl}</strong>")}'
            f'{td(r3)}'
            f'{td(r4)}'
            f'{td(tot, bold=True)}'
            f'</tr>'
        )

    return "\n".join(linhas)


# ── Montar HTML ───────────────────────────────────────────────────────────────
agora = datetime.now().strftime("%d/%m/%Y %H:%M")

html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Comparativo Semanal Zurich Airport</title>
</head>
<body style="margin:0;padding:20px;font-family:Arial,Helvetica,sans-serif;
             background:#f2f5f7;color:#222;">

<!-- Wrapper -->
<div style="max-width:700px;margin:0 auto;background:#ffffff;
            border-radius:6px;overflow:hidden;
            box-shadow:0 2px 8px rgba(0,0,0,0.10);">

  <!-- Header -->
  <div style="background:{C_NAVY};padding:20px 24px;">
    <div style="font-size:11px;color:#9ec8d4;letter-spacing:1px;
                text-transform:uppercase;margin-bottom:4px;">
      Circulação Interna · Efcaz CS
    </div>
    <div style="font-size:20px;font-weight:700;color:#ffffff;">
      Dashboard Zurich Airport
    </div>
    <div style="font-size:14px;color:{C_TEAL};margin-top:4px;">
      Comparativo Semanal &nbsp;·&nbsp;
      <strong style="color:#ffffff;">{DATA_ANT}</strong> →
      <strong style="color:#ffffff;">{DATA_ATU}</strong>
    </div>
  </div>

  <!-- Corpo -->
  <div style="padding:20px 24px;">

    <!-- KPIs rápidos -->
    <div style="display:flex;gap:12px;margin-bottom:20px;flex-wrap:wrap;">
"""

# KPI cards inline
def kpi_card(titulo, valor, var_txt, var_bom):
    bg   = C_BG_VD if var_bom else C_BG_VR
    cor  = C_VERDE  if var_bom else C_VERM
    return f"""
      <div style="flex:1;min-width:130px;background:#f8fbfc;border:1px solid #dde;
                  border-radius:5px;padding:12px;text-align:center;">
        <div style="font-size:11px;color:#777;margin-bottom:4px;">{titulo}</div>
        <div style="font-size:22px;font-weight:700;color:{C_NAVY};">{valor}</div>
        <div style="font-size:11px;font-weight:600;color:{cor};
                    background:{bg};border-radius:3px;padding:2px 6px;
                    display:inline-block;margin-top:4px;">{var_txt}</div>
      </div>"""

conf_var = kpi_atu["pct_conf"] - kpi_ant["pct_conf"]
pend_var = kpi_atu["total_pendencias"] - kpi_ant["total_pendencias"]
aprov_var = kpi_atu["total_aprovado"] - kpi_ant["total_aprovado"]
trab_var = kpi_atu["trab_ativo"] - kpi_ant["trab_ativo"]

html += kpi_card("% Conformidade",
    f"{kpi_atu['pct_conf']:.1f}%",
    f"{'▲' if conf_var >= 0 else '▼'} {abs(conf_var):.1f}pp",
    conf_var >= 0)

html += kpi_card("Docs Aprovados",
    f"{kpi_atu['total_aprovado']:,}".replace(",","."),
    f"{'▲' if aprov_var >= 0 else '▼'} {abs(int(aprov_var))}",
    aprov_var >= 0)

html += kpi_card("Total Pendências",
    f"{kpi_atu['total_pendencias']:,}".replace(",","."),
    f"{'▲' if pend_var >= 0 else '▼'} {abs(int(pend_var))}",
    pend_var <= 0)

html += kpi_card("Trabalhadores Ativos",
    f"{kpi_atu['trab_ativo']:,}".replace(",","."),
    f"{'▲' if trab_var >= 0 else '▼'} {abs(int(trab_var))}",
    trab_var >= 0)

html += f"""
    </div>

    <!-- Tabela comparativo geral -->
    <div style="font-size:14px;font-weight:700;color:{C_NAVY};margin-bottom:8px;">
      1. Comparativo Geral
    </div>
    <table style="width:100%;border-collapse:collapse;font-size:13px;
                  margin-bottom:24px;">
      {tabela_geral()}
    </table>

    <!-- Tabela competência R4 -->
    <div style="font-size:14px;font-weight:700;color:{C_NAVY};margin-bottom:4px;">
      2. Competência — Docs Mensais Empresa (R4)
    </div>
    <div style="font-size:12px;color:#666;margin-bottom:8px;">
      Documentos que exigem indicação do mês/ano de referência (competência).
      Faltando = docs cadastrados sem competência preenchida.
    </div>
    <table style="width:100%;border-collapse:collapse;font-size:13px;
                  margin-bottom:24px;">
      {tabela_comp_r4()}
    </table>

    <!-- Tabela competência R3 -->
    <div style="font-size:14px;font-weight:700;color:{C_NAVY};margin-bottom:4px;">
      3. Competência — Docs Terceiros (R3)
    </div>
    <div style="font-size:12px;color:#666;margin-bottom:8px;">
      Apenas Cartão Ponto e Ficha de EPI exigem competência para trabalhadores terceiros.
    </div>
    <table style="width:100%;border-collapse:collapse;font-size:13px;
                  margin-bottom:24px;">
      {tabela_comp_r3()}
    </table>

    <!-- Distribuição por mês -->
    <div style="font-size:14px;font-weight:700;color:{C_NAVY};margin-bottom:4px;">
      4. Distribuição por Mês de Competência (base atual — top 5)
    </div>
    <div style="font-size:12px;color:#666;margin-bottom:8px;">
      Volume de documentos com competência registrada por mês — R3 e R4 combinados.
    </div>
    <table style="width:100%;border-collapse:collapse;font-size:13px;
                  margin-bottom:24px;">
      {tabela_dist_comp()}
    </table>

  </div><!-- /Corpo -->

  <!-- Rodapé -->
  <div style="background:#f8fbfc;border-top:2px solid {C_TEAL};
              padding:14px 24px;font-size:11px;color:#777;">
    <span style="color:{C_TEAL};font-weight:700;">Efcaz</span> · Customer Success Interno
    &nbsp;|&nbsp; Gerado em {agora}
    &nbsp;|&nbsp; Base: <strong>{DATA_ATU}</strong>
    &nbsp;|&nbsp; 🔗 <a href="https://dash-zurich.vercel.app"
      style="color:{C_TEAL};">dash-zurich.vercel.app</a>
  </div>

</div><!-- /Wrapper -->
</body>
</html>
"""

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)

print(f"E-mail gerado: {OUT}")
print(f"  → Abrir no browser, Ctrl+A, Ctrl+C, colar no Outlook/Gmail")
print()
print("  Resumo de competência (base atual):")
print(f"  R4 — Preenchidos: {comp_r4_atu['total_preenchidos']} | "
      f"Faltando: {comp_r4_atu['total_faltando']} | "
      f"Última comp: {comp_r4_atu['ultima_comp']}")
print(f"  R3 — Preenchidos: {comp_r3_atu['total_preenchidos']} | "
      f"Faltando: {comp_r3_atu['total_faltando']} | "
      f"Última comp: {comp_r3_atu['ultima_comp']}")
