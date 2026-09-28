const EXTRACT_PROMPT = `Você é um assistente de organização de tarefas. Analise o texto abaixo e extraia TODAS as tarefas acionáveis.

Retorne APENAS um JSON array válido com objetos contendo exatamente estes campos:
- "title": título conciso e acionável (máx 80 chars)
- "priority": "alta" | "media" | "baixa"
- "notes": horário, cliente ou contexto relevante (ou "" se não houver)
- "tab": "profissional" | "pessoal"

Sem texto antes ou depois do JSON. Se não houver tarefas, retorne [].

Critérios de prioridade:
- hoje / amanhã / horário específico → "alta"
- prazo em dias → "media"
- sem prazo → "baixa"

Critérios de aba:
- trabalho / cliente / empresa / reunião / projeto → "profissional"
- compras / família / saúde / casa → "pessoal"
- dúvida → usar o destino padrão: {default_tab}

Ignore saudações, agradecimentos e informações sem ação.

Texto:
{text}`

const REFINE_PROMPT = `Você é um assistente que aprimora textos em português brasileiro.
Corrija erros gramaticais, ajuste a pontuação e reescreva de forma clara, profissional e direta — sem perder o sentido original.
Retorne APENAS o texto aprimorado, sem introdução, sem explicação, sem aspas adicionais.

Texto:
{text}`

async function callClaude(prompt) {
  const apiKey = import.meta.env.VITE_ANTHROPIC_API_KEY
  if (!apiKey) throw new Error('VITE_ANTHROPIC_API_KEY não configurada no .env')

  const res = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': apiKey,
      'anthropic-version': '2023-06-01',
      'anthropic-dangerous-direct-browser-access': 'true',
    },
    body: JSON.stringify({
      model: 'claude-haiku-4-5-20251001',
      max_tokens: 2048,
      messages: [{ role: 'user', content: prompt }],
    }),
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.error?.message || `Erro ${res.status} na API Claude`)
  }

  const json = await res.json()
  return json.content[0].text.trim()
}

export async function extractTasks(rawText, defaultTab = 'profissional') {
  const prompt = EXTRACT_PROMPT
    .replace('{text}', rawText)
    .replace('{default_tab}', defaultTab)

  const raw = await callClaude(prompt)
  const cleaned = raw.startsWith('```')
    ? raw.split('\n').filter(l => !l.trim().startsWith('```')).join('\n').trim()
    : raw

  const items = JSON.parse(cleaned)
  return items
    .filter(t => t?.title)
    .map(t => ({
      title: String(t.title).slice(0, 80),
      priority: ['alta', 'media', 'baixa'].includes(t.priority) ? t.priority : 'media',
      notes: String(t.notes || ''),
      tab: ['profissional', 'pessoal'].includes(t.tab) ? t.tab : defaultTab,
    }))
}

export async function refineText(rawText) {
  return callClaude(REFINE_PROMPT.replace('{text}', rawText))
}

// ── Extração com vínculo de cliente ──────────────────────────────────────────

const EXTRACT_CLIENTS_PROMPT = `Você é um assistente de organização de tarefas para um CS Manager.
Analise o texto abaixo e extraia TODAS as tarefas/atividades mencionadas.

Retorne APENAS um JSON array válido com objetos contendo exatamente estes campos:
- "title": título conciso e acionável (máx 80 chars)
- "priority": "alta" | "media" | "baixa"
- "notes": horário ou contexto adicional (ou "" se não houver)
- "tab": "profissional" | "pessoal"
- "client": nome EXATO de um cliente da lista abaixo, ou "" se nenhum for identificado

Lista de clientes disponíveis:
{clients_list}

Regras de cliente:
- Compare nomes mencionados no texto com a lista acima (ignore maiúsculas, acentos parciais, abreviações óbvias)
- Se houver correspondência clara, use o nome EXATO como aparece na lista
- Se o texto mencionar algo como "reunião Zurich", "proposta Dock", "alinhamento Premier Pet" → identifique o cliente
- Se não houver cliente identificável, retorne "client": ""

Critérios de prioridade:
- hoje / amanhã / horário específico / urgente → "alta"
- prazo em dias / esta semana → "media"
- sem prazo definido → "baixa"

Critérios de aba:
- trabalho / cliente / empresa / reunião / projeto → "profissional"
- compras / família / saúde / casa → "pessoal"
- dúvida → {default_tab}

Sem texto antes ou depois do JSON. Se não houver tarefas, retorne [].

Texto:
{text}`

function parseJson(raw) {
  const cleaned = raw.startsWith('```')
    ? raw.split('\n').filter(l => !l.trim().startsWith('```')).join('\n').trim()
    : raw
  return JSON.parse(cleaned)
}

export async function extractTasksWithClients(rawText, clients = [], defaultTab = 'profissional') {
  const clientsList = clients.length
    ? clients.map(c => c.name).join(', ')
    : '(sem clientes cadastrados)'

  const prompt = EXTRACT_CLIENTS_PROMPT
    .replace('{text}', rawText)
    .replace('{clients_list}', clientsList)
    .replace('{default_tab}', defaultTab)

  const raw = await callClaude(prompt)
  const items = parseJson(raw)

  // Monta mapa nome→id para lookup rápido (case-insensitive)
  const clientMap = {}
  for (const c of clients) {
    clientMap[c.name.toLowerCase()] = c
  }

  return items
    .filter(t => t?.title)
    .map(t => {
      const clientName  = String(t.client || '').trim()
      const matchedClient = clientMap[clientName.toLowerCase()] || null
      return {
        title:     String(t.title).slice(0, 80),
        priority:  ['alta', 'media', 'baixa'].includes(t.priority) ? t.priority : 'media',
        notes:     String(t.notes || ''),
        tab:       ['profissional', 'pessoal'].includes(t.tab) ? t.tab : defaultTab,
        client_id: matchedClient ? matchedClient.id : null,
        client_name: matchedClient ? matchedClient.name : '',
      }
    })
}
