// Paleta oficial Efcaz — verificada via CSS do site efcaz.com.br (09/07/2026)
export const TEAL         = '#14B3CC'   // cyan-400 — primária (botões, links, accent)
export const TEAL_HOVER   = '#0BA2B9'   // cyan-500 — hover
export const TEAL_DARK    = '#0E8FA3'   // cyan-600 — dark variant
export const NAVY         = '#153C5C'   // navy-700 — sidebar, elementos escuros
export const NAVY_DARK    = '#112F47'   // navy-800 — hover do navy
export const TEAL_SOFT    = 'rgba(20, 179, 204, 0.10)'  // fundo hover suave

export const PRIORITY = {
  alta:  { label: 'Alta',  color: '#B83232', bg: '#FDECEA', ring: 'ring-red-300' },
  media: { label: 'Média', color: '#8B6A10', bg: '#FDF4DC', ring: 'ring-amber-300' },
  baixa: { label: 'Baixa', color: '#27875A', bg: '#E8F7EE', ring: 'ring-green-300' },
}

export const IN_PROGRESS_COLOR = '#5B7FA6'

export function fmtDate(iso) {
  if (!iso) return ''
  const [y, m, d] = iso.split('-')
  return `${d}/${m}/${y}`
}

export function isoToday() {
  return new Date().toISOString().split('T')[0]
}

export function deadlineStatus(deadline) {
  if (!deadline) return null
  const today = isoToday()
  if (deadline < today) return 'overdue'
  if (deadline === today) return 'today'
  return 'future'
}

export function fmtDateTime(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  return d.toLocaleDateString('pt-BR') + ' às ' + d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
}

export function generateReportHTML(tasks, tabFilter, dateFrom, dateTo) {
  const tabLabel = { todas: 'Todas as abas', pessoal: 'Pessoal', profissional: 'Profissional Efcaz' }
  const now = new Date().toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })
  const period = `${fmtDate(dateFrom)} a ${fmtDate(dateTo)}`

  const nAlta = tasks.filter(t => t.priority === 'alta').length
  const nProf = tasks.filter(t => t.tab === 'profissional').length
  const nPes  = tasks.filter(t => t.tab === 'pessoal').length

  let body = ''
  if (!tasks.length) {
    body = '<div class="empty">Nenhuma tarefa concluída no período.</div>'
  } else {
    let curTab = null
    for (const t of tasks) {
      if (t.tab !== curTab) {
        curTab = t.tab
        body += `<div class="sec">${curTab === 'pessoal' ? 'Pessoal' : 'Profissional Efcaz'}</div>`
      }
      const p = PRIORITY[t.priority] || PRIORITY.media
      const when = t.completed_at ? `Concluída em ${fmtDateTime(t.completed_at)}` : ''
      const ck = (t.checklist_items || []).map(i =>
        `<li class="${i.is_done ? 'done' : 'todo'}">${i.text}</li>`
      ).join('')
      body += `
        <div class="task">
          <div class="ttl"><span class="badge" style="background:${p.color}">${p.label}</span>${t.title}</div>
          ${t.description ? `<div class="desc">${t.description}</div>` : ''}
          ${t.notes ? `<div class="note">${t.notes}</div>` : ''}
          ${ck ? `<ul class="ck">${ck}</ul>` : ''}
          <div class="meta">${when}</div>
        </div>`
    }
  }

  return `<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">
<title>Relatório — Efcaz CS</title>
<style>
body{font-family:Calibri,Arial,sans-serif;margin:0;background:#f4f6f7;color:#333}
.hdr{background:#14B3CC;color:#fff;padding:24px 40px}
.hdr h1{margin:0;font-size:22px}.hdr p{margin:4px 0 0;opacity:.8;font-size:13px}
.body{padding:28px 40px}
.stats{display:flex;gap:16px;margin-bottom:28px}
.stat{background:#fff;border-radius:8px;padding:14px 22px;text-align:center;border-top:4px solid #14B3CC;min-width:100px}
.stat .n{font-size:28px;font-weight:bold;color:#14B3CC}.stat .l{font-size:11px;color:#999;margin-top:2px}
.sec{font-size:11px;font-weight:bold;color:#aaa;text-transform:uppercase;letter-spacing:1px;margin:24px 0 10px;padding-bottom:6px;border-bottom:1px solid #e0e0e0}
.task{background:#fff;border-radius:8px;margin-bottom:8px;padding:14px 18px;border-left:4px solid #14B3CC}
.ttl{font-size:14px;font-weight:bold;margin-bottom:4px}
.desc,.note{font-size:12px;color:#666;margin-bottom:4px}.note{font-style:italic}
.badge{display:inline-block;padding:2px 8px;border-radius:4px;font-size:10px;font-weight:bold;color:#fff;margin-right:8px}
ul.ck{list-style:none;padding:0;margin:6px 0 0}
ul.ck li{font-size:12px;color:#666;padding:2px 0}
ul.ck li.done{color:#059669}ul.ck li.done::before{content:"☑  "}ul.ck li.todo::before{content:"☐  "}
.meta{font-size:11px;color:#bbb;margin-top:8px}
.empty{text-align:center;color:#bbb;padding:50px;font-size:14px}
</style></head><body>
<div class="hdr"><h1>Relatório de Atividades: ${period}</h1><p>${tabLabel[tabFilter] || tabFilter} · Gerado em ${now}</p></div>
<div class="body">
<div class="stats">
  <div class="stat"><div class="n">${tasks.length}</div><div class="l">Concluídas</div></div>
  <div class="stat"><div class="n">${nAlta}</div><div class="l">Prioridade Alta</div></div>
  <div class="stat"><div class="n">${nProf}</div><div class="l">Profissional</div></div>
  <div class="stat"><div class="n">${nPes}</div><div class="l">Pessoal</div></div>
</div>
${body}
</div></body></html>`
}
