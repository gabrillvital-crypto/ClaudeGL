import Papa from 'papaparse'

export async function loadCSV(url: string): Promise<Record<string, string>[]> {
  const res = await fetch(url)
  if (!res.ok) throw new Error(`Failed to fetch ${url}: ${res.status}`)
  const text = await res.text()
  const result = Papa.parse<Record<string, string>>(text, {
    header: true,
    skipEmptyLines: true,
    delimiter: '',  // auto-detect: comma, semicolon, tab, pipe
    transformHeader: (h: string) => h.trim(),
  })
  return result.data
}

export async function loadAllCSVs() {
  const [rawPendForn, rawPendTerc, rawPendCred, rawTerc, rawSit, rawFornSit, rawContratos, rawBuscaAuto] = await Promise.all([
    loadCSV('/data/pendencias_fornecedor_zurich.csv').catch(() => [] as Record<string, string>[]),
    loadCSV('/data/pendencias_terceiros_zurich.csv').catch(() => [] as Record<string, string>[]),
    loadCSV('/data/pendencias_credenciamento_zurich.csv').catch(() => [] as Record<string, string>[]),
    loadCSV('/data/terceiros_zurich.csv'),
    loadCSV('/data/situacao_terceiro_zurich.csv'),
    loadCSV('/data/situacao_fornecedor_zurich.csv'),
    loadCSV('/data/contratos_zurich.csv').catch(() => [] as Record<string, string>[]),
    loadCSV('/data/busca_automatica_zurich.csv').catch(() => [] as Record<string, string>[]),
  ])
  return { rawPendForn, rawPendTerc, rawPendCred, rawTerc, rawSit, rawFornSit, rawContratos, rawBuscaAuto }
}
