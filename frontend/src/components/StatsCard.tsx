import { LucideIcon } from 'lucide-react'
import { formatCurrency, formatNumber } from '../lib/utils'

interface StatsCardProps {
  title: string
  value: number
  icon: LucideIcon
  color?: string
  isCurrency?: boolean
}

const colorClasses: Record<string, string> = {
  blue: 'bg-blue-50 text-blue-600',
  green: 'bg-green-50 text-green-600',
  orange: 'bg-orange-50 text-orange-600',
  red: 'bg-red-50 text-red-600',
  purple: 'bg-purple-50 text-purple-600',
}

export default function StatsCard({ title, value, icon: Icon, color = 'blue', isCurrency = false }: StatsCardProps) {
  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500">{title}</p>
          <p className="text-2xl font-bold mt-1">
            {isCurrency ? formatCurrency(value) : formatNumber(value)}
          </p>
        </div>
        <div className={`p-3 rounded-lg ${colorClasses[color] || colorClasses.blue}`}>
          <Icon size={24} />
        </div>
      </div>
    </div>
  )
}
