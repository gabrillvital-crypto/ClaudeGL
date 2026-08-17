"""
zurich_core.py — Funções compartilhadas do Dashboard Zurich Airport.
Importado por comparativo_semanas.py e email_semanal_zurich.py.
"""
import pandas as pd
import re
import os

# ── Docs com competência ─────────────────────────────────────────────────────
DOCS_COMP_R4 = [
    "COMPROVANTE BANCÁRIO DE PAGAMENTO DOS SALÁRIOS",
    "DCTFWEB",
    "GFD - GUIA DO FGTS DIGITAL MENSAL",
    "FOPAG - (FOLHA DE PAGAMENTO + RESUMO)",
    "KIT RESCISÃO",
    "RECIBO DE FÉRIAS + COMPROVANTE DE PAGAMENTO",
    "GRRF - GUIA DE RECOLHIMENTO RESCISÓRIO DO FGTS",
]

DOCS_COMP_R3 = [
    "CARTÃO PONTO COM TOTAL DE HORAS EXTRAS OU NOTURNAS",
    "FICHA DE EPI",
]

LABELS_R4 = {
    "COMPROVANTE BANCÁRIO DE PAGAMENTO DOS SALÁRIOS": "Comp. Bancário Salários",
    "DCTFWEB": "DCTFWEB",
    "GFD - GUIA DO FGTS DIGITAL MENSAL": "GFD FGTS Digital",
    "FOPAG - (FOLHA DE PAGAMENTO + RESUMO)": "FOPAG",
    "KIT RESCISÃO": "Kit Rescisão",
    "RECIBO DE FÉRIAS + COMPROVANTE DE PAGAMENTO": "Recibo de Férias",
    "GRRF - GUIA DE RECOLHIMENTO RESCISÓRIO DO FGTS": "GRRF",
}

LABELS_R3 = {
    "CARTÃO PONTO COM TOTAL DE HORAS EXTRAS OU NOTURNAS": "Cartão Ponto",
    "FICHA DE EPI": "Ficha de EPI",
}


# ── Utilitários gerais ────────────────────────────────────────────────────────
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


