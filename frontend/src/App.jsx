import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import Sidebar from './components/Sidebar'
import CollectionPlanner from './pages/CollectionPlanner'
import FabricAnalyzer from './pages/FabricAnalyzer'
import DesignEvaluator from './pages/DesignEvaluator'
import CollectionExpander from './pages/CollectionExpander'
import ContentGenerator from './pages/ContentGenerator'
import LaunchPlanner from './pages/LaunchPlanner'
import Pricing from './pages/Pricing'
import SavedItems from './pages/SavedItems'

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex min-h-screen">
        <Sidebar />
        <main className="flex-1 p-6 md:p-8 overflow-y-auto md:ml-0">
          <div className="pt-12 md:pt-0">
            <Routes>
              <Route path="/"          element={<CollectionPlanner />} />
              <Route path="/fabric"    element={<FabricAnalyzer />} />
              <Route path="/evaluate"  element={<DesignEvaluator />} />
              <Route path="/expand"    element={<CollectionExpander />} />
              <Route path="/content"   element={<ContentGenerator />} />
              <Route path="/launch"    element={<LaunchPlanner />} />
              <Route path="/pricing"   element={<Pricing />} />
              <Route path="/saved"     element={<SavedItems />} />
            </Routes>
          </div>
        </main>
      </div>
      <Toaster position="bottom-right" toastOptions={{ style: { fontFamily: 'Inter, sans-serif', fontSize: '14px' } }} />
    </BrowserRouter>
  )
}
