export default function LoadingSpinner({ message = 'SAMA is thinking...' }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 gap-4">
      <div className="w-10 h-10 border-2 border-sama-200 border-t-sama-500 rounded-full animate-spin" />
      <p className="text-sm text-gray-400 font-light">{message}</p>
    </div>
  )
}
