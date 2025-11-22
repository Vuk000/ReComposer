import { useState } from 'react'
import { Copy, Check, AlertCircle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Textarea from '@/components/ui/Textarea'
import { useRewrite } from '@/hooks/useRewrite'
import { useStatus } from '@/hooks/useStatus'
import { useToast } from '@/contexts/ToastContext'

const Rewrite = () => {
  const [originalEmail, setOriginalEmail] = useState('')
  const [rewrittenEmail, setRewrittenEmail] = useState('')
  const [selectedTone, setSelectedTone] = useState<'professional' | 'friendly' | 'persuasive'>('professional')
  const [copied, setCopied] = useState(false)
  const { rewriteEmail, loading, error } = useRewrite()
  const { status } = useStatus()
  const { showToast } = useToast()

  const tones = [
    { value: 'professional', label: 'Professional' },
    { value: 'friendly', label: 'Friendly' },
    { value: 'persuasive', label: 'Persuasive' },
  ] as const

  const handleRewrite = async () => {
    if (!originalEmail.trim()) {
      showToast('Please enter an email to rewrite', 'error')
      return
    }

    const result = await rewriteEmail({
      email_text: originalEmail,
      tone: selectedTone,
    })

    if (result) {
      setRewrittenEmail(result.rewritten_email)
      showToast('Email rewritten successfully!', 'success')
    } else {
      showToast(error || 'Failed to rewrite email', 'error')
    }
  }

  const handleCopy = async () => {
    if (rewrittenEmail) {
      try {
        // Try modern clipboard API first
        if (navigator.clipboard && navigator.clipboard.writeText) {
          await navigator.clipboard.writeText(rewrittenEmail)
        } else {
          // Fallback for older browsers
          const textArea = document.createElement('textarea')
          textArea.value = rewrittenEmail
          textArea.style.position = 'fixed'
          textArea.style.left = '-999999px'
          document.body.appendChild(textArea)
          textArea.select()
          document.execCommand('copy')
          document.body.removeChild(textArea)
        }
        setCopied(true)
        showToast('Copied to clipboard!', 'success')
        setTimeout(() => setCopied(false), 2000)
      } catch (err) {
        showToast('Failed to copy to clipboard', 'error')
      }
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Email Rewriter</h1>
        <p className="text-muted-foreground">Transform your emails with AI-powered rewriting</p>
      </div>

      {status && !status.rewrite_available && (
        <Card className="border-orange-500/50 bg-orange-500/10">
          <CardContent className="pt-6">
            <div className="flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-orange-500 mt-0.5" />
              <div className="flex-1">
                <p className="font-medium text-orange-600 dark:text-orange-400">AI Provider Not Configured</p>
                <p className="text-sm text-orange-600/80 dark:text-orange-400/80 mt-1">
                  Email rewriting is currently unavailable. Please configure OPENAI_API_KEY or ANTHROPIC_API_KEY in the backend environment.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="mb-4 flex flex-wrap gap-2">
        {tones.map((tone) => (
          <button
            key={tone.value}
            onClick={() => setSelectedTone(tone.value)}
            className={`rounded-full px-4 py-2 text-sm font-medium transition-colors ${
              selectedTone === tone.value
                ? 'bg-primary text-primary-foreground'
                : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
            }`}
          >
            {tone.label}
          </button>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Original Email</CardTitle>
          </CardHeader>
          <CardContent>
            <Textarea
              value={originalEmail}
              onChange={(e) => setOriginalEmail(e.target.value)}
              placeholder="Enter your email here..."
              className="min-h-[300px]"
            />
            <Button onClick={handleRewrite} className="mt-4 w-full" disabled={loading}>
              {loading ? 'Rewriting...' : 'Rewrite'}
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Rewritten Email</CardTitle>
              {rewrittenEmail && (
                <Button variant="ghost" size="sm" onClick={handleCopy}>
                  {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                </Button>
              )}
            </div>
          </CardHeader>
          <CardContent>
            <div className="min-h-[300px] rounded-lg border border-border bg-background p-4">
              {rewrittenEmail ? (
                <p className="whitespace-pre-wrap text-sm">{rewrittenEmail}</p>
              ) : (
                <p className="text-muted-foreground">Your rewritten email will appear here...</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default Rewrite

