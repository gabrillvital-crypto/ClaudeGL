import { useState, useEffect } from 'react'
import { loadAllCSVs } from '../utils/csvLoader'
import { processAllData } from '../utils/dataProcessing'
import type { DashboardData } from '../types'

type LoadState = 'idle' | 'loading' | 'success' | 'error'

export function useDashboardData() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [state, setState] = useState<LoadState>('idle')
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setState('loading')
    loadAllCSVs()
      .then(({ rawPend, rawTerc, rawSit, rawFornSit, rawFornCad, rawContratos, rawBuscaAuto }) => {
        const processed = processAllData(rawPend, rawTerc, rawSit, rawFornSit, rawFornCad, rawContratos, rawBuscaAuto)
        setData(processed)
        setState('success')
      })
      .catch(err => {
        console.error('Failed to load dashboard data:', err)
        setError(String(err))
        setState('error')
      })
  }, [])

  return { data, state, error }
}
