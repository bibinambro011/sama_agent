import { NavLink } from 'react-router-dom'
import {
  Sparkles, Layers, Search, Expand, FileText,
  Calendar, Calculator, BookMarked, Menu, X
} from 'lucide-react'
import { useState } from 'react'

const links = [
  { to: '/',           label: 'Collection Planner',  icon: Sparkles },
  { to: '/fabric',     label: 'Fabric Analyzer',     icon: Layers },
  { to: '/evaluate',   label: 'Design Evaluator',    icon: Search },
  { to: '/expand',     label: 'Collection Expander', icon: Expand },
  { to: '/content',    label: 'Content Generator',   icon: FileText },
  { to: '/launch',     label: 'Launch Planner',      icon: Calendar },
  { to: '/pricing',    label: 'Pricing',             icon: Calculator },
  { to: '/saved',      label: 'Saved Items',         icon: BookMarked },
]

export default function Sidebar() {
  const [open, setOpen] = useState(false)

  return (
    <>
      {/* Mobile toggle */}
      <button
        className="fixed top-4 left-4 z-50 md:hidden bg-white rounded-lg p-2 shadow border border-sama-100"
        onClick={() => setOpen(!open)}
      >
        {open ? <X size={20} /> : <Menu size={20} />}
      </button>

      {/* Overlay */}
      {open && (
        <div className="fixed inset-0 bg-black/20 z-40 md:hidden" onClick={() => setOpen(false)} />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed top-0 left-0 h-full w-64 bg-white border-r border-sama-100 z-40
        flex flex-col transition-transform duration-200
        ${open ? 'translate-x-0' : '-translate-x-full'}
        md:translate-x-0 md:static md:flex
      `}>
        <div className="p-6 border-b border-sama-100">
          <h1 className="text-2xl font-serif text-sama-800 tracking-wide">SAMA</h1>
          <p className="text-xs text-gray-400 mt-0.5">The Clothing Atelier</p>
        </div>

        <nav className="flex-1 p-3 space-y-0.5 overflow-y-auto">
          {links.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              onClick={() => setOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                  isActive
                    ? 'bg-sama-50 text-sama-800 font-medium'
                    : 'text-gray-600 hover:bg-gray-50'
                }`
              }
            >
              <Icon size={16} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="p-4 border-t border-sama-100">
          <p className="text-xs text-gray-400 text-center">AI-powered boutique assistant</p>
        </div>
      </aside>
    </>
  )
}
