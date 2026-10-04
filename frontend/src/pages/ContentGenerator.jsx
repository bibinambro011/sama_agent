import { useState } from 'react'
import { chat } from '../api/client'
import ChatInput from '../components/ChatInput'
import LoadingSpinner from '../components/LoadingSpinner'
import ResultActions from '../components/ResultActions'
import CopyButton from '../components/CopyButton'
import toast from 'react-hot-toast'

const REQUEST_TYPES = ['full content pack', 'Reels', 'Photos', 'Stories', 'Captions']

function PillarBalance({ balance }) {
  const pillars = Object.entries(balance).filter(([k]) => !['is_balanced', 'note'].includes(k))
  const total = pillars.reduce((s, [, v]) => s + v, 0)
  return (
    <div className="card">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-medium text-sama-800">Content Pillar Balance</h3>
        <span className={`badge ${balance.is_balanced ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
          {balance.is_balanced ? 'Balanced' : 'Needs Adjustment'}
        </span>
      </div>
      <div className="space-y-2">
        {pillars.map(([k, v]) => (
          <div key={k} className="flex items-center gap-3">
            <span className="text-xs text-gray-500 w-36 shrink-0 capitalize">{k.replace(/_/g, ' ')}</span>
            <div className="flex-1 h-2 bg-gray-100 rounded-full">
              <div className="h-2 rounded-full bg-sama-400" style={{ width: `${total ? (v / total) * 100 : 0}%` }} />
            </div>
            <span className="text-xs text-gray-500 w-4">{v}</span>
          </div>
        ))}
      </div>
      {balance.note && <p className="text-xs text-gray-400 mt-3 italic">{balance.note}</p>}
    </div>
  )
}

export default function ContentGenerator() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [requestType, setRequestType] = useState('full content pack')
  const [lastInput, setLastInput] = useState('')

  const handleSubmit = async (message, feedback = null) => {
    setLoading(true)
    setLastInput(message)
    try {
      const data = await chat(message, null, requestType, feedback)
      setResult(data)
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  const content = result?.result?.content
  const tone = result?.result?.tone

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h2 className="text-3xl font-serif text-sama-800">Content Generator</h2>
        <p className="text-sm text-gray-400 mt-1">Generate Instagram content for your collection</p>
      </div>

      <div className="card space-y-3">
        <div>
          <label className="label">Content Type</label>
          <div className="flex flex-wrap gap-2">
            {REQUEST_TYPES.map(t => (
              <button
                key={t}
                onClick={() => setRequestType(t)}
                className={`px-3 py-1.5 rounded-lg text-sm border transition-colors ${
                  requestType === t ? 'bg-sama-600 text-white border-sama-600' : 'border-gray-200 text-gray-600 hover:border-sama-300'
                }`}
              >
                {t}
              </button>
            ))}
          </div>
        </div>
        <ChatInput
          onSubmit={handleSubmit}
          loading={loading}
          placeholder='e.g. "Create content for my Onam collection launch"'
        />
      </div>

      {loading && <LoadingSpinner message="Creating your content..." />}

      {tone && !tone.passed && (
        <div className="card bg-amber-50 border-amber-200">
          <h3 className="font-medium text-amber-800 mb-2 text-sm">Tone Flags</h3>
          <ul className="space-y-1">
            {tone.flags.map((f, i) => <li key={i} className="text-sm text-amber-700">• {f}</li>)}
          </ul>
          {tone.revised_text && (
            <div className="mt-3">
              <p className="text-xs text-gray-400 mb-1">Revised version:</p>
              <p className="text-sm text-gray-700">{tone.revised_text}</p>
            </div>
          )}
        </div>
      )}

      {content && !loading && (
        <div className="space-y-5">
          {/* Pillar Balance */}
          {content.pillar_balance && <PillarBalance balance={content.pillar_balance} />}

          {/* Reels */}
          {content.reels?.length > 0 && (
            <div>
              <h3 className="font-serif text-xl text-sama-800 mb-3">Reels</h3>
              <div className="space-y-4">
                {content.reels.map((reel, i) => (
                  <div key={i} className="card">
                    <div className="flex items-start justify-between mb-3">
                      <h4 className="font-medium text-gray-800">Reel {i + 1}: {reel.concept}</h4>
                    </div>
                    <div className="space-y-3">
                      <div className="bg-red-50 rounded-lg p-3">
                        <p className="text-xs text-gray-400 mb-1">Hook</p>
                        <p className="text-sm font-medium text-gray-800">{reel.hook}</p>
                      </div>
                      <div>
                        <p className="label">Shot Plan</p>
                        <ol className="space-y-1">
                          {reel.shot_plan.map((s, j) => (
                            <li key={j} className="text-sm text-gray-600 flex gap-2">
                              <span className="text-sama-400 shrink-0">{j + 1}.</span>{s}
                            </li>
                          ))}
                        </ol>
                      </div>
                      <div>
                        <p className="label">On-Screen Text</p>
                        <div className="flex flex-wrap gap-2">
                          {reel.on_screen_text.map((t, j) => (
                            <span key={j} className="badge bg-gray-100 text-gray-700">{t}</span>
                          ))}
                        </div>
                      </div>
                      {reel.voiceover && (
                        <div>
                          <p className="label">Voiceover</p>
                          <p className="text-sm text-gray-600 italic">{reel.voiceover}</p>
                        </div>
                      )}
                      <div className="bg-sama-50 rounded-lg p-3 flex items-start justify-between gap-2">
                        <div className="flex-1">
                          <p className="text-xs text-gray-400 mb-1">Caption</p>
                          <p className="text-sm text-gray-700">{reel.caption}</p>
                          <p className="text-xs text-sama-600 mt-1 font-medium">{reel.cta}</p>
                        </div>
                        <CopyButton text={`${reel.caption}\n\n${reel.cta}`} />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Captions */}
          {content.captions?.length > 0 && (
            <div>
              <h3 className="font-serif text-xl text-sama-800 mb-3">Captions</h3>
              <div className="space-y-3">
                {content.captions.map((caption, i) => (
                  <div key={i} className="card flex items-start justify-between gap-3">
                    <p className="text-sm text-gray-700 flex-1">{caption}</p>
                    <CopyButton text={caption} />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Stories */}
          {content.stories && (
            <div>
              <h3 className="font-serif text-xl text-sama-800 mb-3">Stories</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {[
                  ['Polls', content.stories.polls],
                  ['Questions', content.stories.questions],
                  ['Behind the Scenes', content.stories.behind_the_scenes],
                  ['Design Voting', content.stories.design_voting],
                  ['Ordering Prompts', content.stories.ordering_prompts],
                ].map(([title, items]) => items?.length ? (
                  <div key={title} className="card">
                    <h4 className="font-medium text-sm text-gray-700 mb-2">{title}</h4>
                    <ul className="space-y-1">
                      {items.map((item, j) => (
                        <li key={j} className="text-sm text-gray-600 flex gap-2"><span className="text-sama-400">→</span>{item}</li>
                      ))}
                    </ul>
                  </div>
                ) : null)}
              </div>
            </div>
          )}

          {/* Photos */}
          {content.photos && (
            <div>
              <h3 className="font-serif text-xl text-sama-800 mb-3">Photo Ideas</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {[
                  ['Product Shots', content.photos.product_shots],
                  ['Lifestyle Shots', content.photos.lifestyle_shots],
                  ['Detail Shots', content.photos.detail_shots],
                  ['Fabric Shots', content.photos.fabric_shots],
                  ['Styling Combinations', content.photos.styling_combinations],
                ].map(([title, items]) => items?.length ? (
                  <div key={title} className="card">
                    <h4 className="font-medium text-sm text-gray-700 mb-2">{title}</h4>
                    <ul className="space-y-1">
                      {items.map((item, j) => (
                        <li key={j} className="text-sm text-gray-600 flex gap-2"><span className="text-sama-400">→</span>{item}</li>
                      ))}
                    </ul>
                  </div>
                ) : null)}
              </div>
            </div>
          )}

          <ResultActions
            result={result.result}
            itemType="content"
            title={`Content Pack — ${requestType}`}
            onRegenerate={(feedback) => handleSubmit(lastInput, feedback)}
          />
        </div>
      )}
    </div>
  )
}
