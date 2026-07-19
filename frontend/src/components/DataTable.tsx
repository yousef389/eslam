import { ReactNode } from 'react'

export interface Column {
  key: string
  header: string
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  render?: (item: any) => ReactNode
  className?: string
}

interface DataTableProps<T> {
  columns: Column[]
  data: T[]
  isLoading?: boolean
  emptyMessage?: string
  onRowClick?: (item: T) => void
}

export default function DataTable<T extends Record<string, unknown> = Record<string, unknown>>({
  columns,
  data,
  isLoading,
  emptyMessage,
  onRowClick,
}: DataTableProps<T>) {
  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-8 text-gray-500">
        <div className="h-6 w-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
        <span className="mr-2">جاري التحميل...</span>
      </div>
    )
  }

  if (!data?.length) {
    return (
      <div className="text-center py-8 text-gray-500 bg-white rounded-lg shadow">
        {emptyMessage || 'لا توجد بيانات'}
      </div>
    )
  }

  return (
    <div className="overflow-x-auto bg-white rounded-lg shadow">
      <table className="w-full">
        <thead className="bg-gray-50">
          <tr>
            {columns.map(col => (
              <th
                key={col.key}
                className={`px-4 py-3 text-right text-sm font-semibold text-gray-700 ${col.className || ''}`}
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          {data.map((item, idx) => (
            <tr
              key={(item.id as string) || idx}
              onClick={() => onRowClick?.(item)}
              className={onRowClick ? 'cursor-pointer hover:bg-gray-50 transition-colors' : ''}
            >
              {columns.map(col => (
                <td key={col.key} className={`px-4 py-3 text-sm ${col.className || ''}`}>
                  {col.render ? col.render(item) : String(item[col.key] ?? '')}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
