"""
Atualiza os dados do Dashboard Zurich (Python + React) com os CSVs mais recentes
da pasta Documentos. Basta rodar este script após baixar as planilhas do Metabase.
"""
import shutil
import glob
import os
from datetime import datetime

DOC  = r"C:\Users\gabriel.evangelista\Documents\ClaudeGL\Documentos"
DST1 = r"C:\Users\gabriel.evangelista\Documents\ClaudeGL\Dashboard\data"
DST2 = r"C:\Users\gabriel.evangelista\Documents\ClaudeGL\dashboard-react\public\data"

# Vínculos: padrão de busca no Documentos → nomes fixos nos destinos
# "pastas": lista de pastas destino. Padrão: [DST1, DST2] (Python + React).
#           Use ["DST2"] para arquivos exclusivos do dashboard React.
VINCULOS = [
    {
        # Relatório combinado de pendências → Python usa esse arquivo diretamente
        # React usa como fonte para pendencias_fornecedor_zurich.csv (ver abaixo)
        "padrao":  "zurich_airport___pendencias_por_solicitacao_com_documentos___dados_*.csv",
        "destino": "pendencias_zurich.csv",
        "label":   "Pendências (combinado — Python)",
    },
    {
        # Mesma fonte do item anterior → salvo também como pendencias_fornecedor_zurich.csv
        # O dashboard React lê este arquivo como Area='Fornecedor'
        "padrao":  "zurich_airport___pendencias_por_solicitacao_com_documentos___dados_*.csv",
        "destino": "pendencias_fornecedor_zurich.csv",
        "label":   "Pendências Fornecedor (React)",
        "pastas":  ["DST2"],
    },
    {
        # Relatório exclusivo de pendências de terceiros — exportar do Efcaz separadamente
        # Nome esperado: zurich_airport___pendencias_de_documentos_de_terceiros___dados_*.csv
        # ⚠️  Se este arquivo não existir na pasta Documentos, será pulado (não bloqueia o script)
        "padrao":  "zurich_airport___pendencias_de_documentos_de_terceiros___dados_*.csv",
        "destino": "pendencias_terceiros_zurich.csv",
        "label":   "Pendências Terceiros (React)",
        "pastas":  ["DST2"],
        "opcional": True,
    },
    {
        "padrao":  "relatorio_de_terceiros_cadastrados_*.csv",
        "destino": "terceiros_zurich.csv",
        "label":   "Terceiros cadastrados",
    },
    {
        "padrao":  "situacao_de_preenchimento_documental_do_terceiro_na_ultima_solicitacao_do_fornecedor___dados_*.csv",
        "destino": "situacao_terceiro_zurich.csv",
        "label":   "Situação terceiro (R3)",
    },
    {
        "padrao":  "situacao_de_preenchimento_documental_na_ultima_solicitacao_do_fornecedor___dados_*.csv",
        "destino": "situacao_fornecedor_zurich.csv",
        "label":   "Situação fornecedor (R4)",
    },
    {
        "padrao":  "situacao_dos_documentos_de_busca_automatica___dados_*.csv",
        "destino": "busca_automatica_zurich.csv",
        "label":   "Busca automática",
    },
    {
        "padrao":  "relatorio_de_codigos_de_contrato_dos_fornecedores___dados_*.csv",
        "destinos": ["codigos_contrato_fornecedores_zurich.csv", "contratos_zurich.csv"],
        "label":   "Contratos / Códigos de contrato",
    },
]

def arquivo_mais_recente(pasta, padrao):
    matches = glob.glob(os.path.join(pasta, padrao))
    if not matches:
        return None
    return max(matches, key=os.path.getmtime)

PASTA_MAP = {"DST1": DST1, "DST2": DST2}

print("=" * 65)
print("  ATUALIZAÇÃO DADOS ZURICH AIRPORT")
print(f"  Data/hora: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
print("=" * 65)
print()

erros = []

for v in VINCULOS:
    src = arquivo_mais_recente(DOC, v["padrao"])
    if not src:
        if v.get("opcional"):
            print(f"  ⚠  {v['label']} — não encontrado (opcional, pulando)")
            print()
            continue
        erros.append(f"  ARQUIVO NÃO ENCONTRADO: {v['padrao']}")
        print(f"  ✗ {v['label']} — arquivo não encontrado")
        continue

    nome_src = os.path.basename(src)
    data_src = datetime.fromtimestamp(os.path.getmtime(src)).strftime("%d/%m/%Y %H:%M")

    destinos = v.get("destinos", [v.get("destino")])
    # "pastas": lista de chaves "DST1"/"DST2"; padrão: ambas
    pastas_keys = v.get("pastas", ["DST1", "DST2"])
    pastas_dst  = [PASTA_MAP[k] for k in pastas_keys]

    for destino in destinos:
        for pasta_dst in pastas_dst:
            dst_path = os.path.join(pasta_dst, destino)
            shutil.copy2(src, dst_path)

    pasta_label = " + ".join(pastas_keys).replace("DST1", "Dashboard/data").replace("DST2", "dashboard-react/public/data")
    print(f"  ✓ {v['label']}")
    print(f"    Origem : {nome_src}")
    print(f"    Data   : {data_src}")
    print(f"    Salvo  : {', '.join(destinos)} → {pasta_label}")
    print()

print("=" * 65)
if erros:
    print("  ATENÇÃO — erros encontrados:")
    for e in erros:
        print(e)
else:
    print("  Todos os arquivos atualizados com sucesso.")
    print()
    print("  Próximos passos:")
    print("  1. python relatorio_fornecedores_zurich.py  (gera HTML Python)")
    print("  2. python comparativo_semanas.py            (comparativo semanal)")
    print("  3. git add + commit + push                  (deploy React/Vercel)")
print("=" * 65)
