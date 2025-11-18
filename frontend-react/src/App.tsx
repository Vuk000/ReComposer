import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { ToastProvider } from './contexts/ToastContext'
import ErrorBoundary from './components/shared/ErrorBoundary'
import Landing from './pages/Landing'
import Signup from './pages/auth/Signup'
import Login from './pages/auth/Login'
import ForgotPassword from './pages/auth/ForgotPassword'
import ResetPassword from './pages/auth/ResetPassword'
import AppLayout from './components/layout/AppLayout'
import Dashboard from './pages/app/Dashboard'
import Rewrite from './pages/app/Rewrite'
import Campaigns from './pages/app/Campaigns'
import Settings from './pages/app/Settings'
import ProtectedRoute from './components/auth/ProtectedRoute'

function App() {
  return (
    <ErrorBoundary>
      <ToastProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/login" element={<Login />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/reset-password" element={<ResetPassword />} />
            <Route
              path="/app/*"
              element={
                <ProtectedRoute>
                  <AppLayout />
                </ProtectedRoute>
              }
            >
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="rewrite" element={<Rewrite />} />
              <Route path="campaigns" element={<Campaigns />} />
              <Route path="settings" element={<Settings />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </ToastProvider>
    </ErrorBoundary>
  )
}

export default App

