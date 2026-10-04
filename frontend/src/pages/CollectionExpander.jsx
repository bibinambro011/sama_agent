import { useState } from 'react'
import { chat } from '../api/client'
import ChatInput from '../components/ChatInput'
import LoadingSpinner from '../components/LoadingSpinner'
import ResultActions from '../components/ResultActions'
import toast from 'react-hot-toast'

function PieceBadges({ piece }) {
  const tierColor = { Entry: 'bg-green-100 text-green-700', Mid: 'bg-blue-100 text-blue-700', Premium: 'bg-purple-100 text-purple-700' }
  const complexColor = { Low: 'badge-low', Medium: 'badge-medium', High: 'badge-high' }
  return (
    <div className="flex flex-wrap gap-1.5 mt-2">
      <span className={`badge ${tierColor[piece.price_tier]}`}>{piece.price_tier}</span>
      <span className={complexColor[piece.production_complexity]}>{piece.production_complexity}</span>
      {piece.repeat_production_suitable && <span className="badge bg-blue-50 text-blue-600">Repeat-ready</span>}
    </div>
  )
}

function PieceCard({ piece }) {
  return (
    <div className="card">
      <div className="flex items-start justify-between">
        <h4 className="font-medium text-gray-800">{piece.name}</h4>
        <span className="text-xs text-gray-400">{piece.variation_type}</span>
      </div>
      <p className="text-sm text-gray-600 mt-1">{piece.description}</p>
      <PieceBadges piece={piece} />
    </div>
  )
}

export default function CollectionExpander() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [lastInput, setLastInput] = useState({ msg: '', img: null })

  const handleSubmit = async (message, imageB64, feedback = null) => {
    setLoading(true)
    setLastInput({ msg: message, img: imageB64 })
    try {
      const data = await chat(message, imageB64, null, feedback)
      setResult(data)
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  const exp = result?.result?.expanded

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h2 className="text-3xl font-serif text-sama-800">Collection Expander</h2>
        <p className="text-sm text-gray-400 mt-1">Describe one garment — SAMA will expand it into a full mini collection</p>
      </div>

      <div className="card">
        <ChatInput
          onSubmit={handleSubmit}
          loading={loading}
          placeholder='e.g. "Expand this ivory linen A-line kurta with a keyhole neckline"'
          showImageUpload
        />
      </div>

      {loading && <LoadingSpinner message="Expanding your collection..." />}

      {exp && !loading && (
        <div className="space-y-6">
          <div className="card bg-sama-50 border-sama-200">
            <p className="text-xs text-gray-400 mb-1">Base Garment</p>
            <p className="font-medium text-sama-800">{exp.base_garment}</p>
          </div>

          {[
            ['Sleeve Variations', exp.sleeve_variations],
            ['Neckline Variations', exp.neckline_variations],
            ['Colourways', exp.colourways],
            ['Matching Bottoms', exp.bottoms],
          ].map(([title, pieces]) => (
            <div key={title}>
              <h3 className="font-serif text-lg text-sama-800 mb-3">{title}</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                {pieces.map((p, i) => <PieceCard key={i} piece={p} />)}
              </div>
            </div>
          ))}

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <h3 className="font-serif text-lg text-sama-800 mb-3">Premium Version</h3>
              <PieceCard piece={exp.premium_version} />
            </div>
            <div>
              <h3 className="font-serif text-lg text-sama-800 mb-3">Entry Price Version</h3>
              <PieceCard piece={exp.entry_price_version} />
            </div>
          </div>

          {/* Content Ideas */}
          <div>
            <h3 className="font-serif text-lg text-sama-800 mb-3">Content Ideas</h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {exp.content_ideas.map((c, i) => {
                const formatColor = { Reel: 'bg-red-50 border-red-200', Photo: 'bg-blue-50 border-blue-200', Story: 'bg-purple-50 border-purple-200' }
                return (
                  <div key={i} className={`card border ${formatColor[c.format] || ''}`}>
                    <span className="badge bg-gray-100 text-gray-600 mb-2">{c.format}</span>
                    <h4 className="font-medium text-sm text-gray-800 mb-1">{c.concept}</h4>
                    <p className="text-xs text-gray-500">{c.description}</p>
                  </div>
                )
              })}
            </div>
          </div>

          <ResultActions
            result={result.result}
            itemType="expansion"
            title={exp.base_garment}
            onRegenerate={(feedback) => handleSubmit(lastInput.msg, lastInput.img, feedback)}
          />
        </div>
      )}
    </div>
  )
}
