import pandas as pd
import plotly.graph_objects as go
import json
import re
import numpy as np
from datetime import datetime
import glob as _glob
import os as _os

# ── CAMINHOS ─────────────────────────────────────────────────────────────────
# Pasta base onde o N8N salva os arquivos com nomes fixos
BASE_DIR = r"C:\Users\gabriel.evangelista\Documents\ClaudeGL\Dashboard\data"

PENDENCIAS_CSV     = BASE_DIR + r"\pendencias_zurich.csv"
TERCEIROS_CSV      = BASE_DIR + r"\terceiros_zurich.csv"
SITUACAO_CSV       = BASE_DIR + r"\situacao_terceiro_zurich.csv"
SITUACAO_FORN_CSV  = BASE_DIR + r"\situacao_fornecedor_zurich.csv"
FORNECEDORES_CSV   = BASE_DIR + r"\codigos_contrato_fornecedores_zurich.csv"
BUSCA_AUTO_CSV     = BASE_DIR + r"\busca_automatica_zurich.csv"
OUTPUT_HTML        = r"C:\Users\gabriel.evangelista\Documents\ClaudeGL\Dashboard\relatorio_fornecedores_zurich.html"

# ── CORES ─────────────────────────────────────────────────────────────────────
COR_TEAL        = "#0E8FA3"
COR_TEAL_LIGHT  = "#5BBFCC"
COR_TEAL_ESCURO = "#0A6A7A"
COR_LARANJA    = "#F4793B"
COR_CINZA      = "#6C757D"
COR_VERDE      = "#28A745"
COR_AMARELO    = "#FFC107"
COR_VERMELHO   = "#DC3545"
COR_BG         = "#F8F9FA"
COR_CARD       = "#FFFFFF"

PLOT_CONFIG = dict(
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(family="Calibri, Arial", size=12, color="#333"),
)
M  = dict(l=20, r=20, t=50, b=20)   # margem padrao
ML = dict(l=20, r=20, t=50, b=80)   # margem com legenda embaixo

# ── LEITURA ───────────────────────────────────────────────────────────────────
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

MONTHS_PT = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho",
             "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]

def normalize_competencia(comp):
    s = str(comp).strip()
    if not s or s in ("nan", "A classificar", "Não possui competência"):
        return s
    if re.match(r'^\d{2}/\d{2}\s*-\s*.+\d{4}', s):
        return s
    m = re.match(r'^(0[1-9]|1[0-2])/(20\d{2}|\d{2})$', s)
    if m:
        mm, raw_y = m.group(1), m.group(2)
        yyyy = int(raw_y) if len(raw_y) == 4 else 2000 + int(raw_y)
        yy = str(yyyy)[2:]
        return f"{mm}/{yy} - {MONTHS_PT[int(mm)-1]} {yyyy}"
    return s

def extract_competencia_from_text(text):
    m = re.search(r'\b(0[1-9]|1[0-2])/(20\d{2}|\d{2})\b', str(text))
    if not m:
        return None
    return normalize_competencia(f"{m.group(1)}/{m.group(2)}")

df_pend = read_csv_safe(PENDENCIAS_CSV)
df_terc = read_csv_safe(TERCEIROS_CSV)
df_sit  = read_csv_safe(SITUACAO_CSV)

df_pend["Empresa"] = df_pend["Razao Social"].apply(abbrev) if "Razao Social" in df_pend.columns else df_pend["Razão Social"].apply(abbrev)
df_terc["Empresa"] = df_terc["Razao Social"].apply(abbrev) if "Razao Social" in df_terc.columns else df_terc["Razão Social"].apply(abbrev)
df_sit["Empresa"]  = df_sit["Fornecedor Razão Social"].apply(abbrev) if "Fornecedor Razão Social" in df_sit.columns else df_sit["Fornecedor Razao Social"].apply(abbrev)

# normalizar nome da coluna Razão Social para pendências
col_rs_pend = "Razão Social" if "Razão Social" in df_pend.columns else "Razao Social"
col_rs_terc = "Razão Social" if "Razão Social" in df_terc.columns else "Razao Social"

df_pend["Empresa"] = df_pend[col_rs_pend].apply(abbrev)
df_terc["Empresa"] = df_terc[col_rs_terc].apply(abbrev)

# ── TIPO DE DOCUMENTO ─────────────────────────────────────────────────────────
def extrair_doc(row, area=""):
    doc = str(row.get("Documento", "")).strip()
    if doc and doc != "nan":
        return doc.upper()[:80]
    pend = str(row.get("Pendencia", row.get("Pendência", "")))
    # Apenas a primeira linha contém o nome do documento
    first_line = pend.split('\n')[0].strip()
    if area == "TERCEIROS":
        # "NOME TERCEIRO - NOME DOC, detalhe" ou "NOME - NOME DOC. detalhe"
        dash_idx = first_line.find(" - ")
        if dash_idx >= 0:
            after_dash = first_line[dash_idx + 3:]
            m = re.match(r"^([^,.]+)", after_dash)
            if m:
                return m.group(1).strip().upper()[:80]
        return first_line.upper()[:80] or "OUTROS"
    else:
        # DOCUMENTOS: "NOME DOC, detalhe"
        comma_idx = first_line.find(",")
        return (first_line[:comma_idx] if comma_idx >= 0 else first_line).strip().upper()[:80] or "OUTROS"

_col_area_for_doc = "Área da pendência" if "Área da pendência" in df_pend.columns else "Area da pendencia"
df_pend["Tipo_Doc"] = df_pend.apply(
    lambda row: extrair_doc(row, str(row.get(_col_area_for_doc, "")).strip()),
    axis=1
)
df_pend["Tipo_Doc"] = df_pend["Tipo_Doc"].str[:80]

# ── CONFORMIDADE — NOVA LÓGICA (27/05/2026) ────────────────────────────────────
# "Situação Análise Documento" é a coluna mandatória e tem precedência absoluta:
#   APROVADO  → "Aprovado"  (independente de Status ou Situação da Solicitação)
#   REPROVADO → "Reprovado" (independente de Status ou Situação da Solicitação)
# Quando NÃO ANALISADO ou ausente → usa só o Status do documento:
#   Não anexado          → "Não anexado"
#   A vencer | Vencido   → "Aguardando análise"  (Vencido dobra aqui)
#   N/A (NaN)            → "Aguardando análise"
# Situação Última Solicitação descartada — não é mais usada na classificação.

# Detectar coluna Situação Análise Documento (R3)
col_analise_r3 = next(
    (c for c in df_sit.columns if "lise" in c.lower() and "doc" in c.lower()),
    None
)

def map_status_r3(row):
    # Prioridade 1 — Situação Análise Documento
    if col_analise_r3:
        analise = str(row.get(col_analise_r3, "")).strip().upper()
        if analise == "APROVADO":   return "Aprovado"
        if analise == "REPROVADO":  return "Reprovado"

    # Prioridade 2 — Status do documento (Situação da Solicitação descartada)
    raw_status = row.get("Status", None)
    is_na = pd.isna(raw_status) or str(raw_status).strip().upper() in ("N/A", "NA", "")
    if is_na:
        return "Aguardando análise"
    s = str(raw_status).strip().lower()
    if "anexado" in s:  return "Não anexado"
    # A vencer e Vencido → ambos entram em Aguardando análise
    return "Aguardando análise"

df_sit_calc = df_sit.copy()
df_sit_calc["Status_Cat"] = df_sit_calc.apply(map_status_r3, axis=1)
df_sit_calc = df_sit_calc[df_sit_calc["Status_Cat"].notna()].copy()

TODAS_CATS = ["Aprovado", "Reprovado", "Não anexado", "Aguardando análise"]
conf_emp = (
    df_sit_calc.groupby(["Empresa", "Status_Cat"])
    .size()
    .unstack(fill_value=0)
    .reindex(columns=TODAS_CATS, fill_value=0)
)
conf_emp["Total"]        = conf_emp.sum(axis=1)
conf_emp["Nao_Conforme"] = conf_emp[["Reprovado", "Não anexado", "Aguardando análise"]].sum(axis=1)
conf_emp["Pct_Nao_Conf"] = (conf_emp["Nao_Conforme"] / conf_emp["Total"].replace(0, 1) * 100).round(1)
conf_emp["Pct_Conf"]     = (conf_emp["Aprovado"]     / conf_emp["Total"].replace(0, 1) * 100).round(1)
conf_emp = conf_emp.reset_index().sort_values("Pct_Nao_Conf", ascending=True)

total_docs_sit        = len(df_sit_calc)
total_conformes       = (df_sit_calc["Status_Cat"] == "Aprovado").sum()
total_reprovados_docs = (df_sit_calc["Status_Cat"] == "Reprovado").sum()
total_pendentes_docs  = (df_sit_calc["Status_Cat"].isin(["Não anexado", "Aguardando análise"])).sum()
pct_conformidade      = round(total_conformes / total_docs_sit * 100, 1) if total_docs_sit > 0 else 0
pct_nao_conform       = round((total_reprovados_docs + total_pendentes_docs) / total_docs_sit * 100, 1) if total_docs_sit > 0 else 0
trab_vencidos_count   = df_sit_calc[df_sit_calc["Status_Cat"] == "Reprovado"]["Terceiro CPF/CNPJ"].nunique()
total_nao_anex_r3     = int((df_sit_calc["Status_Cat"] == "Não anexado").sum())
total_aguard_r3       = int((df_sit_calc["Status_Cat"] == "Aguardando análise").sum())
total_terceiros_r3    = int(df_sit_calc["Terceiro CPF/CNPJ"].nunique()) if "Terceiro CPF/CNPJ" in df_sit_calc.columns else 0

# Split de "Aguardando análise" R3: EM_ELABORACAO (solicitação não publicada) vs APROVADO (submetido, real)
col_sit_solic_r3 = next((c for c in df_sit_calc.columns if "ltima" in c.lower() and "solic" in c.lower()), None)
if col_sit_solic_r3:
    _mask_aguard = df_sit_calc["Status_Cat"] == "Aguardando análise"
    total_aguard_r3_elab = int((_mask_aguard & (df_sit_calc[col_sit_solic_r3] == "EM_ELABORACAO")).sum())
else:
    total_aguard_r3_elab = 0
total_aguard_r3_real = total_aguard_r3 - total_aguard_r3_elab

# Status_Final: versão exibível que separa "Aguardando Submissão" de "Em Análise" dentro do R3
def _status_final_r3(row):
    if row["Status_Cat"] != "Aguardando análise":
        return row["Status_Cat"]
    if col_sit_solic_r3 and str(row.get(col_sit_solic_r3, "")).strip() == "EM_ELABORACAO":
        return "Aguardando Submissão"
    return "Em Análise"
df_sit_calc["Status_Final"] = df_sit_calc.apply(_status_final_r3, axis=1)

# ── KPIs PENDÊNCIAS ───────────────────────────────────────────────────────────
col_sit_pend = "Situação da solicitação" if "Situação da solicitação" in df_pend.columns else "Situacao da solicitacao"
col_area_pend = "Área da pendência" if "Área da pendência" in df_pend.columns else "Area da pendencia"

total_fornecedores = df_pend[col_rs_pend].nunique()
total_pendencias   = len(df_pend)
em_elaboracao      = (df_pend[col_sit_pend] == "EM_ELABORACAO").sum()
aprovado_com_pend  = (df_pend[col_sit_pend] == "APROVADO").sum()
pend_terceiros     = (df_pend[col_area_pend] == "TERCEIROS").sum()
pend_documentos    = (df_pend[col_area_pend] == "DOCUMENTOS").sum()

col_status_terc = "Status" if "Status" in df_terc.columns else "status"
total_trab_ativo   = (df_terc[col_status_terc] == "Ativo").sum()
total_trab_inativo = (df_terc[col_status_terc] == "Inativo").sum()
total_forn_geral   = int(df_sit_calc["Fornecedor CPF/CNPJ"].nunique()) if "Fornecedor CPF/CNPJ" in df_sit_calc.columns else 0

# ── DATAFRAMES PARA GRÁFICOS ──────────────────────────────────────────────────
pend_emp = df_pend.groupby("Empresa").size().reset_index(name="Total").sort_values("Total", ascending=True)

tipo_doc = (
    df_pend.groupby("Tipo_Doc").size().reset_index(name="Total")
    .sort_values("Total", ascending=False).head(15).sort_values("Total", ascending=True)
)

status_emp = df_pend.groupby(["Empresa", col_sit_pend]).size().reset_index(name="Total")
empresas_ord = df_pend.groupby("Empresa").size().sort_values(ascending=False).index.tolist()

area_emp = df_pend.groupby(["Empresa", col_area_pend]).size().reset_index(name="Total")

trab_emp = df_terc.groupby(["Empresa", col_status_terc]).size().reset_index(name="Total")
trab_emp_total = trab_emp.groupby("Empresa")["Total"].sum().sort_values(ascending=True)

# ── TABELA DE PENDÊNCIAS (inclui Competência) ─────────────────────────────────
col_marcas = "Marcas e representações" if "Marcas e representações" in df_pend.columns else "Marcas e representacoes"
col_pend_txt = "Pendência" if "Pendência" in df_pend.columns else "Pendencia"
col_cnpj_pend = next((c for c in df_pend.columns if "cpf" in c.lower() or "cnpj" in c.lower()), None)

tabela = df_pend[["Empresa", col_sit_pend, col_area_pend, "Tipo_Doc", col_marcas, col_pend_txt]].copy()
tabela.columns = ["Fornecedor", "Status", "Area", "Documento", "Competencia", "Detalhe"]
tabela["Competencia"] = tabela["Competencia"].fillna("").astype(str).str.strip()
tabela["Competencia"] = tabela["Competencia"].replace("nan", "")
# Regra: apenas 4 docs exibem Competência nas pendências de Fornecedor (Area=DOCUMENTOS)
_DOCS_COM_COMP_PEND = {
    "GFD - GUIA DO FGTS DIGITAL MENSAL",
    "DCTFWEB",
    "FOPAG - (FOLHA DE PAGAMENTO + RESUMO)",
    "COMPROVANTE BANCÁRIO DE PAGAMENTO DOS SALÁRIOS",
}
_eh_forn_pend  = tabela["Area"] == "DOCUMENTOS"
_doc_upper_pen = tabela["Documento"].str.strip().str.upper()
_sem_comp_pen  = _eh_forn_pend & ~_doc_upper_pen.isin({d.upper() for d in _DOCS_COM_COMP_PEND})
tabela.loc[_sem_comp_pen, "Competencia"] = "Não possui competência"
# ASO e Ordens de Serviço nunca possuem Competência (qualquer área)
_DOCS_SEM_COMP_TERC = {"aso", "ordens de serviço"}
_mask_sc_terc = tabela["Documento"].str.strip().str.lower().isin(_DOCS_SEM_COMP_TERC)
tabela.loc[_mask_sc_terc, "Competencia"] = "Não possui competência"

def _calc_comp_pend(row):
    comp = str(row["Competencia"]).strip()
    if comp == "Não possui competência":
        return comp
    norm = normalize_competencia(comp) if comp not in ("", "A classificar") else ""
    if norm and norm not in ("A classificar", ""):
        return norm
    from_pend = extract_competencia_from_text(row["Detalhe"])
    if from_pend:
        return from_pend
    from_doc = extract_competencia_from_text(row["Documento"])
    if from_doc:
        return from_doc
    return "A classificar"

tabela["Detalhe"] = tabela["Detalhe"].astype(str).str.strip()
tabela["Competencia"] = tabela.apply(_calc_comp_pend, axis=1)
tabela["CNPJ"] = df_pend[col_cnpj_pend].apply(
    lambda v: re.sub(r'\D', '', str(v).split('.')[0])
).values if col_cnpj_pend else ""
tabela_json = tabela.to_dict("records")
competencias_lista = sorted([c for c in tabela["Competencia"].unique() if c and c != "nan"])
competencias_json  = json.dumps(competencias_lista)

# ── TABELA DE SITUAÇÃO DOCUMENTAL (3 camadas) ─────────────────────────────────
col_trab_rs = "Terceiro Razão Social" if "Terceiro Razão Social" in df_sit_calc.columns else "Terceiro Razao Social"
col_trab_cpf = "Terceiro CPF/CNPJ"
col_dat_venc = "Data de Vencimento"
col_marcas_sit = next((c for c in df_sit_calc.columns if "marcas" in c.lower()), None)

_cols_sit = ["Empresa", col_trab_rs, "Terceiro CPF/CNPJ", "Fornecedor CPF/CNPJ", "Documento", "Status_Final", col_dat_venc]
if col_marcas_sit:
    _cols_sit.append(col_marcas_sit)
sit_tabela = df_sit_calc[_cols_sit].copy()
_col_names = ["Fornecedor", "Terceiro", "CNPJ_Terceiro", "CNPJ_Forn", "Documento", "Status", "Vencimento"]
if col_marcas_sit:
    _col_names.append("Competencia")
sit_tabela.columns = _col_names
if "Competencia" not in sit_tabela.columns:
    sit_tabela["Competencia"] = "A classificar"
else:
    sit_tabela["Competencia"] = sit_tabela["Competencia"].fillna("").replace("nan", "").apply(
        lambda v: normalize_competencia(v.strip()) if v.strip() else "A classificar"
    )
def _norm_cnpj(v):
    s = str(v).strip()
    if s in ("", "nan", "0", "None"): return ""
    # CNPJ numérico (sem formatação) → garante int sem casas decimais
    if s.replace(".", "").replace("-", "").replace("/", "").isdigit():
        try: return str(int(float(s.replace(".", "").replace("-", "").replace("/", ""))))
        except: pass
    return s
sit_tabela["CNPJ_Forn"] = sit_tabela["CNPJ_Forn"].apply(_norm_cnpj)
sit_tabela["Vencimento"] = pd.to_datetime(sit_tabela["Vencimento"], errors="coerce").dt.strftime("%d/%m/%Y").fillna("")
# Documentos sem vencimento relevante — exibem Competência mas não Vencimento
_DOCS_SEM_VENCIMENTO = {"ficha de epi", "cartão ponto com total de horas extras ou noturnas"}
_mask_sem_venc = sit_tabela["Documento"].str.strip().str.lower().isin(_DOCS_SEM_VENCIMENTO)
sit_tabela.loc[_mask_sem_venc, "Vencimento"] = ""
# Documentos sem Competência no R3 — exibem só Vencimento (se houver)
_DOCS_SEM_COMP_R3 = {"aso", "ordens de serviço"}
_mask_sem_comp_r3 = sit_tabela["Documento"].str.strip().str.lower().isin(_DOCS_SEM_COMP_R3)
sit_tabela.loc[_mask_sem_comp_r3, "Competencia"] = ""

# Mapa Python de duplicatas: nome_abrev -> [cnpj1, cnpj2, ...] (só nomes com 2+ CNPJs distintos)
_col_cnpj_sit = "Fornecedor CPF/CNPJ"
if _col_cnpj_sit in df_sit_calc.columns:
    _grp = (
        df_sit_calc.groupby("Empresa")[_col_cnpj_sit]
        .apply(lambda x: sorted(set(
            str(int(v)) if str(v).replace(".","").isdigit() else str(v).strip()
            for v in x.dropna()
            if str(v).strip() not in ("", "nan", "0")
        )))
    )
    forn_cnpj_map = {k: v for k, v in _grp.items() if len(v) >= 1}
else:
    forn_cnpj_map = {}
forn_cnpj_json = json.dumps(forn_cnpj_map, ensure_ascii=False)
sit_tabela_json = sit_tabela.to_dict("records")

terc_kpi = df_terc[["Empresa", col_status_terc]].rename(columns={"Empresa": "Fornecedor", col_status_terc: "Status"})
terc_kpi_json = terc_kpi.to_dict("records")

# ── R4: SITUAÇÃO DOCUMENTAL POR FORNECEDOR (empresa) ─────────────────────────
# Atualizado para reconhecer Aprovado e Reprovado (adicionados pelo Ricardo 27/05/2026)
def map_status_flex(val):
    if pd.isna(val): return None
    s = str(val).lower().strip()
    # Novos status do Ricardo — têm precedência
    if "aprovado" in s and "ressalva" not in s: return "Aprovado"
    if "reprovado" in s:                         return "Reprovado"
    # Status legacy (busca automática e docs sem análise formal)
    if "vencer" in s:   return "Conforme"
    if "vencido" in s:  return "Vencido"
    if "anexado" in s:  return "Não anexado"
    return None

_sit_forn_ok = False
if _os.path.exists(SITUACAO_FORN_CSV):
    df_sit_forn = read_csv_safe(SITUACAO_FORN_CSV)
    _sit_forn_ok = True

# ── BUSCA AUTOMÁTICA — lookup (cnpj_digits, doc_upper) → (Situação Documento, Situação Análise) ──
_busca_auto_map = {}
if _os.path.exists(BUSCA_AUTO_CSV):
    _df_ba = read_csv_safe(BUSCA_AUTO_CSV)
    _col_ba_cnpj = next((c for c in _df_ba.columns if "cnpj" in c.lower()), None)
    # "Documento" exato primeiro; fallback para coluna com "doc" excluindo as com "situa" ou "venc"
    _col_ba_doc  = next((c for c in _df_ba.columns if c.strip().lower() == "documento"), None) or \
                   next((c for c in _df_ba.columns
                         if "doc" in c.lower() and "situa" not in c.lower() and "venc" not in c.lower()), None)
    _col_ba_sit  = next((c for c in _df_ba.columns
                         if "situa" in c.lower() and "doc" in c.lower() and "lise" not in c.lower()), None)
    _col_ba_anal = next((c for c in _df_ba.columns
                         if "lise" in c.lower() and "doc" in c.lower()), None)
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

