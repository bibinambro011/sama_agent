import { useState, useEffect } from 'react'
import { listSaved, deleteItem, exportCsv } from '../api/client'
import toast from 'react-hot-toast'
import { Trash2, Download, ChevronDown, ChevronUp } from 'lucide-react'

const TYPE_LABELS = {
  collection: 'Collection',
  fabric: 'Fabric Analysis',
  design: 'Design Evaluation',
  expansion: 'Collection Expansion',
  content: 'Content Pack',
  launch: 'Launch Plan',
}

function ItemCard({ item, onDelete }) {
  const [expanded, setExpanded] = useState(false)
  const content = JSON.parse(item.content)

  return (
    <div className="card">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="badge bg-sama-100 text-sama-700">{TYPE_LABELS[item.item_type] || item.item_type}</span>
            <span className="text-xs text-gray-400">{new Date(item.created_at).toLocaleDateString()}</span>
          </div>
          <h3 className="font-medium text-gray-800 truncate">{item.title}</h3>
          {item.feedback && (
            <p className="text-xs text-gray-400 mt-1 italic">Feedback: {item.feedback}</p>
          )}
        </div>
        <div className="flex items-center gap-1 shrink-0">
          {item.item_type === 'launch' && (
            <a href={exportCsv(item.id)} className="p-1.5 rounded hover:bg-gray-50 text-gray-400 hover:text-sama-600">
              <Download size={14} />
            </a>
          )}
          <button onClick={() => setExpanded(!expanded)} className="p-1.5 rounded hover:bg-gray-50 text-gray-400">
            {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
          </button>
          <button onClick={() => onDelete(item.id)} className="p-1.5 rounded hover:bg-red-50 text-gray-400 hover:text-red-500">
            <Trash2 size={14} />
          </button>
        </div>
      </div>

      {expanded && (
        <div className="mt-3 pt-3 border-t border-gray-100">
          <pre className="text-xs text-gray-500 overflow-auto max-h-64 bg-gray-50 rounded p-3 whitespace-pre-wrap">
            {JSON.stringify(content, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )
}

export default function SavedItems() {
  const [items, setItems] = useState([])
  const [filter, setFilter] = useState(null)
  const [loading, setLoading] = useState(true)

  const load = async () => {
    setLoading(true)
    try {
      const data = await listSaved(filter)
      setItems(data)
    } catch {
      toast.error('Failed to load saved items')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [filter])

  const handleDelete = async (id) => {
    try {
      await deleteItem(id)
      setItems(items.filter(i => i.id !== id))
      toast.success('Deleted')
    } catch {
      toast.error('Failed to delete')
    }
  }

  const filters = [null, 'collection', 'fabric', 'design', 'expansion', 'content', 'launch']

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h2 className="text-3xl font-serif text-sama-800">Saved Items</h2>
        <p className="text-sm text-gray-400 mt-1">Your approved outputs and brand memory</p>
      </div>

      <div className="flex flex-wrap gap-2">
        {filters.map(f => (
          <button
            key={f || 'all'}
            onClick={() => setFilter(f)}
            className={`px-3 py-1.5 rounded-lg text-sm border transition-colors ${
              filter === f ? 'bg-sama-600 text-white border-sama-600' : 'border-gray-200 text-gray-600 hover:border-sama-300'
            }`}
          >
            {f ? TYPE_LABELS[f] : 'All'}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="text-center py-12 text-gray-400 text-sm">Loading...</div>
      ) : items.length === 0 ? (
        <div className="text-center py-12 text-gray-400">
          <p className="text-lg font-serif mb-2">Nothing saved yet</p>
          <p className="text-sm">Approve results from any feature to save them here</p>
        </div>
      ) : (
        <div className="space-y-3">
          {items.map(item => (
            <ItemCard key={item.id} item={item} onDelete={handleDelete} />
          ))}
        </div>
      )}
    </div>
  )
}
