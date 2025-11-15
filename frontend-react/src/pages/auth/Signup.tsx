import { useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import AuthLayout from '@/components/layout/AuthLayout'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import { useAuth } from '@/hooks/useAuth'
import { Github, Lock } from 'lucide-react'

const Signup = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [errors, setErrors] = useState<{ email?: string; password?: string }>({})
  const [searchParams] = useSearchParams()
  const plan = searchParams.get('plan')
  const { signup } = useAuth()

  const validate = () => {
    const newErrors: { email?: string; password?: string } = {}
    if (!email) {
      newErrors.email = 'Email is required'
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = 'Email is invalid'
    }
    if (!password) {
      newErrors.password = 'Password is required'
    } else if (password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters'
    }
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!validate()) return

    try {
      await signup(email, password)
    } catch (error: any) {
      setErrors({ email: error.response?.data?.detail || 'Failed to create account' })
    }
  }

  return (
    <AuthLayout>
      <div className="mb-6 flex items-center justify-end">
        <Link to="/login" className="text-sm text-muted-foreground hover:text-foreground">
          Login
        </Link>
      </div>

      <div className="mb-8">
        <h1 className="mb-2 text-3xl font-bold">Create an account</h1>
        <p className="text-muted-foreground">Enter your email below to create your account</p>
      </div>

      {plan && (
        <div className="mb-4 rounded-lg border border-primary/20 bg-primary/10 p-3 text-sm">
          Selected Plan: <span className="font-semibold">{plan === 'pro' ? 'Pro ($49.99/mo)' : 'Standard ($14.99/mo)'}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
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
          {errors.password && <p className="mt-1 text-sm text-destructive">{errors.password}</p>}
        </div>

        <Button type="submit" className="w-full">
          Sign In with Email
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

