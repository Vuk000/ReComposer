import { ReactNode, useState } from 'react'
import { cn } from '@/lib/utils'

export interface Tab {
  id: string
  label: string
  content: ReactNode
}

export interface TabsProps {
  tabs: Tab[]
  defaultTab?: string
  className?: string
}

const Tabs = ({ tabs, defaultTab, className }: TabsProps) => {
  const [activeTab, setActiveTab] = useState(defaultTab || tabs[0]?.id)

  const activeTabContent = tabs.find((tab) => tab.id === activeTab)?.content

  return (
    <div className={cn('w-full', className)}>
      <div className="flex border-b border-border">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={cn(
              'px-4 py-2 text-sm font-medium transition-colors',
              activeTab === tab.id
                ? 'border-b-2 border-primary text-foreground'
                : 'text-muted-foreground hover:text-foreground'
            )}
          >
            {tab.label}
          </button>
        ))}
      </div>
      <div className="mt-4">{activeTabContent}</div>
    </div>
  )
}

export default Tabs

