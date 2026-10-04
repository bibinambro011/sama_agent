import { useState, useRef } from 'react'
import { Send, Image, X } from 'lucide-react'

export default function ChatInput({ onSubmit, loading, placeholder = 'Ask SAMA...', showImageUpload = false }) {
  const [text, setText] = useState('')
  const [imageB64, setImageB64] = useState(null)
  const [imagePreview, setImagePreview] = useState(null)
  const fileRef = useRef()

  const handleImage = (e) => {
    const file = e.target.files[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = (ev) => {
      const b64 = ev.target.result.split(',')[1]
      setImageB64(b64)
      setImagePreview(ev.target.result)
    }
    reader.readAsDataURL(file)
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!text.trim() && !imageB64) return
    onSubmit(text, imageB64)
    setText('')
    setImageB64(null)
    setImagePreview(null)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-2">
      {imagePreview && (
        <div className="relative inline-block">
          <img src={imagePreview} alt="upload" className="h-20 rounded-lg object-cover border border-sama-200" />
          <button
            type="button"
            onClick={() => { setImageB64(null); setImagePreview(null) }}
            className="absolute -top-2 -right-2 bg-white rounded-full p-0.5 shadow border border-gray-200"
          >
            <X size={12} />
          </button>
        </div>
      )}
      <div className="flex gap-2">
        <input
          className="input flex-1"
          value={text}
          onChange={e => setText(e.target.value)}
          placeholder={placeholder}
          disabled={loading}
        />
        {showImageUpload && (
          <>
            <input ref={fileRef} type="file" accept="image/*" className="hidden" onChange={handleImage} />
            <button
              type="button"
              onClick={() => fileRef.current.click()}
              className="btn-secondary px-3"
              disabled={loading}
            >
              <Image size={16} />
            </button>
          </>
        )}
        <button type="submit" className="btn-primary px-3" disabled={loading || (!text.trim() && !imageB64)}>
          <Send size={16} />
        </button>
      </div>
    </form>
  )
}
