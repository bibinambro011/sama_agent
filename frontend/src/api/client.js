import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

export const chat = (message, image_b64 = null, request_type = null, feedback = null) =>
  api.post('/chat', { message, image_b64, request_type, feedback }).then(r => r.data)

export const calcPricing = (data) =>
  api.post('/pricing', data).then(r => r.data)

export const saveItem = (item_type, title, content, feedback = null) =>
  api.post('/save', { item_type, title, content, feedback }).then(r => r.data)

export const listSaved = (item_type = null) =>
  api.get('/saved', { params: item_type ? { item_type } : {} }).then(r => r.data)

export const getSaved = (id) =>
  api.get(`/saved/${id}`).then(r => r.data)

export const addFeedback = (id, feedback) => {
  const form = new FormData()
  form.append('feedback', feedback)
  return api.post(`/saved/${id}/feedback`, form).then(r => r.data)
}

export const deleteItem = (id) =>
  api.delete(`/saved/${id}`).then(r => r.data)

export const exportCsv = (id) =>
  `${window.location.origin}/api/saved/${id}/export-csv`

// ── Business Profile ──────────────────────────────────────────────────────────────
export const getProfile = () => api.get('/profile').then(r => r.data)
export const saveProfile = (data) => api.post('/profile', data).then(r => r.data)

// ── Rules ──────────────────────────────────────────────────────────────────────────
export const listRules = () => api.get('/rules').then(r => r.data)
export const createRule = (rule) => api.post('/rules', rule).then(r => r.data)
export const toggleRule = (id, active) => api.patch(`/rules/${id}`, null, { params: { active } }).then(r => r.data)
export const deleteRule = (id) => api.delete(`/rules/${id}`).then(r => r.data)

// ── Banned Phrases ─────────────────────────────────────────────────────────────
export const listBannedPhrases = () => api.get('/banned-phrases').then(r => r.data)
export const addBannedPhrase = (phrase) => api.post('/banned-phrases', { phrase }).then(r => r.data)
export const toggleBannedPhrase = (id, active) => api.patch(`/banned-phrases/${id}`, null, { params: { active } }).then(r => r.data)
export const deleteBannedPhrase = (id) => api.delete(`/banned-phrases/${id}`).then(r => r.data)

// ── Logs ─────────────────────────────────────────────────────────────────────────────
export const getLogs = (limit = 50) => api.get('/logs', { params: { limit } }).then(r => r.data)
