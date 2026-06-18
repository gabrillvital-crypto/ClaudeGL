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
FORNECEDORES_CSV   = BASE_DIR + r"\fornecedores_zurich.csv"
OUTPUT_HTML        = r"C:\Users\gabriel.evangelista\Documents\ClaudeGL\Dashboard\dashboard_zurich_airport.html"

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
            drop_cols = [c for c in df.columns if re.search(r'^contratos?$', c, re.I)]
            return df.drop(columns=drop_cols, errors="ignore")
        except Exception:
            continue
    raise RuntimeError(f"Nao foi possivel ler: {path}")

def abbrev(name, n=40):
    s = str(name).strip()
    short = re.sub(r'\s+(LTDA|LTDA\.|S/A|SA|EIRELI|ME|EPP).*', '', s, flags=re.I)
    return short[:n] + "..." if len(short) > n else short

df_pend    = read_csv_safe(PENDENCIAS_CSV)
df_terc    = read_csv_safe(TERCEIROS_CSV)
df_sit     = read_csv_safe(SITUACAO_CSV)
df_forn_cad = read_csv_safe(FORNECEDORES_CSV) if _os.path.exists(FORNECEDORES_CSV) else None

df_pend["Empresa"] = df_pend["Razao Social"].apply(abbrev) if "Razao Social" in df_pend.columns else df_pend["Razão Social"].apply(abbrev)
df_terc["Empresa"] = df_terc["Razao Social"].apply(abbrev) if "Razao Social" in df_terc.columns else df_terc["Razão Social"].apply(abbrev)
df_sit["Empresa"]  = df_sit["Fornecedor Razão Social"].apply(abbrev) if "Fornecedor Razão Social" in df_sit.columns else df_sit["Fornecedor Razao Social"].apply(abbrev)

# normalizar nome da coluna Razão Social para pendências
col_rs_pend = "Razão Social" if "Razão Social" in df_pend.columns else "Razao Social"
col_rs_terc = "Razão Social" if "Razão Social" in df_terc.columns else "Razao Social"

df_pend["Empresa"] = df_pend[col_rs_pend].apply(abbrev)
df_terc["Empresa"] = df_terc[col_rs_terc].apply(abbrev)

# ── TIPO DE DOCUMENTO ─────────────────────────────────────────────────────────
def extrair_doc(row):
    doc = str(row.get("Documento", "")).strip()
    if doc and doc != "nan":
        return doc.upper()
    pend = str(row.get("Pendencia", row.get("Pendência", "")))
    m = re.match(r"[A-Z\s]+ - ([^,]+)", pend)
    if m:
        return m.group(1).strip().upper()
    m2 = re.match(r"^([^,]+),", pend)
    if m2:
        return m2.group(1).strip().upper()
    return "OUTROS"

df_pend["Tipo_Doc"] = df_pend.apply(extrair_doc, axis=1)
df_pend["Tipo_Doc"] = df_pend["Tipo_Doc"].str[:50]

# ── CONFORMIDADE — STATUS 3 CAMADAS ───────────────────────────────────────────
# Status no CSV: "A vencer" = Conforme | "Vencido" = Vencido | "Não anexado" = Pendente | "N/A" = ignorar
STATUS_MAP = {"A vencer": "Conforme", "Vencido": "Vencido", "Não anexado": "Pendente"}
df_sit_calc = df_sit[df_sit["Status"].isin(STATUS_MAP.keys())].copy()
df_sit_calc["Status_Cat"] = df_sit_calc["Status"].map(STATUS_MAP)

conf_emp = (
    df_sit_calc.groupby(["Empresa", "Status_Cat"])
    .size()
    .unstack(fill_value=0)
    .reindex(columns=["Conforme", "Vencido", "Pendente"], fill_value=0)
)
conf_emp["Total"]          = conf_emp.sum(axis=1)
conf_emp["Nao_Conforme"]   = conf_emp["Vencido"] + conf_emp["Pendente"]
conf_emp["Pct_Nao_Conf"]   = (conf_emp["Nao_Conforme"] / conf_emp["Total"].replace(0, 1) * 100).round(1)
conf_emp["Pct_Conf"]       = (conf_emp["Conforme"]   / conf_emp["Total"].replace(0, 1) * 100).round(1)
conf_emp = conf_emp.reset_index().sort_values("Pct_Nao_Conf", ascending=True)

total_docs_sit        = len(df_sit_calc)
total_conformes       = (df_sit_calc["Status_Cat"] == "Conforme").sum()
total_vencidos_docs   = (df_sit_calc["Status_Cat"] == "Vencido").sum()
total_pendentes_docs  = (df_sit_calc["Status_Cat"] == "Pendente").sum()
pct_conformidade      = round(total_conformes      / total_docs_sit * 100, 1) if total_docs_sit > 0 else 0
pct_nao_conform       = round((total_vencidos_docs + total_pendentes_docs) / total_docs_sit * 100, 1) if total_docs_sit > 0 else 0
trab_vencidos_count   = df_sit_calc[df_sit_calc["Status_Cat"] == "Vencido"]["Terceiro CPF/CNPJ"].nunique()

# ── KPIs PENDÊNCIAS ───────────────────────────────────────────────────────────
col_sit_pend = "Situação da solicitação" if "Situação da solicitação" in df_pend.columns else "Situacao da solicitacao"
col_area_pend = "Área da pendência" if "Área da pendência" in df_pend.columns else "Area da pendencia"

