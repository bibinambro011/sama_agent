import { useState } from 'react'
import { chat } from '../api/client'
import ChatInput from '../components/ChatInput'
import LoadingSpinner from '../components/LoadingSpinner'
import ResultActions from '../components/ResultActions'
import ScoreBar from '../components/ScoreBar'
import toast from 'react-hot-toast'

const SCORE_LABELS = {
  visual_appeal: 'Visual Appeal',
  sama_brand_fit: 'SAMA Brand Fit',
  wearability: 'Wearability',
  comfort: 'Comfort',
  uniqueness: 'Uniqueness',
  customer_appeal: 'Customer Appeal',
  production_feasibility: 'Production Feasibility',
  cost_feasibility: 'Cost Feasibility',
  styling_potential: 'Styling Potential',
  instagram_potential: 'Instagram Potential',
  repeat_sale_potential: 'Repeat Sale Potential',
}

function Section({ title, items, color = 'gray' }) {
  if (!items?.length) return null
  const colors = {
    green: 'bg-green-50 border-green-200',
    red: 'bg-red-50 border-red-200',
    blue: 'bg-blue-50 border-blue-200',
    sama: 'bg-sama-50 border-sama-200',
    gray: 'bg-gray-50 border-gray-200',
  }
  return (
    <div className={`rounded-lg border p-4 ${colors[color]}`}>
      <h4 className="font-medium text-sm mb-2 text-gray-700">{title}</h4>
      <ul className="space-y-1">
        {items.map((item, i) => (
          <li key={i} className="text-sm text-gray-600 flex gap-2"><span>•</span>{item}</li>
        ))}
      </ul>
    </div>
  )
}

export default function DesignEvaluator() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [lastInput, setLastInput] = useState({ msg: '', img: null })

  const handleSubmit = async (message, imageB64, feedback = null) => {
    setLoading(true)
    setLastInput({ msg: message, img: imageB64 })
    try {
      const data = await chat(message || 'Evaluate this design', imageB64, null, feedback)
      setResult(data)
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  const ev = result?.result?.evaluation

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h2 className="text-3xl font-serif text-sama-800">Design Evaluator</h2>
        <p className="text-sm text-gray-400 mt-1">Upload a design image or describe a garment idea</p>
      </div>

      <div className="card">
        <ChatInput
          onSubmit={handleSubmit}
          loading={loading}
          placeholder='e.g. "A flowy A-line kurta with bishop sleeves in sage green linen"'
          showImageUpload
        />
      </div>

      {loading && <LoadingSpinner message="Evaluating your design..." />}

      {ev && !loading && (
        <div className="space-y-5">
          {/* Overall Score */}
          <div className="card text-center">
            <p className="text-xs text-gray-400 mb-1">Overall Score</p>
            <p className="text-5xl font-serif text-sama-600">{ev.overall_score.toFixed(1)}</p>
            <p className="text-xs text-gray-400 mt-1">out of 10</p>
          </div>

          {/* Score Bars */}
          <div className="card">
            <h3 className="font-medium text-sama-800 mb-4">Detailed Scores</h3>
            <div className="space-y-2.5">
              {Object.entries(SCORE_LABELS).map(([key, label]) => (
                <ScoreBar key={key} label={label} value={ev.scores[key]} />
              ))}
            </div>
          </div>

          {/* Critique */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <Section title="✓ What Works" items={ev.what_works} color="green" />
            <Section title="✗ What Doesn't" items={ev.what_doesnt} color="red" />
            <Section title="→ What to Change" items={ev.what_to_change} color="blue" />
            <Section title="◆ Make it More SAMA" items={ev.how_to_make_more_sama} color="sama" />
            <Section title="$ Make it More Commercial" items={ev.how_to_make_more_commercial} color="gray" />
          </div>

          {/* Design Suggestions */}
          <div className="card">
            <h3 className="font-medium text-sama-800 mb-3">Design Suggestions</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {[
                ['Retain', ev.retain],
                ['Modify', ev.modify],
                ['Sleeve Options', ev.sleeve_options],
                ['Neckline Options', ev.neckline_options],
                ['Back Options', ev.back_options],
                ['Fabric Suggestions', ev.fabric_suggestions],
                ['Embellishments', ev.embellishment_suggestions],
              ].map(([label, items]) => items?.length ? (
                <div key={label}>
                  <p className="label">{label}</p>
                  <ul className="space-y-1">
                    {items.map((item, i) => (
                      <li key={i} className="text-sm text-gray-600 flex gap-2"><span className="text-sama-400">→</span>{item}</li>
                    ))}
                  </ul>
                </div>
              ) : null)}
            </div>
          </div>

          <ResultActions
            result={result.result}
            itemType="design"
            title={`Design Evaluation — Score ${ev.overall_score.toFixed(1)}`}
            onRegenerate={(feedback) => handleSubmit(lastInput.msg, lastInput.img, feedback)}
          />
        </div>
      )}
    </div>
  )
}
