import { ReactNode } from 'react'
import { Link } from 'react-router-dom'

interface AuthLayoutProps {
  children: ReactNode
}

const AuthLayout = ({ children }: AuthLayoutProps) => {
  return (
    <div className="flex min-h-screen">
      {/* Left side - Branding */}
      <div className="hidden w-2/5 bg-[#201a24] p-12 lg:flex lg:flex-col lg:justify-between">
        <Link to="/" className="flex items-center gap-2">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary">
            <span className="text-lg font-bold text-primary-foreground">R</span>
          </div>
          <span className="text-xl font-semibold text-[#8c5cff]">ReCompose</span>
        </Link>
        <div className="space-y-4">
          <p className="text-lg italic text-[#a78bfa]">
            "This library has saved me countless hours of work and helped me deliver stunning designs to my clients faster than ever before."
          </p>
          <p className="text-sm text-[#a78bfa]">– Sofia Davis</p>
        </div>
      </div>

      {/* Right side - Form */}
      <div className="flex w-full flex-1 items-center justify-center bg-[#1a161c] p-8 lg:w-3/5">
        <div className="w-full max-w-md">{children}</div>
      </div>
    </div>
  )
}

export default AuthLayout

