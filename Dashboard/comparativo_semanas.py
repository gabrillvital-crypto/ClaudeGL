import pandas as pd
import re
import os

def read_csv_safe(path):
    for enc in ["utf-8-sig", "latin-1", "utf-8"]:
        try:
            with open(path, encoding=enc, errors="replace") as f:
                sample = f.read(4096)
            sep = ";" if sample.count(";") > sample.count(",") else ","
            df = pd.read_csv(path, encoding=enc, sep=sep, on_bad_lines="skip")
            df.columns = df.columns.str.strip()
            drop_cols = [c for c in df.columns if re.search(r'^contrato\s*\d*$', c, re.I)]
            return df.drop(columns=drop_cols, errors="ignore")
        except Exception:
            continue
    raise RuntimeError(f"Nao foi possivel ler: {path}")

def abbrev(name, n=40):
    s = str(name).strip()
    short = re.sub(r'\s+(LTDA|LTDA\.|S/A|SA|EIRELI|ME|EPP).*', '', s, flags=re.I)
    return short[:n] + "..." if len(short) > n else short

def calcular_kpis(pendencias_csv, terceiros_csv, situacao_terceiro_csv,
                  situacao_forn_csv, busca_auto_csv, fornecedores_csv):

    df_pend = read_csv_safe(pendencias_csv)
    df_terc = read_csv_safe(terceiros_csv)
    df_sit  = read_csv_safe(situacao_terceiro_csv)

    col_rs_pend = "Razão Social" if "Razão Social" in df_pend.columns else "Razao Social"
    col_rs_terc = "Razão Social" if "Razão Social" in df_terc.columns else "Razao Social"
    col_sit_pend = "Situação da solicitação" if "Situação da solicitação" in df_pend.columns else "Situacao da solicitacao"
    col_area_pend = "Área da pendência" if "Área da pendência" in df_pend.columns else "Area da pendencia"
    col_status_terc = "Status" if "Status" in df_terc.columns else "status"

    # --- R3 ---
    col_analise_r3 = next((c for c in df_sit.columns if "lise" in c.lower() and "doc" in c.lower()), None)
    col_sit_solic_r3 = next((c for c in df_sit.columns if "ltima" in c.lower() and "solic" in c.lower()), None)

    forn_rs_col = next((c for c in df_sit.columns if "fornecedor" in c.lower() and ("raz" in c.lower() or "social" in c.lower())), None)
    if forn_rs_col:
        df_sit["Empresa"] = df_sit[forn_rs_col].apply(abbrev)

    def map_status_r3(row):
        if col_analise_r3:
            analise = str(row.get(col_analise_r3, "")).strip().upper()
            if analise == "APROVADO":  return "Aprovado"
            if analise == "REPROVADO": return "Reprovado"
        raw_status = row.get("Status", None)
        is_na = pd.isna(raw_status) or str(raw_status).strip().upper() in ("N/A", "NA", "")
        if is_na: return "Aguardando análise"
        s = str(raw_status).strip().lower()
        if "anexado" in s: return "Não anexado"
        return "Aguardando análise"

    df_sit_calc = df_sit.copy()
    df_sit_calc["Status_Cat"] = df_sit_calc.apply(map_status_r3, axis=1)

    def _status_final_r3(row):
        if row["Status_Cat"] != "Aguardando análise": return row["Status_Cat"]
        if col_sit_solic_r3 and str(row.get(col_sit_solic_r3, "")).strip() == "EM_ELABORACAO":
            return "Aguardando Submissão"
        return "Em Análise"
    df_sit_calc["Status_Final"] = df_sit_calc.apply(_status_final_r3, axis=1)

    total_docs_sit       = len(df_sit_calc)
    total_conformes      = int((df_sit_calc["Status_Cat"] == "Aprovado").sum())
    total_reprovados     = int((df_sit_calc["Status_Cat"] == "Reprovado").sum())
    total_nao_anex_r3    = int((df_sit_calc["Status_Cat"] == "Não anexado").sum())
    total_aguard_r3      = int((df_sit_calc["Status_Cat"] == "Aguardando análise").sum())
    total_terceiros_r3   = int(df_sit_calc["Terceiro CPF/CNPJ"].nunique()) if "Terceiro CPF/CNPJ" in df_sit_calc.columns else 0

    _mask_aguard = df_sit_calc["Status_Cat"] == "Aguardando análise"
    total_aguard_r3_elab = int((_mask_aguard & (df_sit_calc[col_sit_solic_r3] == "EM_ELABORACAO")).sum()) if col_sit_solic_r3 else 0
    total_aguard_r3_real = total_aguard_r3 - total_aguard_r3_elab

    # --- Busca automática ---
    _busca_auto_map = {}
    if os.path.exists(busca_auto_csv):
        _df_ba = read_csv_safe(busca_auto_csv)
        _col_ba_cnpj = next((c for c in _df_ba.columns if "cnpj" in c.lower()), None)
        _col_ba_doc  = next((c for c in _df_ba.columns if c.strip().lower() == "documento"), None) or \
                       next((c for c in _df_ba.columns if "doc" in c.lower() and "situa" not in c.lower() and "venc" not in c.lower()), None)
        _col_ba_sit  = next((c for c in _df_ba.columns if "situa" in c.lower() and "doc" in c.lower() and "lise" not in c.lower()), None)
        _col_ba_anal = next((c for c in _df_ba.columns if "lise" in c.lower() and "doc" in c.lower()), None)
        if _col_ba_cnpj and _col_ba_doc and _col_ba_sit:
            for _, _r in _df_ba.iterrows():
                _ck = re.sub(r'\D', '', str(_r[_col_ba_cnpj]))
                _dk = str(_r[_col_ba_doc]).strip().upper()
                _sk = str(_r[_col_ba_sit]).strip().upper()
                _ak = str(_r[_col_ba_anal]).strip().upper() if _col_ba_anal else ""
                if _ck and _dk and _dk != "NAN":
                    _busca_auto_map[(_ck, _dk)] = (_sk, _ak)

    # --- R4 ---
    r4_total = r4_aprovado = r4_reprovado = r4_irregular = r4_nao_anex = r4_em_analise = r4_vencido = r4_fornecedores = 0
    r4_nao_conf = 0

    if os.path.exists(situacao_forn_csv):
        df_sit_forn = read_csv_safe(situacao_forn_csv)
        col_analise = next((c for c in df_sit_forn.columns if "lise" in c.lower() and "doc" in c.lower()), None)

        def map_status_r4(row):
            cnpj_r = re.sub(r'\D', '', str(row.get("CNPJ", "")))
            doc_r  = str(row.get("Documento", "")).strip().upper()
            analise = str(row.get(col_analise, "")).strip().upper() if col_analise else ""
            sit_ba = _busca_auto_map.get((cnpj_r, doc_r))
            if sit_ba:
                sit_doc, sit_anal_ba = sit_ba
                if sit_doc == "REGULAR":    return "Aprovado"
                if sit_doc == "IRREGULAR":  return "Irregular"
                if sit_anal_ba == "APROVADO":  return "Aprovado"
                if sit_anal_ba == "REPROVADO": return "Reprovado"
                if sit_anal_ba == "VENCIDO":   return "Vencido"
                return "Em análise"
            if analise == "APROVADO":  return "Aprovado"
            if analise == "REPROVADO": return "Reprovado"
            status = str(row.get("Status", "")).strip().lower()
            if "vencer" in status:    return "Aprovado"
            if "anexado" in status:   return "Não Anexado"
            if "vencido" in status:   return "Vencido"
            return "Em análise"

        df_sit_forn["Status_Cat"] = df_sit_forn.apply(map_status_r4, axis=1)
        df_sit_forn_calc = df_sit_forn[df_sit_forn["Status_Cat"].notna()].copy()

        r4_total      = len(df_sit_forn_calc)
        r4_aprovado   = int((df_sit_forn_calc["Status_Cat"] == "Aprovado").sum())
        r4_reprovado  = int((df_sit_forn_calc["Status_Cat"] == "Reprovado").sum())
        r4_irregular  = int((df_sit_forn_calc["Status_Cat"] == "Irregular").sum())
        r4_nao_anex   = int((df_sit_forn_calc["Status_Cat"] == "Não Anexado").sum())
        r4_em_analise = int((df_sit_forn_calc["Status_Cat"] == "Em análise").sum())
        r4_vencido    = int((df_sit_forn_calc["Status_Cat"] == "Vencido").sum())
        r4_nao_conf   = r4_reprovado + r4_irregular + r4_nao_anex + r4_em_analise + r4_vencido
        r4_fornecedores = int(df_sit_forn_calc["CNPJ"].dropna().apply(lambda v: re.sub(r'\D', '', str(v))).nunique()) if "CNPJ" in df_sit_forn_calc.columns else 0

    # --- KPIs pendências ---
    total_pendencias  = len(df_pend)
    forn_com_pend     = df_pend[col_rs_pend].nunique()
    total_trab_ativo  = int((df_terc[col_status_terc] == "Ativo").sum())
    total_trab_inativo= int((df_terc[col_status_terc] == "Inativo").sum())

    # --- Total fornecedores cadastro ---
    total_forn_geral = 0
    if os.path.exists(fornecedores_csv):
        df_forn = read_csv_safe(fornecedores_csv)
        col_cnpj_forn = next((c for c in df_forn.columns if any(k in c.lower() for k in ("cpf", "cnpj", "documento"))), df_forn.columns[0])
        total_forn_geral = df_forn[col_cnpj_forn].nunique()

    total_docs = total_docs_sit + r4_total
    total_aprov_geral = total_conformes + r4_aprovado
    total_reprov_geral = total_reprovados + r4_reprovado + r4_irregular
    pct_conf = round(total_aprov_geral / total_docs * 100, 1) if total_docs > 0 else 0
    pct_nc   = round((total_reprov_geral + total_nao_anex_r3 + total_aguard_r3 + r4_nao_anex + r4_em_analise + r4_vencido) / total_docs * 100, 1) if total_docs > 0 else 0

    return {
        "forn_cadastro":     total_forn_geral,
        "forn_com_pend":     forn_com_pend,
        "total_pendencias":  total_pendencias,
        "trab_ativo":        total_trab_ativo,
        "trab_inativo":      total_trab_inativo,
        "total_terceiros":   total_terceiros_r3,
        # docs R3
        "r3_total":          total_docs_sit,
        "r3_aprovado":       total_conformes,
        "r3_reprovado":      total_reprovados,
        "r3_nao_anex":       total_nao_anex_r3,
        "r3_aguard_sub":     total_aguard_r3_elab,
        "r3_em_analise":     total_aguard_r3_real,
        # docs R4
        "r4_total":          r4_total,
        "r4_aprovado":       r4_aprovado,
        "r4_reprovado":      r4_reprovado + r4_irregular,
        "r4_nao_anex":       r4_nao_anex,
        "r4_em_analise":     r4_em_analise,
        "r4_vencido":        r4_vencido,
        # consolidado
        "total_docs":        total_docs,
        "total_aprovado":    total_aprov_geral,
        "total_reprovado":   total_reprov_geral,
        "pct_conf":          pct_conf,
        "pct_nc":            pct_nc,
    }

