import { useState } from 'react'
import { chat } from '../api/client'
import ChatInput from '../components/ChatInput'
import LoadingSpinner from '../components/LoadingSpinner'
import ResultActions from '../components/ResultActions'
import toast from 'react-hot-toast'

function ComplexityBadge({ value }) {
  const cls = { Low: 'badge-low', Medium: 'badge-medium', High: 'badge-high' }[value] || 'badge'
  return <span className={cls}>{value}</span>
}

function DesignCard({ design, index }) {
  return (
    <div className="card space-y-3">
      <div className="flex items-start justify-between gap-2">
        <h3 className="font-serif text-lg text-sama-800">{index + 1}. {design.garment_type}</h3>
        <ComplexityBadge value={design.production_complexity} />
      </div>
      <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-sm">
        {[
          ['Silhouette', design.silhouette],
          ['Neckline', design.neckline],
          ['Sleeve', design.sleeve],
          ['Length', design.length],
          ['Fabric', design.fabric],
          ['Colour', design.colour],
        ].map(([k, v]) => (
          <div key={k}>
            <span className="text-gray-400 text-xs">{k}: </span>
            <span className="text-gray-700">{v}</span>
          </div>
        ))}
      </div>
      <p className="text-sm text-gray-600 italic">{design.special_detail}</p>
      <p className="text-sm text-sama-700">💡 {design.why_customer_buys}</p>
      <div className="flex items-center gap-2 text-xs text-gray-400">
        <span>Occasion: {design.occasion}</span>
        {design.repeat_production_suitable && (
          <span className="badge bg-blue-50 text-blue-600">Repeat-ready</span>
        )}
      </div>
    </div>
  )
}

export default function CollectionPlanner() {
  const [result, setResult] = useState(null)
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
        <h2 className="text-3xl font-serif text-sama-800">Collection Planner</h2>
        <p className="text-sm text-gray-400 mt-1">Describe a collection, season, or occasion</p>
      </div>

      <div className="card">
        <ChatInput
          onSubmit={handleSubmit}
          loading={loading}
          placeholder='e.g. "Create a collection for Onam" or "designs for monsoon"'
        />
      </div>

      {loading && <LoadingSpinner message="Planning your collection..." />}

      {plan && !loading && (
        <div className="space-y-5">
          {/* Assumptions */}
          {plan.assumptions?.length > 0 && (
            <div className="card bg-amber-50 border-amber-200">
              <h3 className="font-medium text-amber-800 mb-2 text-sm">Assumptions Made</h3>
              <ul className="space-y-1">
                {plan.assumptions.map((a, i) => (
                  <li key={i} className="text-sm text-amber-700 flex gap-2"><span>•</span>{a}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Collection Direction */}
          <div className="card">
            <h3 className="font-serif text-xl text-sama-800 mb-3">Collection Direction</h3>
            <div className="space-y-3">
              <div>
                <span className="label">Name Ideas</span>
                <div className="flex flex-wrap gap-2">
                  {plan.collection_direction.name_ideas.map((n, i) => (
                    <span key={i} className="badge bg-sama-100 text-sama-700 text-sm px-3 py-1">{n}</span>
                  ))}
                </div>
              </div>
              <div>
                <span className="label">Core Story</span>
                <p className="text-sm text-gray-700">{plan.collection_direction.core_story}</p>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <span className="label">Mood</span>
                  <p className="text-sm text-gray-700">{plan.collection_direction.mood}</p>
                </div>
                <div>
                  <span className="label">Price Positioning</span>
                  <p className="text-sm text-gray-700">{plan.collection_direction.price_positioning}</p>
                </div>
              </div>
              <div>
                <span className="label">Colour Palette</span>
                <div className="flex flex-wrap gap-2">
                  {plan.collection_direction.colour_palette.map((c, i) => (
                    <span key={i} className="badge bg-gray-100 text-gray-600">{c}</span>
                  ))}
                </div>
              </div>
              <div>
                <span className="label">Uniquely SAMA</span>
                <p className="text-sm text-sama-700">{plan.collection_direction.uniquely_sama}</p>
              </div>
              <div className="bg-red-50 rounded-lg p-3">
                <span className="label text-red-500">What It Should NOT Become</span>
                <p className="text-sm text-red-600">{plan.collection_direction.what_it_should_not_become}</p>
              </div>
            </div>
          </div>

          {/* Design Ideas */}
          <div>
            <h3 className="font-serif text-xl text-sama-800 mb-3">Design Ideas</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {plan.design_ideas.map((d, i) => <DesignCard key={i} design={d} index={i} />)}
            </div>
          </div>

          {/* Content, Launch, Business */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="card">
              <h3 className="font-medium text-sama-800 mb-2">Content Ideas</h3>
              <ul className="space-y-1.5">
                {plan.content_ideas.map((c, i) => (
                  <li key={i} className="text-sm text-gray-600 flex gap-2"><span className="text-sama-400">→</span>{c}</li>
                ))}
              </ul>
            </div>
            <div className="card">
              <h3 className="font-medium text-sama-800 mb-2">Launch Strategy</h3>
              <p className="text-sm text-gray-600">{plan.launch_strategy}</p>
            </div>
            <div className="card">
              <h3 className="font-medium text-sama-800 mb-2">Business Strategy</h3>
              <p className="text-sm text-gray-600">{plan.business_strategy}</p>
            </div>
          </div>

          {/* Immediate Actions */}
          <div className="card bg-sama-50 border-sama-200">
            <h3 className="font-medium text-sama-800 mb-3">3 Immediate Actions</h3>
            <div className="space-y-2">
              {plan.immediate_actions.map((a, i) => (
                <div key={i} className="flex gap-3 items-start">
                  <span className="w-6 h-6 rounded-full bg-sama-500 text-white text-xs flex items-center justify-center shrink-0 mt-0.5">{i + 1}</span>
                  <p className="text-sm text-sama-800">{a}</p>
                </div>
              ))}
            </div>
          </div>

          <ResultActions
            result={result.result}
            itemType="collection"
            title={plan.collection_direction.name_ideas[0] || 'Collection'}
            onRegenerate={() => handleSubmit(lastInput)}
          />
        </div>
      )}
    </div>
  )
}