if _sit_forn_ok:
    col_r4_rs = df_sit_forn.columns[0]
    df_sit_forn["Empresa"] = df_sit_forn[col_r4_rs].apply(abbrev)

    # "Situação Análise Documento" contém "lise"; "Situação Documento" não
    col_analise   = next((c for c in df_sit_forn.columns if "lise" in c.lower() and "doc" in c.lower()), None)
    col_sit_doc   = next((c for c in df_sit_forn.columns
                          if "situa" in c.lower() and "doc" in c.lower() and "lise" not in c.lower()), None)

    def map_status_r4(row):
        sit_doc   = str(row.get(col_sit_doc, "") if col_sit_doc else "").strip().upper()
        analise   = str(row.get(col_analise, "") if col_analise else "").strip().upper()
        st_row    = str(row.get("Status", "")).strip().lower()
        cnpj_r    = re.sub(r'\D', '', str(row.get("CNPJ", "")))
        doc_r     = str(row.get("Documento", "")).strip().upper()
        auto_entry = _busca_auto_map.get((cnpj_r, doc_r))

        if auto_entry:
            # busca_auto tem prioridade — Status vem do busca_auto (resultado da busca automática)
            sd_ba, an_ba, st_ba = auto_entry
            if sd_ba == "REGULAR":
                return "Vencido" if "vencido" in st_ba else "Aprovado"
            if sd_ba == "IRREGULAR":
                return "Irregular"
            if sd_ba == "ALERTA":
                return "Em análise"
            if sd_ba == "NEUTRO":
                if an_ba == "APROVADO":           return "Aprovado"
                if an_ba == "REPROVADO":          return "Reprovado"
                if "não anexado" in st_ba:        return "Não Anexado"
                return "Em análise"
            # vazio em busca_auto
            if "não anexado" in st_ba: return "Não Anexado"
            return "Em análise"

        # Não está em busca_auto → usa colunas da própria linha sitForn
        if sit_doc == "REGULAR":
            if "vencido" in st_row:
                if analise == "APROVADO":  return "Aprovado"
                if analise == "REPROVADO": return "Reprovado"
                return "Em análise"
            return "Aprovado"
        if sit_doc == "IRREGULAR":
            return "Irregular"
        if sit_doc == "ALERTA":
            return "Em análise"
        if sit_doc == "NEUTRO":
            if "não anexado" in st_row: return "Não Anexado"
            if analise == "APROVADO":   return "Aprovado"
            if analise == "REPROVADO":  return "Reprovado"
            return "Em análise"
        # vazio → mesma regra do NEUTRO
        if "não anexado" in st_row: return "Não Anexado"
        if analise == "APROVADO":   return "Aprovado"
        if analise == "REPROVADO":  return "Reprovado"
        return "Em análise"

    df_sit_forn["Status_Cat"] = df_sit_forn.apply(map_status_r4, axis=1)
    df_sit_forn_calc = df_sit_forn[df_sit_forn["Status_Cat"].notna()].copy()

    col_marcas_r4 = next((c for c in df_sit_forn_calc.columns if "marcas" in c.lower()), None)
    _r4_cols = ["Empresa", "Documento", "Status_Cat", "Data de Vencimento"]
    if col_marcas_r4:
        _r4_cols.append(col_marcas_r4)
    forn_sit_tabela = df_sit_forn_calc[_r4_cols].copy()
    _r4_names = ["Fornecedor", "Documento", "Status", "Vencimento"]
    if col_marcas_r4:
        _r4_names.append("Competencia")
    forn_sit_tabela.columns = _r4_names
    if "CNPJ" in df_sit_forn_calc.columns:
        forn_sit_tabela["CNPJ"] = df_sit_forn_calc["CNPJ"].apply(
            lambda v: re.sub(r'\D', '', str(v))).values
    if "Competencia" not in forn_sit_tabela.columns:
        forn_sit_tabela["Competencia"] = ""
    else:
        forn_sit_tabela["Competencia"] = forn_sit_tabela["Competencia"].fillna("").replace("nan", "").apply(
            lambda v: normalize_competencia(v.strip()) if str(v).strip() else ""
        )
    # Docs de busca automática não exibem Competência — apenas Vencimento é relevante
    if _busca_auto_map and "CNPJ" in forn_sit_tabela.columns:
        _is_auto_mask = forn_sit_tabela.apply(
            lambda row: (re.sub(r'\D', '', str(row.get("CNPJ", ""))), str(row.get("Documento", "")).strip().upper()) in _busca_auto_map,
            axis=1
        )
        forn_sit_tabela.loc[_is_auto_mask, "Competencia"] = ""
    # Apenas estes docs exibem Competência no R4 — todos os demais ficam em branco
    _DOCS_COM_COMP_R4 = {
        "GFD - GUIA DO FGTS DIGITAL MENSAL",
        "DCTFWEB",
        "FOPAG - (FOLHA DE PAGAMENTO + RESUMO)",
        "COMPROVANTE BANCÁRIO DE PAGAMENTO DOS SALÁRIOS",
    }
    _doc_upper_r4 = forn_sit_tabela["Documento"].str.strip().str.upper()
    _sem_comp_r4  = ~_doc_upper_r4.isin({d.upper() for d in _DOCS_COM_COMP_R4})
    forn_sit_tabela.loc[_sem_comp_r4, "Competencia"] = ""
    forn_sit_tabela["Vencimento"] = pd.to_datetime(
        forn_sit_tabela["Vencimento"], errors="coerce"
    ).dt.strftime("%d/%m/%Y").fillna("")
    forn_sit_json = forn_sit_tabela.to_dict("records")

    r4_total        = len(df_sit_forn_calc)
    r4_aprovado     = int((df_sit_forn_calc["Status_Cat"] == "Aprovado").sum())
    r4_reprovado    = int((df_sit_forn_calc["Status_Cat"] == "Reprovado").sum())
    r4_irregular    = int((df_sit_forn_calc["Status_Cat"] == "Irregular").sum())
    r4_alerta       = int((df_sit_forn_calc["Status_Cat"] == "Alerta").sum())
    r4_nao_anex     = int((df_sit_forn_calc["Status_Cat"] == "Não Anexado").sum())
    r4_em_analise   = int((df_sit_forn_calc["Status_Cat"] == "Em análise").sum())
    r4_vencido      = int((df_sit_forn_calc["Status_Cat"] == "Vencido").sum())
    r4_nao_conf     = r4_reprovado + r4_irregular + r4_alerta + r4_nao_anex + r4_em_analise + r4_vencido
    r4_pct_nc       = round(r4_nao_conf / r4_total * 100, 1) if r4_total > 0 else 0.0
    r4_pct_c        = round(r4_aprovado / r4_total * 100, 1) if r4_total > 0 else 0.0
    r4_fornecedores = int(
        df_sit_forn_calc["CNPJ"].dropna()
        .apply(lambda v: re.sub(r'\D', '', str(v))).nunique()
    ) if "CNPJ" in df_sit_forn_calc.columns else int(df_sit_forn_calc["Empresa"].nunique())
else:
    forn_sit_json   = []
    r4_total = r4_aprovado = r4_reprovado = r4_irregular = r4_alerta = r4_nao_anex = r4_em_analise = r4_vencido = r4_fornecedores = 0
    r4_pct_nc = r4_pct_c = 0.0
    r4_nao_conf = 0
    df_sit_forn_calc = pd.DataFrame()

# Total de fornecedores = união de CNPJs do R3 + R4 (evita subcontagem quando
# um fornecedor tem docs de empresa mas nenhum terceiro cadastrado)
def _norm_cnpj_str(v):
    return re.sub(r'\D', '', str(v))

nomes_r3 = set(df_sit_calc["Empresa"].dropna().unique()) if "Empresa" in df_sit_calc.columns else set()
nomes_r4 = set(df_sit_forn_calc["Empresa"].dropna().unique()) if not df_sit_forn_calc.empty and "Empresa" in df_sit_forn_calc.columns else set()
if _os.path.exists(FORNECEDORES_CSV):
    df_forn_geral = read_csv_safe(FORNECEDORES_CSV)
    col_cnpj_forn = next((c for c in df_forn_geral.columns if any(k in c.lower() for k in ("cpf", "cnpj", "documento"))), df_forn_geral.columns[0])
    col_rs_forn   = next((c for c in df_forn_geral.columns if ("raz" in c.lower() or "fornecedor" in c.lower()) and "documento" not in c.lower()), df_forn_geral.columns[0])
    total_forn_geral = df_forn_geral[col_cnpj_forn].nunique()
    # Enriquecer forn_cnpj_map com duplicatas do cadastro
    _cad_grp = df_forn_geral.groupby(col_rs_forn)[col_cnpj_forn].apply(
        lambda x: sorted(set(str(v).strip() for v in x.dropna() if str(v).strip() not in ("", "nan")))
    )
    forn_cnpj_map.update({k: v for k, v in _cad_grp.items() if len(v) >= 1})
    forn_cnpj_json = json.dumps(forn_cnpj_map, ensure_ascii=False)
    all_cadastro_names_json = json.dumps(sorted(df_forn_geral[col_rs_forn].dropna().unique().tolist()), ensure_ascii=False)
else:
    total_forn_geral = len(nomes_r3 | nomes_r4) or total_forn_geral
    all_cadastro_names_json = "[]"

# Fornecedores com ao menos 1 execução (doc enviado em R4 próprio ou R3 via terceiro)
_col_cnpj_r4 = next((c for c in df_sit_forn_calc.columns if "cpf" in c.lower() or "cnpj" in c.lower()), None)
_col_stat_r4 = next((c for c in df_sit_forn_calc.columns if "status" in c.lower()), None)
_col_cnpj_r3 = next((c for c in df_sit_calc.columns if "fornecedor" in c.lower() and ("cpf" in c.lower() or "cnpj" in c.lower())), None)
_col_stat_r3 = next((c for c in df_sit_calc.columns if c.lower() == "status" or c == "Status_Cat"), "Status_Cat")

_forn_exec_r4 = set(str(v) for v in df_sit_forn_calc[_col_cnpj_r4].dropna().unique()) if _col_cnpj_r4 else set()
_forn_exec_r3 = set(str(v) for v in df_sit_calc[_col_cnpj_r3].dropna().unique()) if _col_cnpj_r3 else set()
total_forn_com_execucao = len(_forn_exec_r4 | _forn_exec_r3)

# Fornecedores sem execução: no cadastro mas sem docs em R3 ou R4
def _norm_c(v):
    s = str(v).strip()
    if s.endswith(".0"): s = s[:-2]
    if s in ("", "nan", "None"): return ""
    # CPF tem 11 dígitos — não padeia para 14. CNPJ com < 14 dígitos é repadeia.
    if s.isdigit() and len(s) > 11 and len(s) < 14:
        s = s.zfill(14)
    return s

_exec_norm = {_norm_c(c) for c in (_forn_exec_r4 | _forn_exec_r3)} - {""}
if _os.path.exists(FORNECEDORES_CSV) and "df_forn_geral" in dir():
    _df_se = df_forn_geral[[col_rs_forn, col_cnpj_forn]].copy()
    _df_se["_cnpj_n"] = _df_se[col_cnpj_forn].apply(_norm_c)
    _df_se = _df_se[(_df_se["_cnpj_n"] != "") & (~_df_se["_cnpj_n"].isin(_exec_norm))]
    _df_se = _df_se.drop_duplicates(subset="_cnpj_n")[[col_rs_forn, col_cnpj_forn]]
    _df_se.columns = ["Razão Social", "CPF/CNPJ"]
    sem_exec_json = json.dumps(_df_se.to_dict("records"), ensure_ascii=False)
    total_sem_execucao = len(_df_se)
    total_forn_com_execucao = total_forn_geral - total_sem_execucao
else:
    sem_exec_json = "[]"
    total_sem_execucao = 0

# ── CONTRATOS POR FORNECEDOR ──────────────────────────────────────────────────
# Estrutura: lista de {nome, cnpj, contratos:[...], terceiros_by_contract:{cod:[{nome,cnpj,cargo,aeroporto,status}]}}
_contratos_map = {}

if _os.path.exists(FORNECEDORES_CSV):
    # Lê sem o filtro drop_cols de read_csv_safe (que remove "Contrato 1..10")
    _df_ct = None
    for _enc in ["utf-8-sig", "latin-1", "utf-8"]:
        try:
            with open(FORNECEDORES_CSV, encoding=_enc, errors="replace") as _f: _s = _f.read(4096)
            _sep = ";" if _s.count(";") > _s.count(",") else ","
            _df_ct = pd.read_csv(FORNECEDORES_CSV, encoding=_enc, sep=_sep, on_bad_lines="skip")
            _df_ct.columns = _df_ct.columns.str.strip()
            break
        except Exception: continue
    if _df_ct is None:
        _df_ct = pd.DataFrame()
    _col_ct_cnpj = next((c for c in _df_ct.columns if "doc" in c.lower() and "forn" in c.lower()), _df_ct.columns[0] if len(_df_ct.columns) else "CNPJ")
    _col_ct_nome = next((c for c in _df_ct.columns if "forn" in c.lower() and "doc" not in c.lower()), _df_ct.columns[1])
    def _cnpj_digits(v):
        s = str(v).strip().split('.')[0]  # remove .0 de floats
        return re.sub(r'\D', '', s)

    for _, _r in _df_ct.iterrows():
        _cnpj_c = _cnpj_digits(_r[_col_ct_cnpj])
        _nome_c = str(_r[_col_ct_nome]).strip()
        _codes  = [str(_r.get(f"Contrato {i}", "")).strip()
                   for i in range(1, 11)
                   if str(_r.get(f"Contrato {i}", "")).strip() not in ("", "nan")]
        if _cnpj_c and _cnpj_c not in _contratos_map:
            _contratos_map[_cnpj_c] = {
                "nome": abbrev(_nome_c), "nome_full": _nome_c, "cnpj": _cnpj_c,
                "contratos": sorted(set(_codes)), "terceiros_by_contract": {}
            }
        elif _cnpj_c:
            _contratos_map[_cnpj_c]["contratos"] = sorted(
                set(_contratos_map[_cnpj_c]["contratos"] + _codes))

# Enriquecer com terceiros (usa df_terc que já foi carregado)
_col_terc_forn_cnpj  = next((c for c in df_terc.columns if c.lower().replace(" ","").startswith("cpf/cnpj") and "terceiro" not in c.lower()), None)
_col_terc_cod_ct     = next((c for c in df_terc.columns if "c" in c.lower() and "digo" in c.lower() and "contrato" in c.lower() and "vinc" in c.lower()), None)
_col_terc_aeroporto  = next((c for c in df_terc.columns if "aeroporto" in c.lower() or ("digo" in c.lower() and "aero" in c.lower())), None)
_col_terc_nome_terc  = next((c for c in df_terc.columns if "terceiro" in c.lower() and ("raz" in c.lower() or "social" in c.lower() or "nome" in c.lower())), None)
_col_terc_cnpj_terc  = next((c for c in df_terc.columns if "terceiro" in c.lower() and ("cpf" in c.lower() or "cnpj" in c.lower())), None)
_col_terc_cargo      = next((c for c in df_terc.columns if "cargo" in c.lower()), None)

for _, _r in df_terc.iterrows():
    _forn_cnpj_t = _cnpj_digits(_r.get(_col_terc_forn_cnpj, "") if _col_terc_forn_cnpj else "")
    if not _forn_cnpj_t:
        continue
    if _forn_cnpj_t not in _contratos_map:
        _nome_t = abbrev(str(_r.get(col_rs_terc, "")).strip())
        _contratos_map[_forn_cnpj_t] = {
            "nome": _nome_t, "nome_full": str(_r.get(col_rs_terc, "")).strip(),
            "cnpj": _forn_cnpj_t, "contratos": [], "terceiros_by_contract": {}
        }
    _cod_raw = str(_r.get(_col_terc_cod_ct, "") if _col_terc_cod_ct else "").strip()
    _contratos_terc = [c.strip() for c in _cod_raw.split("/") if c.strip() and c.strip() != "nan"]
    if not _contratos_terc:
        continue
    _aero_raw = str(_r.get(_col_terc_aeroporto, "") if _col_terc_aeroporto else "").strip().upper()
    _terc_info = {
        "nome":       str(_r.get(_col_terc_nome_terc, "") if _col_terc_nome_terc else "").strip(),
        "cnpj":       _cnpj_digits(_r.get(_col_terc_cnpj_terc, "") if _col_terc_cnpj_terc else ""),
        "cargo":      str(_r.get(_col_terc_cargo, "") if _col_terc_cargo else "").strip(),
        "aeroporto":  "CAIF" if _aero_raw == "FLN" else _aero_raw,
        "status":     str(_r.get(col_status_terc, "")).strip(),
    }
    for _ct in _contratos_terc:
        _contratos_map[_forn_cnpj_t]["terceiros_by_contract"].setdefault(_ct, []).append(_terc_info)

contratos_list = sorted(
    [v for v in _contratos_map.values() if v["contratos"] or v["terceiros_by_contract"]],
    key=lambda x: x["nome"]
)
contratos_json = json.dumps(contratos_list, ensure_ascii=False)

# Enriquecer forn_cnpj_map com _contratos_map (fonte autoritativa — cobre todos os fornecedores)
_ct_nome_cnpjs: dict = {}
for _ct_entry in _contratos_map.values():
    _n, _c = _ct_entry.get("nome", ""), _ct_entry.get("cnpj", "")
    if _n and _c:
        _ct_nome_cnpjs.setdefault(_n, set()).add(_c)
for _n, _cnpj_set in _ct_nome_cnpjs.items():
    forn_cnpj_map[_n] = sorted(set(forn_cnpj_map.get(_n, []) + list(_cnpj_set)))
forn_cnpj_json = json.dumps(forn_cnpj_map, ensure_ascii=False)

# ── SIMULAÇÃO COM DADOS DO BD (dados simulados para demo) ─────────────────────
np.random.seed(42)
_meses_dt   = pd.date_range(end="2026-05-01", periods=24, freq="MS")
MESES_HIST  = [d.strftime("%b/%Y") for d in _meses_dt]
_trend      = np.linspace(78.0, pct_nao_conform, 24)
_noise      = np.random.normal(0, 2.5, 24); _noise[-1] = 0
HIST_NC     = np.clip(_trend + _noise, 40, 95).round(1).tolist()
HIST_NC[-1] = pct_nao_conform

_top5 = conf_emp.nlargest(5, "Pct_Nao_Conf")
HIST_FORN_DATA = {}
for _, r in _top5.iterrows():
    base = float(r["Pct_Nao_Conf"])
    t    = np.linspace(min(base + 20, 95), base, 24) + np.random.normal(0, 3.5, 24)
    t[-1] = base
    HIST_FORN_DATA[r["Empresa"]] = np.clip(t, 10, 100).round(1).tolist()

COMP_LABELS_BD = ["Jan/2026", "Fev/2026", "Mar/2026", "Abr/2026", "Mai/2026"]
COMP_W_BD      = [0.14, 0.19, 0.25, 0.23, 0.19]



# ── FIGURAS ───────────────────────────────────────────────────────────────────

# Fig 1 — Pendências por fornecedor
fig1 = go.Figure(go.Bar(
    x=pend_emp["Total"], y=pend_emp["Empresa"], orientation="h",
    marker_color=COR_TEAL, text=pend_emp["Total"], textposition="outside",
))
fig1.update_layout(**PLOT_CONFIG, margin=M,
    title=dict(text="Pendências por Fornecedor", font=dict(size=15, color=COR_TEAL)),
    height=max(350, 40 * len(pend_emp)),
    xaxis=dict(showgrid=True, gridcolor="#eee"), yaxis=dict(automargin=True),
)

# Fig 2 — Top 15 tipos de documento
fig2 = go.Figure(go.Bar(
    x=tipo_doc["Total"], y=tipo_doc["Tipo_Doc"], orientation="h",
    marker_color=COR_LARANJA, text=tipo_doc["Total"], textposition="outside",
))
fig2.update_layout(**PLOT_CONFIG, margin=M,
    title=dict(text="Top 15 Tipos de Documentos com Pendências", font=dict(size=15, color=COR_TEAL)),
    height=500,
    xaxis=dict(showgrid=True, gridcolor="#eee"), yaxis=dict(automargin=True),
)

# Fig 3 — Status (Pendente / Em análise) por empresa
df_elab = status_emp[status_emp[col_sit_pend] == "EM_ELABORACAO"].set_index("Empresa")["Total"]
df_apro = status_emp[status_emp[col_sit_pend] == "APROVADO"].set_index("Empresa")["Total"]
fig3 = go.Figure()
fig3.add_trace(go.Bar(
    name="Pendente (não enviado)", orientation="h", marker_color=COR_VERMELHO,
    x=[df_elab.get(e, 0) for e in empresas_ord], y=empresas_ord,
    text=[df_elab.get(e, 0) for e in empresas_ord], textposition="inside",
))
fig3.add_trace(go.Bar(
    name="Em Análise (c/ pendências)", orientation="h", marker_color=COR_AMARELO,
    x=[df_apro.get(e, 0) for e in empresas_ord], y=empresas_ord,
    text=[df_apro.get(e, 0) for e in empresas_ord], textposition="inside",
))
fig3.update_layout(**PLOT_CONFIG, barmode="stack",
    title=dict(text="Status das Pendências por Fornecedor", font=dict(size=15, color=COR_TEAL)),
    height=max(350, 45 * len(empresas_ord)),
    legend=dict(orientation="h", yanchor="top", y=-0.06, xanchor="center", x=0.5),
    margin=ML, yaxis=dict(automargin=True),
)

# Fig 4 — Área por empresa
df_ter = area_emp[area_emp[col_area_pend] == "TERCEIROS"].set_index("Empresa")["Total"]
df_doc = area_emp[area_emp[col_area_pend] == "DOCUMENTOS"].set_index("Empresa")["Total"]
fig4 = go.Figure()
fig4.add_trace(go.Bar(name="Terceiros", orientation="h", marker_color=COR_TEAL,
    x=[df_ter.get(e, 0) for e in empresas_ord], y=empresas_ord))
fig4.add_trace(go.Bar(name="Documentais (DOCUMENTOS)", orientation="h", marker_color=COR_TEAL_LIGHT,
    x=[df_doc.get(e, 0) for e in empresas_ord], y=empresas_ord))
fig4.update_layout(**PLOT_CONFIG, barmode="group",
    title=dict(text="Pendências por Área — Terceiros vs Documentais", font=dict(size=15, color=COR_TEAL)),
    height=max(350, 50 * len(empresas_ord)),
    legend=dict(orientation="h", yanchor="top", y=-0.06, xanchor="center", x=0.5),
    margin=ML, yaxis=dict(automargin=True),
)

# Fig 5 — Donut
fig5 = go.Figure(go.Pie(
    labels=["Terceiros", "Documentais (DOCUMENTOS)"],
    values=[pend_terceiros, pend_documentos],
    hole=0.55, marker_colors=[COR_TEAL, COR_LARANJA], textinfo="label+percent",
))
fig5.update_layout(**PLOT_CONFIG, margin=M,
    title=dict(text="Distribuição por Área", font=dict(size=15, color=COR_TEAL)),
    height=320, showlegend=False,
)

# Fig 6 — Trabalhadores por empresa
trab_ativo   = trab_emp[trab_emp[col_status_terc] == "Ativo"].set_index("Empresa")["Total"]
trab_inativo = trab_emp[trab_emp[col_status_terc] == "Inativo"].set_index("Empresa")["Total"]
trab_empresas = trab_emp_total.index.tolist()
fig6 = go.Figure()
fig6.add_trace(go.Bar(name="Ativos", orientation="h", marker_color=COR_VERDE,
    x=[trab_ativo.get(e, 0) for e in trab_empresas], y=trab_empresas,
    text=[trab_ativo.get(e, 0) for e in trab_empresas], textposition="inside"))
fig6.add_trace(go.Bar(name="Inativos", orientation="h", marker_color=COR_CINZA,
    x=[trab_inativo.get(e, 0) for e in trab_empresas], y=trab_empresas,
    text=[trab_inativo.get(e, 0) for e in trab_empresas], textposition="inside"))
fig6.update_layout(**PLOT_CONFIG, barmode="stack",
    title=dict(text="Terceiros Cadastrados por Fornecedor", font=dict(size=15, color=COR_TEAL)),
    height=max(350, 38 * len(trab_empresas)),
    legend=dict(orientation="h", yanchor="top", y=-0.06, xanchor="center", x=0.5),
    margin=ML, yaxis=dict(automargin=True),
)

# Fig 7 — % Não Conformidade por fornecedor
cores_conf = [COR_VERDE if p <= 30 else COR_AMARELO if p <= 60 else COR_VERMELHO
              for p in conf_emp["Pct_Nao_Conf"]]
_cd_cols = ["Aprovado", "Reprovado", "Não anexado", "Aguardando análise", "Total"]
_cd_vals  = conf_emp[_cd_cols].values
fig7 = go.Figure(go.Bar(
    x=conf_emp["Pct_Nao_Conf"], y=conf_emp["Empresa"], orientation="h",
    marker_color=cores_conf,
    text=[f"{v}%" for v in conf_emp["Pct_Nao_Conf"]], textposition="outside",
    customdata=_cd_vals,
    hovertemplate=(
        "<b>%{y}</b><br>% Nao Conforme: %{x}%<br>"
        "Aprovado: %{customdata[0]}<br>Reprovado: %{customdata[1]}<br>"
        "Nao anexado: %{customdata[2]}<br>Aguardando analise: %{customdata[3]}<br>"
        "Total docs: %{customdata[4]}"
        "<extra></extra>"
    ),
))
fig7.update_layout(**PLOT_CONFIG, margin=M,
    title=dict(text="% de Não Conformidade por Fornecedor", font=dict(size=15, color=COR_TEAL)),
    height=max(350, 40 * len(conf_emp)),
    xaxis=dict(showgrid=True, gridcolor="#eee", ticksuffix="%", range=[0, 115]),
    yaxis=dict(automargin=True),
)

# Fig 8 — Status 5 camadas por empresa (nova regra de elaboração)
conf_ord = conf_emp.sort_values("Pct_Nao_Conf", ascending=False)
emp_c8   = conf_ord["Empresa"].tolist()
ci       = conf_ord.set_index("Empresa")

def _val(e, col): return int(ci.loc[e, col]) if e in ci.index and col in ci.columns else 0

fig8 = go.Figure()
fig8.add_trace(go.Bar(name="Aprovado", orientation="h", marker_color=COR_VERDE,
    x=[_val(e, "Aprovado") for e in emp_c8], y=emp_c8))
fig8.add_trace(go.Bar(name="Reprovado", orientation="h", marker_color=COR_VERMELHO,
    x=[_val(e, "Reprovado") for e in emp_c8], y=emp_c8))
fig8.add_trace(go.Bar(name="Não anexado", orientation="h", marker_color=COR_AMARELO,
    x=[_val(e, "Não anexado") for e in emp_c8], y=emp_c8))
fig8.add_trace(go.Bar(name="Aguardando análise", orientation="h", marker_color=COR_LARANJA,
    x=[_val(e, "Aguardando análise") for e in emp_c8], y=emp_c8))
fig8.update_layout(**PLOT_CONFIG, barmode="stack",
    title=dict(text="Situação Documental por Fornecedor",
               font=dict(size=15, color=COR_TEAL)),
    height=max(350, 45 * len(emp_c8)),
    legend=dict(orientation="h", yanchor="top", y=-0.06, xanchor="center", x=0.5),
    margin=ML, yaxis=dict(automargin=True),
)

# ── SERIALIZAÇÃO ─────────────────────────────────────────────────────────────
def fig_div(fig, div_id):
    return fig.to_html(full_html=False, include_plotlyjs=False, div_id=div_id)

