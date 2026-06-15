import Papa from 'papaparse'
import { ClienteInput } from '../types'

function parseNum(v: string): number {
  const n = parseFloat(v)
  return isNaN(n) ? 0 : n
}

function parseNullNum(v: string): number | null {
  if (v === '' || v === null || v === undefined) return null
  const n = parseFloat(v)
  return isNaN(n) ? null : n
}

function parseTier(v: string): ClienteInput['tier'] {
  const t = v.trim()
  if (t === 'A' || t === 'B+' || t === 'B' || t === 'C') return t
  return 'C'
}

export async function loadClientes(): Promise<ClienteInput[]> {
  const res = await fetch('./data/clientes.csv')
  const text = await res.text()

  const result = Papa.parse<Record<string, string>>(text, {
    header: true,
    skipEmptyLines: true,
  })

  return result.data.map(row => ({
    cliente: row.cliente?.trim() ?? '',
    tier: parseTier(row.tier ?? ''),
    mrr: parseNum(row.mrr),

    dias_ultimo_login: parseNullNum(row.dias_ultimo_login),
    usuario_ativo: parseNum(row.usuario_ativo),
    usuario_contratado: parseNum(row.usuario_contratado),
    modulos_uso: parseNum(row.modulos_uso),
    modulos_contratado: parseNum(row.modulos_contratado),
    buscas_status: (parseNum(row.buscas_status) as 0 | 1 | 2),

    forn_cadastrado: parseNum(row.forn_cadastrado),
    forn_meta: parseNum(row.forn_meta),
    docs_vencidos: parseNum(row.docs_vencidos),
    docs_total: parseNum(row.docs_total),
    config_sistema_pct: parseNullNum(row.config_sistema_pct),

    conformidade_aprovados: parseNum(row.conformidade_aprovados),
    conformidade_total: parseNum(row.conformidade_total),
    certidoes_status: (parseNum(row.certidoes_status) as 0 | 1 | 2),
    rfi_trimestre: parseNullNum(row.rfi_trimestre),

    nps: parseNullNum(row.nps),
    dias_ultima_interacao: parseNum(row.dias_ultima_interacao),
    tickets_criticos: parseNum(row.tickets_criticos),

    dias_renovacao: parseNum(row.dias_renovacao),
    engagement_renovacao: (parseNum(row.engagement_renovacao) as 0 | 1 | 2),
  }))
}
