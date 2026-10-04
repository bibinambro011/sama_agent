import { useState } from 'react'
import { saveItem } from '../api/client'
import toast from 'react-hot-toast'
import { Check, Edit2, RefreshCw, Save } from 'lucide-react'

export default function ResultActions({ result, itemType, title, onRegenerate }) {
  const [feedback, setFeedback] = useState('')
  const [editing, setEditing] = useState(false)
  const [saved, setSaved] = useState(false)

  const handleSave = async () => {
    try {
      await saveItem(itemType, title, result, feedback || null)
      setSaved(true)
      toast.success('Saved to your collection')
    } catch {
      toast.error('Failed to save')
    }
  }

  const handleRegenerate = () => {
    onRegenerate(feedback || null)
  }

  return (
    <div className="mt-4 pt-4 border-t border-sama-100 space-y-3">
      {editing && (
        <div>
          <label className="label">Your feedback</label>
          <textarea
            className="input h-20 resize-none"
            value={feedback}
            onChange={e => setFeedback(e.target.value)}
            placeholder="e.g. make captions shorter, focus more on occasion wear, add more colour options..."
          />
          <p className="text-xs text-gray-400 mt-1">
            {feedback ? '✓ Feedback will be applied on Regenerate' : 'Leave blank to regenerate without changes'}
          </p>
        </div>
      )}
      <div className="flex flex-wrap gap-2">
        <button onClick={handleSave} disabled={saved} className="btn-primary flex items-center gap-1.5">
          {saved ? <Check size={14} /> : <Save size={14} />}
          {saved ? 'Saved' : 'Approve & Save'}
        </button>
        <button onClick={() => setEditing(!editing)} className={`btn-secondary flex items-center gap-1.5 ${editing && feedback ? 'border-sama-400 text-sama-700' : ''}`}>
          <Edit2 size={14} /> {editing ? 'Hide Feedback' : 'Edit / Feedback'}
        </button>
        <button onClick={handleRegenerate} className="btn-secondary flex items-center gap-1.5">
          <RefreshCw size={14} />
          {feedback ? 'Regenerate with Feedback' : 'Regenerate'}
        </button>
      </div>
    </div>
  )
}