# ─── Bases ───────────────────────────────────────────────────────────────────
DOC = r"C:\Users\gabriel.evangelista\Documents\ClaudeGL\Documentos"
DST = r"C:\Users\gabriel.evangelista\Documents\ClaudeGL\Dashboard\data"

sem_ant = calcular_kpis(
    pendencias_csv       = DOC + r"\zurich_airport___pendencias_por_solicitacao_com_documento___dados_2026-06-30T17_55_36.270947Z.csv",
    terceiros_csv        = DOC + r"\relatorio_de_terceiros_cadastrados_2026-06-30T17_56_39.367188Z.csv",
    situacao_terceiro_csv= DOC + r"\situacao_de_preenchimento_documental_do_terceiro_na_ultima_solicitacao_do_fornecedor___dados_2026-06-30T17_56_26.439497Z.csv",
    situacao_forn_csv    = DOC + r"\situacao_de_preenchimento_documental_na_ultima_solicitacao_do_fornecedor___dados_2026-06-30T17_55_57.834161Z.csv",
    busca_auto_csv       = DOC + r"\situacao_dos_documentos_de_busca_automatica___dados_2026-06-30T17_55_47.39577Z.csv",
    fornecedores_csv     = DOC + r"\relatorio_de_codigos_de_contrato_dos_fornecedores___dados_2026-06-30T17_57_04.519922Z.csv",
)

