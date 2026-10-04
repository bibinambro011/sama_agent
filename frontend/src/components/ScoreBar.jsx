export default function ScoreBar({ label, value }) {
  const color = value >= 8 ? 'bg-green-400' : value >= 6 ? 'bg-sama-400' : 'bg-red-300'
  return (
    <div className="flex items-center gap-3">
      <span className="text-xs text-gray-500 w-40 shrink-0">{label}</span>
      <div className="flex-1 h-2 bg-gray-100 rounded-full">
        <div className={`h-2 rounded-full transition-all ${color}`} style={{ width: `${value * 10}%` }} />
      </div>
      <span className="text-xs font-medium text-gray-700 w-6 text-right">{value}</span>
    </div>
  )
}
