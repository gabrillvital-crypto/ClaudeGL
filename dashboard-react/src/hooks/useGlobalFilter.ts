import { useState, useCallback } from 'react'

export function parseFornVal(val: string): { nome: string; cnpj: string } {
  if (!val) return { nome: '', cnpj: '' }
  const idx = val.indexOf('|||')
  return idx === -1
    ? { nome: val, cnpj: '' }
    : { nome: val.slice(0, idx), cnpj: val.slice(idx + 3) }
}

export function useGlobalFilter() {
  const [selectedFornSet, setSelectedFornSet] = useState<Set<string>>(new Set())
  const [selectedCompSet, setSelectedCompSet] = useState<Set<string>>(new Set())

  const toggleForn = useCallback((key: string) => {
    setSelectedFornSet(prev => {
      const next = new Set(prev)
      if (next.has(key)) next.delete(key)
      else next.add(key)
      return next
    })
  }, [])

  const toggleComp = useCallback((key: string) => {
    setSelectedCompSet(prev => {
      const next = new Set(prev)
      if (next.has(key)) next.delete(key)
      else next.add(key)
      return next
    })
  }, [])

  const clearComp = useCallback(() => {
    setSelectedCompSet(new Set())
  }, [])

  const clearAll = useCallback(() => {
    setSelectedFornSet(new Set())
    setSelectedCompSet(new Set())
  }, [])

  const matchesForn = useCallback(
    (rowNome: string, rowCNPJ?: string) => {
      if (selectedFornSet.size === 0) return true
      for (const raw of selectedFornSet) {
        const { nome, cnpj } = parseFornVal(raw)
        if (rowNome === nome && (!cnpj || !rowCNPJ || rowCNPJ === cnpj)) return true
      }
      return false
    },
    [selectedFornSet]
  )

  const label =
    selectedFornSet.size === 0
      ? 'Todos os fornecedores'
      : selectedFornSet.size === 1
      ? parseFornVal([...selectedFornSet][0]).nome
      : `${selectedFornSet.size} fornecedores selecionados`

  return { selectedFornSet, toggleForn, selectedCompSet, toggleComp, clearComp, clearAll, matchesForn, label }
}
