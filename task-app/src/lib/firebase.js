import { initializeApp } from 'firebase/app'
import {
  getFirestore,
  collection,
  doc,
  addDoc,
  updateDoc,
  deleteDoc,
  getDoc,
  getDocs,
  query,
  where,
  orderBy,
} from 'firebase/firestore'

const firebaseConfig = {
  apiKey: "AIzaSyAzKrGFcrMGPN9CXI0q9VYfWV0__Q8dt4k",
  authDomain: "claudegl.firebaseapp.com",
  projectId: "claudegl",
  storageBucket: "claudegl.firebasestorage.app",
  messagingSenderId: "679635912946",
  appId: "1:679635912946:web:dcb6ca0f59cb7eacc9286b"
}

const app = initializeApp(firebaseConfig)
export const db = getFirestore(app)

// ── Helpers internos ──────────────────────────────────────────────────────────

function docToObj(d) {
  return { id: d.id, ...d.data() }
}

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

// Cache de clientes para evitar múltiplas leituras
let clientsCache = null

async function getClientsMap() {
  if (clientsCache) return clientsCache
  const snap = await getDocs(collection(db, 'clients'))
  clientsCache = {}
  snap.forEach(d => { clientsCache[d.id] = docToObj(d) })
  return clientsCache
}

function attachClient(task, clientsMap) {
  if (task.client_id && clientsMap[task.client_id]) {
    const c = clientsMap[task.client_id]
    task.clients = { name: c.name, tier: c.tier }
  } else {
    task.clients = null
  }
  return task
}

async function tasksWithClients(tasks) {
  const map = await getClientsMap()
  return tasks.map(t => attachClient({ ...t }, map))
}

// ── Seed inicial de clientes ──────────────────────────────────────────────────

const SEED_CLIENTS = [
  { name: 'Zurich', tier: 'A' }, { name: 'CSU Digital', tier: 'A' },
  { name: 'Bom Futuro', tier: 'A' }, { name: 'Eucatex', tier: 'A' },
  { name: 'Norskan', tier: 'A' }, { name: 'Soluções Terceirizadas', tier: 'A' },
  { name: 'Unimed Brasil', tier: 'A' },
  { name: 'Afonso França', tier: 'B' }, { name: 'DATA Engenharia', tier: 'B' },
  { name: 'Geistlich', tier: 'B' }, { name: 'Vinci Airports', tier: 'B' },
  { name: 'Hospital Adventista', tier: 'B' }, { name: 'Bunker One', tier: 'B' },
  { name: 'Dock Brasil', tier: 'B' }, { name: 'Cielo', tier: 'B' },
  { name: 'Sabarã', tier: 'B' }, { name: 'Agência Work On', tier: 'B' },
  { name: 'Tarkett', tier: 'B' }, { name: 'Premier Pet', tier: 'B' },
  { name: 'FPF', tier: 'B' }, { name: 'Transportes Cavalinho', tier: 'B' },
  { name: 'Pacco', tier: 'B' }, { name: 'Engesp', tier: 'B' },
  { name: 'Cebrace', tier: 'B' }, { name: 'BRG', tier: 'B' },
  { name: 'Ponsse', tier: 'B' }, { name: 'Killing SA', tier: 'B' },
  { name: 'Unimed Campo Grande', tier: 'C' }, { name: 'Asso Marítima', tier: 'C' },
  { name: 'Amboretto', tier: 'C' }, { name: 'Unimed Dourados', tier: 'C' },
  { name: 'Alumetaf', tier: 'C' }, { name: 'Advtec', tier: 'C' },
]

export async function seedClientsIfEmpty() {
  const snap = await getDocs(collection(db, 'clients'))
  if (!snap.empty) return
  for (const c of SEED_CLIENTS) {
    await addDoc(collection(db, 'clients'), { ...c, status_cs: '', notes_cs: '' })
  }
  clientsCache = null
}

// ── Tasks ────────────────────────────────────────────────────────────────────

export async function fetchTasks(tab, showDone = false, prioFilter = 'todos') {
  const snap = await getDocs(query(collection(db, 'tasks'), where('tab', '==', tab)))
  let tasks = snap.docs.map(docToObj)
  if (!showDone) tasks = tasks.filter(t => ['pending', 'in_progress'].includes(t.status))
  if (prioFilter !== 'todos') tasks = tasks.filter(t => t.priority === prioFilter)
  const result = await tasksWithClients(tasks)
  return sortTasks(result)
}

export async function fetchTasksInProgress() {
  const snap = await getDocs(query(collection(db, 'tasks'), where('status', '==', 'in_progress')))
  const tasks = snap.docs.map(docToObj)
  const result = await tasksWithClients(tasks)
  return sortTasks(result)
}

export async function fetchTasksDone(prioFilter = 'todos') {
  const snap = await getDocs(query(collection(db, 'tasks'), where('status', '==', 'done')))
  let tasks = snap.docs.map(docToObj)
  if (prioFilter !== 'todos') tasks = tasks.filter(t => t.priority === prioFilter)
  tasks.sort((a, b) => new Date(b.completed_at) - new Date(a.completed_at))
  return tasksWithClients(tasks)
}

