import { Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import AIChat from './pages/AIChat'
import ProtectedRoute from './components/ProtectedRoute'
import BottomNav from './components/BottomNav'

export default function App() {
  return (
    <>
      <div className="pb-16 md:pb-0">
        <Routes>
          <Route path="/" element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } />
          <Route path="/ai" element={
            <ProtectedRoute>
              <AIChat />
            </ProtectedRoute>
          } />
        </Routes>
      </div>
      <BottomNav />
    </>
  )
}
