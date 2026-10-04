import { useState } from 'react'
import { chat, generateBrief, approveBrief } from '../api/client'
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

function BriefReview({ brief, briefId, onApprove, onRegenerate, loading }) {
  const g = brief.hero_garments || []
  return (
    <div className="card border-sama-200 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-serif text-lg text-sama-800">Collection Brief</h3>
        <span className="badge bg-amber-100 text-amber-700">Review before generating content</span>
      </div>

      {brief.assumptions?.length > 0 && (
        <div className="bg-amber-50 rounded-lg p-3">
          <p className="text-xs font-medium text-amber-700 mb-1">Assumptions made:</p>
          <ul className="space-y-0.5">
            {brief.assumptions.map((a, i) => <li key={i} className="text-xs text-amber-600">• {a}</li>)}
          </ul>
        </div>
      )}

      <div className="grid grid-cols-2 gap-3 text-sm">
        <div><span className="label">Occasion</span><p>{brief.occasion}</p></div>
        <div><span className="label">Story Angle</span><p>{brief.story_angle}</p></div>
        <div><span className="label">Target Customer</span><p>{brief.target_customer}</p></div>
        <div><span className="label">Price Positioning</span><p>{brief.price_positioning}</p></div>
      </div>

      <div>
        <span className="label">Palette</span>
        <div className="flex flex-wrap gap-2 mt-1">
          {brief.palette?.map((c, i) => (
            <span key={i} className="badge bg-gray-100 text-gray-700">{c}</span>
          ))}
        </div>
      </div>

      <div>
        <span className="label">Fabric Direction</span>
        <p className="text-sm text-gray-700">{brief.fabric_direction}</p>
      </div>

      <div>
        <span className="label">Signature Details (repeat across all content)</span>
        <ul className="mt-1 space-y-0.5">
          {brief.signature_details?.map((d, i) => (
            <li key={i} className="text-sm text-gray-700">• {d}</li>
          ))}
        </ul>
      </div>

      <div>
        <span className="label">Hero Garments</span>
        <div className="space-y-2 mt-1">
          {g.map((garment, i) => (
            <div key={i} className="bg-sama-50 rounded-lg p-3 text-sm">
              <p className="font-medium text-sama-800">{garment.name} <span className="text-xs text-gray-400">({garment.price_tag})</span></p>
              <p className="text-gray-600">{garment.garment_type} · {garment.fabric} · {garment.colourway}</p>
              <p className="text-gray-500">{garment.neckline} neckline · {garment.sleeve} sleeve · {garment.length}</p>
              <p className="text-sama-600 text-xs mt-1">✦ {garment.signature_detail}</p>
            </div>
          ))}
        </div>
      </div>

      <div>
        <span className="label">Kids Piece</span>
        <p className="text-sm text-gray-700">{brief.kids_piece}</p>
      </div>

      {brief.fill_these_in?.length > 0 && (
        <div className="bg-blue-50 rounded-lg p-3">
          <p className="text-xs font-medium text-blue-700 mb-1">Fill these in before publishing:</p>
          <ul className="space-y-0.5">
            {brief.fill_these_in.map((f, i) => <li key={i} className="text-xs text-blue-600">• {f}</li>)}
          </ul>
        </div>
      )}

      <div className="flex gap-3 pt-2">
        <button
          onClick={onApprove}
          disabled={loading}
          className="btn-primary flex-1"
        >
          Approve Brief & Generate Content
        </button>
        <button
          onClick={onRegenerate}
          disabled={loading}
          className="btn-secondary"
        >
          Regenerate Brief
        </button>
      </div>
    </div>
  )
}

export default function ContentGenerator() {
  const [step, setStep] = useState('input') // 'input' | 'brief' | 'content'
  const [brief, setBrief] = useState(null)
  const [briefId, setBriefId] = useState(null)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [requestType, setRequestType] = useState('full content pack')
  const [lastInput, setLastInput] = useState('')

  const handleSubmit = async (message, feedback = null) => {
    setLoading(true)
    setLastInput(message)
    setResult(null)
    try {
      const data = await generateBrief(message, feedback)
      setBrief(data.brief)
      setBriefId(data.id)
      setStep('brief')
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Something went wrong generating the brief')
    } finally {
      setLoading(false)
    }
  }

  const handleApproveBrief = async () => {
    setLoading(true)
    try {
      await approveBrief(briefId)
      const data = await chat(lastInput, null, requestType, null, briefId)
      setResult(data)
      setStep('content')
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Something went wrong generating content')
    } finally {
      setLoading(false)
    }
  }

  const handleRegenerateBrief = () => {
    setBrief(null)
    setBriefId(null)
    setStep('input')
  }

  const handleRegenerate = async (feedback) => {
    setLoading(true)
    try {
      const data = await chat(lastInput, null, requestType, feedback, briefId)
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

      {step === 'input' && (
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
      )}

      {loading && <LoadingSpinner message={step === 'input' ? 'Building collection brief...' : 'Creating your content...'} />}

      {step === 'brief' && brief && !loading && (
        <BriefReview
          brief={brief}
          briefId={briefId}
          onApprove={handleApproveBrief}
          onRegenerate={handleRegenerateBrief}
          loading={loading}
        />
      )}

      {tone && !tone.passed && (
        <div className="card bg-amber-50 border-amber-200">
          <h3 className="font-medium text-amber-800 mb-2 text-sm">Quality Flags</h3>
          {tone.flags?.length > 0 && (
            <div className="mb-2">
              <p className="text-xs text-amber-600 font-medium mb-1">Tone flags (fixed in output):</p>
              <ul className="space-y-1">
                {tone.flags.map((f, i) => <li key={i} className="text-sm text-amber-700">• {f}</li>)}
              </ul>
            </div>
          )}
          {tone.banned_phrase_hits?.length > 0 && (
            <div className="mb-2">
              <p className="text-xs text-red-600 font-medium mb-1">Banned phrases found:</p>
              <ul className="space-y-1">
                {tone.banned_phrase_hits.map((f, i) => <li key={i} className="text-sm text-red-700">• {f}</li>)}
              </ul>
            </div>
          )}
          {tone.still_failing_fields?.length > 0 && (
            <div>
              <p className="text-xs text-red-600 font-medium mb-1">Still needs attention after 3 attempts:</p>
              <ul className="space-y-1">
                {tone.still_failing_fields.map((f, i) => <li key={i} className="text-sm text-red-700">• {f}</li>)}
              </ul>
            </div>
          )}
        </div>
      )}

      {content && !loading && step === 'content' && (
        <div className="space-y-5">
          {content.pillar_balance && <PillarBalance balance={content.pillar_balance} />}

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
            onRegenerate={handleRegenerate}
          />
        </div>
      )}
    </div>
  )
}
