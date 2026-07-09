import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY
)

export default supabase

// ── Tasks ────────────────────────────────────────────────────────────────────

export async function fetchTasks(tab, showDone = false, prioFilter = 'todos') {
  let q = supabase
    .from('tasks')
    .select('*, clients(name, tier)')
    .eq('tab', tab)

  if (!showDone) q = q.in('status', ['pending', 'in_progress'])
  if (prioFilter !== 'todos') q = q.eq('priority', prioFilter)

  const { data, error } = await q
  if (error) throw error

  return sortTasks(data)
}

export async function fetchTasksInProgress() {
  const { data, error } = await supabase
    .from('tasks')
    .select('*, clients(name, tier)')
    .eq('status', 'in_progress')
    .order('created_at')
  if (error) throw error
  return sortTasks(data)
}

export async function fetchTasksDone(prioFilter = 'todos') {
  let q = supabase
    .from('tasks')
    .select('*, clients(name, tier)')
    .eq('status', 'done')
    .order('completed_at', { ascending: false })
  if (prioFilter !== 'todos') q = q.eq('priority', prioFilter)
  const { data, error } = await q
  if (error) throw error
  return data
}

export async function fetchTasksToday() {
  const today = new Date().toISOString().split('T')[0]
  const { data, error } = await supabase
    .from('tasks')
    .select('*, clients(name, tier)')
    .eq('deadline', today)
    .eq('status', 'pending')
  if (error) throw error
  return sortTasks(data)
}

export async function fetchTasksOverdue() {
  const today = new Date().toISOString().split('T')[0]
  const { data, error } = await supabase
    .from('tasks')
    .select('*, clients(name, tier)')
    .lt('deadline', today)
    .eq('status', 'pending')
    .order('deadline')
  if (error) throw error
  return sortTasks(data)
}

export async function getTask(id) {
  const { data, error } = await supabase
    .from('tasks')
    .select('*, clients(name, tier)')
    .eq('id', id)
    .single()
  if (error) throw error
  return data
}

export async function addTask({ tab, title, notes = '', priority = 'media', deadline = null }) {
  const { data, error } = await supabase
    .from('tasks')
    .insert({ tab, title, notes, priority, deadline, status: 'pending' })
    .select()
    .single()
  if (error) throw error
  return data
}

export async function updateTask(id, fields) {
  const { error } = await supabase.from('tasks').update(fields).eq('id', id)
  if (error) throw error
}

export async function deleteTask(id) {
  const { error } = await supabase.from('tasks').delete().eq('id', id)
  if (error) throw error
}

export async function setTaskStatus(id, status) {
  const fields = { status }
  if (status === 'done') fields.completed_at = new Date().toISOString()
  else fields.completed_at = null
  await updateTask(id, fields)
}

// ── Checklist ────────────────────────────────────────────────────────────────

export async function fetchChecklist(taskId) {
  const { data, error } = await supabase
    .from('checklist_items')
    .select('*')
    .eq('task_id', taskId)
    .order('position')
    .order('id')
  if (error) throw error
  return data
}

export async function addChecklistItem(taskId, text) {
  const { data: items } = await supabase
    .from('checklist_items')
    .select('position')
    .eq('task_id', taskId)
    .order('position', { ascending: false })
    .limit(1)
  const position = (items?.[0]?.position ?? 0) + 1
  const { data, error } = await supabase
    .from('checklist_items')
    .insert({ task_id: taskId, text, is_done: false, position })
    .select()
    .single()
  if (error) throw error
  return data
}

export async function toggleChecklistItem(id, isDone) {
  const { error } = await supabase
    .from('checklist_items')
    .update({ is_done: isDone })
    .eq('id', id)
  if (error) throw error
}

export async function deleteChecklistItem(id) {
  const { error } = await supabase.from('checklist_items').delete().eq('id', id)
  if (error) throw error
}

// ── Clients ──────────────────────────────────────────────────────────────────

export async function fetchClients() {
  const { data, error } = await supabase
    .from('clients')
    .select('*')
    .order('tier')
    .order('name')
  if (error) throw error
  return data
}

// ── Relatório ────────────────────────────────────────────────────────────────

export async function fetchDoneRange(tabFilter, dateFrom, dateTo) {
  let q = supabase
    .from('tasks')
    .select('*, checklist_items(*)')
    .eq('status', 'done')
    .gte('completed_at', dateFrom)
    .lte('completed_at', dateTo)
    .order('completed_at', { ascending: false })
  if (tabFilter !== 'todas') q = q.eq('tab', tabFilter)
  const { data, error } = await q
  if (error) throw error
  return data
}

// ── Helpers ──────────────────────────────────────────────────────────────────

function prioOrder(p) {
  return p === 'alta' ? 0 : p === 'media' ? 1 : 2
}

function statusOrder(s) {
  return s === 'in_progress' ? 0 : s === 'pending' ? 1 : 2
}

function sortTasks(tasks) {
  return [...(tasks || [])].sort((a, b) => {
    const so = statusOrder(a.status) - statusOrder(b.status)
    if (so !== 0) return so
    const po = prioOrder(a.priority) - prioOrder(b.priority)
    if (po !== 0) return po
    return new Date(a.created_at) - new Date(b.created_at)
  })
}
