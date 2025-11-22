import { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import Button from '../ui/Button'

interface MarketingLayoutProps {
  children: ReactNode
}

const MarketingLayout = ({ children }: MarketingLayoutProps) => {
  return (
    <div className="flex min-h-screen flex-col">
      {/* Glassmorphism Navbar */}
      <nav className="sticky top-0 z-50 border-b border-white/10 bg-slate-900/40 backdrop-blur-xl backdrop-saturate-150">
        {/* Gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-r from-primary/5 via-transparent to-purple-500/5" />
        
        <div className="container relative mx-auto flex h-20 items-center justify-between px-6">
          {/* Logo */}
          <Link to="/" className="group flex items-center gap-3 transition-transform duration-300 hover:scale-105">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-purple-600 shadow-lg shadow-primary/25 transition-all duration-300 group-hover:shadow-primary/50 group-hover:rotate-6">
              <span className="text-lg font-bold text-white">R</span>
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-white to-slate-300 bg-clip-text text-transparent transition-all duration-300 group-hover:from-primary group-hover:to-purple-500">
              ReCompose
            </span>
          </Link>

          {/* Navigation Links - Desktop */}
          <div className="hidden md:flex items-center gap-2">
            <a 
              href="#features" 
              className="rounded-xl px-4 py-2.5 text-sm font-medium text-slate-300 transition-all duration-300 hover:scale-105 hover:bg-white/10 hover:text-white hover:shadow-lg hover:shadow-primary/20"
            >
              Features
            </a>
            <a 
              href="#pricing" 
              className="rounded-xl px-4 py-2.5 text-sm font-medium text-slate-300 transition-all duration-300 hover:scale-105 hover:bg-white/10 hover:text-white hover:shadow-lg hover:shadow-primary/20"
            >
              Pricing
            </a>
            <a 
              href="#how-it-works" 
              className="rounded-xl px-4 py-2.5 text-sm font-medium text-slate-300 transition-all duration-300 hover:scale-105 hover:bg-white/10 hover:text-white hover:shadow-lg hover:shadow-primary/20"
            >
              How It Works
            </a>
            <a 
              href="#faq" 
              className="rounded-xl px-4 py-2.5 text-sm font-medium text-slate-300 transition-all duration-300 hover:scale-105 hover:bg-white/10 hover:text-white hover:shadow-lg hover:shadow-primary/20"
            >
              FAQ
            </a>
          </div>

          {/* CTA Buttons */}
          <div className="flex items-center gap-3">
            <Link to="/login" className="hidden sm:block">
              <Button variant="ghost" className="rounded-xl border border-white/10 bg-white/5 backdrop-blur-sm transition-all duration-300 hover:scale-105 hover:bg-white/10 hover:border-white/20">
                Sign In
              </Button>
            </Link>
            <Link to="/signup">
              <Button className="rounded-xl bg-gradient-to-r from-primary to-purple-600 shadow-lg shadow-primary/25 transition-all duration-300 hover:scale-105 hover:shadow-primary/40 hover:shadow-xl">
                Get Started
              </Button>
            </Link>
          </div>
        </div>
      </nav>

      <main className="flex-1">{children}</main>

      {/* Glassmorphism Footer */}
      <footer className="border-t border-white/10 bg-slate-900/60 backdrop-blur-xl py-12">
        <div className="absolute inset-0 bg-gradient-to-r from-primary/5 via-transparent to-purple-500/5" />
        <div className="container relative mx-auto px-6">
          <div className="flex flex-col items-center justify-between gap-6 md:flex-row">
            <div className="flex flex-col items-center gap-2 md:items-start">
              <div className="flex items-center gap-2">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-primary to-purple-600">
                  <span className="text-sm font-bold text-white">R</span>
                </div>
                <span className="font-bold text-white">ReCompose</span>
              </div>
              <p className="text-sm text-slate-400">
                © {new Date().getFullYear()} ReCompose AI. Enterprise Email Intelligence.
              </p>
            </div>
            <div className="flex gap-8">
              <Link to="#" className="text-sm text-slate-400 transition-all duration-300 hover:scale-110 hover:text-primary">
                Terms of Service
              </Link>
              <Link to="#" className="text-sm text-slate-400 transition-all duration-300 hover:scale-110 hover:text-primary">
                Privacy Policy
              </Link>
              <Link to="#" className="text-sm text-slate-400 transition-all duration-300 hover:scale-110 hover:text-primary">
                Documentation
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default MarketingLayout

