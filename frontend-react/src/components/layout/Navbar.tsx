import { Link, useNavigate } from 'react-router-dom'
import { Settings, LogOut, User, Menu } from 'lucide-react'
import { useState } from 'react'
import { useAuth } from '@/hooks/useAuth'
import Sidebar from './Sidebar'

const Navbar = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [showMenu, setShowMenu] = useState(false)
  const [showMobileMenu, setShowMobileMenu] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <>
      <nav className="sticky top-0 z-40 flex h-20 items-center justify-between border-b border-white/10 bg-slate-900/40 px-6 backdrop-blur-xl backdrop-saturate-150">
        {/* Glassmorphism overlay */}
        <div className="absolute inset-0 bg-gradient-to-r from-primary/5 via-transparent to-purple-500/5" />
        
        <div className="relative z-10 flex items-center gap-4">
          <button
            onClick={() => setShowMobileMenu(!showMobileMenu)}
            className="lg:hidden rounded-lg p-2 transition-all hover:bg-white/10"
          >
            <Menu className="h-5 w-5" />
          </button>
          <Link to="/app/dashboard" className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-purple-600 shadow-lg shadow-primary/25">
              <span className="text-lg font-bold text-white">R</span>
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-white to-slate-300 bg-clip-text text-transparent">
              ReCompose
            </span>
          </Link>
        </div>

        <div className="relative z-10">
          <button
            onClick={() => setShowMenu(!showMenu)}
            className="flex items-center gap-3 rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 backdrop-blur-sm transition-all hover:bg-white/10 hover:border-white/20"
          >
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-primary to-purple-600">
              <User className="h-4 w-4 text-white" />
            </div>
            <span className="text-sm font-medium">{user?.email || 'User'}</span>
          </button>

          {showMenu && (
            <>
              <div className="fixed inset-0 z-10" onClick={() => setShowMenu(false)} />
              <div className="absolute right-0 top-full z-20 mt-3 w-56 overflow-hidden rounded-2xl border border-white/10 bg-slate-900/90 backdrop-blur-2xl shadow-2xl shadow-black/40">
                <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-transparent to-purple-500/10" />
                <div className="relative p-2">
                  <Link
                    to="/app/settings"
                    className="flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition-all hover:bg-white/10"
                    onClick={() => setShowMenu(false)}
                  >
                    <Settings className="h-4 w-4 text-primary" />
                    Settings
                  </Link>
                  <button
                    onClick={handleLogout}
                    className="flex w-full items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition-all hover:bg-white/10"
                  >
                    <LogOut className="h-4 w-4 text-red-400" />
                    Logout
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </nav>
      {showMobileMenu && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setShowMobileMenu(false)} />
          <div className="fixed left-0 top-0 h-full w-72 border-r border-white/10 bg-slate-900/95 backdrop-blur-2xl shadow-2xl">
            <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-transparent to-purple-500/10" />
            <div className="relative p-4">
              <Sidebar />
            </div>
          </div>
        </div>
      )}
    </>
  )
}

export default Navbar
