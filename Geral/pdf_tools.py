"""
pdf_tools.py — Manipulação de PDFs para Efcaz CS

Uso:
  python pdf_tools.py mesclar arq1.pdf arq2.pdf ... -o saida.pdf
  python pdf_tools.py dividir arq.pdf 1-3 5 8-10 -o pasta_saida/
  python pdf_tools.py extrair arq.pdf -o texto.txt
  python pdf_tools.py tabelas arq.pdf -o tabelas.xlsx
  python pdf_tools.py info arq.pdf
"""

import argparse
import os
import sys


# ── Helpers ───────────────────────────────────────────────────────────────────

def _check(lib):
    try:
        __import__(lib)
    except ImportError:
        print(f"[ERRO] Biblioteca '{lib}' não instalada. Execute: pip install {lib}")
        sys.exit(1)


def _parse_ranges(specs):
    """Converte ['1-3', '5', '8-10'] em lista de páginas 0-indexadas."""
    pages = []
    for s in specs:
        if '-' in s:
            a, b = s.split('-')
            pages.extend(range(int(a) - 1, int(b)))
        else:
            pages.append(int(s) - 1)
    return pages


# ── Comandos ──────────────────────────────────────────────────────────────────

def cmd_mesclar(args):
    _check("pypdf")
    from pypdf import PdfWriter
    writer = PdfWriter()
    for path in args.arquivos:
        if not os.path.exists(path):
            print(f"[ERRO] Arquivo não encontrado: {path}")
            sys.exit(1)
        writer.append(path)
        print(f"  + {os.path.basename(path)}")
    out = args.output or "mesclado.pdf"
    with open(out, "wb") as f:
        writer.write(f)
    print(f"\n✓ Salvo em: {out}  ({len(writer.pages)} páginas)")


def cmd_dividir(args):
    _check("pypdf")
    from pypdf import PdfReader, PdfWriter
    reader = PdfReader(args.arquivo)
    total  = len(reader.pages)
    pages  = _parse_ranges(args.paginas) if args.paginas else list(range(total))

    out_dir = args.output or "."
    os.makedirs(out_dir, exist_ok=True)

    base = os.path.splitext(os.path.basename(args.arquivo))[0]
    for i, pg in enumerate(pages, 1):
        if pg >= total:
            print(f"  [aviso] Página {pg+1} não existe (total: {total})")
            continue
        w = PdfWriter()
        w.add_page(reader.pages[pg])
        fname = os.path.join(out_dir, f"{base}_p{pg+1:03d}.pdf")
        with open(fname, "wb") as f:
            w.write(f)
        print(f"  ✓ {fname}")

    print(f"\n✓ {len(pages)} arquivo(s) gerado(s) em: {out_dir}")


def cmd_extrair(args):
    _check("pdfplumber")
    import pdfplumber
    out = args.output or os.path.splitext(args.arquivo)[0] + ".txt"
    with pdfplumber.open(args.arquivo) as pdf:
        linhas = []
        for i, page in enumerate(pdf.pages, 1):
            texto = page.extract_text() or ""
            if texto.strip():
                linhas.append(f"{'='*60}\n  PÁGINA {i}\n{'='*60}\n{texto}\n")
        conteudo = "\n".join(linhas)
    with open(out, "w", encoding="utf-8") as f:
        f.write(conteudo)
    chars = len(conteudo)
    print(f"✓ Texto extraído: {chars:,} caracteres → {out}")


def cmd_tabelas(args):
    _check("pdfplumber")
    _check("pandas")
    _check("openpyxl")
    import pdfplumber
    import pandas as pd

    out = args.output or os.path.splitext(args.arquivo)[0] + "_tabelas.xlsx"
    tabelas_encontradas = 0

    with pdfplumber.open(args.arquivo) as pdf, \
         pd.ExcelWriter(out, engine="openpyxl") as writer:
        for i, page in enumerate(pdf.pages, 1):
            tables = page.extract_tables()
            for j, table in enumerate(tables, 1):
                if not table:
                    continue
                df = pd.DataFrame(table[1:], columns=table[0] if table[0] else None)
                sheet = f"Pg{i}_T{j}"
                df.to_excel(writer, sheet_name=sheet, index=False)
                tabelas_encontradas += 1
                print(f"  ✓ Página {i} · Tabela {j} → aba '{sheet}' ({len(df)} linhas)")

    if tabelas_encontradas == 0:
        print("  Nenhuma tabela detectada no PDF.")
        os.remove(out)
    else:
        print(f"\n✓ {tabelas_encontradas} tabela(s) extraída(s) → {out}")


def cmd_info(args):
    _check("pypdf")
    _check("pdfplumber")
    import pdfplumber
    from pypdf import PdfReader
    reader = PdfReader(args.arquivo)
    meta   = reader.metadata or {}

    print(f"\n📄 {os.path.basename(args.arquivo)}")
    print(f"   Páginas   : {len(reader.pages)}")
    print(f"   Título    : {meta.get('/Title', '—')}")
    print(f"   Autor     : {meta.get('/Author', '—')}")
    print(f"   Criado em : {meta.get('/CreationDate', '—')}")
    print(f"   Tamanho   : {os.path.getsize(args.arquivo) / 1024:.1f} KB")

    with pdfplumber.open(args.arquivo) as pdf:
        total_chars  = sum(len(p.extract_text() or "") for p in pdf.pages)
        total_tables = sum(len(p.extract_tables()) for p in pdf.pages)

    print(f"   Caracteres: {total_chars:,}")
    print(f"   Tabelas   : {total_tables}")


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="pdf_tools",
        description="Manipulação de PDFs — Efcaz CS",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # mesclar
    p = sub.add_parser("mesclar", help="Mescla vários PDFs em um")
    p.add_argument("arquivos", nargs="+", help="PDFs de entrada")
    p.add_argument("-o", "--output", help="Arquivo de saída (padrão: mesclado.pdf)")

    # dividir
    p = sub.add_parser("dividir", help="Divide PDF em páginas individuais")
    p.add_argument("arquivo", help="PDF de entrada")
    p.add_argument("paginas", nargs="*", help="Ex: 1-3 5 8-10 (padrão: todas)")
    p.add_argument("-o", "--output", help="Pasta de saída (padrão: pasta atual)")

    # extrair
    p = sub.add_parser("extrair", help="Extrai texto para .txt")
    p.add_argument("arquivo", help="PDF de entrada")
    p.add_argument("-o", "--output", help="Arquivo .txt de saída")

    # tabelas
    p = sub.add_parser("tabelas", help="Extrai tabelas para .xlsx")
    p.add_argument("arquivo", help="PDF de entrada")
    p.add_argument("-o", "--output", help="Arquivo .xlsx de saída")

    # info
    p = sub.add_parser("info", help="Exibe metadados e estatísticas do PDF")
    p.add_argument("arquivo", help="PDF de entrada")

    args = parser.parse_args()
    {"mesclar": cmd_mesclar, "dividir": cmd_dividir,
     "extrair": cmd_extrair, "tabelas": cmd_tabelas,
     "info": cmd_info}[args.cmd](args)


if __name__ == "__main__":
    main()
