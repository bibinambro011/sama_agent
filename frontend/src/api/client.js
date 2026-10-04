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