DATA_HOJE = datetime.now().strftime("%d/%m/%Y %H:%M")
competencias_opts = "".join(f'<option value="{c}">{c}</option>' for c in competencias_lista)
# contratos_json já calculado acima

# ── HTML ──────────────────────────────────────────────────────────────────────
html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Relatório de Fornecedores — Zurich Airport</title>
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.8.2/jspdf.plugin.autotable.min.js"></script>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: Calibri, Arial, sans-serif; background: {COR_BG}; color: #333; }}

  .header {{
    background: {COR_TEAL}; color: white; padding: 20px 32px;
    display: flex; align-items: center; justify-content: space-between;
    box-shadow: 0 2px 8px rgba(0,0,0,.15);
  }}
  .header h1 {{ font-size: 22px; font-weight: 700; letter-spacing: .5px; }}
  .header .subtitle {{ font-size: 13px; opacity: .85; margin-top: 4px; }}
  .header .badge {{
    background: rgba(255,255,255,.18); border: 1px solid rgba(255,255,255,.4);
    border-radius: 6px; padding: 6px 14px; font-size: 13px; text-align: center; line-height: 1.5;
  }}
  .badge-data {{ font-weight: 700; font-size: 15px; display: block; }}

  .container {{ max-width: 1400px; margin: 0 auto; padding: 24px 20px; }}

  .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(155px, 1fr)); gap: 14px; margin-bottom: 28px; }}
  .kpi-card {{
    background: {COR_CARD}; border-radius: 10px; padding: 16px 14px;
    box-shadow: 0 1px 6px rgba(0,0,0,.08); border-top: 4px solid {COR_TEAL}; text-align: center;
    position: relative;
  }}
  .kpi-card[data-tooltip]::after {{
    content: attr(data-tooltip);
    position: absolute; bottom: calc(100% + 8px); left: 50%; transform: translateX(-50%);
    background: #1a2a35; color: #fff; font-size: 12px; font-weight: 400; line-height: 1.45;
    padding: 8px 12px; border-radius: 7px; width: 220px; text-align: left;
    white-space: normal; pointer-events: none; z-index: 9999;
    opacity: 0; visibility: hidden; transition: opacity .18s ease, visibility .18s ease;
    box-shadow: 0 4px 14px rgba(0,0,0,.25);
  }}
  .kpi-card[data-tooltip]::before {{
    content: "";
    position: absolute; bottom: calc(100% + 2px); left: 50%; transform: translateX(-50%);
    border: 6px solid transparent; border-top-color: #1a2a35;
    pointer-events: none; z-index: 9999;
    opacity: 0; visibility: hidden; transition: opacity .18s ease, visibility .18s ease;
  }}
  .kpi-card[data-tooltip]:hover::after,
  .kpi-card[data-tooltip]:hover::before {{ opacity: 1; visibility: visible; }}
  .kpi-card.orange {{ border-top-color: {COR_LARANJA}; }}
  .kpi-card.red    {{ border-top-color: {COR_VERMELHO}; }}
  .kpi-card.yellow {{ border-top-color: {COR_AMARELO}; }}
  .kpi-card.green  {{ border-top-color: {COR_VERDE}; }}
  .kpi-card.gray   {{ border-top-color: {COR_CINZA}; }}
  .kpi-val  {{ font-size: 32px; font-weight: 700; color: {COR_TEAL}; line-height: 1.1; }}
  .kpi-card.orange .kpi-val {{ color: {COR_LARANJA}; }}
  .kpi-card.red    .kpi-val {{ color: {COR_VERMELHO}; }}
  .kpi-card.yellow .kpi-val {{ color: #b38600; }}
  .kpi-card.green  .kpi-val {{ color: {COR_VERDE}; }}
  .kpi-card.gray   .kpi-val {{ color: {COR_CINZA}; }}
  .kpi-label {{ font-size: 11px; color: #666; margin-top: 6px; font-weight: 600; text-transform: uppercase; letter-spacing: .4px; }}

  .section-title {{
    font-size: 16px; font-weight: 700; color: {COR_TEAL};
    margin: 28px 0 14px; padding-bottom: 8px;
    border-bottom: 2px solid {COR_TEAL}; letter-spacing: .3px;
  }}

  .chart-card {{
    background: {COR_CARD}; border-radius: 10px;
    box-shadow: 0 1px 6px rgba(0,0,0,.08); padding: 20px; margin-bottom: 20px;
  }}
  .chart-row {{ display: grid; gap: 20px; margin-bottom: 0; }}
  .chart-row.col2 {{ grid-template-columns: 1fr 1fr; }}
  @media (max-width: 900px) {{ .chart-row.col2 {{ grid-template-columns: 1fr; }} }}

  /* Legenda de cores do % conformidade */
  .legenda-conf {{ display: flex; gap: 18px; margin-bottom: 10px; flex-wrap: wrap; }}
  .legenda-item {{ display: flex; align-items: center; gap: 6px; font-size: 12px; color: #555; }}
  .legenda-dot {{ width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0; }}

  .filtro-bar {{
    background: {COR_CARD}; border-radius: 10px;
    box-shadow: 0 1px 6px rgba(0,0,0,.08); padding: 16px 20px;
    margin-bottom: 16px; display: flex; flex-wrap: wrap; gap: 12px; align-items: center;
  }}
  .filtro-bar label {{ font-size: 12px; font-weight: 700; color: {COR_TEAL}; text-transform: uppercase; }}
  .filtro-bar select, .filtro-bar input {{
    border: 1px solid #cde; border-radius: 6px; padding: 6px 10px;
    font-size: 13px; font-family: Calibri, Arial, sans-serif;
    background: white; color: #333; cursor: pointer;
  }}
  .filtro-bar select:focus, .filtro-bar input:focus {{ outline: 2px solid {COR_TEAL}; border-color: {COR_TEAL}; }}
  .btn-action {{
    border: none; border-radius: 6px; padding: 6px 14px; font-size: 13px;
    cursor: pointer; font-family: Calibri, Arial, sans-serif; font-weight: 600;
  }}
  .btn-limpar {{ background: {COR_TEAL}; color: white; }}
  .btn-limpar:hover {{ background: #0a7a8d; }}
  .btn-export {{ background: {COR_VERDE}; color: white; }}
  .btn-export:hover {{ background: #1e7e34; }}
  .btn-export-pdf {{ background: #c0392b; color: white; }}
  .btn-export-pdf:hover {{ background: #96281b; }}
  .btn-export-csv {{ background: {COR_CINZA}; color: white; }}
  .btn-export-csv:hover {{ background: #545b62; }}
  .btn-toggle {{ background: #6f42c1; color: white; }}
  .btn-toggle:hover {{ background: #5a32a3; }}
  .export-group {{ display: flex; gap: 6px; align-items: center; flex-wrap: wrap; }}
  .export-label {{ font-size: 11px; color: #999; font-weight: 600; text-transform: uppercase; margin-right: 2px; }}
  /* Visualização agrupada */
  .grupo-card {{
    background: #f8f9fa; border-radius: 8px; padding: 12px 16px;
    margin-bottom: 10px; border-left: 4px solid {COR_TEAL};
  }}
  .grupo-card.nc {{ border-left-color: {COR_VERMELHO}; }}
  .grupo-header {{ display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }}
  .grupo-fornecedor {{ font-size: 11px; color: {COR_TEAL}; font-weight: 700; text-transform: uppercase; }}
  .grupo-nome {{ font-size: 14px; font-weight: 700; color: #222; flex: 1; }}
  .grupo-docs {{ display: flex; flex-wrap: wrap; gap: 6px; }}
  .grupo-doc-badge {{
    display: inline-flex; align-items: center; gap: 4px;
    padding: 3px 10px; border-radius: 12px; font-size: 12px; font-weight: 600;
  }}
  .grupo-doc-venc {{ font-size: 10px; opacity: 0.8; }}

  .tabela-wrap {{ overflow-x: auto; }}
  #tabela-count, #sit-count {{ font-size: 13px; color: {COR_CINZA}; margin-bottom: 8px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  thead tr {{ background: {COR_TEAL}; color: white; }}
  thead th {{ padding: 10px 12px; text-align: left; font-weight: 700; position: sticky; top: 0; }}
  tbody tr:nth-child(even) {{ background: #f0f8fa; }}
  tbody tr:hover {{ background: #d4eef3; }}
  tbody td {{ padding: 8px 12px; border-bottom: 1px solid #e5eef1; vertical-align: top; max-width: 400px; word-break: break-word; }}

  .badge {{ display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 700; white-space: nowrap; }}
  .badge-pendente_env  {{ background: #ffeaea; color: {COR_VERMELHO}; }}
  .badge-em_analise    {{ background: #fff7d6; color: #a07800; }}
  .badge-terceiros     {{ background: #e0f4f7; color: {COR_TEAL}; }}
  .badge-documentos    {{ background: #ffe8d6; color: {COR_LARANJA}; }}
  .badge-conforme           {{ background: #d4edda; color: {COR_VERDE}; }}
  .badge-vencido            {{ background: #ffeaea; color: {COR_VERMELHO}; }}
  .badge-pendente           {{ background: #fff3cd; color: #856404; }}
  .badge-nao-anexado        {{ background: #fff3cd; color: #856404; }}
  .badge-aguardando-analise   {{ background: #fff0d6; color: {COR_LARANJA}; }}
  .badge-aguardando-submissao {{ background: #fff3cd; color: #856404; }}
  .badge-em-analise           {{ background: #e8f4f7; color: {COR_TEAL}; }}
  .badge-nao-enviado        {{ background: #f0f0f0; color: {COR_CINZA}; }}
  .badge-aprovado           {{ background: #d4edda; color: {COR_VERDE}; }}
  .badge-reprovado          {{ background: #ffeaea; color: {COR_VERMELHO}; }}
  .badge-competencia     {{ background: #e8f4f8; color: {COR_TEAL}; font-size: 11px; padding: 2px 7px; border-radius: 8px; }}
  .badge-sem-competencia {{ background: #f0f0f0; color: #999; font-size: 11px; padding: 2px 7px; border-radius: 8px; font-style: italic; }}
  .badge-irregular     {{ background: #fff0e0; color: #b35a00; }}
  .badge-alerta        {{ background: #fef3c7; color: #d97706; }}
  .kpi-card.amber      {{ border-top-color: #d97706; }}
  .kpi-card.amber .kpi-val {{ color: #d97706; }}
  .kpi-card[data-kpi-key] {{ cursor: pointer; transition: box-shadow .15s; user-select: none; }}
  .kpi-card[data-kpi-key]:hover {{ box-shadow: 0 4px 12px rgba(0,0,0,.14); }}
  .kpi-card.kpi-active       {{ outline: 2px solid {COR_TEAL}; outline-offset: 2px; box-shadow: 0 4px 12px rgba(14,143,163,.2); }}
  .kpi-card.kpi-active.green  {{ outline-color: {COR_VERDE}; }}
  .kpi-card.kpi-active.red    {{ outline-color: {COR_VERMELHO}; }}
  .kpi-card.kpi-active.yellow {{ outline-color: {COR_AMARELO}; }}
  .kpi-card.kpi-active.orange {{ outline-color: {COR_LARANJA}; }}
  .kpi-ativo-badge {{ position: absolute; top: 4px; right: 6px; font-size: 9px; font-weight: 700;
    color: #fff; background: {COR_TEAL}; border-radius: 10px; padding: 2px 6px; line-height: 1; }}

  /* CONTRATOS DRILL-DOWN */
  .ct-cards-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px,1fr)); gap: 14px; margin-top: 16px; }}
  .ct-card {{
    background: #f8f9fa; border-radius: 10px; padding: 16px; cursor: pointer;
    border: 2px solid #e0e0e0; transition: all 0.15s; user-select: none;
  }}
  .ct-card:hover {{ border-color: {COR_TEAL}; box-shadow: 0 4px 14px rgba(14,143,163,.18); transform: translateY(-2px); }}
  .ct-card-name  {{ font-size: 13px; font-weight: 700; color: #222; margin-bottom: 6px; line-height: 1.3; min-height: 34px; }}
  .ct-card-meta  {{ font-size: 11px; color: #888; margin-top: 4px; }}
  .ct-card-codes {{ display: flex; flex-wrap: wrap; gap: 4px; margin-top: 8px; overflow: hidden; max-height: 58px; }}
  .ct-code-chip  {{ background: #e8f4f8; color: {COR_TEAL}; font-size: 10px; font-weight: 700;
                    padding: 2px 7px; border-radius: 10px; white-space: nowrap;
                    max-width: 150px; overflow: hidden; text-overflow: ellipsis; }}
  .ct-code-chip.active {{ background: {COR_TEAL}; color: white; }}
  .ct-contract-row {{
    display: flex; align-items: center; padding: 13px 16px; cursor: pointer;
    gap: 14px; border-radius: 8px; transition: background 0.1s; border-bottom: 1px solid #f0f0f0;
  }}
  .ct-contract-row:hover {{ background: #f0f8fa; }}
  .ct-contract-code {{ font-size: 14px; font-weight: 700; color: {COR_TEAL}; min-width: 140px; }}
  .ct-contract-meta {{ flex: 1; font-size: 12px; color: #666; }}
  .ct-contract-arrow {{ font-size: 22px; color: #bbb; font-weight: 300; }}
  .ct-search-wrap {{ display: flex; align-items: flex-end; gap: 12px; margin-bottom: 14px; flex-wrap: wrap; }}
  .ct-search-wrap .ct-search-field {{ display: flex; flex-direction: column; gap: 4px; }}
  .ct-search-wrap .ct-search-field label {{
    font-size: 11px; font-weight: 700; color: {COR_TEAL}; text-transform: uppercase; letter-spacing: .04em;
  }}
  .ct-search-wrap input {{
    border: 1px solid #cde; border-radius: 6px; padding: 7px 12px;
    font-size: 13px; font-family: Calibri, Arial, sans-serif; width: 240px;
  }}
  .ct-search-wrap input:focus {{ outline: 2px solid {COR_TEAL}; border-color: {COR_TEAL}; }}
  .ct-chip-filter {{ display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px; }}
  .ct-chip {{
    background: #eee; color: #555; font-size: 11px; font-weight: 700;
    padding: 3px 10px; border-radius: 12px; cursor: pointer; border: 1px solid #ddd;
    transition: all 0.12s;
  }}
  .ct-chip:hover {{ background: #e0f4f7; border-color: {COR_TEAL}; color: {COR_TEAL}; }}
  .ct-chip.selected {{ background: {COR_TEAL}; color: white; border-color: {COR_TEAL}; }}

  /* ALERTA DE AUDITORIA */
  .audit-alert {{
    background: #fff0f0; border: 2px solid {COR_VERMELHO}; border-radius: 10px;
    padding: 0; margin-bottom: 20px; overflow: hidden;
    box-shadow: 0 2px 10px rgba(220,53,69,.15);
  }}
  .audit-alert-header {{
    background: {COR_VERMELHO}; color: white; padding: 14px 20px;
    display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;
  }}
  .audit-alert-header .titulo {{ font-size: 16px; font-weight: 700; }}
  .audit-alert-header .meta   {{ font-size: 12px; opacity: .85; }}
  .audit-alert-header .reprovado-badge {{
    background: white; color: {COR_VERMELHO}; font-weight: 900;
    padding: 4px 14px; border-radius: 20px; font-size: 13px; letter-spacing: .5px;
  }}
  .audit-body {{ padding: 18px 20px; }}
  .audit-conclusao {{
    background: #ffeaea; border-left: 4px solid {COR_VERMELHO};
    padding: 12px 16px; font-size: 13px; color: #555;
    border-radius: 0 6px 6px 0; margin-bottom: 18px; line-height: 1.6;
  }}
  .audit-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }}
  @media (max-width: 900px) {{ .audit-grid {{ grid-template-columns: 1fr; }} }}
  .audit-table {{ width: 100%; border-collapse: collapse; font-size: 12.5px; }}
  .audit-table th {{ background: #f5f5f5; color: #555; padding: 8px 10px; text-align: left; font-weight: 700; border-bottom: 2px solid #ddd; }}
  .audit-table td {{ padding: 7px 10px; border-bottom: 1px solid #eee; vertical-align: top; }}
  .audit-table tbody tr:hover {{ background: #fff5f5; }}
  .sit-vencido    {{ color: {COR_VERMELHO}; font-weight: 700; }}
  .sit-pendente   {{ color: #a07800; font-weight: 700; }}
  .sit-incorreto  {{ color: {COR_LARANJA}; font-weight: 700; }}
  .sit-reprovado  {{ color: {COR_VERMELHO}; font-weight: 700; }}
  .sit-bloqueado  {{ color: #6f42c1; font-weight: 700; }}
  .audit-subtitle {{ font-size: 13px; font-weight: 700; color: {COR_VERMELHO}; margin-bottom: 10px; text-transform: uppercase; letter-spacing: .4px; }}

  .footer {{ text-align: center; color: #aaa; font-size: 12px; padding: 24px 0 12px; }}

  /* DRILL-DOWN */
  .drill-cards-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px,1fr)); gap: 14px; margin-top: 16px; }}
  .drill-card {{
    background: #f8f9fa; border-radius: 10px; padding: 16px; cursor: pointer;
    border: 2px solid #e0e0e0; transition: all 0.15s; user-select: none;
  }}
  .drill-card:hover {{ border-color: {COR_TEAL}; box-shadow: 0 4px 14px rgba(14,143,163,.18); transform: translateY(-2px); }}
  .drill-card-pct {{ font-size: 30px; font-weight: 800; line-height: 1; }}
  .drill-card-label {{ font-size: 10px; color: #888; font-weight: 600; text-transform: uppercase; margin-top: 2px; }}
  .drill-card-name {{ font-size: 12px; font-weight: 700; color: #333; margin-top: 6px; line-height: 1.3; min-height: 32px; }}
  .drill-card-meta {{ font-size: 11px; color: #888; margin-top: 4px; }}
  .drill-card-bars {{ display: flex; height: 6px; border-radius: 3px; overflow: hidden; margin-top: 10px; background: #ddd; }}
  .mini-bar {{ height: 100%; display: inline-block; transition: width 0.3s; }}

  .drill-breadcrumb {{ padding: 0 0 16px; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }}
  .drill-back {{ color: {COR_TEAL}; cursor: pointer; font-weight: 700; font-size: 14px; padding: 4px 10px; border-radius: 6px; background: #e8f7fa; }}
  .drill-back:hover {{ background: #d0eff5; }}
  .drill-crumb-sep {{ color: #bbb; font-size: 18px; }}
  .drill-crumb-current {{ font-weight: 700; color: #333; font-size: 14px; }}

  .drill-worker-list {{ display: flex; flex-direction: column; gap: 0; }}
  .drill-worker {{
    display: flex; align-items: center; padding: 12px 16px; cursor: pointer;
    gap: 14px; border-radius: 8px; transition: background 0.1s; border-bottom: 1px solid #f0f0f0;
  }}
  .drill-worker:hover {{ background: #f0f8fa; }}
  .drill-worker-name {{ font-weight: 700; flex: 1; font-size: 14px; color: #222; }}
  .drill-worker-badges {{ display: flex; gap: 6px; flex-wrap: wrap; }}
  .drill-worker-arrow {{ font-size: 22px; color: #bbb; font-weight: 300; }}

  .drill-doc-list {{ display: flex; flex-direction: column; gap: 0; }}
  .drill-doc {{
    display: flex; align-items: center; padding: 11px 16px;
    gap: 14px; border-bottom: 1px solid #f0f0f0;
  }}
  .drill-doc:nth-child(even) {{ background: #fafafa; }}
  .drill-doc-name {{ flex: 1; font-size: 13px; color: #333; }}
  .drill-doc-venc {{ font-size: 12px; color: #888; min-width: 90px; text-align: right; }}

  .drill-hint {{ color: #999; font-size: 13px; text-align: center; padding: 24px 0; }}
  .section-collapsible.collapsed {{ display: none; }}
  .section-toggle {{
    float: right; cursor: pointer; font-size: 12px;
    background: rgba(14,143,163,.1); border: 1px solid rgba(14,143,163,.3);
    color: {COR_TEAL}; border-radius: 6px; padding: 2px 10px; font-weight: 700;
    user-select: none; line-height: 1.8;
  }}
  .section-toggle:hover {{ background: rgba(14,143,163,.2); }}

  /* FILTRO GLOBAL */
  #global-filtro-bar {{
    background: {COR_TEAL_ESCURO}; padding: 14px 32px;
    display: flex; flex-wrap: wrap; gap: 20px; align-items: flex-end;
    box-shadow: 0 3px 8px rgba(0,0,0,.2);
  }}
  #global-filtro-bar label {{
    font-size: 11px; font-weight: 700; color: rgba(255,255,255,.85);
    text-transform: uppercase; letter-spacing: .5px; margin-bottom: 4px; display: block;
  }}
  #gf-multi-wrap {{ position: relative; display: inline-block; }}
  #gf-multi-btn {{
    border: none; border-radius: 6px; padding: 7px 12px;
    font-size: 13px; font-family: Calibri, Arial, sans-serif;
    background: white; color: #333; cursor: pointer; min-width: 280px;
    display: flex; justify-content: space-between; align-items: center; gap: 10px; user-select: none;
  }}
  #gf-multi-btn:hover {{ background: #f0f8fa; }}
  #gf-multi-panel {{
    display: none; position: absolute; top: calc(100% + 4px); left: 0;
    min-width: 340px; background: white; border: 1px solid #ccc; border-radius: 6px;
    z-index: 2000; box-shadow: 0 6px 18px rgba(0,0,0,.18); overflow: hidden;
  }}
  #gf-multi-search {{
    width: 100%; padding: 9px 12px; border: none; border-bottom: 1px solid #eee;
    font-size: 13px; box-sizing: border-box; outline: none; font-family: Calibri, Arial, sans-serif;
  }}
  #gf-multi-list {{ max-height: 260px; overflow-y: auto; }}
  .gf-item {{
    display: flex; align-items: center; gap: 9px; padding: 7px 12px;
    cursor: pointer; font-size: 13px; color: #333; border-bottom: 1px solid #f5f5f5;
  }}
  .gf-item:hover {{ background: #f0f8fa; }}
  .gf-item.gf-selected {{ background: #e4f4f8; font-weight: 700; }}
  .gf-item input[type=checkbox] {{ cursor: pointer; accent-color: {COR_TEAL}; width: 15px; height: 15px; flex-shrink: 0; }}
  #gf-multi-footer {{
    padding: 7px 12px; border-top: 1px solid #eee; text-align: right;
    font-size: 12px; color: {COR_TEAL}; cursor: pointer; font-weight: 700;
  }}
  #gf-multi-footer:hover {{ background: #f0f8fa; }}
  #gf-multi-panel label {{
    color: #333 !important; font-weight: normal !important; text-transform: none !important;
    letter-spacing: 0 !important; display: inline !important; margin-bottom: 0 !important;
    font-size: 13px !important;
  }}
  #global-filtro-bar .btn-gf-limpar {{
    background: rgba(255,255,255,.2); border: 1px solid rgba(255,255,255,.5);
    color: white; border-radius: 6px; padding: 7px 18px; font-size: 13px;
    font-family: Calibri, Arial, sans-serif; cursor: pointer; font-weight: 700;
  }}
  #global-filtro-bar .btn-gf-limpar:hover {{ background: rgba(255,255,255,.35); }}
  #global-filtro-bar .btn-gf-export {{
    background: rgba(255,255,255,.15); border: 1px solid rgba(255,255,255,.4);
    color: white; border-radius: 6px; padding: 6px 14px; font-size: 12px;
    font-family: Calibri, Arial, sans-serif; cursor: pointer; font-weight: 600;
  }}
  #global-filtro-bar .btn-gf-export:hover {{ background: rgba(255,255,255,.3); }}
  #gf-hint {{ font-size: 12px; color: rgba(255,255,255,.75); align-self: center; margin-left: auto; font-style: italic; }}

  /* MULTI-SELECT GLOBAL — COMPETÊNCIA */
  #gfc-multi-wrap {{ position: relative; display: inline-block; }}
  #gfc-multi-btn {{
    border: none; border-radius: 6px; padding: 7px 12px;
    font-size: 13px; font-family: Calibri, Arial, sans-serif;
    background: white; color: #333; cursor: pointer; min-width: 200px;
    display: flex; justify-content: space-between; align-items: center; gap: 10px; user-select: none;
  }}
  #gfc-multi-btn:hover {{ background: #f0f8fa; }}
  #gfc-multi-panel {{
    display: none; position: absolute; top: calc(100% + 4px); left: 0;
    min-width: 260px; background: white; border: 1px solid #ccc; border-radius: 6px;
    z-index: 2000; box-shadow: 0 6px 18px rgba(0,0,0,.18); overflow: hidden;
  }}
  #gfc-multi-search {{
    width: 100%; padding: 9px 12px; border: none; border-bottom: 1px solid #eee;
    font-size: 13px; box-sizing: border-box; outline: none; font-family: Calibri, Arial, sans-serif;
  }}
  #gfc-multi-list {{ max-height: 220px; overflow-y: auto; }}
  .gfc-item {{
    display: flex; align-items: center; gap: 9px; padding: 7px 12px;
    cursor: pointer; font-size: 13px; color: #333; border-bottom: 1px solid #f5f5f5;
  }}
  .gfc-item:hover {{ background: #f0f8fa; }}
  .gfc-item.gfc-selected {{ background: #e4f4f8; font-weight: 700; }}
  .gfc-item input[type=checkbox] {{ cursor: pointer; accent-color: {COR_TEAL}; width: 15px; height: 15px; flex-shrink: 0; }}
  #gfc-multi-footer {{
    padding: 7px 12px; border-top: 1px solid #eee; text-align: right;
    font-size: 12px; color: {COR_TEAL}; cursor: pointer; font-weight: 700;
  }}
  #gfc-multi-footer:hover {{ background: #f0f8fa; }}
  #gfc-multi-panel label {{
    color: #333 !important; font-weight: normal !important; text-transform: none !important;
    letter-spacing: 0 !important; display: inline !important; margin-bottom: 0 !important;
    font-size: 13px !important;
  }}

  /* MULTI-SELECT LOCAL (filtros internos de cada seção) */
  .lf-multi-wrap {{ position: relative; display: inline-block; }}
  .lf-multi-btn {{
    border: 1px solid #cde; border-radius: 6px; padding: 6px 10px;
    font-size: 13px; font-family: Calibri, Arial, sans-serif;
    background: white; color: #333; cursor: pointer; min-width: 220px;
    display: flex; justify-content: space-between; align-items: center; gap: 8px; user-select: none;
  }}
  .lf-multi-btn:hover {{ border-color: {COR_TEAL}; }}
  .lf-multi-panel {{
    display: none; position: absolute; top: calc(100% + 3px); left: 0;
    min-width: 300px; background: white; border: 1px solid #ccc; border-radius: 6px;
    z-index: 3000; box-shadow: 0 6px 18px rgba(0,0,0,.18); overflow: hidden;
  }}
  .lf-multi-search {{
    width: 100%; padding: 8px 10px; border: none; border-bottom: 1px solid #eee;
    font-size: 12px; box-sizing: border-box; outline: none; font-family: Calibri, Arial, sans-serif;
  }}
  .lf-multi-list {{ max-height: 220px; overflow-y: auto; }}
  .lf-item {{
    display: flex; align-items: center; gap: 8px; padding: 6px 10px;
    cursor: pointer; border-bottom: 1px solid #f5f5f5;
  }}
  .lf-item:hover {{ background: #f0f8fa; }}
  .lf-item.lf-selected {{ background: #e4f4f8; font-weight: 700; }}
  .lf-item input[type=checkbox] {{ cursor: pointer; accent-color: {COR_TEAL}; width: 14px; height: 14px; flex-shrink: 0; }}
  .lf-item label {{
    color: #333 !important; font-weight: normal !important; text-transform: none !important;
    letter-spacing: 0 !important; display: inline !important; margin-bottom: 0 !important;
    font-size: 12px !important; cursor: pointer; flex: 1;
  }}
  .lf-multi-footer {{
    padding: 6px 10px; border-top: 1px solid #eee; text-align: right;
    font-size: 11px; color: {COR_TEAL}; cursor: pointer; font-weight: 700;
  }}
  .lf-multi-footer:hover {{ background: #f0f8fa; }}
</style>
</head>
<body>

<div class="header">
  <div>
    <h1>Relatório de Fornecedores — Zurich Airport</h1>
    <div class="subtitle">Conformidade Documental de Terceiros | Plataforma Efcaz</div>
  </div>
  <div class="badge">
    <span class="badge-data">Gerado em {DATA_HOJE}</span>
    Referencia: {DATA_HOJE[:10]}
  </div>
</div>

<!-- FILTRO GLOBAL -->
<div id="global-filtro-bar">
  <div>
    <label>Fornecedor</label>
    <div id="gf-multi-wrap">
      <div id="gf-multi-btn" onclick="toggleFornDropdown(event)">
        <span id="gf-selected-label">Todos os fornecedores</span>
        <span id="gf-multi-arrow">▾</span>
      </div>
      <div id="gf-multi-panel">
        <input type="text" id="gf-multi-search" placeholder="Buscar fornecedor..." oninput="filterFornItems(this.value)">
        <div id="gf-multi-list"></div>
        <div id="gf-multi-footer" onclick="limparGlobalFiltro()">Limpar seleção</div>
      </div>
    </div>
  </div>
  <div>
    <label>Competência</label>
    <div id="gfc-multi-wrap">
      <div id="gfc-multi-btn" onclick="toggleCompDropdown(event)">
        <span id="gfc-selected-label">Todas as competências</span>
        <span id="gfc-multi-arrow">▾</span>
      </div>
      <div id="gfc-multi-panel">
        <input type="text" id="gfc-multi-search" placeholder="Buscar competência..." oninput="filterCompItems(this.value)">
        <div id="gfc-multi-list"></div>
        <div id="gfc-multi-footer" onclick="limparCompFiltroSilent(); applyGlobalFilter()">Limpar seleção</div>
      </div>
    </div>
  </div>
  <div>
    <label>Aeroporto</label>
    <div style="display:flex;gap:6px;height:34px;align-items:center">
      <button id="gf-aero-CAIF" onclick="toggleAeroporto('CAIF')"
        style="font-size:12px;font-weight:700;padding:4px 12px;border-radius:20px;border:1px solid rgba(255,255,255,.5);cursor:pointer;background:rgba(255,255,255,.15);color:white">CAIF</button>
      <button id="gf-aero-VIX"  onclick="toggleAeroporto('VIX')"
        style="font-size:12px;font-weight:700;padding:4px 12px;border-radius:20px;border:1px solid rgba(255,255,255,.5);cursor:pointer;background:rgba(255,255,255,.15);color:white">VIX</button>
      <button id="gf-aero-MEA"  onclick="toggleAeroporto('MEA')"
        style="font-size:12px;font-weight:700;padding:4px 12px;border-radius:20px;border:1px solid rgba(255,255,255,.5);cursor:pointer;background:rgba(255,255,255,.15);color:white">MEA</button>
      <button id="gf-aero-CAIN" onclick="toggleAeroporto('CAIN')"
        style="font-size:12px;font-weight:700;padding:4px 12px;border-radius:20px;border:1px solid rgba(255,255,255,.5);cursor:pointer;background:rgba(255,255,255,.15);color:white">CAIN</button>
    </div>
  </div>
  <div>
    <label>Terceiros</label>
    <div style="display:flex;gap:6px;height:34px;align-items:center">
      <button id="gf-status-terc-all"    onclick="setStatusTerc('all')"
        style="font-size:12px;font-weight:700;padding:4px 12px;border-radius:20px;border:1px solid rgba(255,255,255,.5);cursor:pointer;background:white;color:{COR_TEAL_ESCURO}">Todos</button>
      <button id="gf-status-terc-ativo"  onclick="setStatusTerc('Ativo')"
        style="font-size:12px;font-weight:700;padding:4px 12px;border-radius:20px;border:1px solid rgba(255,255,255,.5);cursor:pointer;background:rgba(255,255,255,.15);color:white">Ativos</button>
      <button id="gf-status-terc-inativo" onclick="setStatusTerc('Inativo')"
        style="font-size:12px;font-weight:700;padding:4px 12px;border-radius:20px;border:1px solid rgba(255,255,255,.5);cursor:pointer;background:rgba(255,255,255,.15);color:white">Inativos</button>
    </div>
  </div>
  <div style="align-self:flex-end">
    <button class="btn-gf-limpar" onclick="limparGlobalFiltro()">&#10005; Limpar filtros</button>
  </div>
  <div style="align-self:flex-end;margin-left:auto">
    <label style="font-size:11px;font-weight:700;color:rgba(255,255,255,.85);text-transform:uppercase;letter-spacing:.5px;margin-bottom:4px;display:block">Exportar relatório</label>
    <div style="display:flex;gap:6px">
      <button class="btn-gf-export" onclick="exportarRelatorioXLSX()" title="Exportar todas as seções em Excel (3 abas)">&#128196; Excel</button>
      <button class="btn-gf-export" onclick="exportarRelatorioPDF()" title="Exportar todas as seções em PDF">&#128196; PDF</button>
      <button class="btn-gf-export" onclick="exportarRelatorioCSV()" title="Exportar todas as seções em CSV">&#128196; CSV</button>
    </div>
  </div>
  <span id="gf-hint"></span>
</div>

<div class="container">

  <!-- KPIs -->
  <div class="kpi-grid" style="margin-bottom:20px;grid-template-columns:repeat(4,1fr)">
    <!-- Bloco 1: globais — somem quando filtro especifico ativo -->
    <div class="kpi-card" id="kpi-card-total-forn"
         data-tooltip="Número total de empresas fornecedoras cadastradas na base.">
      <div class="kpi-val" id="kpi-total-forn">{total_forn_geral}</div>
      <div class="kpi-label">Total de<br>Fornecedores</div>
    </div>
    <div class="kpi-card teal" id="kpi-card-exec-plat"
         data-tooltip="Quantidade de fornecedores que possuem contratos ativos e movimentações na plataforma.">
      <div class="kpi-val" id="kpi-exec-plat">{total_forn_com_execucao}</div>
      <div class="kpi-label">Fornecedores com<br>Execução na Plataforma</div>
    </div>
    <!-- Bloco 2: docs esperados — somem quando filtro de competência ativo -->
    <div class="kpi-card" id="kpi-card-docs-esp-forn"
         data-tooltip="Quantidade total de documentos que a empresa contratada precisa enviar para a plataforma.">
      <div class="kpi-val" id="kpi-docs-esp-forn">{r4_total}</div>
      <div class="kpi-label">Docs Esperados<br>Fornecedor</div>
    </div>
    <div class="kpi-card" id="kpi-card-docs-esp-terc"
         data-tooltip="Quantidade total de documentos exigidos dos funcionários ou prestadores vinculados ao fornecedor.">
      <div class="kpi-val" id="kpi-docs-esp-terc">{total_docs_sit}</div>
      <div class="kpi-label">Docs Esperados<br>Terceiros</div>
    </div>
    <!-- Bloco 3: status — atualizam com filtro -->
    <div class="kpi-card green" data-kpi-key="docs_aprovados" onclick="toggleKpiCard('docs_aprovados')"
         data-tooltip="Documentos que já foram analisados e validados com sucesso. Clique para filtrar as tabelas.">
      <div class="kpi-val" id="kpi-docs-aprov">{int(total_conformes) + r4_aprovado}</div>
      <div class="kpi-label">Documentos<br>Aprovados</div>
    </div>
    <div class="kpi-card red" data-kpi-key="docs_reprovados" onclick="toggleKpiCard('docs_reprovados')"
         data-tooltip="Total de documentos em situação de não conformidade: Reprovado, Irregular ou Alerta — em R3 (terceiros) e R4 (corporativo). Clique para filtrar as tabelas.">
      <div class="kpi-val" id="kpi-docs-nao-aprov">{int(total_reprovados_docs) + r4_reprovado + r4_irregular + r4_alerta}</div>
      <div class="kpi-label">Documentos<br>Reprovados</div>
    </div>
    <div class="kpi-card yellow" data-kpi-key="docs_nao_enviados" onclick="toggleKpiCard('docs_nao_enviados')"
         data-tooltip="Documentos obrigatórios que ainda estão pendentes de anexo. Clique para filtrar as tabelas.">
      <div class="kpi-val" id="kpi-docs-nao-env">{total_nao_anex_r3 + r4_nao_anex}</div>
      <div class="kpi-label">Documentos<br>Não Enviados</div>
    </div>
    <div class="kpi-card yellow" data-kpi-key="docs_aguard_sub" onclick="toggleKpiCard('docs_aguard_sub')"
         data-tooltip="Documentos inseridos mas ainda não submetidos para análise. Clique para filtrar as tabelas.">
      <div class="kpi-val" id="kpi-docs-aguard-sub">{total_aguard_r3_elab}</div>
      <div class="kpi-label">Aguardando<br>Submissão</div>
    </div>
    <div class="kpi-card orange" data-kpi-key="docs_em_analise" onclick="toggleKpiCard('docs_em_analise')"
         data-tooltip="Documentos já submetidos aguardando validação da equipe de conformidade. Clique para filtrar as tabelas.">
      <div class="kpi-val" id="kpi-docs-em-anal">{total_aguard_r3_real + r4_em_analise}</div>
      <div class="kpi-label">Documentos<br>Em Análise</div>
    </div>
    <div class="kpi-card red" data-kpi-key="docs_vencidos" onclick="toggleKpiCard('docs_vencidos')"
         data-tooltip="Documentos de fornecedores com prazo vencido — exigem renovação imediata. Clique para filtrar as tabelas.">
      <div class="kpi-val" id="kpi-docs-vencido">{r4_vencido}</div>
      <div class="kpi-label">Documentos<br>Vencidos</div>
    </div>
  </div>

  <!-- 3 GRÁFICOS DE CONFORMIDADE -->
  <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-bottom:28px">
    <div class="chart-card" id="pizza-geral-card" style="padding:14px 10px">
      <div style="font-size:11px;font-weight:700;color:{COR_TEAL};text-align:center;text-transform:uppercase;letter-spacing:.4px;margin-bottom:4px">Conformidade<br>Geral</div>
      <div id="fig-pizza-geral" style="height:240px"></div>
    </div>
    <div class="chart-card" id="pizza-forn-card" style="padding:14px 10px">
      <div style="font-size:11px;font-weight:700;color:{COR_TEAL};text-align:center;text-transform:uppercase;letter-spacing:.4px;margin-bottom:4px">Conformidade<br>Fornecedores</div>
      <div id="fig-pizza-forn" style="height:240px"></div>
    </div>
    <div class="chart-card" id="pizza-card" style="padding:14px 10px">
      <div style="font-size:11px;font-weight:700;color:{COR_TEAL};text-align:center;text-transform:uppercase;letter-spacing:.4px;margin-bottom:4px">Conformidade<br>Terceiros</div>
      <div id="fig-pizza" style="height:240px"></div>
    </div>
  </div>

  <!-- ALERTA DE AUDITORIA — OCULTO NA VERSÃO RELATORIO_FORNECEDORES (pós-validação Débora) -->
  <!-- <div class="section-title">Alertas de Auditoria -->
  <div id="auditoria-section" class="section-collapsible collapsed" style="display:none!important">
  <div class="audit-alert">
    <div class="audit-alert-header">
      <div>
        <div class="titulo">NEPOS SISTEMAS DE CONTROLE E AUTOMACAO LTDA</div>
        <div class="meta">Aeroporto: VIX (Vitoria) &nbsp;|&nbsp; Competencia: Marco/2026 &nbsp;|&nbsp; Relatorio: 20/05/2026</div>
      </div>
      <div class="reprovado-badge">REPROVADO</div>
    </div>
    <div class="audit-body">
      <div class="audit-conclusao">
        <strong>Parecer Tecnico:</strong> A auditoria mapeou um cenario de colapso nos prazos de compliance financeiro e fiscal com atrasos acumulados desde o inicio de 2026 (CRF FGTS, DCTFWEB, GFD, FOPAG e Comprovantes Salariais vencidos entre janeiro e fevereiro). Na area ocupacional (SST), ha bloqueio sistemico critico pela ausencia total do PGR e rejeicao tecnica do PCMSO, paralisando a validacao de todos os terceiros ativos. O ex-colaborador Fabio Almeida Tozi apresenta vicio gravissimo de ponto britanico e omissao do Kit Rescisao. <strong>Exposicao maxima da contratante a passivos trabalhistas, fiscais e previdenciarios.</strong>
      </div>
      <div class="audit-grid">
        <div>
          <div class="audit-subtitle">Documentacao da Empresa</div>
          <table class="audit-table">
            <thead><tr><th>Documento</th><th>Vencimento / Ref.</th><th>Situacao</th></tr></thead>
            <tbody>
              <tr><td>Certificado de Regularidade FGTS (CRF)</td><td>25/02/2026</td><td class="sit-vencido">VENCIDO</td></tr>
              <tr><td>DCTFWEB</td><td>20/02/2026</td><td class="sit-vencido">VENCIDO</td></tr>
              <tr><td>FOPAG (Folha de Pagamento)</td><td>30/01/2026</td><td class="sit-vencido">VENCIDO</td></tr>
              <tr><td>GFD (FGTS Digital Mensal)</td><td>09/02/2026</td><td class="sit-vencido">VENCIDO</td></tr>
              <tr><td>Comprovante Bancario de Salarios</td><td>05/02/2026</td><td class="sit-vencido">VENCIDO</td></tr>
              <tr><td>Certidoes TRF3 (Criminal e Civil)</td><td>23/03/2026</td><td class="sit-vencido">VENCIDO</td></tr>
              <tr><td>PGR (Programa Base)</td><td>Nao enviado</td><td class="sit-pendente">PENDENTE</td></tr>
              <tr><td>CIPA (Composicao NR-05)</td><td>Nao enviado</td><td class="sit-pendente">PENDENTE</td></tr>
              <tr><td>PCMSO (Programa Base)</td><td>Inadequado</td><td class="sit-incorreto">ANEXO INCORRETO</td></tr>
              <tr><td>Laudos de Insalubridade/Periculosidade</td><td>Nao enviado</td><td class="sit-pendente">PENDENTE</td></tr>
              <tr><td>SESMT (Composicao NR-04)</td><td>Nao enviado</td><td class="sit-pendente">PENDENTE</td></tr>
            </tbody>
          </table>
        </div>
        <div>
          <div class="audit-subtitle">Prontuarios de Trabalhadores</div>
          <table class="audit-table">
            <thead><tr><th>Colaborador</th><th>Vinculo</th><th>Situacao</th></tr></thead>
            <tbody>
              <tr>
                <td><strong>Claudio Marinho Coutinho</strong><br><small>Ponto vencido 27/04/2026. Ficha EPI nao anexada. ASO/OS bloqueados por falta de PGR/PCMSO.</small></td>
                <td>Efetivo Ativo</td><td class="sit-reprovado">REPROVADO / BLOQUEADO</td>
              </tr>
              <tr>
                <td><strong>Fabio Almeida Tozi</strong><br><small>Omissao total do Kit Rescisao e Ficha EPI. Ponto britanico (marcacao invariavel).</small></td>
                <td>Inativo — Desligado 16/03/2026</td><td class="sit-reprovado">REPROVADO (RESCISAO)</td>
              </tr>
              <tr>
                <td><strong>Demais colaboradores ativos</strong><br><small>Bloqueio cascata: ASO, EPI e OS suspensos pela ausencia do PGR e inadequacao do PCMSO.</small></td>
                <td>Efetivos Ativos</td><td class="sit-bloqueado">BLOQUEADO</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>

  </div><!-- /auditoria-section (oculto) -->

  <!-- CONTRATOS POR FORNECEDOR -->
  <div class="section-title">Contratos por Fornecedor — Drill-down Interativo
    <span class="section-toggle" onclick="toggleSection('ct-section', this)">&#9660; Expandir</span>
  </div>
  <div id="ct-section" class="section-collapsible collapsed">
  <div class="chart-card">
    <p style="font-size:13px;color:#666;margin-bottom:12px;">
      Clique num fornecedor para ver seus contratos. Clique no contrato para ver os terceiros vinculados.
    </p>

    <!-- L1: grid de cards de fornecedores -->
    <div id="ct-level1">
      <div class="ct-search-wrap">
        <div class="ct-search-field">
          <label for="ct-search">Buscar Fornecedor</label>
          <input type="text" id="ct-search" placeholder="Nome ou CNPJ..." oninput="ctRenderL1()">
        </div>
        <div class="ct-search-field">
          <label for="ct-search-cont">Buscar Contrato</label>
          <input type="text" id="ct-search-cont" placeholder="Código do contrato..." oninput="ctRenderL1()">
        </div>
        <button onclick="ctClearSearch()" style="background:{COR_TEAL};color:#fff;border:none;border-radius:6px;padding:7px 14px;font-size:13px;font-weight:700;cursor:pointer;height:36px">Limpar</button>
        <span id="ct-l1-count" style="font-size:12px;color:#999;align-self:center"></span>
      </div>
      <div class="ct-cards-grid" id="ct-cards"></div>
    </div>

    <!-- L2: contratos do fornecedor -->
    <div id="ct-level2" style="display:none">
      <div class="drill-breadcrumb" id="ct-breadcrumb2"></div>
      <div id="ct-chip-filter" class="ct-chip-filter"></div>
      <div id="ct-contract-list"></div>
      <div style="display:flex;gap:8px;margin-top:14px">
        <span class="export-label" style="align-self:center">Exportar:</span>
        <button class="btn-action btn-export"     onclick="ctExportL2XLSX()">Excel</button>
        <button class="btn-action btn-export-csv" onclick="ctExportL2CSV()">CSV</button>
        <button class="btn-action btn-export-pdf" onclick="ctExportL2PDF()">PDF</button>
      </div>
    </div>

    <!-- L3: terceiros do contrato -->
    <div id="ct-level3" style="display:none">
      <div class="drill-breadcrumb" id="ct-breadcrumb3"></div>
      <div class="tabela-wrap">
        <table id="ct-terc-table" style="width:100%">
          <thead>
            <tr>
              <th>Nome</th>
              <th>CPF/CNPJ</th>
              <th>Cargo</th>
              <th>Aeroporto</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody id="ct-terc-body"></tbody>
        </table>
      </div>
      <div style="display:flex;gap:8px;margin-top:14px">
        <span class="export-label" style="align-self:center">Exportar:</span>
        <button class="btn-action btn-export"     onclick="ctExportL3XLSX()">Excel</button>
        <button class="btn-action btn-export-csv" onclick="ctExportL3CSV()">CSV</button>
        <button class="btn-action btn-export-pdf" onclick="ctExportL3PDF()">PDF</button>
      </div>
    </div>

  </div>
  </div><!-- /ct-section -->

  <!-- DRILL-DOWN INTERATIVO -->
  <div class="section-title">Análise Interativa — Fornecedor › Terceiro › Documentos
    <span class="section-toggle" onclick="toggleSection('drill-section', this)">▼ Expandir</span>
  </div>
  <div id="drill-section" class="section-collapsible collapsed">
  <div class="chart-card">
    <p style="font-size:13px;color:#666;margin-bottom:16px;">
      Clique num fornecedor para ver os terceiros. Clique num terceiro para ver os documentos e o status de cada um.
    </p>
    <div id="drill-level1">
      <div class="drill-cards-grid" id="supplier-cards"></div>
    </div>
    <div id="drill-level2" style="display:none">
      <div class="drill-breadcrumb" id="breadcrumb2"></div>
      <div class="drill-worker-list" id="worker-list"></div>
    </div>
    <div id="drill-level3" style="display:none">
      <div class="drill-breadcrumb" id="breadcrumb3"></div>
      <div class="drill-doc-list" id="doc-list"></div>
    </div>
  </div>
  </div><!-- /drill-section -->

  <!-- SITUACAO DOCUMENTAL POR TRABALHADOR -->
  <div class="section-title">
    Situação Documental por Terceiro — Aprovado / Reprovado / Não Anexado / Aguardando Submissão / Em Análise
    <span class="section-toggle" onclick="toggleSection('sit-section', this)">▼ Expandir</span>
  </div>
  <div id="sit-section" class="section-collapsible collapsed">

  <div class="kpi-grid" style="margin-bottom:16px;grid-template-columns:repeat(auto-fit,minmax(140px,1fr))">
    <div class="kpi-card red">
      <div class="kpi-val" id="sit-kpi-nc">{pct_nao_conform}%</div>
      <div class="kpi-label">% Nao Conf.<br>Terceiros</div>
    </div>
    <div class="kpi-card green">
      <div class="kpi-val" id="sit-kpi-c">{pct_conformidade}%</div>
      <div class="kpi-label">% Conf.<br>Terceiros</div>
    </div>
    <div class="kpi-card green">
      <div class="kpi-val" id="sit-kpi-aprov">{total_conformes}</div>
      <div class="kpi-label">Docs<br>Aprovados</div>
    </div>
    <div class="kpi-card red">
      <div class="kpi-val" id="sit-kpi-reprov">{total_reprovados_docs}</div>
      <div class="kpi-label">Docs<br>Reprovados</div>
    </div>
    <div class="kpi-card yellow">
      <div class="kpi-val" id="sit-kpi-nao-anex">{total_nao_anex_r3}</div>
      <div class="kpi-label">Nao<br>Anexado</div>
    </div>
    <div class="kpi-card yellow">
      <div class="kpi-val" id="sit-kpi-aguard-sub">{total_aguard_r3_elab}</div>
      <div class="kpi-label">Ag.<br>Submissão</div>
    </div>
    <div class="kpi-card orange">
      <div class="kpi-val" id="sit-kpi-aguard-real">{total_aguard_r3_real}</div>
      <div class="kpi-label">Em<br>Análise</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-val" id="sit-kpi-terc">{total_terceiros_r3}</div>
      <div class="kpi-label">Terceiros<br>com Docs</div>
    </div>
  </div>

  <div class="filtro-bar">
    <div>
      <label>Status</label><br>
      <select id="sit-status" onchange="filtrarSit()">
        <option value="">Todos</option>
        <option value="Aprovado">Aprovado</option>
        <option value="Reprovado">Reprovado</option>
        <option value="Não anexado">Não anexado</option>
        <option value="Aguardando Submissão">Aguardando Submissão</option>
        <option value="Em Análise">Em Análise</option>
      </select>
    </div>
    <div>
      <label>Competência</label><br>
      <select id="sit-comp" onchange="filtrarSit()">
        <option value="">Todas</option>
      </select>
    </div>
    <div>
      <label>Buscar documento</label><br>
      <input type="text" id="sit-busca" placeholder="Ex: ASO, Ficha de EPI..." oninput="dbFiltrarSit()" style="width:220px">
    </div>
    <div style="align-self:flex-end">
      <button class="btn-action btn-limpar" onclick="limparSit()">Limpar</button>
    </div>
    <div style="align-self:flex-end">
      <button id="btn-modo-sit" class="btn-action btn-toggle" onclick="toggleModoAgrupado()">Modo Agrupado</button>
    </div>
    <div style="align-self:flex-end">
      <span class="export-label">Exportar:</span>
      <span class="export-group">
        <button class="btn-action btn-export" onclick="exportarSitXLSX()">Excel</button>
        <button class="btn-action btn-export-pdf" onclick="exportarSitPDF()">PDF</button>
        <button class="btn-action btn-export-csv" onclick="exportarSit()">CSV</button>
      </span>
    </div>
  </div>

  <div class="chart-card">
    <div id="sit-count"></div>
    <div id="sit-modo-linha">
    <div class="tabela-wrap">
      <table id="sit-table">
        <thead>
          <tr>
            <th>Fornecedor</th>
            <th>Terceiro</th>
            <th>Documento</th>
            <th>Competência</th>
            <th>Status</th>
            <th>Vencimento</th>
          </tr>
        </thead>
        <tbody id="sit-body"></tbody>
      </table>
    </div>
    <div id="sit-pagination" style="display:flex;align-items:center;gap:10px;margin-top:10px;font-size:13px;color:{COR_CINZA}"></div>
    </div>
    <div id="sit-modo-agrupado" style="display:none">
      <div id="sit-grupos"></div>
    </div>
  </div>

  </div><!-- /sit-section -->

  <!-- SITUACAO DOCUMENTAL DA EMPRESA (R4) -->
  <div class="section-title">
    Situação Documental da Empresa (Documentação Corporativa)
    <span class="section-toggle" onclick="toggleSection('forn-sit-section', this)">&#9660; Expandir</span>
  </div>
  <div id="forn-sit-section" class="section-collapsible collapsed">

  <div class="kpi-grid" style="margin-bottom:16px;grid-template-columns:repeat(auto-fit,minmax(150px,1fr))">
    <div class="kpi-card red">
      <div class="kpi-val" id="r4-kpi-nc">{r4_pct_nc}%</div>
      <div class="kpi-label">% Nao Conf.<br>Empresa</div>
    </div>
    <div class="kpi-card green">
      <div class="kpi-val" id="r4-kpi-c">{r4_pct_c}%</div>
      <div class="kpi-label">% Conf.<br>Empresa</div>
    </div>
    <div class="kpi-card green">
      <div class="kpi-val" id="r4-kpi-aprov">{r4_aprovado}</div>
      <div class="kpi-label">Docs<br>Aprovados</div>
    </div>
    <div class="kpi-card red">
      <div class="kpi-val" id="r4-kpi-reprov">{r4_reprovado}</div>
      <div class="kpi-label">Docs<br>Reprovados</div>
    </div>
    <div class="kpi-card yellow">
      <div class="kpi-val" id="r4-kpi-nao-anex">{r4_nao_anex}</div>
      <div class="kpi-label">Nao<br>Anexado</div>
    </div>
    <div class="kpi-card orange">
      <div class="kpi-val" id="r4-kpi-em-analise">{r4_em_analise}</div>
      <div class="kpi-label">Em<br>Analise</div>
    </div>
    <div class="kpi-card red">
      <div class="kpi-val" id="r4-kpi-vencido">{r4_vencido}</div>
      <div class="kpi-label">Vencido<br>(sem revisao)</div>
    </div>
    <div class="kpi-card orange"
         data-tooltip="Documentos com débito detectado pela busca automática (certidões IRREGULAR).">
      <div class="kpi-val" id="r4-kpi-irregular">{r4_irregular}</div>
      <div class="kpi-label">Irregular<br>(Débito Detectado)</div>
    </div>
    <div class="kpi-card amber"
         data-tooltip="Busca automática não executou — verificar manualmente o motivo.">
      <div class="kpi-val" id="r4-kpi-alerta">{r4_alerta}</div>
      <div class="kpi-label">Alerta<br>(Verificar Busca)</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-val" id="r4-kpi-forn">{r4_fornecedores}</div>
      <div class="kpi-label">Fornecedores<br>com Docs</div>
    </div>
  </div>

  <div class="filtro-bar">
    <div>
      <label>Status</label><br>
      <div class="lf-multi-wrap" id="fss-emp-wrap">
        <div class="lf-multi-btn" onclick="toggleLfDropdown('fss',event)">
          <span id="fss-emp-lbl">Todos</span><span id="fss-emp-arr">&#9660;</span>
        </div>
        <div class="lf-multi-panel" id="fss-emp-panel">
          <div class="lf-multi-list" id="fss-emp-list"></div>
          <div class="lf-multi-footer" onclick="clearFsStatSel()">Limpar seleção</div>
        </div>
      </div>
    </div>
    <div>
      <label>Competência</label><br>
      <select id="fs-comp" onchange="filtrarFornSit()">
        <option value="">Todas</option>
      </select>
    </div>
    <div>
      <label>Buscar documento</label><br>
      <input type="text" id="forn-sit-busca" placeholder="Ex: FGTS, CND, TRF3..." oninput="dbFiltrarFornSit()" style="width:220px">
    </div>
    <div style="align-self:flex-end">
      <button class="btn-action btn-limpar" onclick="limparFornSit()">Limpar</button>
    </div>
    <div style="align-self:flex-end">
      <span class="export-label">Exportar:</span>
      <span class="export-group">
        <button class="btn-action btn-export" onclick="exportarFornSitXLSX()">Excel</button>
        <button class="btn-action btn-export-pdf" onclick="exportarFornSitPDF()">PDF</button>
        <button class="btn-action btn-export-csv" onclick="exportarFornSitCSV()">CSV</button>
      </span>
    </div>
  </div>

  <div class="chart-card">
    <div id="forn-sit-count"></div>
    <div class="tabela-wrap">
      <table id="forn-sit-table">
        <thead>
          <tr>
            <th>Fornecedor</th>
            <th>Documento</th>
            <th>Competência</th>
            <th>Status</th>
            <th>Vencimento</th>
          </tr>
        </thead>
        <tbody id="forn-sit-body"></tbody>
      </table>
    </div>
  </div>

  </div><!-- /forn-sit-section -->

  <!-- DETALHAMENTO DAS PENDENCIAS -->
  <div class="section-title">
    Detalhamento das Pendencias (com Competencia)
    <span class="section-toggle" onclick="toggleSection('pend-section', this)">▼ Expandir</span>
  </div>
  <div id="pend-section" class="section-collapsible collapsed">

  <div class="filtro-bar">
    <div>
      <label>Area</label><br>
      <select id="filtro-area" onchange="filtrarTabela()">
        <option value="">Todas</option>
        <option value="TERCEIROS">Terceiros</option>
        <option value="DOCUMENTOS">Fornecedor</option>
      </select>
    </div>
    <div>
      <label>Competencia</label><br>
      <select id="filtro-competencia" onchange="filtrarTabela()">
        <option value="">Todas</option>
        {competencias_opts}
      </select>
    </div>
    <div>
      <label>Buscar</label><br>
      <input type="text" id="filtro-busca" placeholder="Documento ou pendencia..." oninput="dbFiltrarTabela()" style="width:200px">
    </div>
    <div style="align-self:flex-end">
      <button class="btn-action btn-limpar" onclick="limparFiltros()">Limpar</button>
    </div>
    <div style="align-self:flex-end">
      <span class="export-label">Exportar:</span>
      <span class="export-group">
        <button class="btn-action btn-export" onclick="exportarPendXLSX()">Excel</button>
        <button class="btn-action btn-export-pdf" onclick="exportarPendPDF()">PDF</button>
        <button class="btn-action btn-export-csv" onclick="exportarPend()">CSV</button>
      </span>
    </div>
  </div>

  <div class="chart-card">
    <div id="tabela-count"></div>
    <div class="tabela-wrap">
      <table id="tabela-pend">
        <thead>
          <tr>
            <th>Fornecedor</th>
            <th>Area</th>
            <th>Documento</th>
            <th>Competencia</th>
            <th>Detalhe da Pendencia</th>
          </tr>
        </thead>
        <tbody id="tabela-body"></tbody>
      </table>
    </div>
    <div id="pend-pagination" style="display:flex;align-items:center;gap:10px;margin-top:10px;font-size:13px;color:{COR_CINZA}"></div>
  </div><!-- /pend-section -->

</div>

<!-- ── FORNECEDORES SEM EXECUÇÃO ─────────────────────────────────────────── -->
<div class="section-header" style="margin-top:24px">
  Fornecedor sem interação com a plataforma
  <span style="background:#6C757D;color:#fff;font-size:11px;padding:2px 8px;border-radius:10px;margin-left:8px">{total_sem_execucao}</span>
  <span class="section-toggle" onclick="toggleSection('sem-exec-section', this)">&#9660; Expandir</span>
</div>
<div id="sem-exec-section" class="section-collapsible collapsed">
  <p style="font-size:12px;color:#666;margin:0 0 12px 0">
    Cadastrados na plataforma mas sem nenhuma interação registrada em R3 (terceiros) ou R4 (corporativo). Verificar se estão ativos e se devem ser engajados.
  </p>
  <div class="chart-card">
    <div class="tabela-wrap">
      <table id="sem-exec-tabela" style="width:100%">
        <thead>
          <tr><th>Razão Social</th><th>CPF/CNPJ</th></tr>
        </thead>
        <tbody id="sem-exec-body"></tbody>
      </table>
    </div>
  </div>
</div>

<div class="footer">
  Dashboard gerado automaticamente pela plataforma Efcaz &mdash; {DATA_HOJE} &mdash; Uso interno
</div>

<script>
const DADOS        = {json.dumps(tabela_json, ensure_ascii=False)};
const SIT          = {json.dumps(sit_tabela_json, ensure_ascii=False)};
const TERC_KPI     = {json.dumps(terc_kpi_json, ensure_ascii=False)};
const FORN_SIT     = {json.dumps(forn_sit_json, ensure_ascii=False)};
const FORN_CNPJ_MAP  = {forn_cnpj_json};
const ALL_CADASTRO   = {all_cadastro_names_json};
const SEM_EXEC       = {sem_exec_json};
const CONTRATOS      = {contratos_json};

// ── KPI DINAMICO ──────────────────────────────────────────────────────────────
function updateKPICards() {{
  const s  = SIT.filter(r => matchesForn(r.Fornecedor, r.CNPJ_Forn) && matchesCompGlobal(r.Competencia));
  const fs = FORN_SIT.filter(r => matchesForn(r["Fornecedor"], r["CNPJ"]) && matchesCompGlobal(r["Competencia"]));

  // Bloco 2: docs esperados
  const docsEspForn = fs.length;
  const docsEspTerc = s.length;

  // Bloco 3: status (R3 + R4 combinados)
  const aprovR3     = s.filter(r => r.Status === "Aprovado").length;
  const aprovR4     = fs.filter(r => r.Status === "Aprovado").length;
  const naoAnexR3    = s.filter(r => r.Status === "Não anexado").length;
  const aguardR3Elab = s.filter(r => r.Status === "Aguardando Submissão").length;
  const aguardR3Real = s.filter(r => r.Status === "Em Análise").length;
  const naoAnexR4    = fs.filter(r => r.Status === "Não Anexado").length;
  const emAnalR4     = fs.filter(r => r.Status === "Em análise").length;
  const vencidoR4    = fs.filter(r => r.Status === "Vencido").length;
  const reprovR3     = s.filter(r => r.Status === "Reprovado").length;
  const reprovR4     = fs.filter(r => r.Status === "Reprovado").length;
  const irregularR4  = fs.filter(r => r.Status === "Irregular").length;
  const alertaR4     = fs.filter(r => r.Status === "Alerta").length;
  const docsAprov    = aprovR3 + aprovR4;
  const docsNaoAprov = reprovR3 + reprovR4 + irregularR4 + alertaR4;
  const docsNaoEnv   = naoAnexR3 + naoAnexR4;
  const docsAguardSub = aguardR3Elab;
  const docsEmAnal    = aguardR3Real + emAnalR4;
  const docsVencido   = vencidoR4;

  const setEl = (id, val) => {{ const e = document.getElementById(id); if (e) e.textContent = val; }};
  setEl("kpi-docs-esp-forn",  docsEspForn);
  setEl("kpi-docs-esp-terc",  docsEspTerc);
  setEl("kpi-docs-aprov",     docsAprov);
  setEl("kpi-docs-nao-aprov", docsNaoAprov);
  setEl("kpi-docs-nao-env",   docsNaoEnv);
  setEl("kpi-docs-aguard-sub", docsAguardSub);
  setEl("kpi-docs-em-anal",   docsEmAnal);
  setEl("kpi-docs-vencido",   docsVencido);

  renderPizza(s);
  renderPizzaForn(fs);
  renderPizzaGeral(s, fs);
}}


const COR_CONF    = "#10B981";
const COR_NAO_CONF = "#EF4444";

function _makePizzaTrace(conforme, naoConforme, hole) {{
  const total = conforme + naoConforme;
  const pctConf    = total > 0 ? (conforme    / total * 100).toFixed(1) : "0.0";
  const pctNaoConf = total > 0 ? (naoConforme / total * 100).toFixed(1) : "0.0";
  return {{
    type: "pie",
    labels: ["Conforme " + pctConf + "%", "Não Conforme " + pctNaoConf + "%"],
    values: [conforme, naoConforme],
    hole: hole || 0,
    marker: {{ colors: [COR_CONF, COR_NAO_CONF] }},
    textinfo: "none",
    hovertemplate: "<b>%{{label}}</b><br>%{{value}} docs (%{{percent}})<extra></extra>"
  }};
}}
function _makePizzaLayout(annotations) {{
  return {{
    paper_bgcolor: "white", plot_bgcolor: "white",
    font: {{ family: "Calibri, Arial", size: 11 }},
    margin: {{ l: 10, r: 10, t: 10, b: 40 }},
    height: 240, showlegend: true,
    legend: {{ orientation: "h", y: -0.12, x: 0.5, xanchor: "center", font: {{ size: 11 }} }},
    annotations: annotations || []
  }};
}}
function _pizzaAnnotation(conforme, naoConforme) {{
  const total = conforme + naoConforme;
  const pct = total > 0 ? (conforme / total * 100).toFixed(1) : "0.0";
  return [{{ text: "<b>" + pct + "%</b><br><span style='font-size:10px'>conforme</span>",
    x: 0.5, y: 0.5, xanchor: "center", yanchor: "middle",
    showarrow: false, font: {{ size: 15, color: "#1a2a35", family: "Calibri, Arial" }} }}];
}}
function renderPizza(sitData) {{
  const conforme    = sitData.filter(r => r.Status === "Aprovado").length;
  const naoConforme = sitData.filter(r => r.Status !== "Aprovado").length;
  Plotly.newPlot("fig-pizza", [_makePizzaTrace(conforme, naoConforme, 0.58)],
    _makePizzaLayout(_pizzaAnnotation(conforme, naoConforme)), {{ displayModeBar: false, responsive: true }});
}}
function renderPizzaForn(data) {{
  const conforme    = data.filter(r => r.Status === "Aprovado").length;
  const naoConforme = data.filter(r => r.Status !== "Aprovado").length;
  Plotly.newPlot("fig-pizza-forn", [_makePizzaTrace(conforme, naoConforme, 0.58)],
    _makePizzaLayout(_pizzaAnnotation(conforme, naoConforme)), {{ displayModeBar: false, responsive: true }});
}}
function renderPizzaGeral(sitData, fornSitData) {{
  const confR3  = sitData.filter(r => r.Status === "Aprovado").length;
  const ncR3    = sitData.filter(r => r.Status !== "Aprovado").length;
  const confR4  = fornSitData.filter(r => r.Status === "Aprovado").length;
  const ncR4    = fornSitData.filter(r => r.Status !== "Aprovado").length;
  const conforme    = confR3 + confR4;
  const naoConforme = ncR3  + ncR4;
  const total = conforme + naoConforme;
  const pct   = total > 0 ? (conforme / total * 100).toFixed(1) : "0.0";
  Plotly.newPlot("fig-pizza-geral", [_makePizzaTrace(conforme, naoConforme, 0.58)],
    _makePizzaLayout(_pizzaAnnotation(conforme, naoConforme)), {{ displayModeBar: false, responsive: true }});
}}

// ── SELECTS FORNECEDOR ────────────────────────────────────────────────────────
function preencherSelect(selectId, dados, campo) {{
  const vals = [...new Set(dados.map(r => r[campo]))].sort();
  const sel = document.getElementById(selectId);
  vals.forEach(v => {{
    const o = document.createElement("option");
    o.value = v; o.text = v; sel.appendChild(o);
  }});
}}
// Formata CPF (11 dígitos) ou CNPJ (14 dígitos) com pontuação
function fmtDoc(d) {{
  const n = String(d || "").replace(/[^0-9]/g, "");
  if (n.length === 11) return n.replace(/([0-9]{{3}})([0-9]{{3}})([0-9]{{3}})([0-9]{{2}})/, "$1.$2.$3-$4");
  if (n.length === 14) return n.replace(/([0-9]{{2}})([0-9]{{3}})([0-9]{{3}})([0-9]{{4}})([0-9]{{2}})/, "$1.$2.$3/$4-$5");
  return d || "";
}}
// Parseia valor composto "nome|||cnpj" ou simples "nome"
function parseFornVal(val) {{
  if (!val) return {{ nome: "", cnpj: "" }};
  const idx = val.indexOf("|||");
  return idx === -1 ? {{ nome: val, cnpj: "" }} : {{ nome: val.slice(0, idx), cnpj: val.slice(idx + 3) }};
}}

// ── UTILITÁRIOS DE PERFORMANCE ────────────────────────────────────────────────
function debounce(fn, delay) {{
  let timer;
  return function(...args) {{ clearTimeout(timer); timer = setTimeout(() => fn.apply(this, args), delay); }};
}}

// Paginação R3
const SIT_PAGE_SIZE = 150;
let sitPage = 0;
function renderSitPage() {{
  const start = sitPage * SIT_PAGE_SIZE;
  const rows  = sitFiltrado.slice(start, start + SIT_PAGE_SIZE);
  const tbody = document.getElementById("sit-body");
  tbody.innerHTML = rows.map(r => `
    <tr>
      <td>${{r["Fornecedor"]}}</td>
      <td>${{r["Terceiro"]}}</td>
      <td>${{r["Documento"]}}</td>
      <td>${{r["Competencia"] ? '<span class="badge-competencia">' + r["Competencia"] + '</span>' : '<span style="color:#aaa">—</span>'}}</td>
      <td>${{badgeSit(r["Status"])}}</td>
      <td>${{r["Vencimento"] || "—"}}</td>
    </tr>
  `).join("");
  const total = sitFiltrado.length;
  const pages = Math.ceil(total / SIT_PAGE_SIZE);
  const el = document.getElementById("sit-pagination");
  if (!el) return;
  if (pages <= 1) {{ el.innerHTML = ""; return; }}
  el.innerHTML = `
    <button onclick="sitPage=Math.max(0,sitPage-1);renderSitPage()"
      style="padding:4px 12px;border:1px solid #ccc;border-radius:4px;cursor:pointer;background:white" ${{sitPage===0?'disabled':''}}>‹ Anterior</button>
    <span>Página ${{sitPage+1}} de ${{pages}} &nbsp;(${{total}} registros)</span>
    <button onclick="sitPage=Math.min(${{pages-1}},sitPage+1);renderSitPage()"
      style="padding:4px 12px;border:1px solid #ccc;border-radius:4px;cursor:pointer;background:white" ${{sitPage===pages-1?'disabled':''}}>Próximo ›</button>
  `;
}}

// Paginação Pendências
const PEND_PAGE_SIZE = 150;
let pendPage = 0;
function renderPendPage() {{
  const start = pendPage * PEND_PAGE_SIZE;
  const rows  = pendFiltrado.slice(start, start + PEND_PAGE_SIZE);
  const tbody = document.getElementById("tabela-body");
  tbody.innerHTML = rows.map(r => `
    <tr>
      <td>
        <div>${{r["Fornecedor"]}}</div>
        ${{r["CNPJ"] ? '<div style="font-size:11px;color:#999;font-family:monospace;margin-top:2px">' + fmtDoc(r["CNPJ"]) + '</div>' : ''}}
      </td>
      <td>${{badgeArea(r["Area"])}}</td>
      <td><strong>${{r["Documento"]}}</strong></td>
      <td>${{r["Competencia"] === "Não possui competência"
        ? '<span style="color:#aaa;font-size:11px">Não possui</span>'
        : r["Competencia"] && r["Competencia"] !== "A classificar"
          ? '<span class="badge-competencia">' + r["Competencia"] + '</span>'
          : '<span style="color:#aaa">—</span>'}}</td>
      <td style="max-width:380px;white-space:pre-wrap;font-size:12px">${{r["Detalhe"] || "—"}}</td>
    </tr>
  `).join("");
  const total = pendFiltrado.length;
  const pages = Math.ceil(total / PEND_PAGE_SIZE);
  const el = document.getElementById("pend-pagination");
  if (!el) return;
  if (pages <= 1) {{ el.innerHTML = ""; return; }}
  el.innerHTML = `
    <button onclick="pendPage=Math.max(0,pendPage-1);renderPendPage()"
      style="padding:4px 12px;border:1px solid #ccc;border-radius:4px;cursor:pointer;background:white" ${{pendPage===0?'disabled':''}}>‹ Anterior</button>
    <span>Página ${{pendPage+1}} de ${{pages}} &nbsp;(${{total}} registros)</span>
    <button onclick="pendPage=Math.min(${{pages-1}},pendPage+1);renderPendPage()"
      style="padding:4px 12px;border:1px solid #ccc;border-radius:4px;cursor:pointer;background:white" ${{pendPage===pages-1?'disabled':''}}>Próximo ›</button>
  `;
}}

// Aliases debounced para inputs de busca (300ms)
const dbFiltrarSit      = debounce(filtrarSit, 300);
const dbFiltrarFornSit  = debounce(filtrarFornSit, 300);
const dbFiltrarTabela   = debounce(filtrarTabela, 300);

// ── MULTI-SELECT GLOBAL FILTER ─────────────────────────────────────────────
let selectedFornSet = new Set();
let selectedCompSet = new Set();
let gfStatusTerc    = 'all';

// Retorna Set de CPFs (dígitos) dos terceiros com status selecionado
function buildStatusTercSet() {{
  if (gfStatusTerc === 'all') return null;
  const cpfs = new Set();
  CONTRATOS.forEach(f => {{
    Object.values(f.terceiros_by_contract).forEach(tercs => {{
      tercs.forEach(t => {{
        if (t.status === gfStatusTerc) {{
          const c = (t.cnpj || '').replace(/\D/g,'');
          if (c) cpfs.add(c);
        }}
      }});
    }});
  }});
  return cpfs;
}}

function setStatusTerc(val) {{
  gfStatusTerc = val;
  ['all','Ativo','Inativo'].forEach(v => {{
    const id  = 'gf-status-terc-' + (v === 'all' ? 'all' : v.toLowerCase());
    const btn = document.getElementById(id);
    if (!btn) return;
    btn.style.background = (v === val) ? 'white' : 'rgba(255,255,255,.15)';
    btn.style.color      = (v === val) ? '{COR_TEAL_ESCURO}' : 'white';
  }});
  applyGlobalFilter();
}}

// ── FILTRO AEROPORTO ──────────────────────────────────────────────────────────
let gfAeroportoSet = new Set();

// Constrói índice de CPFs de terceiros, CNPJs de fornecedores e nomes de terceiros
// para os aeroportos selecionados — mesma lógica do React aeroportoFilter useMemo
function buildAeroportoFilter() {{
  if (gfAeroportoSet.size === 0) return null;
  const terceirosCPFs  = new Set();
  const fornCNPJs      = new Set();
  const terceirosNomes = new Set();
  CONTRATOS.forEach(f => {{
    Object.values(f.terceiros_by_contract).forEach(tercs => {{
      tercs.forEach(t => {{
        const aero = (t.aeroporto || '').toUpperCase().trim();
        if (gfAeroportoSet.has(aero)) {{
          const c = (t.cnpj || '').replace(/\D/g,'');
          if (c) terceirosCPFs.add(c);
          fornCNPJs.add(f.cnpj);
          if (t.nome) terceirosNomes.add(t.nome.toUpperCase().trim());
        }}
      }});
    }});
  }});
  return {{ terceirosCPFs, fornCNPJs, terceirosNomes }};
}}

function toggleAeroporto(code) {{
  if (gfAeroportoSet.has(code)) gfAeroportoSet.delete(code);
  else gfAeroportoSet.add(code);
  const btn = document.getElementById('gf-aero-' + code);
  if (btn) {{
    btn.style.background = gfAeroportoSet.has(code) ? 'white' : 'rgba(255,255,255,.15)';
    btn.style.color      = gfAeroportoSet.has(code) ? '{COR_TEAL_ESCURO}' : 'white';
  }}
  applyGlobalFilter();
}}

function matchesForn(rowNome, rowCNPJ) {{
  if (selectedFornSet.size === 0) return true;
  for (const raw of selectedFornSet) {{
    const {{nome, cnpj}} = parseFornVal(raw);
    if (rowNome === nome && (!cnpj || !rowCNPJ || rowCNPJ === cnpj)) return true;
  }}
  return false;
}}

function buildFornMultiSelect() {{
  const allNames = new Set([
    ...DADOS.map(r => r["Fornecedor"]),
    ...SIT.map(r => r["Fornecedor"]),
    ...FORN_SIT.map(r => r["Fornecedor"])
  ]);
  const seen = new Set();
  const pares = [];
  [...allNames].forEach(nome => {{
    const cnpjs = FORN_CNPJ_MAP[nome] || [];
    const isDup = cnpjs.length > 1;
    if (isDup) {{
      cnpjs.forEach(cnpj => {{
        const key = nome + "|||" + cnpj;
        if (!seen.has(key)) {{ seen.add(key); pares.push({{key, label: nome + " (" + fmtDoc(cnpj) + ")"}}); }}
      }});
    }} else {{
      if (!seen.has(nome)) {{
        seen.add(nome);
        const cnpj = cnpjs[0] || "";
        pares.push({{key: nome, label: cnpj ? nome + " (" + fmtDoc(cnpj) + ")" : nome}});
      }}
    }}
  }});
  pares.sort((a, b) => a.label.localeCompare(b.label));

  const list = document.getElementById("gf-multi-list");
  list.innerHTML = "";
  pares.forEach(({{key, label}}) => {{
    const div = document.createElement("div");
    div.className = "gf-item";
    div.dataset.key = key;
    div.dataset.lbl = label.toLowerCase();
    const cbId = "gf-cb-" + key.replace(/[^a-z0-9]/gi, "_");
    div.innerHTML = `<input type="checkbox" id="${{cbId}}"><label for="${{cbId}}" style="cursor:pointer;flex:1;font-size:13px">${{label}}</label>`;
    div.querySelector("input").addEventListener("change", e => {{
      if (e.target.checked) {{ selectedFornSet.add(key); div.classList.add("gf-selected"); }}
      else {{ selectedFornSet.delete(key); div.classList.remove("gf-selected"); }}
      applyGlobalFilter();
    }});
    list.appendChild(div);
  }});
}}

function toggleFornDropdown(e) {{
  e.stopPropagation();
  const panel = document.getElementById("gf-multi-panel");
  const arrow = document.getElementById("gf-multi-arrow");
  const isOpen = panel.style.display === "block";
  panel.style.display = isOpen ? "none" : "block";
  arrow.textContent = isOpen ? "▾" : "▴";
  if (!isOpen) document.getElementById("gf-multi-search").focus();
}}

function filterFornItems(q) {{
  const lq = q.toLowerCase();
  document.querySelectorAll("#gf-multi-list .gf-item").forEach(div => {{
    div.style.display = div.dataset.lbl.includes(lq) ? "" : "none";
  }});
}}

document.addEventListener("click", e => {{
  const wrap = document.getElementById("gf-multi-wrap");
  if (wrap && !wrap.contains(e.target)) {{
    document.getElementById("gf-multi-panel").style.display = "none";
    document.getElementById("gf-multi-arrow").textContent = "▾";
  }}
  const wrapC = document.getElementById("gfc-multi-wrap");
  if (wrapC && !wrapC.contains(e.target)) {{
    document.getElementById("gfc-multi-panel").style.display = "none";
    document.getElementById("gfc-multi-arrow").textContent = "▾";
  }}
}});

function matchesCompGlobal(rowComp) {{
  if (selectedCompSet.size === 0) return true;
  return selectedCompSet.has(rowComp || "A classificar");
}}

function buildCompMultiSelect() {{
  const comps = [...new Set([
    ...SIT.map(r => r["Competencia"] || "A classificar"),
    ...FORN_SIT.map(r => r["Competencia"]).filter(Boolean),
    ...DADOS.map(r => r["Competencia"] || "A classificar")
  ])].filter(Boolean).sort();
  const list = document.getElementById("gfc-multi-list");
  list.innerHTML = "";
  comps.forEach(comp => {{
    const div = document.createElement("div");
    div.className = "gfc-item";
    div.dataset.key = comp;
    div.dataset.lbl = comp.toLowerCase();
    const cbId = "gfc-cb-" + comp.replace(/[^a-z0-9]/gi, "_");
    div.innerHTML = `<input type="checkbox" id="${{cbId}}"><label for="${{cbId}}" style="cursor:pointer;flex:1;font-size:13px">${{comp}}</label>`;
    div.querySelector("input").addEventListener("change", e => {{
      if (e.target.checked) {{ selectedCompSet.add(comp); div.classList.add("gfc-selected"); }}
      else {{ selectedCompSet.delete(comp); div.classList.remove("gfc-selected"); }}
      applyGlobalFilter();
    }});
    list.appendChild(div);
  }});
}}

function toggleCompDropdown(e) {{
  e.stopPropagation();
  const panel = document.getElementById("gfc-multi-panel");
  const arrow = document.getElementById("gfc-multi-arrow");
  const isOpen = panel.style.display === "block";
  panel.style.display = isOpen ? "none" : "block";
  arrow.textContent = isOpen ? "▾" : "▴";
  if (!isOpen) document.getElementById("gfc-multi-search").focus();
}}

function filterCompItems(q) {{
  const lq = q.toLowerCase();
  document.querySelectorAll("#gfc-multi-list .gfc-item").forEach(div => {{
    div.style.display = div.dataset.lbl.includes(lq) ? "" : "none";
  }});
}}

function limparCompFiltroSilent() {{
  selectedCompSet.clear();
  document.querySelectorAll("#gfc-multi-list .gfc-item").forEach(div => {{
    const cb = div.querySelector("input[type=checkbox]");
    if (cb) cb.checked = false;
    div.classList.remove("gfc-selected");
  }});
  const s = document.getElementById("gfc-multi-search");
  if (s) {{ s.value = ""; filterCompItems(""); }}
  document.getElementById("gfc-selected-label").textContent = "Todas as competências";
}}

// Popula select de fornecedor; usa FORN_CNPJ_MAP (gerado pelo Python) para detectar
// empresas com mesma razão social e CNPJs diferentes → cria uma opção por CNPJ
function buildFornSelect(selId, names) {{
  const seen = new Set();
  const pares = [];
  [...new Set(names)].forEach(nome => {{
    const cnpjs = FORN_CNPJ_MAP[nome] || [];  // [] = sem duplicata
    const isDup = cnpjs.length > 1;
    if (isDup) {{
      cnpjs.forEach(cnpj => {{
        const key = nome + "|||" + cnpj;
        if (!seen.has(key)) {{ seen.add(key); pares.push({{nome, cnpj, isDup: true}}); }}
      }});
    }} else {{
      if (!seen.has(nome)) {{
        seen.add(nome);
        pares.push({{nome, cnpj: cnpjs[0] || "", isDup: false}});
      }}
    }}
  }});
  pares.sort((a, b) => a.nome.localeCompare(b.nome));
  const sel = document.getElementById(selId);
  pares.forEach(({{nome, cnpj, isDup}}) => {{
    const o = document.createElement("option");
    o.value = isDup ? nome + "|||" + cnpj : nome;
    o.text  = isDup ? nome + " (" + cnpj + ")" : nome;
    sel.appendChild(o);
  }});
}}

// ── MULTI-SELECT LOCAL — Sets de seleção por seção ────────────────────────────

function matchesLocalSet(set, nome, cnpj) {{
  if (set.size === 0) return true;
  for (const raw of set) {{
    const {{nome: n, cnpj: c}} = parseFornVal(raw);
    if (nome === n && (!c || !cnpj || cnpj === c)) return true;
  }}
  return false;
}}

function buildLfPares(names) {{
  const seen = new Set(); const pares = [];
  [...new Set(names)].forEach(nome => {{
    const cnpjs = FORN_CNPJ_MAP[nome] || [];
    if (cnpjs.length > 1) {{
      cnpjs.forEach(cnpj => {{
        const key = nome + "|||" + cnpj;
        if (!seen.has(key)) {{ seen.add(key); pares.push({{key, label: nome + " (" + cnpj + ")"}}); }}
      }});
    }} else {{
      if (!seen.has(nome)) {{
        seen.add(nome);
        const cnpj = cnpjs[0] || "";
        pares.push({{key: nome, label: cnpj ? nome + " (" + cnpj + ")" : nome}});
      }}
    }}
  }});
  pares.sort((a, b) => a.label.localeCompare(b.label));
  return pares;
}}

function buildLfMultiSelect(pfx, pares, set, onChangeFn) {{
  const list = document.getElementById(pfx + "-emp-list");
  if (!list) return;
  list.innerHTML = "";
  pares.forEach(({{key, label}}) => {{
    const div = document.createElement("div");
    div.className = "lf-item";
    div.dataset.key = key; div.dataset.lbl = label.toLowerCase();
    const cbId = pfx + "-lf-" + key.replace(/[^a-z0-9]/gi, "_");
    div.innerHTML = `<input type="checkbox" id="${{cbId}}"><label for="${{cbId}}">${{label}}</label>`;
    div.querySelector("input").addEventListener("change", e => {{
      if (e.target.checked) {{ set.add(key); div.classList.add("lf-selected"); }}
      else {{ set.delete(key); div.classList.remove("lf-selected"); }}
      updateLfLabel(pfx, set);
      onChangeFn();
    }});
    list.appendChild(div);
  }});
}}

function updateLfLabel(pfx, set) {{
  const lbl = document.getElementById(pfx + "-emp-lbl");
  if (!lbl) return;
  lbl.textContent = set.size === 0 ? "Todos"
    : set.size === 1 ? parseFornVal([...set][0]).nome
    : set.size + " selecionados";
}}

function toggleLfDropdown(pfx, e) {{
  e.stopPropagation();
  const panel = document.getElementById(pfx + "-emp-panel");
  const arr   = document.getElementById(pfx + "-emp-arr");
  const isOpen = panel.style.display === "block";
  document.querySelectorAll(".lf-multi-panel").forEach(p => p.style.display = "none");
  document.querySelectorAll(".lf-multi-btn span:last-child").forEach(a => a.textContent = "▾");
  if (!isOpen) {{
    panel.style.display = "block";
    if (arr) arr.textContent = "▴";
    const s = panel.querySelector(".lf-multi-search");
    if (s) s.focus();
  }}
}}

function filterLfItems(pfx, q) {{
  const lq = q.toLowerCase();
  document.querySelectorAll("#" + pfx + "-emp-list .lf-item").forEach(div => {{
    div.style.display = div.dataset.lbl.includes(lq) ? "" : "none";
  }});
}}

function clearLfSel(pfx, set, onChangeFn) {{
  set.clear();
  document.querySelectorAll("#" + pfx + "-emp-list .lf-item").forEach(div => {{
    div.classList.remove("lf-selected");
    const cb = div.querySelector("input"); if (cb) cb.checked = false;
  }});
  updateLfLabel(pfx, set);
  onChangeFn();
}}

// Fechar painéis locais ao clicar fora
document.addEventListener("click", e => {{
  if (!e.target.closest(".lf-multi-wrap")) {{
    document.querySelectorAll(".lf-multi-panel").forEach(p => p.style.display = "none");
  }}
}});


// Popular select de competência R3
(function() {{
  const sel = document.getElementById("sit-comp");
  if (!sel) return;
  const comps = [...new Set(SIT.map(r => r["Competencia"]).filter(Boolean))].sort();
  comps.forEach(c => {{
    const opt = document.createElement("option");
    opt.value = opt.textContent = c;
    sel.appendChild(opt);
  }});
}})();

// Popular select de competência R4
(function() {{
  const sel = document.getElementById("fs-comp");
  if (!sel) return;
  const comps = [...new Set(FORN_SIT.map(r => r["Competencia"]).filter(Boolean))].sort();
  comps.forEach(c => {{
    const opt = document.createElement("option");
    opt.value = opt.textContent = c;
    sel.appendChild(opt);
  }});
}})();

// ── BADGES ────────────────────────────────────────────────────────────────────
function badgeStatus(s) {{
  if (!s) return "";
  if (s === "EM_ELABORACAO") return '<span class="badge badge-pendente_env">Pendente (nao enviado)</span>';
  return '<span class="badge badge-em_analise">Em Analise</span>';
}}
function badgeArea(a) {{
  if (!a) return "";
  if (a === "TERCEIROS") return '<span class="badge badge-terceiros">Terceiros</span>';
  return '<span class="badge badge-documentos">Fornecedor</span>';
}}
function badgeSit(s) {{
  if (s === "Aprovado")             return '<span class="badge badge-conforme">Aprovado</span>';
  if (s === "Reprovado")            return '<span class="badge badge-vencido">Reprovado</span>';
  if (s === "Irregular")            return '<span class="badge badge-irregular">Irregular (Débito)</span>';
  if (s === "Irregular (Débito)")   return '<span class="badge badge-irregular">Irregular (Débito)</span>';
  if (s === "Alerta")               return '<span class="badge badge-alerta">Alerta</span>';
  if (s === "Não anexado")          return '<span class="badge badge-pendente">Não anexado</span>';
  if (s === "Não Anexado")          return '<span class="badge badge-pendente">Não Anexado</span>';
  if (s === "Aguardando Submissão") return '<span class="badge badge-aguardando-submissao">Aguardando Submissão</span>';
  if (s === "Em Análise")           return '<span class="badge badge-em-analise">Em Análise</span>';
  if (s === "Aguardando análise")   return '<span class="badge badge-aguardando-analise">Aguardando análise</span>';
  if (s === "Em análise")           return '<span class="badge badge-em-analise">Em análise</span>';
  if (s === "Vencido")              return '<span class="badge badge-vencido">Vencido</span>';
  if (s === "Não Analisado")        return '<span class="badge badge-aguardando-analise">Não Analisado</span>';
  if (s === "A vencer")             return '<span class="badge badge-conforme">A vencer</span>';
  return '<span class="badge badge-pendente">' + s + '</span>';
}}

// ── KPI CLICÁVEL ──────────────────────────────────────────────────────────────
let activeKpiKey = null;
const KPI_STATUS_MAP_GLOBAL = {{
  docs_aprovados:    {{ sit: ["Aprovado"],             forn: ["Aprovado"] }},
  docs_reprovados:   {{ sit: ["Reprovado"],             forn: ["Reprovado", "Irregular", "Alerta"] }},
  docs_nao_enviados: {{ sit: ["Não anexado"],           forn: ["Não Anexado"] }},
  docs_aguard_sub:   {{ sit: ["Aguardando Submissão"],  forn: [] }},
  docs_em_analise:   {{ sit: ["Em Análise"],            forn: ["Em análise"] }},
  docs_vencidos:     {{ sit: [],                        forn: ["Vencido"] }},
}};
function toggleKpiCard(key) {{
  activeKpiKey = (activeKpiKey === key) ? null : key;
  document.querySelectorAll(".kpi-card[data-kpi-key]").forEach(el => {{
    const isAtivo = el.dataset.kpiKey === activeKpiKey;
    el.classList.toggle("kpi-active", isAtivo);
    let badge = el.querySelector(".kpi-ativo-badge");
    if (isAtivo) {{
      if (!badge) {{ badge = document.createElement("div"); badge.className = "kpi-ativo-badge"; badge.textContent = "ativo"; el.appendChild(badge); }}
    }} else {{
      if (badge) badge.remove();
    }}
  }});
  filtrarSit();
  filtrarFornSit();
}}

// ── TABELA SITUACAO ───────────────────────────────────────────────────────────
let sitFiltrado = [];
function filtrarSit() {{
  const stat  = document.getElementById("sit-status").value;
  const comp  = document.getElementById("sit-comp").value;
  const busca = document.getElementById("sit-busca").value.toLowerCase();
  const stSet   = buildStatusTercSet();
  const aeroFlt = buildAeroportoFilter();
  sitFiltrado = SIT.filter(r => {{
    if (!matchesForn(r["Fornecedor"], r["CNPJ_Forn"])) return false;
    if (!matchesCompGlobal(r["Competencia"])) return false;
    if (stat  && r["Status"]      !== stat)  return false;
    if (comp  && r["Competencia"] !== comp)  return false;
    if (busca && !r["Documento"].toLowerCase().includes(busca)) return false;
    if (stSet) {{
      const cpfTerc = (r["CNPJ_Terceiro"] || '').replace(/\D/g,'');
      if (!stSet.has(cpfTerc)) return false;
    }}
    if (aeroFlt) {{
      const cpfTerc = (r["CNPJ_Terceiro"] || '').replace(/\D/g,'');
      if (!aeroFlt.terceirosCPFs.has(cpfTerc)) return false;
    }}
    if (activeKpiKey) {{
      const ss = (KPI_STATUS_MAP_GLOBAL[activeKpiKey] || {{}}).sit || [];
      if (ss.length > 0 && !ss.includes(r["Status"])) return false;
    }}
    return true;
  }});
  sitPage = 0;
  renderSitPage();
  document.getElementById("sit-count").textContent =
    `${{sitFiltrado.length}} registro(s) exibido(s) de ${{SIT.length}} no total`;
  if (modoAgrupado) renderSitAgrupado(sitFiltrado);

  // KPIs dinâmicos R3
  const aprov3    = sitFiltrado.filter(r => r["Status"] === "Aprovado").length;
  const reprov3   = sitFiltrado.filter(r => r["Status"] === "Reprovado").length;
  const naoAnex3  = sitFiltrado.filter(r => r["Status"] === "Não anexado").length;
  const aguardSub3 = sitFiltrado.filter(r => r["Status"] === "Aguardando Submissão").length;
  const emAnal3    = sitFiltrado.filter(r => r["Status"] === "Em Análise").length;
  const aguard3    = aguardSub3 + emAnal3;
  const tot3      = aprov3 + reprov3 + naoAnex3 + aguard3;
  const pctNC3    = tot3 > 0 ? ((reprov3 + naoAnex3 + aguard3) / tot3 * 100).toFixed(1) : "0.0";
  const pctC3     = tot3 > 0 ? (aprov3 / tot3 * 100).toFixed(1) : "0.0";
  const terc3     = new Set(sitFiltrado.map(r => r["Terceiro"])).size;
  [["sit-kpi-nc", pctNC3 + "%"], ["sit-kpi-c", pctC3 + "%"],
   ["sit-kpi-aprov", aprov3], ["sit-kpi-reprov", reprov3],
   ["sit-kpi-nao-anex", naoAnex3], ["sit-kpi-aguard-sub", aguardSub3],
   ["sit-kpi-aguard-real", emAnal3], ["sit-kpi-terc", terc3]
  ].forEach(([id, val]) => {{ const e = document.getElementById(id); if (e) e.textContent = val; }});
}}
function limparSit() {{
  ["sit-status","sit-comp","sit-busca"].forEach(id => {{
    const el = document.getElementById(id); if (el) el.value = "";
  }});
  filtrarSit();
}}

// ── TABELA PENDENCIAS ─────────────────────────────────────────────────────────
let pendFiltrado = [];
function filtrarTabela() {{
  const area  = document.getElementById("filtro-area").value;
  const comp  = document.getElementById("filtro-competencia").value;
  const busca = document.getElementById("filtro-busca").value.toLowerCase();
  const aeroFltPend = buildAeroportoFilter();
  pendFiltrado = DADOS.filter(r => {{
    if (!matchesForn(r["Fornecedor"], r["CNPJ"])) return false;
    if (!matchesCompGlobal(r["Competencia"])) return false;
    if (area && r["Area"]        !== area) return false;
    if (comp && r["Competencia"] !== comp) return false;
    if (busca) {{
      const txt = (r["Documento"] + " " + r["Detalhe"]).toLowerCase();
      if (!txt.includes(busca)) return false;
    }}
    if (aeroFltPend) {{
      if (r["Area"] === "TERCEIROS") {{
        const det = (r["Detalhe"] || "").toUpperCase();
        if (![...aeroFltPend.terceirosNomes].some(nome => det.includes(nome))) return false;
      }} else {{
        const cnpjForn = (r["CNPJ"] || "").replace(/\D/g,"");
        if (!aeroFltPend.fornCNPJs.has(cnpjForn)) return false;
      }}
    }}
    return true;
  }});
  pendPage = 0;
  renderPendPage();
  document.getElementById("tabela-count").textContent =
    `${{pendFiltrado.length}} pendencia(s) exibida(s) de ${{DADOS.length}} no total`;
}}
function limparFiltros() {{
  ["filtro-area","filtro-competencia","filtro-busca"].forEach(id => {{
    const el = document.getElementById(id); if (el) el.value = "";
  }});
  filtrarTabela();
}}

// ── STATUS MULTI-SELECT R4 ────────────────────────────────────────────────────
const FS_STATUS_OPTIONS = [
  {{ key: "Aprovado",    label: "Aprovado" }},
  {{ key: "Reprovado",   label: "Reprovado" }},
  {{ key: "Irregular",   label: "Irregular (Débito)" }},
  {{ key: "Alerta",      label: "Alerta" }},
  {{ key: "Não Anexado", label: "Não Anexado" }},
  {{ key: "Em análise",  label: "Em análise" }},
  {{ key: "Vencido",     label: "Vencido" }},
];
let fsStatSet = new Set();
function buildFsStatMultiSelect() {{
  const list = document.getElementById("fss-emp-list");
  if (!list) return;
  list.innerHTML = "";
  FS_STATUS_OPTIONS.forEach(({{key, label}}) => {{
    const div = document.createElement("div");
    div.className = "lf-item";
    div.dataset.key = key;
    const cbId = "fss-lf-" + key.replace(/[^a-z0-9]/gi, "_");
    div.innerHTML = `<input type="checkbox" id="${{cbId}}"><label for="${{cbId}}">${{label}}</label>`;
    div.querySelector("input").addEventListener("change", e => {{
      if (e.target.checked) {{ fsStatSet.add(key); div.classList.add("lf-selected"); }}
      else {{ fsStatSet.delete(key); div.classList.remove("lf-selected"); }}
      updateFsStatLabel();
      filtrarFornSit();
    }});
    list.appendChild(div);
  }});
}}
function updateFsStatLabel() {{
  const lbl = document.getElementById("fss-emp-lbl");
  if (!lbl) return;
  lbl.textContent = fsStatSet.size === 0 ? "Todos"
    : fsStatSet.size === 1 ? [...fsStatSet][0]
    : fsStatSet.size + " selecionados";
}}
function clearFsStatSilent() {{
  fsStatSet.clear();
  document.querySelectorAll("#fss-emp-list .lf-item").forEach(div => {{
    div.classList.remove("lf-selected");
    const cb = div.querySelector("input"); if (cb) cb.checked = false;
  }});
  updateFsStatLabel();
}}
function clearFsStatSel() {{ clearFsStatSilent(); filtrarFornSit(); }}

// ── TABELA SITUACAO DA EMPRESA (R4) ───────────────────────────────────────────
let fornSitFiltrado = [];
function filtrarFornSit() {{
  const busca = document.getElementById("forn-sit-busca").value.toLowerCase();
  const comp  = (document.getElementById("fs-comp") || {{}}).value || "";
  const cleanDoc = s => String(s || "").replace(/�/g, "");
  const aeroFltR4 = buildAeroportoFilter();
  fornSitFiltrado = FORN_SIT.filter(r => {{
    if (!matchesForn(r["Fornecedor"], r["CNPJ"])) return false;
    if (!matchesCompGlobal(r["Competencia"])) return false;
    if (fsStatSet.size > 0 && !fsStatSet.has(r["Status"])) return false;
    if (comp && r["Competencia"] !== comp) return false;
    if (busca && !cleanDoc(r["Documento"]).toLowerCase().includes(busca)) return false;
    if (aeroFltR4) {{
      const cnpjForn = (r["CNPJ"] || '').replace(/\D/g,'');
      if (!aeroFltR4.fornCNPJs.has(cnpjForn)) return false;
    }}
    if (activeKpiKey) {{
      const fs = (KPI_STATUS_MAP_GLOBAL[activeKpiKey] || {{}}).forn || [];
      if (fs.length > 0 && !fs.includes(r["Status"])) return false;
    }}
    return true;
  }});
  const tbody = document.getElementById("forn-sit-body");
  tbody.innerHTML = fornSitFiltrado.map(r => `
    <tr>
      <td>
        <div>${{r["Fornecedor"]}}</div>
        ${{r["CNPJ"] ? '<div style="font-size:11px;color:#999;font-family:monospace;margin-top:2px">' + fmtDoc(r["CNPJ"]) + '</div>' : ''}}
      </td>
      <td>${{cleanDoc(r["Documento"])}}</td>
      <td>${{r["Competencia"] ? '<span class="badge-competencia">' + r["Competencia"] + '</span>' : '<span style="color:#aaa">—</span>'}}</td>
      <td>${{badgeSit(r["Status"])}}</td>
      <td>${{r["Vencimento"] || "—"}}</td>
    </tr>
  `).join("");
  const cnt = document.getElementById("forn-sit-count");
  if (cnt) cnt.textContent = `${{fornSitFiltrado.length}} registro(s) de ${{FORN_SIT.length}} no total`;

  // KPIs dinâmicos R4
  const aprov4     = fornSitFiltrado.filter(r => r["Status"]==="Aprovado").length;
  const reprov4    = fornSitFiltrado.filter(r => r["Status"]==="Reprovado").length;
  const irreg4     = fornSitFiltrado.filter(r => r["Status"]==="Irregular").length;
  const alerta4    = fornSitFiltrado.filter(r => r["Status"]==="Alerta").length;
  const naoAnex4   = fornSitFiltrado.filter(r => r["Status"]==="Não Anexado").length;
  const emAnalise4 = fornSitFiltrado.filter(r => r["Status"]==="Em análise").length;
  const vencido4   = fornSitFiltrado.filter(r => r["Status"]==="Vencido").length;
  const tot4       = aprov4 + reprov4 + irreg4 + alerta4 + naoAnex4 + emAnalise4 + vencido4;
  const pctNC4     = tot4>0 ? ((reprov4+irreg4+alerta4+naoAnex4+emAnalise4+vencido4)/tot4*100).toFixed(1) : "0.0";
  const pctC4      = tot4>0 ? (aprov4/tot4*100).toFixed(1) : "0.0";
  const forn4      = new Set(fornSitFiltrado.map(r=>r["Fornecedor"])).size;
  [["r4-kpi-nc", pctNC4+"%"], ["r4-kpi-c", pctC4+"%"],
   ["r4-kpi-aprov", aprov4], ["r4-kpi-reprov", reprov4],
   ["r4-kpi-irregular", irreg4], ["r4-kpi-alerta", alerta4], ["r4-kpi-nao-anex", naoAnex4],
   ["r4-kpi-em-analise", emAnalise4], ["r4-kpi-vencido", vencido4], ["r4-kpi-forn", forn4]
  ].forEach(([id, val]) => {{ const e=document.getElementById(id); if(e) e.textContent=val; }});
}}
function limparFornSit() {{
  clearFsStatSilent();
  const busca = document.getElementById("forn-sit-busca"); if (busca) busca.value = "";
  const comp  = document.getElementById("fs-comp"); if (comp) comp.value = "";
  filtrarFornSit();
}}
function exportarFornSitXLSX() {{
  downloadXLSX(fornSitFiltrado, ["Fornecedor","CNPJ","Documento","Competencia","Status","Vencimento"], "situacao_empresa_zurich.xlsx");
}}
function exportarFornSitPDF() {{
  const {{ jsPDF }} = window.jspdf;
  const doc = new jsPDF({{ orientation: "landscape", unit: "mm", format: "a4" }});

  // Cabeçalho
  doc.setFontSize(14);
  doc.setTextColor(14, 143, 163);
  doc.text("Situacao Documental da Empresa — Zurich Airport", 14, 14);
  doc.setFontSize(9);
  doc.setTextColor(120);
  doc.text("Gerado em: " + new Date().toLocaleString("pt-BR"), 14, 20);

  // Filtro ativo
  const fsLblEl = document.getElementById("fs-emp-lbl");
  const fornLabel = (fsLblEl && fsLblEl.textContent !== "Todos")
    ? "Fornecedor(es): " + fsLblEl.textContent : "Todos os fornecedores";
  doc.setFontSize(9);
  doc.setTextColor(80);
  doc.text(fornLabel, 14, 25);

  // KPI cards — lê valores atuais do DOM (respeitam filtro ativo)
  const kpiLabels = [
    "% Nao Conf.", "% Conf.", "Docs Aprovados", "Docs Reprovados",
    "Nao Analisado", "Fornecedores"
  ];
  const kpiIds = [
    "r4-kpi-nc", "r4-kpi-c", "r4-kpi-aprov", "r4-kpi-reprov",
    "r4-kpi-nao-anal", "r4-kpi-forn"
  ];
  const kpiVals = kpiIds.map(id => document.getElementById(id)?.textContent?.trim() || "—");

  doc.autoTable({{
    head: [kpiLabels],
    body: [kpiVals],
    startY: 29,
    styles: {{ fontSize: 9, cellPadding: 4, halign: "center", fontStyle: "bold" }},
    headStyles: {{ fillColor: [10, 106, 122], textColor: 255, fontStyle: "bold", halign: "center", fontSize: 8 }},
    bodyStyles: {{ fontSize: 12, fontStyle: "bold", halign: "center" }},
    columnStyles: {{
      0: {{ textColor: [220, 53, 69] }},
      1: {{ textColor: [40, 167, 69] }},
      2: {{ textColor: [40, 167, 69] }},
      3: {{ textColor: [220, 53, 69] }},
      4: {{ textColor: [244, 121, 59] }},
      5: {{ textColor: [14, 143, 163] }}
    }},
    margin: {{ left: 10, right: 10 }},
  }});

  // Linha separadora visual
  const y1 = doc.lastAutoTable.finalY + 5;
  doc.setDrawColor(14, 143, 163);
  doc.setLineWidth(0.5);
  doc.line(10, y1, 287, y1);

  // Tabela de dados
  const headers = ["Fornecedor", "Documento", "Status", "Vencimento"];
  doc.autoTable({{
    head: [headers],
    body: fornSitFiltrado.map(r => headers.map(h => String(r[h] ?? ""))),
    startY: y1 + 3,
    styles: {{ font: "helvetica", fontSize: 8, cellPadding: 2 }},
    headStyles: {{ fillColor: [14, 143, 163], textColor: 255, fontStyle: "bold" }},
    alternateRowStyles: {{ fillColor: [240, 248, 250] }},
    margin: {{ left: 10, right: 10 }},
    didParseCell: function(data) {{
      if (data.section === "body" && data.column.index === 2) {{
        const v = String(data.cell.raw || "");
        if (v === "Aprovado")           data.cell.styles.textColor = [40, 167, 69];
        else if (v === "Reprovado")     data.cell.styles.textColor = [220, 53, 69];
        else if (v === "Vencido")       data.cell.styles.textColor = [220, 53, 69];
        else if (v === "Não anexado")   data.cell.styles.textColor = [133, 100, 4];
        else if (v === "A vencer")      data.cell.styles.textColor = [40, 167, 69];
      }}
    }}
  }});

  doc.save("situacao_empresa_zurich.pdf");
}}
function exportarFornSitCSV() {{
  downloadCSV(fornSitFiltrado, ["Fornecedor","CNPJ","Documento","Competencia","Status","Vencimento"], "situacao_empresa_zurich.csv");
}}

// ── EXPORTAR CSV ──────────────────────────────────────────────────────────────
function csvEscape(v) {{
  const s = String(v ?? "");
  return s.includes(",") || s.includes('"') || s.includes("\\n") ? '"' + s.replace(/"/g, '""') + '"' : s;
}}
function downloadCSV(rows, headers, filename) {{
  const lines = [headers.join(","), ...rows.map(r => headers.map(h => csvEscape(r[h])).join(","))];
  const blob = new Blob([lines.join("\\n")], {{type: "text/csv;charset=utf-8;"}});
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a"); a.href = url; a.download = filename;
  a.click(); URL.revokeObjectURL(url);
}}
function exportarSit() {{
  downloadCSV(sitFiltrado, ["Fornecedor","Terceiro","Documento","Competencia","Status","Vencimento"],
    "situacao_documental_zurich.csv");
}}
function exportarPend() {{
  downloadCSV(pendFiltrado, ["Fornecedor","CNPJ","Area","Documento","Competencia","Detalhe"],
    "pendencias_zurich.csv");
}}

// ── EXPORTAR EXCEL ────────────────────────────────────────────────────────────
function downloadXLSX(rows, headers, filename) {{
  const wsData = [headers, ...rows.map(r => headers.map(h => r[h] ?? ""))];
  const wb = XLSX.utils.book_new();
  const ws = XLSX.utils.aoa_to_sheet(wsData);
  const colWidths = headers.map(h => ({{wch: Math.max(h.length, 18)}}) );
  ws["!cols"] = colWidths;
  XLSX.utils.book_append_sheet(wb, ws, "Dados");
  XLSX.writeFile(wb, filename);
}}
function exportarSitXLSX() {{
  downloadXLSX(sitFiltrado, ["Fornecedor","Terceiro","Documento","Competencia","Status","Vencimento"],
    "situacao_documental_zurich.xlsx");
}}
function exportarPendXLSX() {{
  downloadXLSX(pendFiltrado, ["Fornecedor","CNPJ","Area","Documento","Competencia","Detalhe"],
    "pendencias_zurich.xlsx");
}}

// ── EXPORTAR PDF ──────────────────────────────────────────────────────────────
function downloadPDF(rows, headers, filename, title) {{
  const {{ jsPDF }} = window.jspdf;
  const doc = new jsPDF({{ orientation: "landscape", unit: "mm", format: "a4" }});
  doc.setFontSize(13);
  doc.setTextColor(14, 143, 163);
  doc.text(title, 14, 14);
  doc.setFontSize(9);
  doc.setTextColor(100);
  doc.text("Gerado em: " + new Date().toLocaleString("pt-BR"), 14, 20);
  doc.autoTable({{
    head: [headers],
    body: rows.map(r => headers.map(h => String(r[h] ?? ""))),
    startY: 25,
    styles: {{ font: "helvetica", fontSize: 8, cellPadding: 2 }},
    headStyles: {{ fillColor: [14, 143, 163], textColor: 255, fontStyle: "bold" }},
    alternateRowStyles: {{ fillColor: [240, 248, 250] }},
    margin: {{ left: 10, right: 10 }},
  }});
  doc.save(filename);
}}
function exportarSitPDF() {{
  const {{ jsPDF }} = window.jspdf;
  const doc = new jsPDF({{ orientation: "landscape", unit: "mm", format: "a4" }});

  // Cabeçalho
  doc.setFontSize(14);
  doc.setTextColor(14, 143, 163);
  doc.text("Situação Documental por Terceiro — Zurich Airport", 14, 14);
  doc.setFontSize(9);
  doc.setTextColor(120);
  doc.text("Gerado em: " + new Date().toLocaleString("pt-BR"), 14, 20);

  // Filtro ativo
  const sitLblEl = document.getElementById("sit-emp-lbl");
  const empLabel = (sitLblEl && sitLblEl.textContent !== "Todos")
    ? "Fornecedor(es): " + sitLblEl.textContent : "Todos os fornecedores";
  doc.setFontSize(9);
  doc.setTextColor(80);
  doc.text(empLabel, 14, 25);

  // KPI summary — lê valores atuais do DOM (respeitam filtro ativo)
  const kpiLabels = ["% Nao Conf.", "% Conforme", "Aprovados", "Reprovados", "Nao Anexado", "Ag. Submissão", "Em Análise", "Terceiros"];
  const kpiIds    = ["sit-kpi-nc", "sit-kpi-c", "sit-kpi-aprov", "sit-kpi-reprov", "sit-kpi-nao-anex", "sit-kpi-aguard-sub", "sit-kpi-aguard-real", "sit-kpi-terc"];
  const kpiVals   = kpiIds.map(id => document.getElementById(id)?.textContent?.trim() || "—");

  doc.autoTable({{
    head: [kpiLabels],
    body: [kpiVals],
    startY: 29,
    styles: {{ fontSize: 9, cellPadding: 4, halign: "center", fontStyle: "bold" }},
    headStyles: {{ fillColor: [10, 106, 122], textColor: 255, fontStyle: "bold", halign: "center", fontSize: 8 }},
    bodyStyles: {{ fontSize: 12, fontStyle: "bold", halign: "center" }},
    columnStyles: {{
      0: {{ textColor: [220, 53, 69] }},
      1: {{ textColor: [40, 167, 69] }},
      2: {{ textColor: [40, 167, 69] }},
      3: {{ textColor: [220, 53, 69] }},
      4: {{ textColor: [133, 100, 4] }},
      5: {{ textColor: [244, 121, 59] }},
      6: {{ textColor: [14, 143, 163] }}
    }},
    margin: {{ left: 10, right: 10 }},
  }});

  // Linha separadora
  const y1 = doc.lastAutoTable.finalY + 5;
  doc.setDrawColor(14, 143, 163);
  doc.setLineWidth(0.5);
  doc.line(10, y1, 287, y1);

  // Tabela de dados
  const headers = ["Fornecedor", "Terceiro", "Documento", "Status", "Competencia", "Vencimento"];
  doc.autoTable({{
    head: [headers],
    body: sitFiltrado.map(r => headers.map(h => String(r[h] ?? ""))),
    startY: y1 + 3,
    styles: {{ font: "helvetica", fontSize: 8, cellPadding: 2 }},
    headStyles: {{ fillColor: [14, 143, 163], textColor: 255, fontStyle: "bold" }},
    alternateRowStyles: {{ fillColor: [240, 248, 250] }},
    margin: {{ left: 10, right: 10 }},
    didParseCell: function(data) {{
      if (data.section === "body" && data.column.index === 3) {{
        const v = String(data.cell.raw || "");
        if (v === "Aprovado")                  data.cell.styles.textColor = [40, 167, 69];
        else if (v === "Reprovado")            data.cell.styles.textColor = [220, 53, 69];
        else if (v === "Não anexado")          data.cell.styles.textColor = [133, 100, 4];
        else if (v === "Aguardando Submissão") data.cell.styles.textColor = [133, 100, 4];
        else if (v === "Em Análise")           data.cell.styles.textColor = [14, 143, 163];
      }}
    }}
  }});

  doc.save("situacao_documental_zurich.pdf");
}}
function exportarPendPDF() {{
  downloadPDF(pendFiltrado, ["Fornecedor","CNPJ","Area","Documento","Competencia","Detalhe"],
    "pendencias_zurich.pdf", "Detalhamento de Pendências — Zurich Airport");
}}

// ── MODO AGRUPADO ─────────────────────────────────────────────────────────────
let modoAgrupado = false;
function toggleModoAgrupado() {{
  modoAgrupado = !modoAgrupado;
  document.getElementById("btn-modo-sit").textContent = modoAgrupado ? "Modo Linha" : "Modo Agrupado";
  document.getElementById("sit-modo-linha").style.display    = modoAgrupado ? "none"  : "block";
  document.getElementById("sit-modo-agrupado").style.display = modoAgrupado ? "block" : "none";
  if (modoAgrupado) renderSitAgrupado(sitFiltrado);
}}
function renderSitAgrupado(dados) {{
  const grupos = {{}};
  dados.forEach(r => {{
    const key = r["Fornecedor"] + "|||" + r["Terceiro"];
    if (!grupos[key]) grupos[key] = {{ fornecedor: r["Fornecedor"], terceiro: r["Terceiro"], docs: [], temNC: false }};
    grupos[key].docs.push(r);
    if (r["Status"] !== "Conforme") grupos[key].temNC = true;
  }});
  const corSit = {{ "Conforme": {{bg:"#d4edda",fg:"#155724"}}, "Vencido": {{bg:"#ffeaea",fg:"#721c24"}}, "Pendente": {{bg:"#fff3cd",fg:"#856404"}} }};
  const html = Object.values(grupos).map(g => {{
    const docsHtml = g.docs.map(d => {{
      const c = corSit[d["Status"]] || {{bg:"#eee",fg:"#333"}};
      const venc = d["Vencimento"] ? ` <span class="grupo-doc-venc">(${{d["Vencimento"]}})</span>` : "";
      return `<span class="grupo-doc-badge" style="background:${{c.bg}};color:${{c.fg}}">${{d["Documento"]}}${{venc}}</span>`;
    }}).join("");
    return `<div class="grupo-card${{g.temNC ? " nc" : ""}}">
      <div class="grupo-header">
        <div>
          <div class="grupo-fornecedor">${{g.fornecedor}}</div>
          <div class="grupo-nome">${{g.terceiro}}</div>
        </div>
        <div style="font-size:11px;color:#999">${{g.docs.length}} doc(s)</div>
      </div>
      <div class="grupo-docs">${{docsHtml}}</div>
    </div>`;
  }}).join("");
  document.getElementById("sit-grupos").innerHTML = html || '<p style="color:#aaa;text-align:center;padding:24px">Nenhum resultado</p>';
}}

// ── DRILL-DOWN ────────────────────────────────────────────────────────────────
const drillData = {{}};
SIT.forEach(r => {{
  const f = r["Fornecedor"], t = r["Terceiro"];
  if (!drillData[f]) drillData[f] = {{}};
  if (!drillData[f][t]) drillData[f][t] = [];
  drillData[f][t].push({{ doc: r["Documento"], status: r["Status"], venc: r["Vencimento"] }});
}});

const fornStats = {{}};
Object.keys(drillData).forEach(f => {{
  let conf=0, venc=0, pend=0;
  Object.values(drillData[f]).forEach(docs => docs.forEach(d => {{
    if (d.status==="Aprovado") conf++;
    else if (d.status==="Reprovado") venc++;
    else pend++;
  }}));
  const total = conf+venc+pend;
  const pctC = total>0 ? Math.round(conf/total*100) : 0;
  fornStats[f] = {{conf, venc, pend, total, pctC,
                   trabCount: Object.keys(drillData[f]).length}};
}});

function corC(pct) {{ return pct>=70 ? "#28A745" : pct>=40 ? "#FFC107" : "#DC3545"; }}

function showLevel(n) {{
  [1,2,3].forEach(i => document.getElementById("drill-level"+i).style.display = i===n ? "block" : "none");
}}

function renderLevel1() {{
  showLevel(1);
  let keys = Object.keys(fornStats).sort((a,b) => fornStats[a].pctC - fornStats[b].pctC);
  if (selectedFornSet.size > 0) {{
    const nomes = new Set([...selectedFornSet].map(r => parseFornVal(r).nome));
    keys = keys.filter(f => nomes.has(f));
  }}
  document.getElementById("supplier-cards").innerHTML = keys.map(f => {{
    const s = fornStats[f];
    const cor = corC(s.pctC);
    const pConf = s.total>0 ? (s.conf/s.total*100).toFixed(1) : 0;
    const pVenc = s.total>0 ? (s.venc/s.total*100).toFixed(1) : 0;
    const pPend = s.total>0 ? (s.pend/s.total*100).toFixed(1) : 0;
    return `<div class="drill-card" data-forn="${{encodeURIComponent(f)}}" onclick="renderLevel2(decodeURIComponent(this.dataset.forn))">
      <div class="drill-card-pct" style="color:${{cor}}">${{s.pctC}}%</div>
      <div class="drill-card-label">conforme</div>
      <div class="drill-card-name">${{f}}</div>
      <div class="drill-card-meta">${{s.trabCount}} terceiros &middot; ${{s.total}} docs</div>
      <div class="drill-card-bars">
        <span class="mini-bar" style="background:#28A745;width:${{pConf}}%" title="Conforme: ${{s.conf}}"></span>
        <span class="mini-bar" style="background:#FFC107;width:${{pPend}}%" title="Pendente: ${{s.pend}}"></span>
        <span class="mini-bar" style="background:#DC3545;width:${{pVenc}}%" title="Vencido: ${{s.venc}}"></span>
      </div>
    </div>`;
  }}).join("");
}}

function renderLevel2(forn) {{
  showLevel(2);
  document.getElementById("breadcrumb2").innerHTML =
    `<span class="drill-back" onclick="renderLevel1()">← Todos os fornecedores</span>
     <span class="drill-crumb-sep">›</span>
     <span class="drill-crumb-current">${{forn}}</span>`;

  const workers = Object.keys(drillData[forn] || {{}}).sort();
  document.getElementById("worker-list").innerHTML = workers.map(t => {{
    const docs = drillData[forn][t];
    const conf = docs.filter(d=>d.status==="Aprovado").length;
    const venc = docs.filter(d=>d.status==="Reprovado").length;
    const pend = docs.filter(d=>d.status==="Não anexado"||d.status==="Aguardando Submissão"||d.status==="Em Análise").length;
    const arrowCor = venc>0 ? "#DC3545" : pend>0 ? "#FFC107" : "#28A745";
    return `<div class="drill-worker" data-forn="${{encodeURIComponent(forn)}}" data-trab="${{encodeURIComponent(t)}}"
               onclick="renderLevel3(decodeURIComponent(this.dataset.forn), decodeURIComponent(this.dataset.trab))">
      <div class="drill-worker-name">${{t}}</div>
      <div class="drill-worker-badges">
        ${{conf>0 ? `<span class="badge badge-conforme">${{conf}} conforme</span>` : ""}}
        ${{venc>0 ? `<span class="badge badge-vencido">${{venc}} vencido</span>` : ""}}
        ${{pend>0 ? `<span class="badge badge-pendente">${{pend}} pendente</span>` : ""}}
      </div>
      <div class="drill-worker-arrow" style="color:${{arrowCor}}">›</div>
    </div>`;
  }}).join("");
}}

function renderLevel3(forn, trab) {{
  showLevel(3);
  document.getElementById("breadcrumb3").innerHTML =
    `<span class="drill-back" data-forn="${{encodeURIComponent(forn)}}"
        onclick="renderLevel2(decodeURIComponent(this.dataset.forn))">← ${{forn}}</span>
     <span class="drill-crumb-sep">›</span>
     <span class="drill-crumb-current">${{trab}}</span>`;

  const docs = (drillData[forn] || {{}})[trab] || [];
  document.getElementById("doc-list").innerHTML = docs.map(d => {{
    const cls = d.status==="Aprovado" ? "badge-conforme" : d.status==="Reprovado" ? "badge-vencido" : "badge-pendente";
    return `<div class="drill-doc">
      <div class="drill-doc-name">${{d.doc}}</div>
      <span class="badge ${{cls}}">${{d.status}}</span>
      <div class="drill-doc-venc">${{d.venc || "—"}}</div>
    </div>`;
  }}).join("") || '<div class="drill-hint">Nenhum documento encontrado</div>';
}}

renderLevel1();

// ── CONTRATOS DRILL-DOWN ──────────────────────────────────────────────────────
let ctFornAtual = null;
let ctContratosAtual = [];
let ctContratosVisiveis = new Set(); // chips selecionados (vazio = todos)

function ctShowLevel(n) {{
  [1,2,3].forEach(i => document.getElementById("ct-level"+i).style.display = i===n ? "block" : "none");
}}

function ctRenderL1() {{
  const qForn = (document.getElementById("ct-search")?.value || "").toLowerCase().trim();
  const qCont = (document.getElementById("ct-search-cont")?.value || "").toLowerCase().trim();
  let lista = CONTRATOS;
  // Filtro fornecedor — busca em nome, nome_full e CNPJ (dígitos)
  if (qForn) {{
    const qDigits = qForn.replace(/\D/g, "");
    lista = lista.filter(f =>
      f.nome.toLowerCase().includes(qForn) ||
      f.nome_full.toLowerCase().includes(qForn) ||
      (qDigits && f.cnpj && f.cnpj.includes(qDigits))
    );
  }}
  // Filtro contrato — busca nos códigos de contrato do fornecedor
  if (qCont) {{
    lista = lista.filter(f => {{
      const allCt = [...new Set([...f.contratos, ...Object.keys(f.terceiros_by_contract)])];
      return allCt.some(c => c.toLowerCase().includes(qCont));
    }});
  }}
  if (selectedFornSet.size > 0) {{
    const nomes = new Set([...selectedFornSet].map(r => parseFornVal(r).nome));
    lista = lista.filter(f => nomes.has(f.nome) || nomes.has(f.nome_full));
  }}
  if (gfAeroportoSet.size > 0) {{
    lista = lista.filter(f =>
      Object.values(f.terceiros_by_contract).some(tercs =>
        tercs.some(t => gfAeroportoSet.has((t.aeroporto || '').toUpperCase().trim()))
      )
    );
  }}
  if (gfStatusTerc !== 'all') {{
    lista = lista.filter(f =>
      Object.values(f.terceiros_by_contract).some(tercs =>
        tercs.some(t => t.status === gfStatusTerc)
      )
    );
  }}
  document.getElementById("ct-l1-count").textContent = lista.length + " fornecedor(es)";
  document.getElementById("ct-cards").innerHTML = lista.map(f => {{
    // Usa a mesma união que o L2 — contratos do CSV + contratos com terceiros vinculados
    const allCt  = [...new Set([...f.contratos, ...Object.keys(f.terceiros_by_contract)])].sort();
    const nContr = allCt.length;
    const nTerc  = Object.values(f.terceiros_by_contract).reduce((a,b)=>a+b.length,0);
    const preview = allCt.slice(0,3);
    const more    = nContr > 3 ? ` <span style="color:#999;font-size:10px">+${{nContr-3}}</span>` : "";
    return `<div class="ct-card" onclick="ctRenderL2('${{encodeURIComponent(f.cnpj)}}')">
      <div class="ct-card-name">${{f.nome}}</div>
      ${{f.cnpj ? '<div style="font-size:11px;color:#999;font-family:monospace;margin:-2px 0 4px">' + fmtDoc(f.cnpj) + '</div>' : ''}}
      <div class="ct-card-codes">
        ${{preview.map(c=>`<span class="ct-code-chip" title="${{c}}">${{c}}</span>`).join("")}}${{more}}
        ${{nContr===0 ? '<span style="color:#bbb;font-size:11px">Sem contratos</span>' : ""}}
      </div>
      <div class="ct-card-meta">${{nContr}} contrato(s) &middot; ${{nTerc}} terceiro(s)</div>
    </div>`;
  }}).join("") || '<div class="drill-hint">Nenhum fornecedor encontrado</div>';
}}

function ctClearSearch() {{
  const s = document.getElementById("ct-search");
  const sc = document.getElementById("ct-search-cont");
  if (s) s.value = "";
  if (sc) sc.value = "";
  ctRenderL1();
}}

function ctRenderL2(cnpjEnc) {{
  ctShowLevel(2);
  const cnpj = decodeURIComponent(cnpjEnc);
  ctFornAtual = CONTRATOS.find(f => f.cnpj === cnpj) || null;
  if (!ctFornAtual) return;

  document.getElementById("ct-breadcrumb2").innerHTML =
    `<span class="drill-back" onclick="ctBackToL1()">← Fornecedores</span>
     <span class="drill-crumb-sep">›</span>
     <span class="drill-crumb-current">${{ctFornAtual.nome}}</span>`;

  // Monta lista de contratos únicos (do campo contratos + chaves de terceiros_by_contract)
  const ctSet = new Set([...ctFornAtual.contratos,
                          ...Object.keys(ctFornAtual.terceiros_by_contract)]);
  ctContratosAtual = [...ctSet].sort();
  ctContratosVisiveis = new Set();

  // Chips (só exibe quando >1 contrato)
  const chipDiv = document.getElementById("ct-chip-filter");
  if (ctContratosAtual.length > 1) {{
    chipDiv.innerHTML = ctContratosAtual.map(c =>
      `<span class="ct-chip" data-ct="${{encodeURIComponent(c)}}" onclick="ctToggleChip(this)">${{c}}</span>`
    ).join("");
  }} else {{
    chipDiv.innerHTML = "";
  }}

  ctRenderContratos();
}}

function ctToggleChip(el) {{
  const ct = decodeURIComponent(el.dataset.ct);
  if (ctContratosVisiveis.has(ct)) {{ ctContratosVisiveis.delete(ct); el.classList.remove("selected"); }}
  else {{ ctContratosVisiveis.add(ct); el.classList.add("selected"); }}
  ctRenderContratos();
}}

function ctRenderContratos() {{
  if (!ctFornAtual) return;
  const visivel = ctContratosVisiveis.size === 0
    ? ctContratosAtual
    : ctContratosAtual.filter(c => ctContratosVisiveis.has(c));
  document.getElementById("ct-contract-list").innerHTML = visivel.map(c => {{
    const tercs = ctFornAtual.terceiros_by_contract[c] || [];
    const ativos = tercs.filter(t => t.status === "Ativo").length;
    const aerops = [...new Set(tercs.map(t=>t.aeroporto).filter(Boolean))].join(", ") || "—";
    return `<div class="ct-contract-row" onclick="ctRenderL3('${{encodeURIComponent(c)}}')">
      <div class="ct-contract-code">${{c}}</div>
      <div class="ct-contract-meta">${{tercs.length}} terceiro(s) &middot; ${{ativos}} ativo(s) &middot; ${{aerops}}</div>
      <div class="ct-contract-arrow">›</div>
    </div>`;
  }}).join("") || '<div class="drill-hint">Nenhum contrato</div>';
}}

function ctRenderL3(ctEnc) {{
  ctShowLevel(3);
  const ct = decodeURIComponent(ctEnc);
  if (!ctFornAtual) return;
  const tercsAll = ctFornAtual.terceiros_by_contract[ct] || [];
  const tercs = tercsAll.filter(t => {{
    if (gfStatusTerc !== 'all' && t.status !== gfStatusTerc) return false;
    if (gfAeroportoSet.size > 0 && !gfAeroportoSet.has((t.aeroporto || '').toUpperCase().trim())) return false;
    return true;
  }});

  document.getElementById("ct-breadcrumb3").innerHTML =
    `<span class="drill-back" onclick="ctShowLevel(2)">← ${{ctFornAtual.nome}}</span>
     <span class="drill-crumb-sep">›</span>
     <span class="drill-crumb-current">${{ct}}</span>`;

  document.getElementById("ct-terc-body").innerHTML = tercs.map(t => {{
    const badgeCls = t.status === "Ativo" ? "badge-conforme" : "badge-nao-enviado";
    return `<tr>
      <td>${{t.nome || "—"}}</td>
      <td style="font-family:monospace;font-size:12px">${{fmtDoc(t.cnpj) || "—"}}</td>
      <td>${{t.cargo || "—"}}</td>
      <td>${{t.aeroporto || "—"}}</td>
      <td><span class="badge ${{badgeCls}}">${{t.status || "—"}}</span></td>
    </tr>`;
  }}).join("") || '<tr><td colspan="5" style="text-align:center;color:#aaa">Nenhum terceiro</td></tr>';

  // guarda para export
  window._ctL3Current = {{ contrato: ct, dados: tercs }};
}}

function ctBackToL1() {{
  ctShowLevel(1);
  ctRenderL1();
}}

// Exportações L2 — listagem de terceiros do fornecedor (todos os contratos visíveis)
function _ctL2TercRows() {{
  const visivel = ctContratosVisiveis.size === 0
    ? ctContratosAtual
    : ctContratosAtual.filter(c => ctContratosVisiveis.has(c));
  const rows = [];
  visivel.forEach(c => {{
    const ts = ctFornAtual.terceiros_by_contract[c] || [];
    ts.forEach(t => rows.push({{
      Contrato: c, Aeroporto: t.aeroporto || "", Nome: t.nome || "",
      "CPF/CNPJ": t.cnpj || "", Cargo: t.cargo || "", Status: t.status || ""
    }}));
  }});
  return {{ rows, nContratos: visivel.length, nTerceiros: rows.length }};
}}
function ctExportL2XLSX() {{
  const {{ rows }} = _ctL2TercRows();
  downloadXLSX(rows, ["Contrato","Aeroporto","Nome","CPF/CNPJ","Cargo","Status"],
    "terceiros_" + (ctFornAtual?.nome||"") + ".xlsx");
}}
function ctExportL2CSV() {{
  const {{ rows }} = _ctL2TercRows();
  downloadCSV(rows, ["Contrato","Aeroporto","Nome","CPF/CNPJ","Cargo","Status"],
    "terceiros_" + (ctFornAtual?.nome||"") + ".csv");
}}
function ctExportL2PDF() {{
  const {{ rows, nContratos, nTerceiros }} = _ctL2TercRows();
  const fornNome = ctFornAtual?.nome || "";
  const {{ jsPDF }} = window.jspdf;
  const doc = new jsPDF({{ orientation: "landscape", unit: "mm", format: "a4" }});
  const W = doc.internal.pageSize.getWidth();
  doc.setFontSize(13); doc.setTextColor(14, 143, 163);
  doc.text("Terceiros — " + fornNome, 14, 14);
  doc.setFontSize(10); doc.setTextColor(80);
  doc.text(nContratos + " contratos · " + nTerceiros + " terceiros", W - 14, 14, {{ align: "right" }});
  doc.setFontSize(9); doc.setTextColor(120);
  doc.text("Gerado em: " + new Date().toLocaleString("pt-BR"), 14, 20);
  const hs = ["Contrato","Aeroporto","Nome","CPF/CNPJ","Cargo","Status"];
  doc.autoTable({{
    head: [hs],
    body: rows.map(r => hs.map(h => r[h] || "")),
    startY: 25,
    styles: {{ fontSize: 8, cellPadding: 2.5 }},
    headStyles: {{ fillColor: [14, 143, 163], textColor: 255, fontStyle: "bold" }},
    alternateRowStyles: {{ fillColor: [245, 252, 253] }},
    columnStyles: {{
      0: {{ cellWidth: 30 }},
      1: {{ cellWidth: 18 }},
      2: {{ cellWidth: 72 }},
      3: {{ cellWidth: 30 }},
      4: {{ cellWidth: 55 }},
      5: {{ cellWidth: 18 }}
    }},
    didParseCell(data) {{
      if (data.section === "body" && data.column.index === 5) {{
        const v = String(data.cell.raw || "");
        if (v === "Ativo") data.cell.styles.textColor = [5, 150, 105];
        else               data.cell.styles.textColor = [180, 40, 40];
      }}
    }}
  }});
  doc.save("terceiros_" + fornNome + ".pdf");
}}

// Exportações L3 (terceiros do contrato)
function _ctL3Rows() {{
  const d = window._ctL3Current;
  if (!d) return [];
  return d.dados.map(t => ({{ Fornecedor: ctFornAtual?.nome||"", Contrato: d.contrato,
    Nome: t.nome, "CPF/CNPJ": t.cnpj, Cargo: t.cargo, Aeroporto: t.aeroporto, Status: t.status }}));
}}
function ctExportL3XLSX() {{
  downloadXLSX(_ctL3Rows(), ["Fornecedor","Contrato","Nome","CPF/CNPJ","Cargo","Aeroporto","Status"],
    "terceiros_contrato.xlsx");
}}
function ctExportL3CSV() {{
  downloadCSV(_ctL3Rows(), ["Fornecedor","Contrato","Nome","CPF/CNPJ","Cargo","Aeroporto","Status"],
    "terceiros_contrato.csv");
}}
function ctExportL3PDF() {{
  downloadPDF(_ctL3Rows(), ["Fornecedor","Contrato","Nome","CPF/CNPJ","Cargo","Aeroporto","Status"],
    "terceiros_contrato.pdf", "Terceiros por Contrato — Zurich Airport");
}}

// Init L1
ctRenderL1();

// ── TOGGLE SECOES ─────────────────────────────────────────────────────────────
function toggleSection(id, btn) {{
  const el = document.getElementById(id);
  const isCollapsed = el.classList.toggle('collapsed');
  btn.textContent = isCollapsed ? '▼ Expandir' : '▲ Recolher';
}}

// ── EXPORTAÇÃO GLOBAL ─────────────────────────────────────────────────────────
function _filtroAtivоLabel() {{
  const fCount = selectedFornSet.size;
  const cCount = selectedCompSet.size;
  const parts = [];
  if (fCount > 0) parts.push(fCount <= 2 ? [...selectedFornSet].map(r => parseFornVal(r).nome).join(", ") : fCount + " fornecedores");
  if (cCount > 0) parts.push(cCount <= 2 ? [...selectedCompSet].join(", ") : cCount + " competências");
  return parts.length ? "Filtro: " + parts.join(" · ") : "Todos os fornecedores e competências";
}}

function exportarRelatorioXLSX() {{
  const wb = XLSX.utils.book_new();

  const hdR3 = ["Fornecedor", "Terceiro", "Documento", "Competencia", "Status", "Vencimento"];
  const wsR3Data = [hdR3, ...sitFiltrado.map(r => hdR3.map(h => r[h] ?? ""))];
  const wsR3 = XLSX.utils.aoa_to_sheet(wsR3Data);
  wsR3["!cols"] = hdR3.map(h => ({{wch: Math.max(h.length, 18)}}));
  XLSX.utils.book_append_sheet(wb, wsR3, "R3 - Terceiros");

  const hdR4 = ["Fornecedor", "Documento", "Competencia", "Status", "Vencimento"];
  const wsR4Data = [hdR4, ...fornSitFiltrado.map(r => hdR4.map(h => r[h] ?? ""))];
  const wsR4 = XLSX.utils.aoa_to_sheet(wsR4Data);
  wsR4["!cols"] = hdR4.map(h => ({{wch: Math.max(h.length, 18)}}));
  XLSX.utils.book_append_sheet(wb, wsR4, "R4 - Empresa");

  const hdPend = ["Fornecedor", "CNPJ", "Area", "Documento", "Competencia", "Detalhe"];
  const wsPendData = [hdPend, ...pendFiltrado.map(r => hdPend.map(h => r[h] ?? ""))];
  const wsPend = XLSX.utils.aoa_to_sheet(wsPendData);
  wsPend["!cols"] = hdPend.map(h => ({{wch: Math.max(h.length, 18)}}));
  XLSX.utils.book_append_sheet(wb, wsPend, "Pendencias");

  XLSX.writeFile(wb, "relatorio_zurich.xlsx");
}}

function exportarRelatorioPDF() {{
  const {{ jsPDF }} = window.jspdf;
  const doc = new jsPDF({{ orientation: "landscape", unit: "mm", format: "a4" }});
  const filtroLabel = _filtroAtivоLabel();
  let y = 14;

  const _titulo = (txt) => {{
    doc.setFontSize(13); doc.setTextColor(14, 143, 163);
    doc.text(txt, 14, y); y += 7;
    doc.setFontSize(8); doc.setTextColor(100);
    doc.text(filtroLabel, 14, y); y += 6;
  }};

  _titulo("R3 — Situação Documental dos Terceiros");
  const hdR3 = ["Fornecedor", "Terceiro", "Documento", "Competencia", "Status", "Vencimento"];
  doc.autoTable({{
    head: [hdR3],
    body: sitFiltrado.map(r => hdR3.map(h => String(r[h] ?? ""))),
    startY: y, styles: {{ font: "helvetica", fontSize: 7, cellPadding: 2 }},
    headStyles: {{ fillColor: [14, 143, 163], textColor: 255, fontStyle: "bold" }},
    alternateRowStyles: {{ fillColor: [240, 248, 250] }},
    margin: {{ left: 10, right: 10 }},
  }});
  y = doc.lastAutoTable.finalY + 10;

  if (y > 175) {{ doc.addPage(); y = 14; }}
  _titulo("R4 — Situação Documental da Empresa");
  const hdR4 = ["Fornecedor", "CNPJ", "Documento", "Competencia", "Status", "Vencimento"];
  doc.autoTable({{
    head: [hdR4],
    body: fornSitFiltrado.map(r => hdR4.map(h => String(r[h] ?? ""))),
    startY: y, styles: {{ font: "helvetica", fontSize: 7, cellPadding: 2 }},
    headStyles: {{ fillColor: [14, 143, 163], textColor: 255, fontStyle: "bold" }},
    alternateRowStyles: {{ fillColor: [240, 248, 250] }},
    margin: {{ left: 10, right: 10 }},
  }});
  y = doc.lastAutoTable.finalY + 10;

  if (y > 175) {{ doc.addPage(); y = 14; }}
  _titulo("Pendências");
  const hdPend = ["Fornecedor", "CNPJ", "Area", "Documento", "Competencia", "Detalhe"];
  doc.autoTable({{
    head: [hdPend],
    body: pendFiltrado.map(r => hdPend.map(h => String(r[h] ?? ""))),
    startY: y, styles: {{ font: "helvetica", fontSize: 7, cellPadding: 2 }},
    headStyles: {{ fillColor: [14, 143, 163], textColor: 255, fontStyle: "bold" }},
    alternateRowStyles: {{ fillColor: [240, 248, 250] }},
    margin: {{ left: 10, right: 10 }},
  }});

  doc.save("relatorio_zurich.pdf");
}}

function exportarRelatorioCSV() {{
  const hdR3  = ["Secao","Fornecedor","CNPJ","Terceiro","Documento","Competencia","Status","Vencimento"];
  const rows = [
    hdR3,
    ...sitFiltrado.map(r    => ["R3-Terceiros",  r["Fornecedor"]||"", r["CNPJ_Forn"]||"", r["Terceiro"]||"",  r["Documento"]||"", r["Competencia"]||"", r["Status"]||"", r["Vencimento"]||""]),
    ...fornSitFiltrado.map(r=> ["R4-Empresa",    r["Fornecedor"]||"", r["CNPJ"]||"",       "",                 r["Documento"]||"", r["Competencia"]||"", r["Status"]||"", r["Vencimento"]||""]),
    ...pendFiltrado.map(r   => ["Pendencias",    r["Fornecedor"]||"", r["CNPJ"]||"",       "",                 r["Documento"]||"", r["Competencia"]||"", r["Status"]||"", r["Detalhe"]||""]),
  ];
  const lines = rows.map(r => r.map(v => csvEscape(v)).join(","));
  const blob = new Blob([lines.join("\\n")], {{type: "text/csv;charset=utf-8;"}});
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a"); a.href = url; a.download = "relatorio_zurich.csv";
  a.click(); URL.revokeObjectURL(url);
}}

// ── FILTRO GLOBAL ─────────────────────────────────────────────────────────────
function expandSection(id) {{
  const el = document.getElementById(id);
  if (!el) return;
  if (el.classList.contains("collapsed")) {{
    el.classList.remove("collapsed");
    const toggle = el.previousElementSibling ? el.previousElementSibling.querySelector(".section-toggle") : null;
    if (toggle) toggle.textContent = "▲ Recolher";
  }}
}}

function applyGlobalFilter() {{
  const fCount = selectedFornSet.size;
  const cCount = selectedCompSet.size;

  filtrarTabela();
  filtrarSit();
  filtrarFornSit();
  updateKPICards();
  renderLevel1();
  ctRenderL1();

  // Expande secoes quando filtro ativo
  if (fCount > 0 || cCount > 0) {{
    ["ct-section","drill-section","pend-section","sit-section","forn-sit-section"].forEach(expandSection);
  }}

  // Label do botao fornecedor
  const lbl = fCount === 0 ? "Todos os fornecedores"
    : fCount === 1 ? parseFornVal([...selectedFornSet][0]).nome
    : fCount + " fornecedores selecionados";
  document.getElementById("gf-selected-label").textContent = lbl;

  // Label do botao comp
  const compLbl = cCount === 0 ? "Todas as competências"
    : cCount === 1 ? [...selectedCompSet][0]
    : cCount + " competências selecionadas";
  document.getElementById("gfc-selected-label").textContent = compLbl;

  // Hint
  const parts = [];
  if (fCount > 0) parts.push(fCount <= 2 ? [...selectedFornSet].map(r => parseFornVal(r).nome).join(", ") : fCount + " fornecedores");
  if (cCount > 0) parts.push(cCount <= 2 ? [...selectedCompSet].join(", ") : cCount + " competências");
  if (gfAeroportoSet.size > 0) parts.push("aeroporto: " + [...gfAeroportoSet].join("+"));
  if (gfStatusTerc !== 'all') parts.push("terceiros: " + (gfStatusTerc === 'Ativo' ? 'Ativos' : 'Inativos'));
  document.getElementById("gf-hint").textContent = parts.length ? "Filtro ativo: " + parts.join(" · ") : "";

  // Cards globais somem com qualquer seleção
  const displayGlobal = (fCount > 0 || cCount > 0) ? "none" : "";
  ["kpi-card-total-forn","kpi-card-exec-plat"].forEach(id => {{
    const el = document.getElementById(id);
    if (el) el.style.display = displayGlobal;
  }});

  // Cards "docs esperados" somem quando filtro de competência ativo
  const displayEsp = cCount > 0 ? "none" : "";
  ["kpi-card-docs-esp-forn","kpi-card-docs-esp-terc"].forEach(id => {{
    const el = document.getElementById(id);
    if (el) el.style.display = displayEsp;
  }});
}}

function limparGlobalFiltro() {{
  selectedFornSet.clear();
  document.querySelectorAll("#gf-multi-list .gf-item").forEach(div => {{
    const cb = div.querySelector("input[type=checkbox]");
    if (cb) cb.checked = false;
    div.classList.remove("gf-selected");
  }});
  const search = document.getElementById("gf-multi-search");
  if (search) {{ search.value = ""; filterFornItems(""); }}
  limparCompFiltroSilent();
  gfAeroportoSet.clear();
  ['CAIF','VIX','MEA','CAIN'].forEach(a => {{
    const btn = document.getElementById('gf-aero-' + a);
    if (btn) {{ btn.style.background = 'rgba(255,255,255,.15)'; btn.style.color = 'white'; }}
  }});
  gfStatusTerc = 'all';
  ['all','ativo','inativo'].forEach(v => {{
    const btn = document.getElementById('gf-status-terc-' + v);
    if (btn) {{
      btn.style.background = v === 'all' ? 'white' : 'rgba(255,255,255,.15)';
      btn.style.color      = v === 'all' ? '{COR_TEAL_ESCURO}' : 'white';
    }}
  }});
  applyGlobalFilter();
}}

// ── INIT ──────────────────────────────────────────────────────────────────────
buildFornMultiSelect();
buildCompMultiSelect();
buildFsStatMultiSelect();

// ── TABELA SEM EXECUÇÃO ──────────────────────────────────────────────────────
(function() {{
  const tbody = document.getElementById("sem-exec-body");
  if (!tbody) return;
  SEM_EXEC.forEach(r => {{
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${{r["Razão Social"] || "—"}}</td><td style="font-family:monospace">${{r["CPF/CNPJ"] || "—"}}</td>`;
    tbody.appendChild(tr);
  }});
}})();

filtrarSit();
filtrarTabela();
filtrarFornSit();
renderPizza(SIT);
renderPizzaForn(FORN_SIT);
renderPizzaGeral(SIT, FORN_SIT);
</script>
</body>
</html>"""

with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Dashboard gerado: {OUTPUT_HTML}")
print(f"  Fornecedores com pendencias : {total_fornecedores}")
print(f"  Total pendencias            : {total_pendencias}")
print(f"  % Conformidade geral        : {pct_conformidade}%")
print(f"  % Nao conformidade          : {pct_nao_conform}%")
print(f"  Docs reprovados             : {total_reprovados_docs}")
print(f"  Docs pendentes              : {total_pendentes_docs}")
print(f"  Docs conformes              : {total_conformes}")
print(f"  Trabalhadores ativos        : {total_trab_ativo}")
print(f"  --- R4 Empresa ---")
print(f"  Fornecedores (R4)           : {r4_fornecedores}")
print(f"  % Nao conf empresa          : {r4_pct_nc}%")
print(f"  Docs em analise empresa     : {r4_em_analise}")
print(f"  Docs vencidos empresa       : {r4_vencido}")
