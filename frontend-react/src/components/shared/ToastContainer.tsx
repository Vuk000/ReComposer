import Toast, { ToastProps } from './Toast'

export const ToastContainer = ({ toasts, onClose }: { toasts: Omit<ToastProps, 'onClose'>[]; onClose: (id: string) => void }) => {
  if (toasts.length === 0) return null

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
      {toasts.map((toast) => (
        <Toast key={toast.id} {...toast} onClose={onClose} />
      ))}
    </div>
  )
}

