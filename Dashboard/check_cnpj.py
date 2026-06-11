import pandas as pd

cnpj_busca = "00973749002401"

def norm_c(v):
    s = str(v).strip()
    if s.endswith(".0"):
        s = s[:-2]
    if s in ("", "nan", "None"):
        return ""
    if s.isdigit() and len(s) < 14:
        s = s.zfill(14)
    return s

# R2 — terceiros cadastrados
df_r2 = pd.read_csv("data/terceiros_zurich.csv", dtype=str)
print("=== R2 colunas ===")
print(list(df_r2.columns))

col_cnpj_r2 = next((c for c in df_r2.columns if "cpf" in c.lower() or "cnpj" in c.lower() or "documento" in c.lower()), None)
col_rs_r2   = next((c for c in df_r2.columns if "raz" in c.lower() or "nome" in c.lower()), None)

print("\n=== R2 — busca por Top Service (nome) ===")
for col in df_r2.columns:
    hits = df_r2[df_r2[col].astype(str).str.upper().str.contains("TOP SERVICE", na=False)]
    if not hits.empty:
        print("  coluna: " + col)
        for _, r in hits.head(5).iterrows():
            print("  " + str(r.to_dict()))
        break

print("\n=== R2 — busca por CNPJ ===")
for col in df_r2.columns:
    df_r2["_n_" + col] = df_r2[col].apply(norm_c)
    hits = df_r2[df_r2["_n_" + col] == cnpj_busca]
    if not hits.empty:
        print("  Encontrado na coluna: " + col)
        print(hits.head(5).to_string())

# R1 — pendencias
df_r1 = pd.read_csv("data/pendencias_zurich.csv", dtype=str)
print("\n=== R1 colunas ===")
print(list(df_r1.columns))

print("\n=== R1 — busca por Top Service ===")
for col in df_r1.columns:
    hits = df_r1[df_r1[col].astype(str).str.upper().str.contains("TOP SERVICE", na=False)]
    if not hits.empty:
        print("  coluna: " + col)
        for cnpj_col in df_r1.columns:
            if "cnpj" in cnpj_col.lower() or "cpf" in cnpj_col.lower():
                cnpjs_top = hits[cnpj_col].apply(norm_c).unique()
                print("  CNPJs encontrados: " + str(cnpjs_top))
        break

# R3 — verificar todas as colunas com CNPJ
df_r3 = pd.read_csv("data/situacao_terceiro_zurich.csv", dtype=str)
print("\n=== R3 colunas ===")
print(list(df_r3.columns))
print("\n=== R3 — busca por Top Service em TODOS as colunas ===")
for col in df_r3.columns:
    hits = df_r3[df_r3[col].astype(str).str.upper().str.contains("TOP SERVICE", na=False)]
    if not hits.empty:
        print("  coluna: " + col + " -> " + str(len(hits)) + " linhas")
        cnpj_cols = [c for c in df_r3.columns if "cpf" in c.lower() or "cnpj" in c.lower()]
        for cc in cnpj_cols:
            vals = hits[cc].apply(norm_c).unique()
            print("    " + cc + ": " + str(vals))
