import { useState } from 'react'
import { chat } from '../api/client'
import ChatInput from '../components/ChatInput'
import LoadingSpinner from '../components/LoadingSpinner'
import ResultActions from '../components/ResultActions'
import toast from 'react-hot-toast'

const CATEGORY_COLORS = {
  'Elevated Casual': 'bg-green-50 text-green-700 border-green-200',
  'Formality': 'bg-blue-50 text-blue-700 border-blue-200',
  'Occasion': 'bg-purple-50 text-purple-700 border-purple-200',
  'Seasonal': 'bg-orange-50 text-orange-700 border-orange-200',
}

export default function FabricAnalyzer() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [lastInput, setLastInput] = useState({ msg: '', img: null })

  const handleSubmit = async (message, imageB64, feedback = null) => {
    setLoading(true)
    setLastInput({ msg: message, img: imageB64 })
    try {
      const data = await chat(message || 'Analyze this fabric', imageB64, null, feedback)
      setResult(data)
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  const analysis = result?.result?.analysis

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h2 className="text-3xl font-serif text-sama-800">Fabric Analyzer</h2>
        <p className="text-sm text-gray-400 mt-1">Upload a fabric photo or describe it in text</p>
      </div>

      <div className="card">
        <ChatInput
          onSubmit={handleSubmit}
          loading={loading}
          placeholder='e.g. "Soft ivory linen with a subtle texture" or upload a photo'
          showImageUpload
        />
      </div>

      {loading && <LoadingSpinner message="Analyzing your fabric..." />}

      {analysis && !loading && (
        <div className="space-y-5">
          {/* Properties */}
          <div className="card">
            <h3 className="font-serif text-xl text-sama-800 mb-4">Fabric Properties</h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {[
                ['Texture', analysis.texture],
                ['Weight', analysis.weight],
                ['Fall', analysis.fall],
                ['Colour', analysis.colour_description],
                ['Print', analysis.print_description],
              ].map(([k, v]) => (
                <div key={k} className="bg-sama-50 rounded-lg p-3">
                  <p className="text-xs text-gray-400 mb-1">{k}</p>
                  <p className="text-sm text-gray-700">{v}</p>
                </div>
              ))}
            </div>
            <div className="mt-3 grid grid-cols-1 sm:grid-cols-3 gap-3">
              {[
                ['Season Suitability', analysis.season_suitability],
                ['Garment Suitability', analysis.garment_suitability],
                ['Collection Fit', analysis.collection_suitability],
              ].map(([k, v]) => (
                <div key={k}>
                  <p className="label">{k}</p>
                  <div className="flex flex-wrap gap-1">
                    {v.map((item, i) => (
                      <span key={i} className="badge bg-gray-100 text-gray-600">{item}</span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Garment Concepts */}
          <div>
            <h3 className="font-serif text-xl text-sama-800 mb-3">Garment Concepts</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {analysis.garment_concepts.map((g, i) => (
                <div key={i} className={`card border ${CATEGORY_COLORS[g.category] || 'border-gray-200'}`}>
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="font-medium text-gray-800">{g.name}</h4>
                    <span className={`badge border ${CATEGORY_COLORS[g.category]}`}>{g.category}</span>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">{g.description}</p>
                  <p className="text-xs text-gray-400 italic">{g.why_it_works}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Recommendation */}
          <div className="card bg-sama-50 border-sama-200">
            <h3 className="font-medium text-sama-800 mb-2">Recommended Direction</h3>
            <p className="text-sm font-medium text-sama-700 mb-1">{analysis.recommended_direction}</p>
            <p className="text-sm text-gray-600">{analysis.recommended_direction_reason}</p>
          </div>

          <ResultActions
            result={result.result}
            itemType="fabric"
            title={analysis.recommended_direction}
            onRegenerate={(feedback) => handleSubmit(lastInput.msg, lastInput.img, feedback)}
          />
        </div>
      )}
    </div>
  )
}
