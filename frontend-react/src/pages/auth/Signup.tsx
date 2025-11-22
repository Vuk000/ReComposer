import { useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import AuthLayout from '@/components/layout/AuthLayout'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import PasswordRequirements from '@/components/auth/PasswordRequirements'
import { Github, Lock, Sparkles } from 'lucide-react'
import api from '@/lib/api'

const Signup = () => {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [errors, setErrors] = useState<{ name?: string; email?: string; password?: string; confirmPassword?: string }>({})
  const [loading, setLoading] = useState(false)
  const [searchParams] = useSearchParams()
  const plan = searchParams.get('plan')
  const billing = searchParams.get('billing') || 'monthly'

  const validatePassword = (pwd: string): boolean => {
    if (pwd.length < 8) return false
    const hasLetter = /[a-zA-Z]/.test(pwd)
    const hasNumber = /\d/.test(pwd)
    return hasLetter && hasNumber
  }

  const validate = () => {
    const newErrors: { name?: string; email?: string; password?: string; confirmPassword?: string } = {}
    
    if (!name.trim()) {
      newErrors.name = 'Name is required'
    }
    
    if (!email) {
      newErrors.email = 'Email is required'
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = 'Email is invalid'
    }
    
    if (!password) {
      newErrors.password = 'Password is required'
    } else if (!validatePassword(password)) {
      newErrors.password = 'Password must be at least 8 characters with at least one letter and one number'
    }
    
    if (!confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password'
    } else if (password !== confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match'
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!validate()) return

    setLoading(true)
    try {
      // Sign up directly (don't use signup function to avoid auto-navigation)
      await api.post('/auth/signup', { email, password })
      
      // Login to get token
      const loginResponse = await api.post<{ access_token: string }>('/auth/login', { email, password })
      localStorage.setItem('token', loginResponse.data.access_token)
      
      // If plan is selected, create checkout session
      if (plan && (plan === 'standard' || plan === 'pro')) {
        try {
          const interval = billing === 'yearly' ? 'year' : 'month'
          const response = await api.post<{ checkout_url: string }>('/billing/create-checkout', {
            plan,
            interval,
          })
          
          // Redirect to Stripe checkout
          window.location.href = response.data.checkout_url
          return
        } catch (checkoutError) {
          console.error('Failed to create checkout session:', checkoutError)
          const err = checkoutError as { response?: { data?: { detail?: string } }; message?: string }
          setErrors({ email: err.response?.data?.detail || err.message || 'Failed to create checkout session. You can upgrade later in settings.' })
          // Still redirect to dashboard if checkout fails
          window.location.href = '/app/dashboard'
          return
        }
      } else {
        // No plan selected, redirect to dashboard
        window.location.href = '/app/dashboard'
      }
    } catch (error) {
      const err = error as { response?: { data?: { detail?: string } }; message?: string }
      setErrors({ email: err.response?.data?.detail || err.message || 'Failed to create account' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthLayout variant="signup">
      <div className="mb-6 flex items-center justify-end">
        <Link to="/login" className="text-sm text-muted-foreground transition-colors hover:text-primary">
          Already have an account? <span className="font-semibold">Login</span>
        </Link>
      </div>

      <div className="mb-8">
        <div className="mb-3 flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-primary" />
          <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-purple-500 bg-clip-text text-transparent">
            Create your account
          </h1>
        </div>
        <p className="text-muted-foreground">
          Join thousands of professionals optimizing their email communications
        </p>
      </div>

      {plan && (
        <div className="mb-4 rounded-lg border border-primary/30 bg-gradient-to-r from-primary/10 to-purple-500/10 p-3 text-sm">
          <span className="font-medium">Selected Plan: </span>
          <span className="font-semibold text-primary">
            {plan === 'pro' 
              ? `Professional (${billing === 'yearly' ? '$479.90/year' : '$49.99/month'})` 
              : `Standard (${billing === 'yearly' ? '$143.90/year' : '$14.99/month'})`}
          </span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <Input
            type="text"
            placeholder="Full Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className={errors.name ? 'border-destructive' : ''}
          />
          {errors.name && <p className="mt-1 text-sm text-destructive">{errors.name}</p>}
        </div>

        <div>
          <Input
            type="email"
            placeholder="name@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className={errors.email ? 'border-destructive' : ''}
          />
          {errors.email && <p className="mt-1 text-sm text-destructive">{errors.email}</p>}
        </div>

        <div>
          <Input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className={errors.password ? 'border-destructive' : ''}
          />
          {password && <PasswordRequirements password={password} />}
          {errors.password && <p className="mt-1 text-sm text-destructive">{errors.password}</p>}
        </div>

        <div>
          <Input
            type="password"
            placeholder="Confirm Password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            className={errors.confirmPassword ? 'border-destructive' : ''}
          />
          {errors.confirmPassword && <p className="mt-1 text-sm text-destructive">{errors.confirmPassword}</p>}
          {confirmPassword && password && confirmPassword === password && (
            <p className="mt-1 text-sm text-green-600 dark:text-green-400">✓ Passwords match</p>
          )}
        </div>

        <Button type="submit" className="w-full bg-gradient-to-r from-primary to-purple-600 transition-all hover:scale-[1.02] hover:shadow-lg" disabled={loading}>
          {loading ? 'Creating account...' : plan ? 'Get Started & Continue to Payment' : 'Create Account'}
        </Button>
      </form>

      <div className="my-6 flex items-center gap-4">
        <div className="flex-1 border-t border-border" />
        <span className="text-xs text-muted-foreground">OR CONTINUE WITH</span>
        <div className="flex-1 border-t border-border" />
      </div>

      <div className="space-y-3">
        <Button variant="outline" className="w-full" type="button">
          <Github className="mr-2 h-4 w-4" />
          GitHub
        </Button>
        <Button variant="outline" className="w-full" type="button">
          <Lock className="mr-2 h-4 w-4" />
          SAML SSO
        </Button>
      </div>

      <p className="mt-6 text-center text-xs text-muted-foreground">
        By clicking continue, you agree to our{' '}
        <Link to="#" className="underline hover:text-foreground">
          Terms of Service
        </Link>{' '}
        and{' '}
        <Link to="#" className="underline hover:text-foreground">
          Privacy Policy
        </Link>
        .
      </p>
    </AuthLayout>
  )
}

export default Signup

