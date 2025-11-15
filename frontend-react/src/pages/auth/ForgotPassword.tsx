import { useState } from 'react'
import { Link } from 'react-router-dom'
import AuthLayout from '@/components/layout/AuthLayout'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'

const ForgotPassword = () => {
  const [email, setEmail] = useState('')
  const [submitted, setSubmitted] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    // TODO: Implement password reset API call
    setSubmitted(true)
  }

  if (submitted) {
    return (
      <AuthLayout>
        <div className="mb-8">
          <h1 className="mb-2 text-3xl font-bold">Check your email</h1>
          <p className="text-muted-foreground">
            We've sent a password reset link to {email}. Please check your inbox.
          </p>
        </div>
        <Link to="/login">
          <Button variant="outline" className="w-full">
            Back to Login
          </Button>
        </Link>
      </AuthLayout>
    )
  }

  return (
    <AuthLayout>
      <div className="mb-6 flex items-center justify-end">
        <Link to="/login" className="text-sm text-muted-foreground hover:text-foreground">
          Back to Login
        </Link>
      </div>

      <div className="mb-8">
        <h1 className="mb-2 text-3xl font-bold">Forgot password?</h1>
        <p className="text-muted-foreground">Enter your email and we'll send you a reset link</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          type="email"
          placeholder="name@example.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />

        <Button type="submit" className="w-full">
          Send Reset Link
        </Button>
      </form>
    </AuthLayout>
  )
}

export default ForgotPassword