# Preferir cadastro completo (fornecedores_zurich.csv) para total real
if df_forn_cad is not None:
    _col_cnpj_forn = next((c for c in df_forn_cad.columns if re.search(r'cpf|cnpj', c, re.I)), None)
    total_fornecedores = df_forn_cad[_col_cnpj_forn].nunique() if _col_cnpj_forn else df_pend[col_rs_pend].nunique()
else:
    total_fornecedores = df_pend[col_rs_pend].nunique()
total_pendencias   = len(df_pend)
em_elaboracao      = (df_pend[col_sit_pend] == "EM_ELABORACAO").sum()
aprovado_com_pend  = (df_pend[col_sit_pend] == "APROVADO").sum()
pend_terceiros     = (df_pend[col_area_pend] == "TERCEIROS").sum()
pend_documentos    = (df_pend[col_area_pend] == "DOCUMENTOS").sum()

col_status_terc = "Status" if "Status" in df_terc.columns else "status"
total_trab_ativo   = (df_terc[col_status_terc] == "Ativo").sum()
total_trab_inativo = (df_terc[col_status_terc] == "Inativo").sum()

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

tabela = df_pend[["Empresa", col_sit_pend, col_area_pend, "Tipo_Doc", col_marcas, col_pend_txt]].copy()
tabela.columns = ["Fornecedor", "Status", "Area", "Documento", "Competencia", "Detalhe"]
tabela["Competencia"] = tabela["Competencia"].fillna("").astype(str).str.strip().replace("nan", "")
tabela["Detalhe"] = tabela["Detalhe"].astype(str).str[:250]
tabela_json = tabela.to_dict("records")
competencias_lista = sorted([c for c in tabela["Competencia"].unique() if c and c != "nan"])
competencias_json  = json.dumps(competencias_lista)

# ── TABELA DE SITUAÇÃO DOCUMENTAL (3 camadas) ─────────────────────────────────
col_trab_rs = "Terceiro Razão Social" if "Terceiro Razão Social" in df_sit_calc.columns else "Terceiro Razao Social"
col_trab_cpf = "Terceiro CPF/CNPJ"
col_dat_venc = "Data de Vencimento"

sit_tabela = df_sit_calc[["Empresa", col_trab_rs, "Documento", "Status_Cat", col_dat_venc]].copy()
sit_tabela.columns = ["Fornecedor", "Terceiro", "Documento", "Status", "Vencimento"]
sit_tabela["Vencimento"] = pd.to_datetime(sit_tabela["Vencimento"], errors="coerce").dt.strftime("%d/%m/%Y").fillna("")
sit_tabela_json = sit_tabela.to_dict("records")

terc_kpi = df_terc[["Empresa", col_status_terc]].rename(columns={"Empresa": "Fornecedor", col_status_terc: "Status"})
terc_kpi_json = terc_kpi.to_dict("records")

# ── R4: SITUAÇÃO DOCUMENTAL POR FORNECEDOR (empresa) ─────────────────────────
def map_status_flex(val):
    if pd.isna(val): return None
    s = str(val).lower()
    if "vencer" in s: return "Conforme"
    if "vencido" in s: return "Vencido"
    if "anexado" in s: return "Pendente"
    return None

_sit_forn_ok = False
if _os.path.exists(SITUACAO_FORN_CSV):
    df_sit_forn = read_csv_safe(SITUACAO_FORN_CSV)
    _sit_forn_ok = True

if _sit_forn_ok:
    col_r4_rs = df_sit_forn.columns[0]
    df_sit_forn["Empresa"] = df_sit_forn[col_r4_rs].apply(abbrev)
    df_sit_forn["Status_Cat"] = df_sit_forn["Status"].apply(map_status_flex)
    df_sit_forn_calc = df_sit_forn[df_sit_forn["Status_Cat"].notna()].copy()

    forn_sit_tabela = df_sit_forn_calc[["Empresa", "Documento", "Status_Cat", "Data de Vencimento"]].copy()
    forn_sit_tabela.columns = ["Fornecedor", "Documento", "Status", "Vencimento"]
    forn_sit_tabela["Vencimento"] = pd.to_datetime(
        forn_sit_tabela["Vencimento"], errors="coerce"
    ).dt.strftime("%d/%m/%Y").fillna("")
    forn_sit_json = forn_sit_tabela.to_dict("records")

    r4_total        = len(df_sit_forn_calc)
    r4_conf         = int((df_sit_forn_calc["Status_Cat"] == "Conforme").sum())
    r4_venc         = int((df_sit_forn_calc["Status_Cat"] == "Vencido").sum())
    r4_pend         = int((df_sit_forn_calc["Status_Cat"] == "Pendente").sum())
    r4_pct_nc       = round((r4_venc + r4_pend) / r4_total * 100, 1) if r4_total > 0 else 0.0
    r4_pct_c        = round(r4_conf / r4_total * 100, 1) if r4_total > 0 else 0.0
    r4_fornecedores = int(df_sit_forn_calc["Empresa"].nunique())
else:
    forn_sit_json   = []
    r4_total = r4_conf = r4_venc = r4_pend = r4_fornecedores = 0
    r4_pct_nc = r4_pct_c = 0.0
    df_sit_forn_calc = pd.DataFrame()

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

# Fig 7 — % Não Conformidade por fornecedor (NOVO)
cores_conf = [COR_VERDE if p <= 30 else COR_AMARELO if p <= 60 else COR_VERMELHO
              for p in conf_emp["Pct_Nao_Conf"]]
