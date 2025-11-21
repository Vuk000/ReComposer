import { useState } from 'react'
import { Link, useSearchParams, useNavigate } from 'react-router-dom'
import AuthLayout from '@/components/layout/AuthLayout'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import api from '@/lib/api'
import { useToast } from '@/contexts/ToastContext'

const ResetPassword = () => {
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [errors, setErrors] = useState<{ password?: string; confirmPassword?: string }>({})
  const [loading, setLoading] = useState(false)
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const token = searchParams.get('token')
  const { showToast } = useToast()

  const validate = () => {
    const newErrors: { password?: string; confirmPassword?: string } = {}
    if (!password) {
      newErrors.password = 'Password is required'
    } else if (password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters'
    } else {
      // Check for at least one letter and one number
      const hasLetter = /[a-zA-Z]/.test(password)
      const hasNumber = /[0-9]/.test(password)
      if (!hasLetter || !hasNumber) {
        newErrors.password = 'Password must contain at least one letter and one number'
      }
    }
    if (password !== confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match'
    }
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!validate() || !token) return

    setLoading(true)
    try {
      await api.post('/api/auth/reset-password', {
        token,
        password,
      })
      showToast('Password reset successfully! You can now login.', 'success')
      navigate('/login')
    } catch (err) {
      const error = err as { response?: { data?: { detail?: string } }; message?: string }
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to reset password'
      setErrors({ password: errorMessage })
      showToast(errorMessage, 'error')
    } finally {
      setLoading(false)
    }
  }

  if (!token) {
    return (
      <AuthLayout>
        <div className="mb-8">
          <h1 className="mb-2 text-3xl font-bold">Invalid reset link</h1>
          <p className="text-muted-foreground">This password reset link is invalid or has expired.</p>
        </div>
        <Link to="/forgot-password">
          <Button className="w-full">Request New Link</Button>
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
        <h1 className="mb-2 text-3xl font-bold">Reset password</h1>
        <p className="text-muted-foreground">Enter your new password below</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <Input
            type="password"
            placeholder="New password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className={errors.password ? 'border-destructive' : ''}
          />
          {errors.password && <p className="mt-1 text-sm text-destructive">{errors.password}</p>}
        </div>

        <div>
          <Input
            type="password"
            placeholder="Confirm password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            className={errors.confirmPassword ? 'border-destructive' : ''}
          />
          {errors.confirmPassword && <p className="mt-1 text-sm text-destructive">{errors.confirmPassword}</p>}
        </div>

        <Button type="submit" className="w-full" disabled={loading}>
          {loading ? 'Resetting...' : 'Reset Password'}
        </Button>
      </form>
    </AuthLayout>
  )
}

export default ResetPassword

