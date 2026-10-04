import { useState } from 'react'
import { calcPricing } from '../api/client'
import toast from 'react-hot-toast'

const FIELDS = [
  { key: 'fabric_cost', label: 'Fabric Cost' },
  { key: 'stitching_cost', label: 'Stitching Cost' },
  { key: 'trims_and_embellishments', label: 'Trims & Embellishments' },
  { key: 'labour', label: 'Labour' },
  { key: 'packaging', label: 'Packaging' },
  { key: 'overheads', label: 'Overheads' },
  { key: 'target_margin_pct', label: 'Target Margin %' },
  { key: 'perceived_value_uplift_pct', label: 'Perceived Value Uplift %' },
]

const DEFAULTS = {
  fabric_cost: 500, stitching_cost: 300, trims_and_embellishments: 100,
  labour: 200, packaging: 50, overheads: 100,
  target_margin_pct: 50, perceived_value_uplift_pct: 0,
}

export default function Pricing() {
  const [form, setForm] = useState(DEFAULTS)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleChange = (key, value) => setForm(f => ({ ...f, [key]: parseFloat(value) || 0 }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const data = await calcPricing(form)
      setResult(data)
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Calculation failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h2 className="text-3xl font-serif text-sama-800">Pricing Calculator</h2>
        <p className="text-sm text-gray-400 mt-1">All arithmetic is done in code — no AI guesswork</p>
      </div>

      <form onSubmit={handleSubmit} className="card space-y-4">
        <div className="grid grid-cols-2 gap-4">
          {FIELDS.map(({ key, label }) => (
            <div key={key}>
              <label className="label">{label}</label>
              <div className="relative">
                {!key.includes('pct') && (
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm">₹</span>
                )}
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  value={form[key]}
                  onChange={e => handleChange(key, e.target.value)}
                  className={`input ${!key.includes('pct') ? 'pl-7' : ''}`}
                />
                {key.includes('pct') && (
                  <span className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm">%</span>
                )}
              </div>
            </div>
          ))}
        </div>
        <button type="submit" className="btn-primary w-full" disabled={loading}>
          {loading ? 'Calculating...' : 'Calculate Price'}
        </button>
      </form>

      {result && (
        <div className="space-y-4">
          {/* Price Tiers */}
          <div className="grid grid-cols-3 gap-3">
            {[
              { label: 'Entry Price', value: result.entry_price, color: 'bg-green-50 border-green-200 text-green-800' },
              { label: 'Hero Price', value: result.hero_price, color: 'bg-sama-50 border-sama-200 text-sama-800' },
              { label: 'Premium Price', value: result.premium_price, color: 'bg-purple-50 border-purple-200 text-purple-800' },
            ].map(({ label, value, color }) => (
              <div key={label} className={`card border text-center ${color}`}>
                <p className="text-xs mb-1 opacity-70">{label}</p>
                <p className="text-2xl font-serif">₹{value.toLocaleString()}</p>
              </div>
            ))}
          </div>

          {/* Summary */}
          <div className="card">
            <div className="flex justify-between items-center mb-4">
              <h3 className="font-medium text-sama-800">Cost Breakdown</h3>
              <div className="text-right">
                <p className="text-xs text-gray-400">Margin Achieved</p>
                <p className="text-lg font-serif text-sama-600">{result.margin_achieved_pct}%</p>
              </div>
            </div>
            <div className="space-y-2">
              {Object.entries(result.cost_breakdown).map(([k, v]) => (
                <div key={k} className="flex justify-between text-sm">
                  <span className="text-gray-500 capitalize">{k.replace(/_/g, ' ')}</span>
                  <span className="text-gray-700">₹{v.toLocaleString()}</span>
                </div>
              ))}
              <div className="border-t border-gray-100 pt-2 flex justify-between text-sm font-medium">
                <span>Total Cost</span>
                <span>₹{result.total_cost.toLocaleString()}</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
