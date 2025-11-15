import { useEffect, useState } from 'react'
import { X } from 'lucide-react'
import { cn } from '@/lib/utils'

export interface ToastProps {
  id: string
  message: string
  type: 'success' | 'error' | 'info'
  duration?: number
  onClose: (id: string) => void
}

const Toast = ({ id, message, type, duration = 5000, onClose }: ToastProps) => {
  const [isVisible, setIsVisible] = useState(true)

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(false)
      setTimeout(() => onClose(id), 300)
    }, duration)

    return () => clearTimeout(timer)
  }, [duration, id, onClose])

  return (
    <div
      className={cn(
        'flex items-center gap-3 rounded-[1.4rem] border border-border bg-card p-4 shadow-lg transition-all',
        {
          'translate-x-0 opacity-100': isVisible,
          'translate-x-full opacity-0': !isVisible,
        }
      )}
    >
      <div
        className={cn('h-2 w-2 rounded-full', {
          'bg-chart-1': type === 'success',
          'bg-destructive': type === 'error',
          'bg-chart-4': type === 'info',
        })}
      />
      <p className="flex-1 text-sm text-foreground">{message}</p>
      <button
        onClick={() => {
          setIsVisible(false)
          setTimeout(() => onClose(id), 300)
        }}
        className="text-muted-foreground hover:text-foreground"
      >
        <X className="h-4 w-4" />
      </button>
    </div>
  )
}

export default Toast