sem_atual = calcular_kpis(
    pendencias_csv       = DST + r"\pendencias_zurich.csv",
    terceiros_csv        = DST + r"\terceiros_zurich.csv",
    situacao_terceiro_csv= DST + r"\situacao_terceiro_zurich.csv",
    situacao_forn_csv    = DST + r"\situacao_fornecedor_zurich.csv",
    busca_auto_csv       = DST + r"\busca_automatica_zurich.csv",
    fornecedores_csv     = DST + r"\codigos_contrato_fornecedores_zurich.csv",
)

# ─── Comparativo ──────────────────────────────────────────────────────────────
def delta(a, b, inverso=False):
    d = b - a
    if d == 0: return "  →  sem alteração"
    sinal = "▲" if d > 0 else "▼"
    bom = (d < 0) if not inverso else (d > 0)
    cor = "✅" if bom else "⚠️"
    return f"  {sinal} {abs(d):+.0f} {cor}"

def deltapct(a, b, inverso=False):
    d = round(b - a, 1)
    if d == 0: return "  →  sem alteração"
    sinal = "▲" if d > 0 else "▼"
    bom = (d < 0) if not inverso else (d > 0)
    cor = "✅" if bom else "⚠️"
    return f"  {sinal} {abs(d):.1f}pp {cor}"