fig7 = go.Figure(go.Bar(
    x=conf_emp["Pct_Nao_Conf"], y=conf_emp["Empresa"], orientation="h",
    marker_color=cores_conf,
    text=[f"{v}%" for v in conf_emp["Pct_Nao_Conf"]], textposition="outside",
    customdata=conf_emp[["Conforme", "Vencido", "Pendente", "Total"]].values,
    hovertemplate=(
        "<b>%{y}</b><br>% Nao Conforme: %{x}%<br>"
        "Conforme: %{customdata[0]}<br>Vencido: %{customdata[1]}<br>"
        "Pendente (nao enviado): %{customdata[2]}<br>Total docs: %{customdata[3]}"
        "<extra></extra>"
    ),
))
fig7.update_layout(**PLOT_CONFIG, margin=M,
    title=dict(text="% de Não Conformidade por Fornecedor", font=dict(size=15, color=COR_TEAL)),
    height=max(350, 40 * len(conf_emp)),
    xaxis=dict(showgrid=True, gridcolor="#eee", ticksuffix="%", range=[0, 115]),
    yaxis=dict(automargin=True),
)

# Fig 8 — Status 3 camadas por empresa (Conforme / Vencido / Pendente) (NOVO)
conf_ord = conf_emp.sort_values("Pct_Nao_Conf", ascending=False)
emp_c8   = conf_ord["Empresa"].tolist()
ci       = conf_ord.set_index("Empresa")
fig8 = go.Figure()
fig8.add_trace(go.Bar(name="Conforme", orientation="h", marker_color=COR_VERDE,
    x=[int(ci.loc[e, "Conforme"]) if e in ci.index else 0 for e in emp_c8], y=emp_c8))
fig8.add_trace(go.Bar(name="Vencido", orientation="h", marker_color=COR_VERMELHO,
    x=[int(ci.loc[e, "Vencido"])  if e in ci.index else 0 for e in emp_c8], y=emp_c8))
fig8.add_trace(go.Bar(name="Pendente (nao enviado)", orientation="h", marker_color=COR_AMARELO,
    x=[int(ci.loc[e, "Pendente"]) if e in ci.index else 0 for e in emp_c8], y=emp_c8))
