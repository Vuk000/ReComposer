import { useState } from 'react'
import { Copy, Check } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Textarea from '@/components/ui/Textarea'
import { useRewrite } from '@/hooks/useRewrite'
import { useToast } from '@/contexts/ToastContext'

const Rewrite = () => {
  const [originalEmail, setOriginalEmail] = useState('')
  const [rewrittenEmail, setRewrittenEmail] = useState('')
  const [selectedTone, setSelectedTone] = useState<'professional' | 'friendly' | 'persuasive'>('professional')
  const [copied, setCopied] = useState(false)
  const { rewriteEmail, loading, error } = useRewrite()
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
      await navigator.clipboard.writeText(rewrittenEmail)
      setCopied(true)
      showToast('Copied to clipboard!', 'success')
      setTimeout(() => setCopied(false), 2000)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Email Rewriter</h1>
        <p className="text-muted-foreground">Transform your emails with AI-powered rewriting</p>
      </div>

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

