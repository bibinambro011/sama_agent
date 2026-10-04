import { useState } from 'react'
import { chat, exportCsv } from '../api/client'
import ChatInput from '../components/ChatInput'
import LoadingSpinner from '../components/LoadingSpinner'
import ResultActions from '../components/ResultActions'
import toast from 'react-hot-toast'
import { Download } from 'lucide-react'

const PHASE_COLORS = {
  'Pre-launch': 'bg-gray-100 text-gray-600',
  'Teaser': 'bg-yellow-100 text-yellow-700',
  'Preview': 'bg-orange-100 text-orange-700',
  'Launch': 'bg-sama-100 text-sama-700',
  'Post-launch': 'bg-green-100 text-green-700',
}

export default function LaunchPlanner() {
  const [result, setResult] = useState(null)
  const [savedId, setSavedId] = useState(null)
  const [loading, setLoading] = useState(false)
  const [lastInput, setLastInput] = useState('')

  const handleSubmit = async (message, feedback = null) => {
    setLoading(true)
    setLastInput(message)
    try {
      const data = await chat(message, null, null, feedback)
      setResult(data)
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  const plan = result?.result?.plan

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h2 className="text-3xl font-serif text-sama-800">Launch Planner</h2>
        <p className="text-sm text-gray-400 mt-1">Get a day-by-day launch timeline from T-21 to T+7</p>
      </div>

      <div className="card">
        <ChatInput
          onSubmit={handleSubmit}
          loading={loading}
          placeholder='e.g. "Plan the launch for my Onam collection of 8 pieces"'
        />
      </div>

      {loading && <LoadingSpinner message="Planning your launch..." />}

      {plan && !loading && (
        <div className="space-y-5">
          <div className="flex items-center justify-between">
            <h3 className="font-serif text-xl text-sama-800">{plan.collection_name}</h3>
            {savedId && (
              <a href={exportCsv(savedId)} className="btn-secondary flex items-center gap-1.5 text-sm">
                <Download size={14} /> Export CSV
              </a>
            )}
          </div>

          {/* Timeline */}
          <div className="card overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-100">
                  <th className="text-left py-2 pr-4 text-xs text-gray-400 font-medium">Day</th>
                  <th className="text-left py-2 pr-4 text-xs text-gray-400 font-medium">Phase</th>
                  <th className="text-left py-2 pr-4 text-xs text-gray-400 font-medium">Content</th>
                  <th className="text-left py-2 pr-4 text-xs text-gray-400 font-medium">Platform</th>
                  <th className="text-left py-2 text-xs text-gray-400 font-medium">Notes</th>
                </tr>
              </thead>
              <tbody>
                {plan.timeline.map((day, i) => (
                  <tr key={i} className="border-b border-gray-50 hover:bg-sama-50/30">
                    <td className="py-2 pr-4 font-medium text-sama-700 whitespace-nowrap">{day.date_label}</td>
                    <td className="py-2 pr-4">
                      <span className={`badge ${PHASE_COLORS[day.phase] || 'bg-gray-100 text-gray-600'}`}>
                        {day.phase}
                      </span>
                    </td>
                    <td className="py-2 pr-4 text-gray-700">{day.content_item}</td>
                    <td className="py-2 pr-4 text-gray-500 whitespace-nowrap">{day.platform}</td>
                    <td className="py-2 text-gray-400 text-xs">{day.notes}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <ResultActions
            result={result.result}
            itemType="launch"
            title={plan.collection_name}
            onRegenerate={(feedback) => handleSubmit(lastInput, feedback)}
          />
        </div>
      )}
    </div>
  )
}