fig8.update_layout(**PLOT_CONFIG, barmode="stack",
    title=dict(text="Situação Documental por Fornecedor — Conforme / Vencido / Pendente",
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

# ── HTML ──────────────────────────────────────────────────────────────────────
html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dashboard Gestao de Terceiros — Zurich Airport</title>
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
  }}
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
  .badge-conforme      {{ background: #d4edda; color: {COR_VERDE}; }}
  .badge-vencido       {{ background: #ffeaea; color: {COR_VERMELHO}; }}
  .badge-pendente      {{ background: #fff3cd; color: #856404; }}
  .badge-competencia   {{ background: #e8f4f8; color: {COR_TEAL}; font-size: 11px; padding: 2px 7px; border-radius: 8px; }}

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
  #global-filtro-bar select {{
    border: none; border-radius: 6px; padding: 7px 12px;
    font-size: 13px; font-family: Calibri, Arial, sans-serif;
    background: white; color: #333; cursor: pointer; min-width: 220px;
  }}
  #global-filtro-bar .btn-gf-limpar {{
    background: rgba(255,255,255,.2); border: 1px solid rgba(255,255,255,.5);
    color: white; border-radius: 6px; padding: 7px 18px; font-size: 13px;
    font-family: Calibri, Arial, sans-serif; cursor: pointer; font-weight: 700;
  }}
  #global-filtro-bar .btn-gf-limpar:hover {{ background: rgba(255,255,255,.35); }}
  #gf-hint {{ font-size: 12px; color: rgba(255,255,255,.75); align-self: center; margin-left: auto; font-style: italic; }}
</style>
</head>
<body>

<div class="header">
  <div>
    <h1>Gestao de Terceiros — Zurich Airport</h1>
    <div class="subtitle">Dashboard de Conformidade Documental | Plataforma Efcaz</div>
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
    <select id="gf-fornecedor" onchange="applyGlobalFilter()">
      <option value="">Todos os fornecedores</option>
    </select>
  </div>
  <div>
    <label>Competencia</label>
    <select id="gf-competencia" onchange="applyGlobalFilter()">
      <option value="">Todas as competencias</option>
    </select>
  </div>
  <div style="align-self:flex-end">
    <button class="btn-gf-limpar" onclick="limparGlobalFiltro()">&#10005; Limpar filtros</button>
  </div>
  <span id="gf-hint"></span>
</div>

<div class="container">

  <!-- KPIs -->
  <div class="kpi-grid">
    <div class="kpi-card">
      <div class="kpi-val" id="kpi-forn">{total_fornecedores}</div>
      <div class="kpi-label">Fornecedores<br>com Pendencias</div>
    </div>
    <div class="kpi-card orange">
      <div class="kpi-val" id="kpi-totpend">{total_pendencias}</div>
      <div class="kpi-label">Total de<br>Pendencias</div>
    </div>
    <div class="kpi-card red">
      <div class="kpi-val" id="kpi-elab">{em_elaboracao}</div>
      <div class="kpi-label">Pendente<br>(nao enviado)</div>
    </div>
    <div class="kpi-card yellow">
      <div class="kpi-val" id="kpi-aprov">{aprovado_com_pend}</div>
      <div class="kpi-label">Em Analise<br>(c/ Pendencias)</div>
    </div>
    <div class="kpi-card red">
      <div class="kpi-val" id="kpi-pct-nc">{pct_nao_conform}%</div>
      <div class="kpi-label">% Nao<br>Conformidade Geral</div>
    </div>
    <div class="kpi-card green">
      <div class="kpi-val" id="kpi-pct-c">{pct_conformidade}%</div>
      <div class="kpi-label">% Conformidade<br>Geral</div>
    </div>
    <div class="kpi-card red">
      <div class="kpi-val" id="kpi-venc">{total_vencidos_docs}</div>
      <div class="kpi-label">Docs<br>Vencidos</div>
    </div>
    <div class="kpi-card yellow">
      <div class="kpi-val" id="kpi-pend">{total_pendentes_docs}</div>
      <div class="kpi-label">Docs Pendentes<br>(nao enviados)</div>
    </div>
    <div class="kpi-card green">
      <div class="kpi-val" id="kpi-conf">{total_conformes}</div>
      <div class="kpi-label">Docs<br>Conformes</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-val" id="kpi-pend-terc">{pend_terceiros}</div>
      <div class="kpi-label">Pend. de<br>Terceiros</div>
    </div>
    <div class="kpi-card orange">
      <div class="kpi-val" id="kpi-pend-doc">{pend_documentos}</div>
      <div class="kpi-label">Pend.<br>Documentais</div>
    </div>
    <div class="kpi-card green">
      <div class="kpi-val" id="kpi-terc-ativo">{total_trab_ativo}</div>
      <div class="kpi-label">Terceiros<br>Ativos</div>
    </div>
  </div>

  <!-- ALERTA DE AUDITORIA -->
  <div class="section-title">Alertas de Auditoria
    <span class="section-toggle" onclick="toggleSection('auditoria-section', this)">▼ Expandir</span>
  </div>
  <div id="auditoria-section" class="section-collapsible collapsed">
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

  </div><!-- /auditoria-section -->

  <!-- CONFORMIDADE DOCUMENTAL (NOVO) -->
  <div class="section-title">Conformidade Documental por Fornecedor
    <span class="section-toggle" onclick="toggleSection('conf-section', this)">▼ Expandir</span>
  </div>
  <div id="conf-section" class="section-collapsible collapsed">

  <div class="legenda-conf">
    <div class="legenda-item"><div class="legenda-dot" style="background:{COR_VERDE}"></div> &le;30% nao conforme — Situacao controlada</div>
    <div class="legenda-item"><div class="legenda-dot" style="background:{COR_AMARELO}"></div> 31–60% — Atencao necessaria</div>
    <div class="legenda-item"><div class="legenda-dot" style="background:{COR_VERMELHO}"></div> &gt;60% — Risco alto</div>
  </div>

  <div class="chart-row col2">
    <div class="chart-card">{fig_div(fig7, "fig7")}</div>
    <div class="chart-card">{fig_div(fig8, "fig8")}</div>
  </div>

  </div><!-- /conf-section -->

  <!-- VISAO GERAL -->
  <div class="section-title">Visao Geral de Pendencias
    <span class="section-toggle" onclick="toggleSection('visao-section', this)">▼ Expandir</span>
  </div>
  <div id="visao-section" class="section-collapsible collapsed">
  <div class="chart-row col2">
    <div class="chart-card">{fig_div(fig1, "fig1")}</div>
    <div class="chart-card">{fig_div(fig5, "fig5")}</div>
  </div>
  </div><!-- /visao-section -->

  <!-- STATUS -->
  <div class="section-title">Status das Solicitacoes
    <span class="section-toggle" onclick="toggleSection('status-section', this)">▼ Expandir</span>
  </div>
  <div id="status-section" class="section-collapsible collapsed">
  <div class="chart-card">{fig_div(fig3, "fig3")}</div>
  </div><!-- /status-section -->

  <!-- AREA -->
  <div class="section-title">Pendencias por Area
    <span class="section-toggle" onclick="toggleSection('area-section', this)">▼ Expandir</span>
  </div>
  <div id="area-section" class="section-collapsible collapsed">
  <div class="chart-card">{fig_div(fig4, "fig4")}</div>
  </div><!-- /area-section -->

  <!-- TIPOS DE DOCUMENTOS -->
  <div class="section-title">Tipos de Documentos com Mais Pendencias
    <span class="section-toggle" onclick="toggleSection('tipos-section', this)">▼ Expandir</span>
  </div>
  <div id="tipos-section" class="section-collapsible collapsed">
  <div class="chart-card">{fig_div(fig2, "fig2")}</div>
  </div><!-- /tipos-section -->

  <!-- TRABALHADORES -->
  <div class="section-title">Terceiros Cadastrados por Fornecedor
    <span class="section-toggle" onclick="toggleSection('trab-section', this)">▼ Expandir</span>
  </div>
  <div id="trab-section" class="section-collapsible collapsed">
  <div class="chart-card">{fig_div(fig6, "fig6")}</div>
  </div><!-- /trab-section -->

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

  <!-- SITUACAO DOCUMENTAL POR TRABALHADOR (NOVO) -->
  <div class="section-title">
    Situacao Documental por Terceiro — Conforme / Vencido / Pendente
    <span class="section-toggle" onclick="toggleSection('sit-section', this)">▼ Expandir</span>
  </div>
  <div id="sit-section" class="section-collapsible collapsed">

  <div class="filtro-bar">
    <div>
      <label>Fornecedor</label><br>
      <select id="sit-empresa" onchange="filtrarSit()"><option value="">Todos</option></select>
    </div>
    <div>
      <label>Status</label><br>
      <select id="sit-status" onchange="filtrarSit()">
        <option value="">Todos</option>
        <option value="Conforme">Conforme</option>
        <option value="Vencido">Vencido</option>
        <option value="Pendente">Pendente (nao enviado)</option>
      </select>
    </div>
    <div>
      <label>Buscar documento</label><br>
      <input type="text" id="sit-busca" placeholder="Ex: ASO, Ficha de EPI..." oninput="filtrarSit()" style="width:220px">
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
            <th>Status</th>
            <th>Vencimento</th>
          </tr>
        </thead>
        <tbody id="sit-body"></tbody>
      </table>
    </div>
    </div>
    <div id="sit-modo-agrupado" style="display:none">
      <div id="sit-grupos"></div>
    </div>
  </div>

  </div><!-- /sit-section -->

  <!-- SITUACAO DOCUMENTAL DA EMPRESA (R4) -->
  <div class="section-title">
    Situacao Documental da Empresa (Documentacao Corporativa)
    <span class="section-toggle" onclick="toggleSection('forn-sit-section', this)">&#9660; Expandir</span>
  </div>
  <div id="forn-sit-section" class="section-collapsible collapsed">

  <div class="kpi-grid" style="margin-bottom:16px;grid-template-columns:repeat(auto-fit,minmax(140px,1fr))">
    <div class="kpi-card red">
      <div class="kpi-val" id="r4-kpi-nc">{r4_pct_nc}%</div>
      <div class="kpi-label">% Nao Conf.<br>Empresa</div>
    </div>
    <div class="kpi-card green">
      <div class="kpi-val" id="r4-kpi-c">{r4_pct_c}%</div>
      <div class="kpi-label">% Conf.<br>Empresa</div>
    </div>
    <div class="kpi-card red">
      <div class="kpi-val" id="r4-kpi-venc">{r4_venc}</div>
      <div class="kpi-label">Docs<br>Vencidos</div>
    </div>
    <div class="kpi-card yellow">
      <div class="kpi-val" id="r4-kpi-pend">{r4_pend}</div>
      <div class="kpi-label">Docs<br>Pendentes</div>
    </div>
    <div class="kpi-card green">
      <div class="kpi-val" id="r4-kpi-conf">{r4_conf}</div>
      <div class="kpi-label">Docs<br>Conformes</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-val" id="r4-kpi-forn">{r4_fornecedores}</div>
      <div class="kpi-label">Fornecedores<br>com Docs</div>
    </div>
  </div>

  <div class="filtro-bar">
    <div>
      <label>Fornecedor</label><br>
      <select id="forn-sit-empresa" onchange="filtrarFornSit()"><option value="">Todos</option></select>
    </div>
    <div>
      <label>Status</label><br>
      <select id="forn-sit-status" onchange="filtrarFornSit()">
        <option value="">Todos</option>
        <option value="Conforme">Conforme</option>
        <option value="Vencido">Vencido</option>
        <option value="Pendente">Pendente (nao enviado)</option>
      </select>
    </div>
    <div>
      <label>Buscar documento</label><br>
      <input type="text" id="forn-sit-busca" placeholder="Ex: FGTS, CND, TRF3..." oninput="filtrarFornSit()" style="width:220px">
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
      <label>Fornecedor</label><br>
      <select id="filtro-empresa" onchange="filtrarTabela()"><option value="">Todos</option></select>
    </div>
    <div>
      <label>Status</label><br>
      <select id="filtro-status" onchange="filtrarTabela()">
        <option value="">Todos</option>
        <option value="EM_ELABORACAO">Pendente (nao enviado)</option>
        <option value="APROVADO">Em Analise</option>
      </select>
    </div>
    <div>
      <label>Area</label><br>
      <select id="filtro-area" onchange="filtrarTabela()">
        <option value="">Todas</option>
        <option value="TERCEIROS">Terceiros</option>
        <option value="DOCUMENTOS">Documentos</option>
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
      <input type="text" id="filtro-busca" placeholder="Documento ou pendencia..." oninput="filtrarTabela()" style="width:200px">
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
            <th>Status</th>
            <th>Area</th>
            <th>Documento</th>
            <th>Competencia</th>
            <th>Detalhe da Pendencia</th>
          </tr>
        </thead>
        <tbody id="tabela-body"></tbody>
      </table>
    </div>
  </div><!-- /pend-section -->

</div>

<div class="footer">
  Dashboard gerado automaticamente pela plataforma Efcaz &mdash; {DATA_HOJE} &mdash; Uso interno
</div>

<script>
const DADOS    = {json.dumps(tabela_json, ensure_ascii=False)};
const SIT      = {json.dumps(sit_tabela_json, ensure_ascii=False)};
const TERC_KPI = {json.dumps(terc_kpi_json, ensure_ascii=False)};
const FORN_SIT = {json.dumps(forn_sit_json, ensure_ascii=False)};

// ── KPI DINAMICO ──────────────────────────────────────────────────────────────
function updateKPICards(forn) {{
  const d = forn ? DADOS.filter(r => r.Fornecedor === forn) : DADOS;
  const s = forn ? SIT.filter(r => r.Fornecedor === forn) : SIT;
  const t = forn ? TERC_KPI.filter(r => r.Fornecedor === forn) : TERC_KPI;

  const fornCount = forn ? 1 : new Set(d.map(r => r.Fornecedor)).size;
  const totPend   = d.length;
  const elab      = d.filter(r => r.Status === "EM_ELABORACAO").length;
  const aprov     = d.filter(r => r.Status === "APROVADO").length;
  const pTerc     = d.filter(r => r.Area === "TERCEIROS").length;
  const pDoc      = d.filter(r => r.Area === "DOCUMENTOS").length;

  const conf  = s.filter(r => r.Status === "Conforme").length;
  const venc  = s.filter(r => r.Status === "Vencido").length;
  const pend  = s.filter(r => r.Status === "Pendente").length;
  const total = conf + venc + pend;
  const pctNC = total > 0 ? (((venc + pend) / total) * 100).toFixed(1) : "0.0";
  const pctC  = total > 0 ? ((conf / total) * 100).toFixed(1) : "0.0";

  const tercAtivo = t.filter(r => r.Status === "Ativo").length;

  document.getElementById("kpi-forn").textContent      = fornCount;
  document.getElementById("kpi-totpend").textContent   = totPend;
  document.getElementById("kpi-elab").textContent      = elab;
  document.getElementById("kpi-aprov").textContent     = aprov;
  document.getElementById("kpi-pct-nc").textContent    = pctNC + "%";
  document.getElementById("kpi-pct-c").textContent     = pctC + "%";
  document.getElementById("kpi-venc").textContent      = venc;
  document.getElementById("kpi-pend").textContent      = pend;
  document.getElementById("kpi-conf").textContent      = conf;
  document.getElementById("kpi-pend-terc").textContent = pTerc;
  document.getElementById("kpi-pend-doc").textContent  = pDoc;
  document.getElementById("kpi-terc-ativo").textContent = tercAtivo;
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
preencherSelect("filtro-empresa",   DADOS,    "Fornecedor");
preencherSelect("sit-empresa",     SIT,      "Fornecedor");
preencherSelect("forn-sit-empresa", FORN_SIT, "Fornecedor");

// ── BADGES ────────────────────────────────────────────────────────────────────
function badgeStatus(s) {{
  if (!s) return "";
  if (s === "EM_ELABORACAO") return '<span class="badge badge-pendente_env">Pendente (nao enviado)</span>';
  return '<span class="badge badge-em_analise">Em Analise</span>';
}}
function badgeArea(a) {{
  if (!a) return "";
  if (a === "TERCEIROS") return '<span class="badge badge-terceiros">Terceiros</span>';
  return '<span class="badge badge-documentos">Documentos</span>';
}}
function badgeSit(s) {{
  if (s === "Conforme") return '<span class="badge badge-conforme">Conforme</span>';
  if (s === "Vencido")  return '<span class="badge badge-vencido">Vencido</span>';
  return '<span class="badge badge-pendente">Pendente (nao enviado)</span>';
}}

// ── TABELA SITUACAO ───────────────────────────────────────────────────────────
let sitFiltrado = [];
function filtrarSit() {{
  const emp   = document.getElementById("sit-empresa").value;
  const stat  = document.getElementById("sit-status").value;
  const busca = document.getElementById("sit-busca").value.toLowerCase();
  sitFiltrado = SIT.filter(r => {{
    if (emp  && r["Fornecedor"] !== emp)  return false;
    if (stat && r["Status"]     !== stat) return false;
    if (busca && !r["Documento"].toLowerCase().includes(busca)) return false;
    return true;
  }});
  const tbody = document.getElementById("sit-body");
  tbody.innerHTML = sitFiltrado.map(r => `
    <tr>
      <td>${{r["Fornecedor"]}}</td>
      <td>${{r["Terceiro"]}}</td>
      <td>${{r["Documento"]}}</td>
      <td>${{badgeSit(r["Status"])}}</td>
      <td>${{r["Vencimento"] || "—"}}</td>
    </tr>
  `).join("");
  document.getElementById("sit-count").textContent =
    `${{sitFiltrado.length}} registro(s) exibido(s) de ${{SIT.length}} no total`;
  if (modoAgrupado) renderSitAgrupado(sitFiltrado);
}}
function limparSit() {{
  ["sit-empresa","sit-status","sit-busca"].forEach(id => {{
    const el = document.getElementById(id);
    if (el) el.value = "";
  }});
  filtrarSit();
}}

// ── TABELA PENDENCIAS ─────────────────────────────────────────────────────────
let pendFiltrado = [];
function filtrarTabela() {{
  const emp    = document.getElementById("filtro-empresa").value;
  const status = document.getElementById("filtro-status").value;
  const area   = document.getElementById("filtro-area").value;
  const comp   = document.getElementById("filtro-competencia").value;
  const busca  = document.getElementById("filtro-busca").value.toLowerCase();
  pendFiltrado = DADOS.filter(r => {{
    if (emp    && r["Fornecedor"]  !== emp)    return false;
    if (status && r["Status"]      !== status) return false;
    if (area   && r["Area"]        !== area)   return false;
    if (comp   && r["Competencia"] !== comp)   return false;
    if (busca) {{
      const txt = (r["Documento"] + " " + r["Detalhe"]).toLowerCase();
      if (!txt.includes(busca)) return false;
    }}
    return true;
  }});
  const tbody = document.getElementById("tabela-body");
  tbody.innerHTML = pendFiltrado.map(r => `
    <tr>
      <td>${{r["Fornecedor"]}}</td>
      <td>${{badgeStatus(r["Status"])}}</td>
      <td>${{badgeArea(r["Area"])}}</td>
      <td><strong>${{r["Documento"]}}</strong></td>
      <td>${{r["Competencia"] ? '<span class="badge-competencia">' + r["Competencia"] + '</span>' : '<span style="color:#aaa">—</span>'}}</td>
      <td style="font-size:12px">${{r["Detalhe"]}}</td>
    </tr>
  `).join("");
  document.getElementById("tabela-count").textContent =
    `${{pendFiltrado.length}} pendencia(s) exibida(s) de ${{DADOS.length}} no total`;
}}
function limparFiltros() {{
  ["filtro-empresa","filtro-status","filtro-area","filtro-competencia","filtro-busca"].forEach(id => {{
    const el = document.getElementById(id);
    if (el) el.value = "";
  }});
  filtrarTabela();
}}

// ── TABELA SITUACAO DA EMPRESA (R4) ───────────────────────────────────────────
let fornSitFiltrado = [];
function filtrarFornSit() {{
  const emp   = document.getElementById("forn-sit-empresa").value;
  const stat  = document.getElementById("forn-sit-status").value;
  const busca = document.getElementById("forn-sit-busca").value.toLowerCase();
  const cleanDoc = s => String(s || "").replace(/�/g, "");
  fornSitFiltrado = FORN_SIT.filter(r => {{
    if (emp  && r["Fornecedor"] !== emp)  return false;
    if (stat && r["Status"]     !== stat) return false;
    if (busca && !cleanDoc(r["Documento"]).toLowerCase().includes(busca)) return false;
    return true;
  }});
  const tbody = document.getElementById("forn-sit-body");
  tbody.innerHTML = fornSitFiltrado.map(r => `
    <tr>
      <td>${{r["Fornecedor"]}}</td>
      <td>${{cleanDoc(r["Documento"])}}</td>
      <td>${{badgeSit(r["Status"])}}</td>
      <td>${{r["Vencimento"] || "—"}}</td>
    </tr>
  `).join("");
  const cnt = document.getElementById("forn-sit-count");
  if (cnt) cnt.textContent = `${{fornSitFiltrado.length}} registro(s) de ${{FORN_SIT.length}} no total`;

  // KPIs dinâmicos R4
  const conf4 = fornSitFiltrado.filter(r => r["Status"]==="Conforme").length;
  const venc4 = fornSitFiltrado.filter(r => r["Status"]==="Vencido").length;
  const pend4 = fornSitFiltrado.filter(r => r["Status"]==="Pendente").length;
  const tot4  = conf4+venc4+pend4;
  const pctNC4 = tot4>0 ? ((venc4+pend4)/tot4*100).toFixed(1) : "0.0";
  const pctC4  = tot4>0 ? (conf4/tot4*100).toFixed(1) : "0.0";
  const forn4  = new Set(fornSitFiltrado.map(r=>r["Fornecedor"])).size;
  const el4 = id => {{ const e=document.getElementById(id); if(e) e.textContent=arguments[1]; }};
  [["r4-kpi-nc", pctNC4+"%"], ["r4-kpi-c", pctC4+"%"],
   ["r4-kpi-venc", venc4], ["r4-kpi-pend", pend4],
   ["r4-kpi-conf", conf4], ["r4-kpi-forn", forn4]
  ].forEach(([id, val]) => {{ const e=document.getElementById(id); if(e) e.textContent=val; }});
}}
function limparFornSit() {{
  ["forn-sit-empresa","forn-sit-status","forn-sit-busca"].forEach(id => {{
    const el = document.getElementById(id); if (el) el.value = "";
  }});
  filtrarFornSit();
}}
function exportarFornSitXLSX() {{
  downloadXLSX(fornSitFiltrado, ["Fornecedor","Documento","Status","Vencimento"], "situacao_empresa_zurich.xlsx");
}}
function exportarFornSitPDF() {{
  downloadPDF(fornSitFiltrado, ["Fornecedor","Documento","Status","Vencimento"],
    "situacao_empresa_zurich.pdf", "Situacao Documental da Empresa — Zurich Airport");
}}
function exportarFornSitCSV() {{
  downloadCSV(fornSitFiltrado, ["Fornecedor","Documento","Status","Vencimento"], "situacao_empresa_zurich.csv");
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
  downloadCSV(sitFiltrado, ["Fornecedor","Terceiro","Documento","Status","Vencimento"],
    "situacao_documental_zurich.csv");
}}
function exportarPend() {{
  downloadCSV(pendFiltrado, ["Fornecedor","Status","Area","Documento","Competencia","Detalhe"],
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
  downloadXLSX(sitFiltrado, ["Fornecedor","Terceiro","Documento","Status","Vencimento"],
    "situacao_documental_zurich.xlsx");
}}
function exportarPendXLSX() {{
  downloadXLSX(pendFiltrado, ["Fornecedor","Status","Area","Documento","Competencia","Detalhe"],
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
  downloadPDF(sitFiltrado, ["Fornecedor","Terceiro","Documento","Status","Vencimento"],
    "situacao_documental_zurich.pdf", "Situação Documental por Terceiro — Zurich Airport");
}}
function exportarPendPDF() {{
  downloadPDF(pendFiltrado, ["Fornecedor","Status","Area","Documento","Competencia","Detalhe"],
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
    if (d.status==="Conforme") conf++;
    else if (d.status==="Vencido") venc++;
    else pend++;
  }}));
  const total = conf+venc+pend;
  fornStats[f] = {{conf, venc, pend, total, pctNC: total>0 ? Math.round((venc+pend)/total*100) : 0,
                   trabCount: Object.keys(drillData[f]).length}};
}});

function corNC(pct) {{ return pct<=30 ? "#28A745" : pct<=60 ? "#FFC107" : "#DC3545"; }}

function showLevel(n) {{
  [1,2,3].forEach(i => document.getElementById("drill-level"+i).style.display = i===n ? "block" : "none");
}}

function renderLevel1(filterForn) {{
  showLevel(1);
  let keys = Object.keys(fornStats).sort((a,b) => fornStats[b].pctNC - fornStats[a].pctNC);
  if (filterForn) keys = keys.filter(f => f === filterForn);
  document.getElementById("supplier-cards").innerHTML = keys.map(f => {{
    const s = fornStats[f];
    const cor = corNC(s.pctNC);
    const pConf = s.total>0 ? (s.conf/s.total*100).toFixed(1) : 0;
    const pVenc = s.total>0 ? (s.venc/s.total*100).toFixed(1) : 0;
    const pPend = s.total>0 ? (s.pend/s.total*100).toFixed(1) : 0;
    return `<div class="drill-card" data-forn="${{encodeURIComponent(f)}}" onclick="renderLevel2(decodeURIComponent(this.dataset.forn))">
      <div class="drill-card-pct" style="color:${{cor}}">${{s.pctNC}}%</div>
      <div class="drill-card-label">nao conforme</div>
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
    const conf = docs.filter(d=>d.status==="Conforme").length;
    const venc = docs.filter(d=>d.status==="Vencido").length;
    const pend = docs.filter(d=>d.status==="Pendente").length;
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
    const cls = d.status==="Conforme" ? "badge-conforme" : d.status==="Vencido" ? "badge-vencido" : "badge-pendente";
    return `<div class="drill-doc">
      <div class="drill-doc-name">${{d.doc}}</div>
      <span class="badge ${{cls}}">${{d.status}}</span>
      <div class="drill-doc-venc">${{d.venc || "—"}}</div>
    </div>`;
  }}).join("") || '<div class="drill-hint">Nenhum documento encontrado</div>';
}}

renderLevel1();

// ── TOGGLE SECOES ─────────────────────────────────────────────────────────────
function toggleSection(id, btn) {{
  const el = document.getElementById(id);
  const isCollapsed = el.classList.toggle('collapsed');
  btn.textContent = isCollapsed ? '▼ Expandir' : '▲ Recolher';
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
  const forn = document.getElementById("gf-fornecedor").value;
  const comp = document.getElementById("gf-competencia").value;

  // Sincroniza tabela pendencias
  const selEmp = document.getElementById("filtro-empresa");
  if (selEmp) selEmp.value = forn;
  const selComp = document.getElementById("filtro-competencia");
  if (selComp) selComp.value = comp;
  filtrarTabela();

  // Sincroniza tabela situacao documental (R3)
  const selSit = document.getElementById("sit-empresa");
  if (selSit) selSit.value = forn;
  filtrarSit();

  // Sincroniza tabela situacao empresa (R4)
  const selFornSit = document.getElementById("forn-sit-empresa");
  if (selFornSit) selFornSit.value = forn;
  filtrarFornSit();

  // KPI cards dinamicos
  updateKPICards(forn || undefined);

  // Drill-down com filtro
  renderLevel1(forn || undefined);

  // Expande secoes automaticamente quando filtro esta ativo
  if (forn || comp) {{
    expandSection("drill-section");
    expandSection("pend-section");
    expandSection("sit-section");
    expandSection("forn-sit-section");
  }}

  // Hint de filtro ativo
  const parts = [];
  if (forn) parts.push(forn);
  if (comp) parts.push("Competencia: " + comp);
  document.getElementById("gf-hint").textContent = parts.length ? "Filtro ativo: " + parts.join(" | ") : "";
}}

function limparGlobalFiltro() {{
  ["gf-fornecedor","gf-competencia"].forEach(id => {{ document.getElementById(id).value = ""; }});
  applyGlobalFilter();
}}

// ── INIT ──────────────────────────────────────────────────────────────────────
// Popula selects do filtro global
(function() {{
  const gfForn = document.getElementById("gf-fornecedor");
  Object.keys(fornStats).sort().forEach(f => {{
    const o = document.createElement("option"); o.value = f; o.text = f; gfForn.appendChild(o);
  }});
  const gfComp = document.getElementById("gf-competencia");
  const comps = {competencias_json};
  comps.forEach(c => {{
    const o = document.createElement("option"); o.value = c; o.text = c; gfComp.appendChild(o);
  }});
}})();

filtrarSit();
filtrarTabela();
filtrarFornSit();
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
print(f"  Docs vencidos               : {total_vencidos_docs}")
print(f"  Docs pendentes              : {total_pendentes_docs}")
print(f"  Docs conformes              : {total_conformes}")
print(f"  Trabalhadores ativos        : {total_trab_ativo}")
print(f"  --- R4 Empresa ---")
print(f"  Fornecedores (R4)           : {r4_fornecedores}")
print(f"  % Nao conf empresa          : {r4_pct_nc}%")
print(f"  Docs vencidos empresa       : {r4_venc}")
print(f"  Docs pendentes empresa      : {r4_pend}")
print(f"  Docs conformes empresa      : {r4_conf}")