# ── KPIs gerais ──────────────────────────────────────────────────────────────
def calcular_kpis(pendencias_csv, terceiros_csv, situacao_terceiro_csv,
                  situacao_forn_csv, busca_auto_csv, fornecedores_csv):

    df_pend = read_csv_safe(pendencias_csv)
    df_terc = read_csv_safe(terceiros_csv)
    df_sit  = read_csv_safe(situacao_terceiro_csv)

    col_rs_pend   = "Razão Social" if "Razão Social" in df_pend.columns else "Razao Social"
    col_sit_pend  = "Situação da solicitação" if "Situação da solicitação" in df_pend.columns else "Situacao da solicitacao"
    col_area_pend = "Área da pendência" if "Área da pendência" in df_pend.columns else "Area da pendencia"
    col_status_terc = "Status" if "Status" in df_terc.columns else "status"

    # ── R3 ──
    col_analise_r3   = next((c for c in df_sit.columns if "lise" in c.lower() and "doc" in c.lower()), None)
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

    total_docs_sit    = len(df_sit_calc)
    total_conformes   = int((df_sit_calc["Status_Cat"] == "Aprovado").sum())
    total_reprovados  = int((df_sit_calc["Status_Cat"] == "Reprovado").sum())
    total_nao_anex_r3 = int((df_sit_calc["Status_Cat"] == "Não anexado").sum())
    total_aguard_r3   = int((df_sit_calc["Status_Cat"] == "Aguardando análise").sum())
    total_terceiros_r3 = int(df_sit_calc["Terceiro CPF/CNPJ"].nunique()) if "Terceiro CPF/CNPJ" in df_sit_calc.columns else 0

    _mask_aguard = df_sit_calc["Status_Cat"] == "Aguardando análise"
    total_aguard_r3_elab = int((_mask_aguard & (df_sit_calc[col_sit_solic_r3] == "EM_ELABORACAO")).sum()) if col_sit_solic_r3 else 0
    total_aguard_r3_real = total_aguard_r3 - total_aguard_r3_elab

    # ── Busca automática ──
    _busca_auto_map = {}
    if os.path.exists(busca_auto_csv):
        _df_ba = read_csv_safe(busca_auto_csv)
        _col_ba_cnpj  = next((c for c in _df_ba.columns if "cnpj" in c.lower()), None)
        _col_ba_doc   = next((c for c in _df_ba.columns if c.strip().lower() == "documento"), None) or \
                        next((c for c in _df_ba.columns if "doc" in c.lower() and "situa" not in c.lower() and "venc" not in c.lower()), None)
        _col_ba_sit   = next((c for c in _df_ba.columns if "situa" in c.lower() and "doc" in c.lower() and "lise" not in c.lower()), None)
        _col_ba_anal  = next((c for c in _df_ba.columns if "lise" in c.lower() and "doc" in c.lower()), None)
        _col_ba_status = next((c for c in _df_ba.columns if c.strip().lower() == "status"), None)
        if _col_ba_cnpj and _col_ba_doc and _col_ba_sit:
            for _, _r in _df_ba.iterrows():
                _ck  = re.sub(r'\D', '', str(_r[_col_ba_cnpj]))
                _dk  = str(_r[_col_ba_doc]).strip().upper()
                _sk  = str(_r[_col_ba_sit]).strip().upper()
                _ak  = str(_r[_col_ba_anal]).strip().upper() if _col_ba_anal else ""
                _stk = str(_r[_col_ba_status]).strip().lower() if _col_ba_status else ""
                if _ck and _dk and _dk != "NAN":
                    _busca_auto_map[(_ck, _dk)] = (_sk, _ak, _stk)

    # ── R4 ──
    r4_total = r4_aprovado = r4_reprovado = r4_irregular = r4_nao_anex = r4_em_analise = r4_vencido = 0

    if os.path.exists(situacao_forn_csv):
        df_sit_forn = read_csv_safe(situacao_forn_csv)
        col_analise = next((c for c in df_sit_forn.columns if "lise" in c.lower() and "doc" in c.lower()), None)
        col_sit_doc = next((c for c in df_sit_forn.columns if "situa" in c.lower() and "doc" in c.lower() and "lise" not in c.lower()), None)

        def map_status_r4(row):
            cnpj_r  = re.sub(r'\D', '', str(row.get("CNPJ", "")))
            doc_r   = str(row.get("Documento", "")).strip().upper()
            analise = str(row.get(col_analise, "")).strip().upper() if col_analise else ""
            sit_doc = str(row.get(col_sit_doc, "")).strip().upper() if col_sit_doc else ""
            status_r = str(row.get("Status", "")).strip().lower()
            sit_ba = _busca_auto_map.get((cnpj_r, doc_r))
            if sit_ba:
                sd_ba, an_ba, st_ba = sit_ba
                if sd_ba == "REGULAR":
                    return "Vencido" if "vencido" in st_ba else "Aprovado"
                if sd_ba == "IRREGULAR": return "Irregular"
                if sd_ba == "ALERTA":    return "Em análise"
                if sd_ba == "NEUTRO":
                    if an_ba == "APROVADO":         return "Aprovado"
                    if an_ba == "REPROVADO":        return "Reprovado"
                    if "não anexado" in st_ba:      return "Não Anexado"
                    return "Em análise"
                if "não anexado" in st_ba: return "Não Anexado"
                return "Em análise"
            if sit_doc == "REGULAR":
                if "vencido" in status_r:
                    if analise == "APROVADO":  return "Aprovado"
                    if analise == "REPROVADO": return "Reprovado"
                    return "Em análise"
                return "Aprovado"
            if sit_doc == "IRREGULAR": return "Irregular"
            if sit_doc == "ALERTA":    return "Em análise"
            if "não anexado" in status_r: return "Não Anexado"
            if analise == "APROVADO":  return "Aprovado"
            if analise == "REPROVADO": return "Reprovado"
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

    total_pendencias   = len(df_pend)
    forn_com_pend      = df_pend[col_rs_pend].nunique()
    total_trab_ativo   = int((df_terc[col_status_terc] == "Ativo").sum())
    total_trab_inativo = int((df_terc[col_status_terc] == "Inativo").sum())

    total_forn_geral = 0
    if os.path.exists(fornecedores_csv):
        df_forn = read_csv_safe(fornecedores_csv)
        col_cnpj_forn = next((c for c in df_forn.columns if any(k in c.lower() for k in ("cpf", "cnpj", "documento"))), df_forn.columns[0])
        total_forn_geral = df_forn[col_cnpj_forn].nunique()

    total_docs       = total_docs_sit + r4_total
    total_aprov_geral = total_conformes + r4_aprovado
    total_reprov_geral = total_reprovados + r4_reprovado + r4_irregular
    pct_conf = round(total_aprov_geral / total_docs * 100, 1) if total_docs > 0 else 0
    pct_nc   = round((total_reprov_geral + total_nao_anex_r3 + total_aguard_r3 + r4_nao_anex + r4_em_analise + r4_vencido) / total_docs * 100, 1) if total_docs > 0 else 0

    return {
        "forn_cadastro":   total_forn_geral,
        "forn_com_pend":   forn_com_pend,
        "total_pendencias": total_pendencias,
        "trab_ativo":      total_trab_ativo,
        "trab_inativo":    total_trab_inativo,
        "total_terceiros": total_terceiros_r3,
        "r3_total":        total_docs_sit,
        "r3_aprovado":     total_conformes,
        "r3_reprovado":    total_reprovados,
        "r3_nao_anex":     total_nao_anex_r3,
        "r3_aguard_sub":   total_aguard_r3_elab,
        "r3_em_analise":   total_aguard_r3_real,
        "r4_total":        r4_total,
        "r4_aprovado":     r4_aprovado,
        "r4_reprovado":    r4_reprovado + r4_irregular,
        "r4_nao_anex":     r4_nao_anex,
        "r4_em_analise":   r4_em_analise,
        "r4_vencido":      r4_vencido,
        "total_docs":      total_docs,
        "total_aprovado":  total_aprov_geral,
        "total_reprovado": total_reprov_geral,
        "pct_conf":        pct_conf,
        "pct_nc":          pct_nc,
    }


