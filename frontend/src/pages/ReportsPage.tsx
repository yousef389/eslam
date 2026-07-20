import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell,
} from 'recharts'
import {
  FileText, Download, Printer, TrendingUp, TrendingDown,
  DollarSign, Users, Truck, Package,
} from 'lucide-react'
import api from '../lib/api'
import { formatCurrency, formatDate } from '../lib/utils'
import PageHeader from '../components/PageHeader'
import LoadingSpinner from '../components/LoadingSpinner'

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

interface DashboardStats {
  total_customers?: number
  total_suppliers?: number
  total_products?: number
  low_stock_count?: number
  cashbox_balance?: number
  daily_sales?: number
  daily_purchases?: number
  monthly_sales?: number
  monthly_purchases?: number
  recent_transactions?: Transaction[]
  [key: string]: unknown
}

const TABS = [
  { key: 'sales', label: 'تقرير المبيعات', icon: TrendingUp },
  { key: 'purchases', label: 'تقرير المشتريات', icon: TrendingDown },
  { key: 'profit', label: 'تقرير الأرباح', icon: DollarSign },
  { key: 'cashbox', label: 'تقرير الخزنة', icon: DollarSign },
  { key: 'customers', label: 'تقرير العملاء', icon: Users },
  { key: 'suppliers', label: 'تقرير الموردين', icon: Truck },
  { key: 'debts', label: 'تقرير الديون', icon: FileText },
  { key: 'inventory', label: 'تقرير المخزون', icon: Package },
] as const

const CHART_COLORS = ['#22c55e', '#3b82f6', '#ef4444', '#f59e0b', '#8b5cf6', '#06b6d4']

function SummaryCard({ title, value, icon: Icon, color, isCurrency = true }: {
  title: string; value: number; icon: React.ElementType; color: string; isCurrency?: boolean
}) {
  const colorMap: Record<string, string> = {
    green: 'bg-green-50 text-green-600',
    blue: 'bg-blue-50 text-blue-600',
    red: 'bg-red-50 text-red-600',
    orange: 'bg-orange-50 text-orange-600',
    purple: 'bg-purple-50 text-purple-600',
    indigo: 'bg-indigo-50 text-indigo-600',
    teal: 'bg-teal-50 text-teal-600',
    amber: 'bg-amber-50 text-amber-600',
  }

  return (
    <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-100">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500 font-medium">{title}</p>
          <p className="text-2xl font-bold mt-1 text-gray-900">
            {isCurrency ? formatCurrency(value) : value}
          </p>
        </div>
        <div className={`p-3 rounded-xl ${colorMap[color] || colorMap.blue}`}>
          <Icon size={22} />
        </div>
      </div>
    </div>
  )
}

function BarCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
      <h3 className="text-base font-semibold text-gray-800 mb-4">{title}</h3>
      {children}
    </div>
  )
}

function EmptyState({ message }: { message: string }) {
  return (
    <div className="text-center py-16 text-gray-400">
      <FileText size={48} className="mx-auto mb-3 opacity-40" />
      <p className="text-sm">{message}</p>
    </div>
  )
}

