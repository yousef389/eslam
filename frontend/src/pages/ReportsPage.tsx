import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { TrendingUp, TrendingDown, DollarSign, Users, Truck } from 'lucide-react'
import api from '../lib/api'
import { formatCurrency, formatDate } from '../lib/utils'
import PageHeader from '../components/PageHeader'
import StatsCard from '../components/StatsCard'
import DataTable from '../components/DataTable'

interface ReportSummary {
  total_sales: number
  total_purchases: number
  net_profit: number
  total_receivable: number
  total_payable: number
  transaction_count: number
}

interface Transaction {
  id: string
  transaction_number: string
  type: string
  amount: number
  description: string
  reference_type?: string
  created_at: string
}

interface PaginatedResponse {
  data: Transaction[]
  meta: { total: number; page: number; per_page: number }
}

export default function ReportsPage() {
  const [fromDate, setFromDate] = useState(() => {
    const now = new Date()
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-01`
  })
  const [toDate, setToDate] = useState(() => new Date().toISOString().split('T')[0])
  const [txPage, setTxPage] = useState(1)
  const [txType, setTxType] = useState('')

  const { data: summary, isLoading: loadingSummary } = useQuery<ReportSummary>({
    queryKey: ['report-summary', fromDate, toDate],
    queryFn: () => {
      const params: Record<string, string> = { from_date: fromDate, to_date: toDate }
      return api.get('/accounting/reports/summary', { params }).then(res => res.data.data)
    },
  })

  const { data: txData, isLoading: loadingTx } = useQuery<PaginatedResponse>({
    queryKey: ['report-transactions', txPage, fromDate, toDate, txType],
    queryFn: () => {
      const params: Record<string, unknown> = { page: txPage, per_page: 20, from_date: fromDate, to_date: toDate }
      if (txType) params.transaction_type = txType
      return api.get('/accounting/reports/transactions', { params }).then(res => res.data)
    },
  })

  const summaryData = summary || {
    total_sales: 0,
    total_purchases: 0,
    net_profit: 0,
    total_receivable: 0,
    total_payable: 0,
    transaction_count: 0,
  }

  const transactions = txData?.data || []
  const txMeta = txData?.meta

  const chartData = [
    { name: 'المبيعات', value: Number(summaryData.total_sales) || 0, fill: '#3b82f6' },
    { name: 'المشتريات', value: Number(summaryData.total_purchases) || 0, fill: '#ef4444' },
    { name: 'صافي الربح', value: Number(summaryData.net_profit) || 0, fill: '#22c55e' },
  ]

  const txColumns = [
    {
      key: 'transaction_number',
      header: 'رقم العملية',
      render: (item: Transaction) => <span className="font-mono text-sm">{item.transaction_number}</span>,
    },
    {
      key: 'type',
      header: 'النوع',
      render: (item: Transaction) => {
        const typeLabels: Record<string, string> = { sale: 'مبيعات', purchase: 'مشتريات', debt_payment: 'دفعة دين', cashbox: 'صندوق' }
        return <span className="text-sm">{typeLabels[item.type] || item.type}</span>
      },
    },
    { key: 'amount', header: 'المبلغ', render: (item: Transaction) => formatCurrency(item.amount) },
    { key: 'description', header: 'الوصف', render: (item: Transaction) => item.description },
    { key: 'created_at', header: 'التاريخ', render: (item: Transaction) => formatDate(item.created_at) },
  ]

  return (
    <div>
      <PageHeader title="التقارير" subtitle="عرض التقارير والإحصائيات المالية" />

      <div className="flex gap-4 mb-6">
        <div>
          <label className="block text-sm font-medium mb-1">من تاريخ</label>
          <input type="date" value={fromDate} onChange={e => setFromDate(e.target.value)} className="px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">إلى تاريخ</label>
          <input type="date" value={toDate} onChange={e => setToDate(e.target.value)} className="px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-8">
        <StatsCard title="إجمالي المبيعات" value={Number(summaryData.total_sales)} icon={TrendingUp} color="green" isCurrency />
        <StatsCard title="إجمالي المشتريات" value={Number(summaryData.total_purchases)} icon={TrendingDown} color="red" isCurrency />
        <StatsCard title="صافي الربح" value={Number(summaryData.net_profit)} icon={DollarSign} color="blue" isCurrency />
        <StatsCard title="المبالغ المستحقة" value={Number(summaryData.total_receivable)} icon={Users} color="orange" isCurrency />
        <StatsCard title="المبالغ الدائنة" value={Number(summaryData.total_payable)} icon={Truck} color="purple" isCurrency />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold mb-4">مقارنة المبيعات والمشتريات</h3>
          {loadingSummary ? (
            <div className="text-center py-8 text-gray-500">جاري التحميل...</div>
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip formatter={(value: number) => formatCurrency(value)} />
                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                  {chartData.map((entry, index) => (
                    <rect key={index} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold mb-4">ملخص</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
              <span className="text-gray-700">إجمالي المبيعات</span>
              <span className="font-bold text-green-600">{formatCurrency(Number(summaryData.total_sales))}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-red-50 rounded-lg">
              <span className="text-gray-700">إجمالي المشتريات</span>
              <span className="font-bold text-red-600">{formatCurrency(Number(summaryData.total_purchases))}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
              <span className="text-gray-700">صافي الربح</span>
              <span className="font-bold text-blue-600">{formatCurrency(Number(summaryData.net_profit))}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
              <span className="text-gray-700">عدد المعاملات</span>
              <span className="font-bold">{summaryData.transaction_count}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">المعاملات</h3>
          <select value={txType} onChange={e => { setTxType(e.target.value); setTxPage(1) }} className="px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="">جميع الأنواع</option>
            <option value="sale">مبيعات</option>
            <option value="purchase">مشتريات</option>
            <option value="debt_payment">دفعة دين</option>
            <option value="cashbox">صندوق</option>
          </select>
        </div>

        <DataTable columns={txColumns} data={transactions as unknown as Record<string, unknown>[]} isLoading={loadingTx} emptyMessage="لا توجد معاملات" />

        {txMeta && txMeta.total > 20 && (
          <div className="flex justify-center gap-2 mt-4">
            <button onClick={() => setTxPage(p => Math.max(1, p - 1))} disabled={txPage === 1} className="px-3 py-1 border rounded-lg disabled:opacity-50 hover:bg-gray-50">السابق</button>
            <span className="px-3 py-1">صفحة {txPage} من {Math.ceil(txMeta.total / 20)}</span>
            <button onClick={() => setTxPage(p => p + 1)} disabled={txPage >= Math.ceil(txMeta.total / 20)} className="px-3 py-1 border rounded-lg disabled:opacity-50 hover:bg-gray-50">التالي</button>
          </div>
        )}
      </div>
    </div>
  )
}
