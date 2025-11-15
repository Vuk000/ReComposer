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
      <nav className="flex h-16 items-center justify-between border-b border-border bg-card px-6">
        <div className="flex items-center gap-4">
          <button
            onClick={() => setShowMobileMenu(!showMobileMenu)}
            className="lg:hidden"
          >
            <Menu className="h-6 w-6" />
          </button>
          <Link to="/app/dashboard" className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
              <span className="text-sm font-bold text-primary-foreground">R</span>
            </div>
            <span className="text-lg font-semibold">ReCompose</span>
          </Link>
        </div>

        <div className="relative">
          <button
            onClick={() => setShowMenu(!showMenu)}
            className="flex items-center gap-2 rounded-lg px-3 py-2 hover:bg-accent"
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary">
              <User className="h-4 w-4 text-primary-foreground" />
            </div>
            <span className="text-sm">{user?.email || 'User'}</span>
          </button>

          {showMenu && (
            <>
              <div className="fixed inset-0 z-10" onClick={() => setShowMenu(false)} />
              <div className="absolute right-0 top-full z-20 mt-2 w-48 rounded-lg border border-border bg-card p-2 shadow-lg">
                <Link
                  to="/app/settings"
                  className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm hover:bg-accent"
                  onClick={() => setShowMenu(false)}
                >
                  <Settings className="h-4 w-4" />
                  Settings
                </Link>
                <button
                  onClick={handleLogout}
                  className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm hover:bg-accent"
                >
                  <LogOut className="h-4 w-4" />
                  Logout
                </button>
              </div>
            </>
          )}
        </div>
      </nav>
      {showMobileMenu && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="fixed inset-0 bg-black/50" onClick={() => setShowMobileMenu(false)} />
          <div className="fixed left-0 top-0 h-full w-64 bg-sidebar p-4">
            <Sidebar />
          </div>
        </div>
      )}
    </>
  )
}

export default Navbar
