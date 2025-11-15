import { Link, useLocation } from 'react-router-dom'
import { LayoutDashboard, FileText, Send, Settings } from 'lucide-react'
import { cn } from '@/lib/utils'

const Sidebar = () => {
  const location = useLocation()

  const navItems = [
    { path: '/app/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/app/rewrite', label: 'Email Rewriter', icon: FileText },
    { path: '/app/campaigns', label: 'Campaigns', icon: Send },
    { path: '/app/settings', label: 'Settings', icon: Settings },
  ]

  return (
    <aside className="h-full w-64 border-r border-border bg-sidebar p-4">
      <nav className="space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = location.pathname === item.path

          return (
            <Link
              key={item.path}
              to={item.path}
              className={cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                {
                  'bg-sidebar-accent text-sidebar-accent-foreground': isActive,
                  'text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground': !isActive,
                }
              )}
            >
              <Icon className="h-5 w-5" />
              {item.label}
            </Link>
          )
        })}
      </nav>
    </aside>
  )
}

export default Sidebar