export async function fetchTasksToday() {
  const today = new Date().toISOString().split('T')[0]
  const snap = await getDocs(query(collection(db, 'tasks'), where('deadline', '==', today), where('status', '==', 'pending')))
  const tasks = snap.docs.map(docToObj)
  const result = await tasksWithClients(tasks)
  return sortTasks(result)
}

export async function fetchTasksOverdue() {
  const today = new Date().toISOString().split('T')[0]
  const snap = await getDocs(query(collection(db, 'tasks'), where('status', '==', 'pending')))
  let tasks = snap.docs.map(docToObj).filter(t => t.deadline && t.deadline < today)
  tasks.sort((a, b) => a.deadline.localeCompare(b.deadline))
  const result = await tasksWithClients(tasks)
  return sortTasks(result)
}

export async function getTask(id) {
  const d = await getDoc(doc(db, 'tasks', id))
  if (!d.exists()) throw new Error('Task not found')
  const task = docToObj(d)
  const map = await getClientsMap()
  return attachClient(task, map)
}

export async function addTask({ tab, title, notes = '', priority = 'media', deadline = null, client_id = null }) {
  const data = {
    tab, title, notes, priority, deadline, client_id,
    status: 'pending',
    description: '',
    created_at: new Date().toISOString(),
    completed_at: null,
  }
  const ref = await addDoc(collection(db, 'tasks'), data)
  return { id: ref.id, ...data }
}

export async function updateTask(id, fields) {
  await updateDoc(doc(db, 'tasks', id), fields)
}

export async function deleteTask(id) {
  const snap = await getDocs(query(collection(db, 'checklist_items'), where('task_id', '==', id)))
  for (const d of snap.docs) await deleteDoc(d.ref)
  await deleteDoc(doc(db, 'tasks', id))
}

export async function setTaskStatus(id, status) {
  const fields = { status }
  if (status === 'done') fields.completed_at = new Date().toISOString()
  else fields.completed_at = null
  await updateTask(id, fields)
}

// ── Checklist ────────────────────────────────────────────────────────────────

export async function fetchChecklist(taskId) {
  const snap = await getDocs(query(
    collection(db, 'checklist_items'),
    where('task_id', '==', taskId),
    orderBy('position'),
  ))
  return snap.docs.map(docToObj)
}

export async function addChecklistItem(taskId, text) {
  const snap = await getDocs(query(
    collection(db, 'checklist_items'),
    where('task_id', '==', taskId),
    orderBy('position', 'desc')
  ))
  const position = snap.empty ? 1 : (snap.docs[0].data().position ?? 0) + 1
  const ref = await addDoc(collection(db, 'checklist_items'), {
    task_id: taskId, text, is_done: false, position
  })
  return { id: ref.id, task_id: taskId, text, is_done: false, position }
}

export async function toggleChecklistItem(id, isDone) {
  await updateDoc(doc(db, 'checklist_items', id), { is_done: isDone })
}

export async function deleteChecklistItem(id) {
  await deleteDoc(doc(db, 'checklist_items', id))
}

// ── Clients ──────────────────────────────────────────────────────────────────

export async function fetchClients() {
  const map = await getClientsMap()
  const clients = Object.values(map)
  return clients.sort((a, b) => {
    const tierOrder = { A: 0, 'B+': 1, B: 2, C: 3 }
    const td = (tierOrder[a.tier] ?? 9) - (tierOrder[b.tier] ?? 9)
    if (td !== 0) return td
    return a.name.localeCompare(b.name)
  })
}

// ── Checklist Bulk (para TabList) ─────────────────────────────────────────────

export async function fetchChecklistBulk(taskIds) {
  if (!taskIds.length) return []
  // Firestore suporta 'in' com até 30 itens; batch se necessário
  const chunks = []
  for (let i = 0; i < taskIds.length; i += 30) chunks.push(taskIds.slice(i, i + 30))
  const all = []
  for (const chunk of chunks) {
    const snap = await getDocs(query(collection(db, 'checklist_items'), where('task_id', 'in', chunk)))
    snap.forEach(d => all.push(docToObj(d)))
  }
  return all
}

// ── Relatório ────────────────────────────────────────────────────────────────

export async function fetchDoneRange(tabFilter, dateFrom, dateTo) {
  const snap = await getDocs(query(collection(db, 'tasks'), where('status', '==', 'done')))
  let tasks = snap.docs.map(docToObj).filter(t =>
    t.completed_at >= dateFrom && t.completed_at <= dateTo
  )
  if (tabFilter !== 'todas') tasks = tasks.filter(t => t.tab === tabFilter)
  tasks.sort((a, b) => new Date(b.completed_at) - new Date(a.completed_at))

  return Promise.all(tasks.map(async (task) => {
    const cSnap = await getDocs(query(collection(db, 'checklist_items'), where('task_id', '==', task.id)))
    task.checklist_items = cSnap.docs.map(docToObj)
    return task
  }))
}
