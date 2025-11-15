import { ReactNode, useState } from 'react'
import { ChevronDown } from 'lucide-react'
import { cn } from '@/lib/utils'

export interface AccordionItem {
  id: string
  title: string
  content: ReactNode
}

export interface AccordionProps {
  items: AccordionItem[]
  allowMultiple?: boolean
  className?: string
}

const Accordion = ({ items, allowMultiple = false, className }: AccordionProps) => {
  const [openItems, setOpenItems] = useState<Set<string>>(new Set())

  const toggleItem = (id: string) => {
    setOpenItems((prev) => {
      const newSet = new Set(prev)
      if (newSet.has(id)) {
        newSet.delete(id)
      } else {
        if (!allowMultiple) {
          newSet.clear()
        }
        newSet.add(id)
      }
      return newSet
    })
  }

  return (
    <div className={cn('space-y-4', className)}>
      {items.map((item, index) => {
        const isOpen = openItems.has(item.id)
        return (
          <div
            key={item.id}
            className={cn(
              'group relative overflow-hidden rounded-xl border transition-all duration-300',
              isOpen
                ? 'border-primary/50 bg-gradient-to-br from-primary/10 via-primary/5 to-transparent shadow-lg shadow-primary/10'
                : 'border-border/50 bg-card/50 hover:border-primary/30 hover:bg-card'
            )}
          >
            {/* Decorative gradient overlay */}
            <div
              className={cn(
                'absolute inset-0 bg-gradient-to-r from-primary/5 to-transparent opacity-0 transition-opacity duration-300',
                isOpen && 'opacity-100'
              )}
            />
            
            <button
              onClick={() => toggleItem(item.id)}
              className="relative flex w-full items-center justify-between p-6 text-left transition-all"
            >
              <div className="flex items-start gap-4 flex-1">
                <div className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary/20 text-primary transition-all group-hover:bg-primary/30">
                  <span className="text-sm font-bold">{index + 1}</span>
                </div>
                <span className="text-lg font-semibold leading-relaxed">{item.title}</span>
              </div>
              <ChevronDown
                className={cn(
                  'ml-4 h-5 w-5 shrink-0 text-primary transition-all duration-300',
                  isOpen && 'rotate-180'
                )}
              />
            </button>
            
            {isOpen && (
              <div className="relative overflow-hidden">
                <div className="mx-6 mb-2 h-px bg-gradient-to-r from-transparent via-primary/30 to-transparent" />
                <div className="px-6 pb-6 pl-16">
                  <div className="text-base leading-relaxed text-muted-foreground animate-fade-in">
                    {item.content}
                  </div>
                </div>
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}

export default Accordion

