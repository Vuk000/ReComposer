import { Check, X } from 'lucide-react'

interface PasswordRequirementsProps {
  password: string
  show?: boolean
}

interface Requirement {
  label: string
  met: boolean
}

const PasswordRequirements = ({ password, show = true }: PasswordRequirementsProps) => {
  if (!show) return null

  const requirements: Requirement[] = [
    {
      label: 'At least 8 characters',
      met: password.length >= 8,
    },
    {
      label: 'At least one letter',
      met: /[a-zA-Z]/.test(password),
    },
    {
      label: 'At least one number',
      met: /\d/.test(password),
    },
  ]

  return (
    <div className="mt-2 space-y-1.5 rounded-lg border border-border/50 bg-muted/30 p-3">
      <p className="mb-2 text-xs font-semibold text-muted-foreground">Password Requirements:</p>
      {requirements.map((req, index) => (
        <div key={index} className="flex items-center gap-2 text-xs">
          {req.met ? (
            <Check className="h-3.5 w-3.5 text-green-500" />
          ) : (
            <X className="h-3.5 w-3.5 text-muted-foreground" />
          )}
          <span className={req.met ? 'text-green-600 dark:text-green-400' : 'text-muted-foreground'}>
            {req.label}
          </span>
        </div>
      ))}
    </div>
  )
}

export default PasswordRequirements