linhas = [
    ("", "MÉTRICA", "26/06/2026", "30/06/2026", "VARIAÇÃO"),
    ("─", "", "", "", ""),
    ("📋", "VISÃO GERAL", "", "", ""),
    ("", "Fornecedores cadastrados",  sem_ant["forn_cadastro"],    sem_atual["forn_cadastro"],    delta(sem_ant["forn_cadastro"],    sem_atual["forn_cadastro"],    inverso=True)),
    ("", "Fornecedores c/ pendências", sem_ant["forn_com_pend"],    sem_atual["forn_com_pend"],    delta(sem_ant["forn_com_pend"],    sem_atual["forn_com_pend"])),
    ("", "Total de pendências",       sem_ant["total_pendencias"], sem_atual["total_pendencias"], delta(sem_ant["total_pendencias"], sem_atual["total_pendencias"])),
    ("─", "", "", "", ""),
    ("👷", "TERCEIROS", "", "", ""),
    ("", "Trabalhadores ativos",      sem_ant["trab_ativo"],       sem_atual["trab_ativo"],       delta(sem_ant["trab_ativo"],       sem_atual["trab_ativo"],       inverso=True)),
    ("", "Trabalhadores inativos",    sem_ant["trab_inativo"],     sem_atual["trab_inativo"],     delta(sem_ant["trab_inativo"],     sem_atual["trab_inativo"])),
    ("─", "", "", "", ""),
    ("📄", "DOCS TERCEIROS (R3)", "", "", ""),
    ("", "Total docs R3",             sem_ant["r3_total"],         sem_atual["r3_total"],         delta(sem_ant["r3_total"],         sem_atual["r3_total"],         inverso=True)),
    ("", "  ✅ Aprovados",            sem_ant["r3_aprovado"],      sem_atual["r3_aprovado"],      delta(sem_ant["r3_aprovado"],      sem_atual["r3_aprovado"],      inverso=True)),
    ("", "  ❌ Reprovados",           sem_ant["r3_reprovado"],     sem_atual["r3_reprovado"],     delta(sem_ant["r3_reprovado"],     sem_atual["r3_reprovado"])),
    ("", "  📭 Não enviados",         sem_ant["r3_nao_anex"],      sem_atual["r3_nao_anex"],      delta(sem_ant["r3_nao_anex"],      sem_atual["r3_nao_anex"])),
    ("", "  ⏳ Aguard. submissão",    sem_ant["r3_aguard_sub"],    sem_atual["r3_aguard_sub"],    delta(sem_ant["r3_aguard_sub"],    sem_atual["r3_aguard_sub"])),
    ("", "  🔍 Em análise",           sem_ant["r3_em_analise"],    sem_atual["r3_em_analise"],    delta(sem_ant["r3_em_analise"],    sem_atual["r3_em_analise"],    inverso=True)),
    ("─", "", "", "", ""),
    ("🏢", "DOCS EMPRESA (R4)", "", "", ""),
    ("", "Total docs R4",             sem_ant["r4_total"],         sem_atual["r4_total"],         delta(sem_ant["r4_total"],         sem_atual["r4_total"],         inverso=True)),
    ("", "  ✅ Aprovados",            sem_ant["r4_aprovado"],      sem_atual["r4_aprovado"],      delta(sem_ant["r4_aprovado"],      sem_atual["r4_aprovado"],      inverso=True)),
    ("", "  ❌ Reprovados",           sem_ant["r4_reprovado"],     sem_atual["r4_reprovado"],     delta(sem_ant["r4_reprovado"],     sem_atual["r4_reprovado"])),
    ("", "  📭 Não enviados",         sem_ant["r4_nao_anex"],      sem_atual["r4_nao_anex"],      delta(sem_ant["r4_nao_anex"],      sem_atual["r4_nao_anex"])),
    ("", "  🔍 Em análise",           sem_ant["r4_em_analise"],    sem_atual["r4_em_analise"],    delta(sem_ant["r4_em_analise"],    sem_atual["r4_em_analise"],    inverso=True)),
    ("", "  📅 Vencidos",             sem_ant["r4_vencido"],       sem_atual["r4_vencido"],       delta(sem_ant["r4_vencido"],       sem_atual["r4_vencido"])),
    ("─", "", "", "", ""),
    ("📊", "CONSOLIDADO", "", "", ""),
    ("", "Total docs (R3+R4)",        sem_ant["total_docs"],       sem_atual["total_docs"],       delta(sem_ant["total_docs"],       sem_atual["total_docs"],       inverso=True)),
    ("", "Total aprovados",           sem_ant["total_aprovado"],   sem_atual["total_aprovado"],   delta(sem_ant["total_aprovado"],   sem_atual["total_aprovado"],   inverso=True)),
    ("", "Total reprovados",          sem_ant["total_reprovado"],  sem_atual["total_reprovado"],  delta(sem_ant["total_reprovado"],  sem_atual["total_reprovado"])),
    ("", "% Conformidade geral",      f"{sem_ant['pct_conf']}%",   f"{sem_atual['pct_conf']}%",   deltapct(sem_ant["pct_conf"],      sem_atual["pct_conf"],         inverso=True)),
    ("", "% Não conformidade",        f"{sem_ant['pct_nc']}%",     f"{sem_atual['pct_nc']}%",     deltapct(sem_ant["pct_nc"],        sem_atual["pct_nc"])),
]

print("\n" + "═"*85)
print(f"  COMPARATIVO SEMANAL — ZURICH AIRPORT")
print(f"  Semana anterior: 30/06/2026  →  Semana atual: 03/07/2026")
print("═"*85)

for row in linhas:
    ico, metrica, ant, atu, var = row
    if metrica == "" and ico == "─":
        print("─"*85)
        continue
    if ant == "" and atu == "":
        print(f"\n  {ico} {metrica}")
        continue
    print(f"  {ico:<2} {metrica:<35} {str(ant):>10}   {str(atu):>10}   {var}")

print("═"*85 + "\n")