# ── Utilitários de competência ────────────────────────────────────────────────
def _is_comp(val):
    return pd.notna(val) and str(val).strip() != ""

def _parse_comp(s):
    """'07/26 - Julho 2026' → (2026, 7) para ordenação"""
    if not _is_comp(s): return None
    m = re.match(r'(\d{2})/(\d{2})', str(s).strip())
    return (2000 + int(m.group(2)), int(m.group(1))) if m else None

def _label_comp(s):
    """'07/26 - Julho 2026' → '07/26'"""
    m = re.match(r'(\d{2}/\d{2})', str(s).strip())
    return m.group(1) if m else str(s)[:5]

def _ultima_comp(df, col_comp="Marcas e Representações"):
    series = df[col_comp].dropna().astype(str).str.strip().replace("", pd.NA).dropna()
    if series.empty: return "—"
    validas = [(s, _parse_comp(s)) for s in series.unique() if _parse_comp(s)]
    if not validas: return "—"
    validas.sort(key=lambda x: x[1], reverse=True)
    return validas[0][0]

def _dist_comp(df, col_comp="Marcas e Representações", top=4):
    """Distribuição por competência — top N mais recentes."""
    series = df[col_comp].dropna().astype(str).str.strip().replace("", pd.NA).dropna()
    counts = series.value_counts().to_dict()
    validas = {}
    for k, v in counts.items():
        p = _parse_comp(k)
        if p:
            validas[p] = (_label_comp(k), validas.get(p, ("", 0))[1] + v)
    dist_sorted = sorted(validas.items(), key=lambda x: x[0], reverse=True)[:top]
    return [(v[0], v[1]) for _, v in dist_sorted]  # [(label, count), ...]


def calcular_comp_r4(sit_forn_csv):
    """
    Competência dos 7 docs mensais (R4 — Fornecedores).
    Retorna:
      por_doc: {nome_doc: {total, preenchidos, faltando}}
      total_preenchidos, total_faltando
      ultima_comp
      dist_por_comp: [(label, count), ...] top 4 mais recentes
    """
    df = read_csv_safe(sit_forn_csv)
    col_comp = "Marcas e Representações"
    df["_doc_norm"] = df["Documento"].astype(str).str.strip().str.upper()
    df_comp = df[df["_doc_norm"].isin([d.upper() for d in DOCS_COMP_R4])].copy()

    por_doc = {}
    for doc in DOCS_COMP_R4:
        sub = df_comp[df_comp["_doc_norm"] == doc.upper()]
        total = len(sub)
        preenchidos = int(sub[col_comp].apply(_is_comp).sum())
        por_doc[doc] = {"total": total, "preenchidos": preenchidos, "faltando": total - preenchidos}

    return {
        "por_doc":          por_doc,
        "total_preenchidos": sum(v["preenchidos"] for v in por_doc.values()),
        "total_faltando":   sum(v["faltando"]    for v in por_doc.values()),
        "ultima_comp":      _ultima_comp(df_comp, col_comp),
        "dist_por_comp":    _dist_comp(df_comp, col_comp),
    }


def calcular_comp_r3(sit_terc_csv):
    """
    Competência dos 2 docs com competência (R3 — Terceiros): Cartão Ponto e Ficha de EPI.
    Exclui ASO, OS e Capacitação que aparecem preenchidos indevidamente.
    """
    df = read_csv_safe(sit_terc_csv)
    col_comp = "Marcas e Representações"
    df["_doc_norm"] = df["Documento"].astype(str).str.strip().str.upper()
    df_comp = df[df["_doc_norm"].isin([d.upper() for d in DOCS_COMP_R3])].copy()

    por_doc = {}
    for doc in DOCS_COMP_R3:
        sub = df_comp[df_comp["_doc_norm"] == doc.upper()]
        total = len(sub)
        preenchidos = int(sub[col_comp].apply(_is_comp).sum())
        por_doc[doc] = {"total": total, "preenchidos": preenchidos, "faltando": total - preenchidos}

    return {
        "por_doc":          por_doc,
        "total_preenchidos": sum(v["preenchidos"] for v in por_doc.values()),
        "total_faltando":   sum(v["faltando"]    for v in por_doc.values()),
        "ultima_comp":      _ultima_comp(df_comp, col_comp),
        "dist_por_comp":    _dist_comp(df_comp, col_comp),
    }
