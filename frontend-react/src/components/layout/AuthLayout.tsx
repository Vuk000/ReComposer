import { ReactNode } from 'react'
import { Link } from 'react-router-dom'

interface AuthLayoutProps {
  children: ReactNode
  variant?: 'login' | 'signup'
}

const AuthLayout = ({ children, variant = 'login' }: AuthLayoutProps) => {
  const isSignup = variant === 'signup'
  
  const testimonials = {
    signup: {
      quote: "ReCompose transformed our email communications. Our response rates increased by 40% within the first month.",
      author: "– Sarah Chen, Marketing Director"
    },
    login: {
      quote: "This library has saved me countless hours of work and helped me deliver stunning designs to my clients faster than ever before.",
      author: "– Sofia Davis"
    }
  }

  const currentTestimonial = testimonials[variant]

  return (
    <div className="flex min-h-screen">
      {/* Left side - Branding */}
      <div className={`hidden w-2/5 p-12 lg:flex lg:flex-col lg:justify-between ${
        isSignup 
          ? 'bg-gradient-to-br from-[#201a24] via-[#2a1f2e] to-[#201a24]' 
          : 'bg-[#201a24]'
      }`}>
        <Link to="/" className="flex items-center gap-2 transition-transform hover:scale-105">
          <div className={`flex h-10 w-10 items-center justify-center rounded-lg transition-all ${
            isSignup 
              ? 'bg-gradient-to-br from-primary to-purple-600 shadow-lg shadow-primary/25' 
              : 'bg-primary'
          }`}>
            <span className="text-lg font-bold text-primary-foreground">R</span>
          </div>
          <span className={`text-xl font-semibold ${
            isSignup 
              ? 'bg-gradient-to-r from-primary to-purple-500 bg-clip-text text-transparent' 
              : 'text-[#8c5cff]'
          }`}>
            ReCompose
          </span>
        </Link>
        <div className="space-y-4">
          <p className={`text-lg italic ${
            isSignup 
              ? 'text-[#c4b5fd]' 
              : 'text-[#a78bfa]'
          }`}>
            "{currentTestimonial.quote}"
          </p>
          <p className={`text-sm ${
            isSignup 
              ? 'text-[#c4b5fd]' 
              : 'text-[#a78bfa]'
          }`}>
            {currentTestimonial.author}
          </p>
        </div>
      </div>

      {/* Right side - Form */}
      <div className={`flex w-full flex-1 items-center justify-center p-8 lg:w-3/5 ${
        isSignup 
          ? 'bg-gradient-to-br from-[#1a161c] to-[#1f1a24]' 
          : 'bg-[#1a161c]'
      }`}>
        <div className="w-full max-w-md">{children}</div>
      </div>
    </div>
  )
}

export default AuthLayout