function TransactionsTable({ data, isLoading }: { data: Transaction[]; isLoading: boolean }) {
  if (isLoading) return <LoadingSpinner />

  const typeLabels: Record<string, string> = {
    sale: 'مبيعات',
    purchase: 'مشتريات',
    debt_payment: 'دفعة دين',
    cashbox: 'إيداع صندوق',
    cashbox_withdrawal: 'سحب من صندوق',
  }

  const typeColors: Record<string, string> = {
    sale: 'bg-green-100 text-green-700',
    purchase: 'bg-red-100 text-red-700',
    debt_payment: 'bg-blue-100 text-blue-700',
    cashbox: 'bg-purple-100 text-purple-700',
    cashbox_withdrawal: 'bg-orange-100 text-orange-700',
  }

  if (data.length === 0) return <EmptyState message="لا توجد معاملات في الفترة المحددة" />

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-100">
            <th className="text-right py-3 px-4 font-semibold text-gray-600">رقم العملية</th>
            <th className="text-right py-3 px-4 font-semibold text-gray-600">النوع</th>
            <th className="text-right py-3 px-4 font-semibold text-gray-600">المبلغ</th>
            <th className="text-right py-3 px-4 font-semibold text-gray-600">الوصف</th>
            <th className="text-right py-3 px-4 font-semibold text-gray-600">التاريخ</th>
          </tr>
        </thead>
        <tbody>
          {data.map((tx) => (
            <tr key={tx.id} className="border-b border-gray-50 hover:bg-gray-50 transition-colors">
              <td className="py-3 px-4 font-mono text-xs text-gray-700">{tx.transaction_number}</td>
              <td className="py-3 px-4">
                <span className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-medium ${typeColors[tx.type] || 'bg-gray-100 text-gray-700'}`}>
                  {typeLabels[tx.type] || tx.type}
                </span>
              </td>
              <td className="py-3 px-4 font-semibold text-gray-900">{formatCurrency(tx.amount)}</td>
              <td className="py-3 px-4 text-gray-600 max-w-[200px] truncate">{tx.description}</td>
              <td className="py-3 px-4 text-gray-500">{formatDate(tx.created_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default function ReportsPage() {
  const [activeTab, setActiveTab] = useState<string>('sales')
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

  const { data: dashboardStats, isLoading: loadingDashboard } = useQuery<DashboardStats>({
    queryKey: ['dashboard-stats'],
    queryFn: () => api.get('/dashboard/stats').then(res => res.data.data || res.data),
  })

  const s = summary || {
    total_sales: 0,
    total_purchases: 0,
    net_profit: 0,
    total_receivable: 0,
    total_payable: 0,
    transaction_count: 0,
  }

  const transactions = txData?.data || []
  const txMeta = txData?.meta

  const handlePrint = () => window.print()

  const handleExport = () => {
    alert('قريباً - تصدير PDF')
  }

  const avgInvoice = s.transaction_count > 0 ? s.total_sales / s.transaction_count : 0

  const salesBarData = [
    { name: 'المبيعات', value: Number(s.total_sales) || 0, fill: '#22c55e' },
    { name: 'المشتريات', value: Number(s.total_purchases) || 0, fill: '#ef4444' },
  ]

  const profitPieData = [
    { name: 'المبيعات', value: Math.max(0, Number(s.total_sales) || 0) },
    { name: 'المشتريات', value: Math.max(0, Number(s.total_purchases) || 0) },
    { name: 'صافي الربح', value: Math.max(0, Number(s.net_profit) || 0) },
  ].filter(d => d.value > 0)

  const debtsPieData = [
    { name: 'المبالغ المستحقة (العملاء)', value: Math.max(0, Number(s.total_receivable) || 0) },
    { name: 'المبالغ الدائنة (الموردين)', value: Math.max(0, Number(s.total_payable) || 0) },
  ].filter(d => d.value > 0)

  const renderTabContent = () => {
    if (loadingSummary) return <LoadingSpinner size="lg" />

    switch (activeTab) {
      case 'sales':
        return (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <SummaryCard title="إجمالي المبيعات" value={Number(s.total_sales)} icon={TrendingUp} color="green" />
              <SummaryCard title="عدد الفواتير" value={s.transaction_count} icon={FileText} color="blue" isCurrency={false} />
              <SummaryCard title="متوسط الفاتورة" value={avgInvoice} icon={DollarSign} color="indigo" />
            </div>

            <BarCard title="مقارنة المبيعات والمشتريات">
              <ResponsiveContainer width="100%" height={320}>
                <BarChart data={salesBarData} barSize={60}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="name" tick={{ fontSize: 13 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip formatter={(value: number) => formatCurrency(value)} />
                  <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                    {salesBarData.map((entry, index) => (
                      <Cell key={index} fill={entry.fill} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </BarCard>

            <BarCard title="المعاملات">
              <TransactionsTable data={transactions} isLoading={loadingTx} />
              {txMeta && txMeta.total > 20 && (
                <div className="flex justify-center gap-2 mt-4 pt-4 border-t border-gray-100">
                  <button
                    onClick={() => setTxPage(p => Math.max(1, p - 1))}
                    disabled={txPage === 1}
                    className="px-4 py-1.5 text-sm border rounded-lg disabled:opacity-40 hover:bg-gray-50 transition-colors"
                  >
                    السابق
                  </button>
                  <span className="px-4 py-1.5 text-sm text-gray-600">
                    صفحة {txPage} من {Math.ceil(txMeta.total / 20)}
                  </span>
                  <button
                    onClick={() => setTxPage(p => p + 1)}
                    disabled={txPage >= Math.ceil(txMeta.total / 20)}
                    className="px-4 py-1.5 text-sm border rounded-lg disabled:opacity-40 hover:bg-gray-50 transition-colors"
                  >
                    التالي
                  </button>
                </div>
              )}
            </BarCard>
          </div>
        )

      case 'purchases':
        return (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <SummaryCard title="إجمالي المشتريات" value={Number(s.total_purchases)} icon={TrendingDown} color="red" />
              <SummaryCard title="عدد فواتير المشتريات" value={s.transaction_count} icon={FileText} color="orange" isCurrency={false} />
            </div>

            <BarCard title="المشتريات مقابل المبيعات">
              <ResponsiveContainer width="100%" height={320}>
                <BarChart data={salesBarData} barSize={60}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="name" tick={{ fontSize: 13 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip formatter={(value: number) => formatCurrency(value)} />
                  <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                    {salesBarData.map((entry, index) => (
                      <Cell key={index} fill={entry.fill} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </BarCard>

            <BarCard title="معاملات المشتريات">
              <TransactionsTable data={transactions.filter(t => t.type === 'purchase')} isLoading={loadingTx} />
            </BarCard>
          </div>
        )

      case 'profit':
        return (
          <div className="space-y-6">
            <div className="bg-gradient-to-br from-blue-600 to-indigo-700 rounded-xl p-8 text-white">
              <p className="text-sm opacity-80 mb-1">صافي الأرباح</p>
              <p className="text-4xl font-bold mb-4">{formatCurrency(Number(s.net_profit))}</p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
                <div className="bg-white/10 rounded-lg p-4">
                  <p className="text-xs opacity-70">إجمالي المبيعات</p>
                  <p className="text-lg font-bold">{formatCurrency(Number(s.total_sales))}</p>
                </div>
                <div className="bg-white/10 rounded-lg p-4">
                  <p className="text-xs opacity-70">إجمالي المشتريات</p>
                  <p className="text-lg font-bold">{formatCurrency(Number(s.total_purchases))}</p>
                </div>
                <div className="bg-white/10 rounded-lg p-4">
                  <p className="text-xs opacity-70">نسبة الربح</p>
                  <p className="text-lg font-bold">
                    {s.total_sales > 0 ? `${((Number(s.net_profit) / Number(s.total_sales)) * 100).toFixed(1)}%` : '0%'}
                  </p>
                </div>
              </div>
            </div>

            {profitPieData.length > 0 && (
              <BarCard title="توزيع الأرباح">
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={profitPieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={110}
                      paddingAngle={4}
                      dataKey="value"
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    >
                      {profitPieData.map((_, index) => (
                        <Cell key={index} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value: number) => formatCurrency(value)} />
                  </PieChart>
                </ResponsiveContainer>
              </BarCard>
            )}
          </div>
        )

      case 'cashbox':
        return (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <SummaryCard
                title="رصيد الخزنة الحالي"
                value={Number(dashboardStats?.cashbox_balance) || 0}
                icon={DollarSign}
                color="teal"
              />
              <SummaryCard
                title="إجمالي المبيعات"
                value={Number(s.total_sales) || 0}
                icon={TrendingUp}
                color="green"
              />
              <SummaryCard
                title="إجمالي المشتريات"
                value={Number(s.total_purchases) || 0}
                icon={TrendingDown}
                color="red"
              />
            </div>

            <BarCard title=" movements الخزنة (المعاملات)">
              <TransactionsTable
                data={transactions.filter(t => t.type === 'cashbox' || t.type === 'cashbox_withdrawal')}
                isLoading={loadingTx}
              />
            </BarCard>
          </div>
        )

      case 'customers':
        return (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <SummaryCard
                title="إجمالي المستحقات من العملاء"
                value={Number(s.total_receivable) || 0}
                icon={Users}
                color="orange"
              />
              <SummaryCard
                title="عدد العملاء"
                value={Number(dashboardStats?.total_customers) || 0}
                icon={Users}
                color="blue"
                isCurrency={false}
              />
            </div>

            <BarCard title="تفاصيل المستحقات">
              <div className="space-y-3">
                <div className="flex justify-between items-center p-4 bg-orange-50 rounded-lg">
                  <span className="text-gray-700 font-medium">المبالغ المستحقة من العملاء</span>
                  <span className="font-bold text-orange-600 text-lg">{formatCurrency(Number(s.total_receivable))}</span>
                </div>
                <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                  <span className="text-gray-700 font-medium">الرصيد الصافي للعملاء</span>
                  <span className="font-bold text-gray-900 text-lg">
                    {formatCurrency((Number(s.total_receivable) || 0) - (Number(s.total_payable) || 0))}
                  </span>
                </div>
              </div>
            </BarCard>
          </div>
        )

      case 'suppliers':
        return (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <SummaryCard
                title="إجمالي الدائنة للموردين"
                value={Number(s.total_payable) || 0}
                icon={Truck}
                color="purple"
              />
              <SummaryCard
                title="عدد الموردين"
                value={Number(dashboardStats?.total_suppliers) || 0}
                icon={Truck}
                color="indigo"
                isCurrency={false}
              />
            </div>

            <BarCard title="تفاصيل الدائنة">
              <div className="space-y-3">
                <div className="flex justify-between items-center p-4 bg-purple-50 rounded-lg">
                  <span className="text-gray-700 font-medium">المبالغ الدائنة للموردين</span>
                  <span className="font-bold text-purple-600 text-lg">{formatCurrency(Number(s.total_payable))}</span>
                </div>
                <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                  <span className="text-gray-700 font-medium">الرصيد الصافي للموردين</span>
                  <span className="font-bold text-gray-900 text-lg">
                    {formatCurrency((Number(s.total_payable) || 0) - (Number(s.total_receivable) || 0))}
                  </span>
                </div>
              </div>
            </BarCard>
          </div>
        )

      case 'debts':
        return (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <SummaryCard
                title="المبالغ المستحقة (العملاء)"
                value={Number(s.total_receivable) || 0}
                icon={Users}
                color="orange"
              />
              <SummaryCard
                title="المبالغ الدائنة (الموردين)"
                value={Number(s.total_payable) || 0}
                icon={Truck}
                color="purple"
              />
              <SummaryCard
                title="صافي الديون"
                value={(Number(s.total_receivable) || 0) - (Number(s.total_payable) || 0)}
                icon={DollarSign}
                color="blue"
              />
            </div>

            {debtsPieData.length > 0 && (
              <BarCard title="توزيع الديون">
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={debtsPieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={110}
                      paddingAngle={4}
                      dataKey="value"
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    >
                      {debtsPieData.map((_, index) => (
                        <Cell key={index} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value: number) => formatCurrency(value)} />
                  </PieChart>
                </ResponsiveContainer>
              </BarCard>
            )}

            <BarCard title="معاملات الديون">
              <TransactionsTable
                data={transactions.filter(t => t.type === 'debt_payment')}
                isLoading={loadingTx}
              />
            </BarCard>
          </div>
        )

      case 'inventory':
        return (
          <div className="space-y-6">
            {loadingDashboard ? (
              <LoadingSpinner />
            ) : (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <SummaryCard
                    title="إجمالي المنتجات"
                    value={Number(dashboardStats?.total_products) || 0}
                    icon={Package}
                    color="teal"
                    isCurrency={false}
                  />
                  <SummaryCard
                    title="منتجاتStock منخفض"
                    value={Number(dashboardStats?.low_stock_count) || 0}
                    icon={Package}
                    color="red"
                    isCurrency={false}
                  />
                </div>

                <BarCard title="ملخص المخزون">
                  <div className="space-y-3">
                    <div className="flex justify-between items-center p-4 bg-teal-50 rounded-lg">
                      <span className="text-gray-700 font-medium">إجمالي المنتجات المسجلة</span>
                      <span className="font-bold text-teal-600 text-lg">{Number(dashboardStats?.total_products) || 0}</span>
                    </div>
                    <div className="flex justify-between items-center p-4 bg-red-50 rounded-lg">
                      <span className="text-gray-700 font-medium">منتجاتStock منخفض</span>
                      <span className="font-bold text-red-600 text-lg">{Number(dashboardStats?.low_stock_count) || 0}</span>
                    </div>
                    <div className="flex justify-between items-center p-4 bg-green-50 rounded-lg">
                      <span className="text-gray-700 font-medium">المنتجات الطبيعية (Stock جيد)</span>
                      <span className="font-bold text-green-600 text-lg">
                        {(Number(dashboardStats?.total_products) || 0) - (Number(dashboardStats?.low_stock_count) || 0)}
                      </span>
                    </div>
                  </div>
                </BarCard>
              </>
            )}
          </div>
        )

      default:
        return null
    }
  }

  return (
    <div className="min-h-screen">
      <PageHeader
        title="التقارير"
        subtitle="عرض التقارير والإحصائيات المالية"
        action={
          <div className="flex gap-2">
            <button
              onClick={handlePrint}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <Printer size={16} />
              طباعة
            </button>
            <button
              onClick={handleExport}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Download size={16} />
              تصدير PDF
            </button>
          </div>
        }
      />

      <div className="flex flex-wrap gap-2 mb-6 p-1 bg-gray-50 rounded-xl">
        {TABS.map((tab) => {
          const Icon = tab.icon
          return (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium rounded-lg transition-all ${
                activeTab === tab.key
                  ? 'bg-white text-blue-600 shadow-sm border border-gray-200'
                  : 'text-gray-500 hover:text-gray-700 hover:bg-white/50'
              }`}
            >
              <Icon size={16} />
              {tab.label}
            </button>
          )
        })}
      </div>

      <div className="flex flex-wrap items-center gap-4 mb-6 p-4 bg-white rounded-xl shadow-sm border border-gray-100">
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-gray-600">من تاريخ</label>
          <input
            type="date"
            value={fromDate}
            onChange={(e) => setFromDate(e.target.value)}
            className="px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-gray-600">إلى تاريخ</label>
          <input
            type="date"
            value={toDate}
            onChange={(e) => setToDate(e.target.value)}
            className="px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        {activeTab === 'sales' && (
          <div className="flex items-center gap-2 mr-auto">
            <label className="text-sm font-medium text-gray-600">نوع المعاملة</label>
            <select
              value={txType}
              onChange={(e) => { setTxType(e.target.value); setTxPage(1) }}
              className="px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">جميع الأنواع</option>
              <option value="sale">مبيعات</option>
              <option value="purchase">مشتريات</option>
              <option value="debt_payment">دفعة دين</option>
              <option value="cashbox">إيداع صندوق</option>
              <option value="cashbox_withdrawal">سحب من صندوق</option>
            </select>
          </div>
        )}
      </div>

      {renderTabContent()}
    </div>
  )
}
