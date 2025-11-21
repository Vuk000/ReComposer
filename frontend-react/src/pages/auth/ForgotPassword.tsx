import { useState } from 'react'
import { Link } from 'react-router-dom'
import AuthLayout from '@/components/layout/AuthLayout'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import api from '@/lib/api'
import { useToast } from '@/contexts/ToastContext'

const ForgotPassword = () => {
  const [email, setEmail] = useState('')
  const [submitted, setSubmitted] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const { showToast } = useToast()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email) return

    setLoading(true)
    setError('')
    try {
      await api.post('/api/auth/forgot-password', { email })
      setSubmitted(true)
      showToast('Password reset link sent! Check your email.', 'success')
    } catch (err) {
      const error = err as { response?: { data?: { detail?: string } }; message?: string }
      setError(error.response?.data?.detail || error.message || 'Failed to send reset link')
      showToast(error.response?.data?.detail || error.message || 'Failed to send reset link', 'error')
    } finally {
      setLoading(false)
    }
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

        {error && <p className="text-sm text-destructive">{error}</p>}
        <Button type="submit" className="w-full" disabled={loading}>
          {loading ? 'Sending...' : 'Send Reset Link'}
        </Button>
      </form>
    </AuthLayout>
  )
}

export default ForgotPassword

