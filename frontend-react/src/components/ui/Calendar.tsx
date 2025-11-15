import { useState } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { cn } from '@/lib/utils'
import Button from './Button'

export interface CalendarProps {
  selectedDate?: Date
  onDateSelect?: (date: Date) => void
  className?: string
}

const Calendar = ({ selectedDate, onDateSelect, className }: CalendarProps) => {
  const [currentDate, setCurrentDate] = useState(selectedDate || new Date())

  const year = currentDate.getFullYear()
  const month = currentDate.getMonth()

  const firstDayOfMonth = new Date(year, month, 1).getDay()
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const daysInPrevMonth = new Date(year, month, 0).getDate()

  const monthNames = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December',
  ]

  const weekDays = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa']

  const prevMonth = () => {
    setCurrentDate(new Date(year, month - 1, 1))
  }

  const nextMonth = () => {
    setCurrentDate(new Date(year, month + 1, 1))
  }

  const handleDateClick = (day: number) => {
    const date = new Date(year, month, day)
    onDateSelect?.(date)
  }

  const isSelected = (day: number) => {
    if (!selectedDate) return false
    return (
      selectedDate.getDate() === day &&
      selectedDate.getMonth() === month &&
      selectedDate.getFullYear() === year
    )
  }

  const isToday = (day: number) => {
    const today = new Date()
    return (
      today.getDate() === day &&
      today.getMonth() === month &&
      today.getFullYear() === year
    )
  }

  return (
    <div className={cn('rounded-[1.4rem] border border-border bg-card p-4', className)}>
      <div className="mb-4 flex items-center justify-between">
        <Button variant="ghost" size="sm" onClick={prevMonth}>
          <ChevronLeft className="h-4 w-4" />
        </Button>
        <h3 className="font-semibold">
          {monthNames[month]} {year}
        </h3>
        <Button variant="ghost" size="sm" onClick={nextMonth}>
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>

      <div className="grid grid-cols-7 gap-1">
        {weekDays.map((day) => (
          <div key={day} className="p-2 text-center text-xs font-medium text-muted-foreground">
            {day}
          </div>
        ))}

        {Array.from({ length: firstDayOfMonth }).map((_, i) => {
          const day = daysInPrevMonth - firstDayOfMonth + i + 1
          return (
            <button
              key={`prev-${day}`}
              className="p-2 text-center text-sm text-muted-foreground/50"
              disabled
            >
              {day}
            </button>
          )
        })}

        {Array.from({ length: daysInMonth }).map((_, i) => {
          const day = i + 1
          return (
            <button
              key={day}
              onClick={() => handleDateClick(day)}
              className={cn(
                'rounded-lg p-2 text-sm transition-colors hover:bg-accent',
                isSelected(day) && 'bg-primary text-primary-foreground',
                !isSelected(day) && isToday(day) && 'border-2 border-primary',
                !isSelected(day) && !isToday(day) && 'text-foreground'
              )}
            >
              {day}
            </button>
          )
        })}
      </div>
    </div>
  )
}

export default Calendar

