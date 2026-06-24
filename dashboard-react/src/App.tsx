import { useMemo } from 'react'
import { useDashboardData } from './hooks/useDashboardData'
import { useGlobalFilter } from './hooks/useGlobalFilter'
import { Header } from './components/Header'
import { GlobalFilter } from './components/GlobalFilter'
import { KPIGrid } from './components/KPIGrid'
import { ConformidadeCharts } from './components/ConformidadeCharts'
import { Section } from './components/Section'
import { R3Section } from './components/R3Section'
import { SituacaoEmpresaSection } from './components/SituacaoEmpresaSection'
import { PendenciasSection } from './components/PendenciasSection'
import { ContratosSection } from './components/ContratosSection'

function fmtCNPJ(digits: string): string {
  const d = digits.replace(/\D/g, '')
  if (d.length === 11) return d.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4')
  if (d.length === 14) return d.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5')
  return digits
}

export function App() {
  const { data, state, error } = useDashboardData()
  const { selectedFornSet, toggleForn, clearAll, matchesForn } = useGlobalFilter()

  const hasFilter = selectedFornSet.size > 0

  // Opções para o dropdown — fonte: relatório de contratos (autoritativo) + fallback R3/R4
  // Uma linha por CNPJ único; filiais com mesmo nome ganham checkboxes independentes
  const fornOptions = useMemo(() => {
    if (!data) return []
    const seen = new Set<string>()
    const opts: { key: string; label: string }[] = []
    Object.entries(data.fornCNPJMap)
      .sort(([a], [b]) => a.localeCompare(b, 'pt-BR', { sensitivity: 'base' }))
      .forEach(([name, cnpjs]) => {
        if (cnpjs.length > 0) {
          cnpjs.forEach(cnpj => {
            const key = `${name}|||${cnpj}`
            if (!seen.has(key)) {
              seen.add(key)
              opts.push({ key, label: `${name} — ${fmtCNPJ(cnpj)}` })
            }
          })
        } else {
          if (!seen.has(name)) {
            seen.add(name)
            opts.push({ key: name, label: name })
          }
        }
      })
    return opts
  }, [data])

  // Dados filtrados
  const sitFiltered = useMemo(() => {
    if (!data) return []
    return hasFilter ? data.sit_tabela.filter(r => matchesForn(r.Fornecedor, r.CNPJ_Forn)) : data.sit_tabela
  }, [data, hasFilter, matchesForn])

  const fornSitFiltered = useMemo(() => {
    if (!data) return []
    return hasFilter ? data.forn_sit.filter(r => matchesForn(r.Fornecedor, r.CNPJ_Forn)) : data.forn_sit
  }, [data, hasFilter, matchesForn])

  const tabelaFiltered = useMemo(() => {
    if (!data) return []
    return hasFilter ? data.tabela.filter(r => matchesForn(r.Fornecedor, r.CNPJ_Forn)) : data.tabela
  }, [data, hasFilter, matchesForn])

  const contratosFiltered = useMemo(() => {
    if (!data) return []
    return hasFilter ? data.contratosData.filter(f => matchesForn(f.nome, f.cnpj)) : data.contratosData
  }, [data, hasFilter, matchesForn])

  // KPIs reativos ao filtro
  const kpis = useMemo(() => {
    if (!data) return null
    if (!hasFilter) {
      return {
        total_forn_geral:        data.total_forn_geral,
        total_forn_com_execucao: data.total_forn_com_execucao,
        r4_total:                data.r4_total,
        total_docs_sit:          data.total_docs_sit,
        docs_aprovados:          data.docs_aprovados,
        docs_reprovados:         data.docs_reprovados,
        docs_nao_enviados:       data.docs_nao_enviados,
        docs_aguard_sub:         data.docs_aguard_sub,
        docs_em_analise:         data.docs_em_analise,
        docs_vencidos:           data.docs_vencidos,
      }
    }
    const sit  = sitFiltered
    const forn = fornSitFiltered
    return {
      total_forn_geral:        data.total_forn_geral,
      total_forn_com_execucao: data.total_forn_com_execucao,
      r4_total:                forn.length,
      total_docs_sit:          sit.length,
      docs_aprovados:
        sit.filter(r => r.Status === 'Aprovado').length
        + forn.filter(r => r.Status === 'Aprovado').length
        + forn.filter(r => r.Status === 'Regular').length,
      docs_reprovados:
        sit.filter(r => r.Status === 'Reprovado').length
        + forn.filter(r => r.Status === 'Reprovado').length
        + forn.filter(r => r.Status === 'Irregular').length,
      docs_nao_enviados:
        sit.filter(r => r.Status === 'Não anexado').length
        + forn.filter(r => r.Status === 'Não Anexado').length,
      docs_aguard_sub:         sit.filter(r => r.Status === 'Aguardando Submissão').length,
      docs_em_analise:
        sit.filter(r => r.Status === 'Em Análise').length
        + forn.filter(r => r.Status === 'Em análise').length
        + forn.filter(r => r.Status === 'Não Analisado').length,
      docs_vencidos:           forn.filter(r => r.Status === 'Vencido').length,
    }
  }, [data, hasFilter, sitFiltered, fornSitFiltered])

  // Sub-KPIs R4 reativos
  const r4Kpis = useMemo(() => {
    if (!data) return null
    if (!hasFilter) {
      return {
        r4_total:          data.r4_total,
        r4_aprovado:       data.r4_aprovado,
        r4_reprovado:      data.r4_reprovado,
        r4_nao_anex:       data.r4_nao_anex,
        r4_em_analise:     data.r4_em_analise,
        r4_vencido:        data.r4_vencido,
        r4_regular:        data.r4_regular,
        r4_nao_analisado:  data.r4_nao_analisado,
        r4_irregular:      data.r4_irregular,
        r4_pct_nc:         data.r4_pct_nc,
        r4_pct_c:          data.r4_pct_c,
        r4_fornecedores:   data.r4_fornecedores,
      }
    }
    const forn          = fornSitFiltered
    const total         = forn.length
    const aprovado      = forn.filter(r => r.Status === 'Aprovado').length
    const reprovado     = forn.filter(r => r.Status === 'Reprovado').length
    const nao_anex      = forn.filter(r => r.Status === 'Não Anexado').length
    const em_anal       = forn.filter(r => r.Status === 'Em análise').length
    const vencido       = forn.filter(r => r.Status === 'Vencido').length
    const regular       = forn.filter(r => r.Status === 'Regular').length
    const nao_analisado = forn.filter(r => r.Status === 'Não Analisado').length
    const irregular     = forn.filter(r => r.Status === 'Irregular').length
    const nao_conf      = reprovado + nao_anex + em_anal + vencido + nao_analisado + irregular
    return {
      r4_total:          total,
      r4_aprovado:       aprovado,
      r4_reprovado:      reprovado,
      r4_nao_anex:       nao_anex,
      r4_em_analise:     em_anal,
      r4_vencido:        vencido,
      r4_regular:        regular,
      r4_nao_analisado:  nao_analisado,
      r4_irregular:      irregular,
      r4_pct_nc:         total > 0 ? Math.round(nao_conf / total * 1000) / 10 : 0,
      r4_pct_c:          total > 0 ? Math.round((aprovado + regular) / total * 1000) / 10 : 0,
      r4_fornecedores:   new Set(forn.map(r => r.Fornecedor)).size,
    }
  }, [data, hasFilter, fornSitFiltered])

  if (state === 'loading' || state === 'idle') {
    return (
      <div className="min-h-screen bg-[#F8F9FA] flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-[#0E8FA3] border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-[#0E8FA3] font-semibold text-lg">Carregando dados...</p>
          <p className="text-gray-400 text-sm mt-1">Lendo arquivos CSV da plataforma Efcaz</p>
        </div>
      </div>
    )
  }

  if (state === 'error' || !data || !kpis || !r4Kpis) {
    return (
      <div className="min-h-screen bg-[#F8F9FA] flex items-center justify-center">
        <div className="bg-white rounded-xl shadow-md p-8 max-w-lg text-center">
          <div className="text-5xl mb-4">⚠️</div>
          <h2 className="text-xl font-bold text-red-600 mb-2">Erro ao carregar dados</h2>
          <p className="text-gray-500 text-sm mb-4">{error}</p>
          <div className="bg-gray-50 rounded-lg p-4 text-left text-xs text-gray-600">
            <p className="font-semibold mb-1">Verifique:</p>
            <ul className="list-disc list-inside space-y-1">
              <li>O servidor Vite está rodando (execute iniciar.bat)</li>
              <li>Os arquivos CSV estão em <code>dashboard-react/data/</code></li>
            </ul>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div id="dashboard-root" className="min-h-screen bg-[#F8F9FA] font-sans">
      <Header geradoEm={data.geradoEm} />

      <GlobalFilter
        fornOptions={fornOptions}
        selectedFornSet={selectedFornSet}
        onFornToggle={toggleForn}
        onFornClear={clearAll}
        onClear={clearAll}
      />

      <div className="max-w-[1400px] mx-auto px-5 py-6">

        {/* KPIs — 2 globais somem quando filtro ativo */}
        <KPIGrid {...kpis} hideGlobal={hasFilter} />

        {/* 3 donuts de conformidade */}
        <ConformidadeCharts sitData={sitFiltered} fornData={fornSitFiltered} />

        {/* Situação R3 — Drill-Down interativo + Modo Agrupado */}
        <Section title="Situação Documental por Terceiro — Drill-Down Interativo">
          <R3Section data={sitFiltered} geradoEm={data.geradoEm} />
        </Section>

        {/* Situação R4 */}
        <Section title="Situação Documental da Empresa (Documentação Corporativa)">
          <SituacaoEmpresaSection data={fornSitFiltered} gfForn="" geradoEm={data.geradoEm} {...r4Kpis} />
        </Section>

        {/* Pendências */}
        <Section title="Detalhamento das Pendências (com Competência)">
          <PendenciasSection data={tabelaFiltered} gfForn="" competencias={data.competencias} geradoEm={data.geradoEm} />
        </Section>

        {/* Contratos por Fornecedor */}
        <Section title={`Contratos por Fornecedor — Drill-Down Interativo`}>
          <ContratosSection data={contratosFiltered} />
        </Section>

        {/* Fornecedores sem Execução */}
        <Section title={`Fornecedor sem interação com a plataforma — ${data.sem_execucao.length}`}>
          <p className="text-[12px] text-[#666] mb-3">
            Cadastrados na plataforma mas sem nenhuma interação registrada em R3 (terceiros) ou R4 (corporativo).
            Verificar se estão ativos e se devem ser engajados.
          </p>
          <div className="bg-white rounded-xl shadow-sm p-4">
            <div className="overflow-x-auto">
              <table className="w-full text-[13px] border-collapse">
                <thead>
                  <tr className="bg-[#0E8FA3] text-white">
                    <th className="px-3 py-2.5 text-left font-bold">Razão Social</th>
                    <th className="px-3 py-2.5 text-left font-bold">CPF/CNPJ</th>
                  </tr>
                </thead>
                <tbody>
                  {data.sem_execucao.map((r, i) => (
                    <tr key={i} className={`border-b border-[#e5eef1] hover:bg-[#d4eef3] ${i % 2 === 1 ? 'bg-[#f0f8fa]' : ''}`}>
                      <td className="px-3 py-2">{r.Razao_Social || '—'}</td>
                      <td className="px-3 py-2 font-mono text-sm">{r.CPF_CNPJ || '—'}</td>
                    </tr>
                  ))}
                  {data.sem_execucao.length === 0 && (
                    <tr>
                      <td colSpan={2} className="px-3 py-6 text-center text-[#999]">
                        Todos os fornecedores possuem execução na plataforma
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </Section>

        <footer className="text-center text-gray-400 text-xs py-6 mt-4 border-t border-gray-200">
          Dashboard gerado automaticamente pela plataforma Efcaz &mdash; {data.geradoEm} &mdash; Uso interno
        </footer>

      </div>
    </div>
  )
}
