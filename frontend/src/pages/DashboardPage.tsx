import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts'
import {
  Package,
  Users,
  ShoppingCart,
  AlertTriangle,
  TrendingUp,
  DollarSign,
  Wallet,
  Truck,
  FileText,
  Clock,
  Bell,
  Plus,
  BarChart3,
} from 'lucide-react'
import api from '../lib/api'
import { formatCurrency } from '../lib/utils'
import StatsCard from '../components/StatsCard'

interface RecentActivity {
  order_number: string
  customer_id: string
  total: number
  status: 'draft' | 'confirmed' | 'shipped' | 'delivered' | 'cancelled'
  created_at: string
}

interface DashboardStats {
  daily_sales: number
  monthly_sales: number
  total_products: number
  total_customers: number
  low_stock_items: number
  pending_orders: number
  total_purchases: number
  net_profit: number
  cashbox_balance: number
  customer_debts_total: number
  supplier_debts_total: number
  invoice_count: number
  recent_activities: RecentActivity[]
}

const statusConfig: Record<
  string,
  { label: string; className: string }
> = {
  draft: { label: 'مسودة', className: 'bg-gray-100 text-gray-700' },
  confirmed: { label: 'مؤكد', className: 'bg-blue-100 text-blue-700' },
  shipped: { label: 'تم الشحن', className: 'bg-yellow-100 text-yellow-700' },
  delivered: { label: 'تم التوصيل', className: 'bg-green-100 text-green-700' },
  cancelled: { label: 'ملغي', className: 'bg-red-100 text-red-700' },
}

function timeAgo(dateStr: string): string {
  const now = new Date()
  const date = new Date(dateStr)
  const diffMs = now.getTime() - date.getTime()
  const diffMin = Math.floor(diffMs / 60000)
  const diffHr = Math.floor(diffMs / 3600000)
  const diffDay = Math.floor(diffMs / 86400000)

  if (diffMin < 1) return 'الآن'
  if (diffMin < 60) return `منذ ${diffMin} دقيقة`
  if (diffHr < 24) return `منذ ${diffHr} ساعة`
  return `منذ ${diffDay} يوم`
}

const defaultStats: DashboardStats = {
  daily_sales: 0,
  monthly_sales: 0,
  total_products: 0,
  total_customers: 0,
  low_stock_items: 0,
  pending_orders: 0,
  total_purchases: 0,
  net_profit: 0,
  cashbox_balance: 0,
  customer_debts_total: 0,
  supplier_debts_total: 0,
  invoice_count: 0,
  recent_activities: [],
}

export default function DashboardPage() {
  const navigate = useNavigate()

  const { data: stats, isLoading } = useQuery<DashboardStats>({
    queryKey: ['dashboard-stats'],
    queryFn: () => api.get('/dashboard/stats').then((res) => res.data.data),
  })

  const s = { ...defaultStats, ...stats }

  const chartData = [
    { name: 'المبيعات', value: Number(s.monthly_sales) || 0, fill: '#3b82f6' },
    { name: 'المشتريات', value: Number(s.total_purchases) || 0, fill: '#8b5cf6' },
  ]

  const debtData = [
    { name: 'مديونيات العملاء', value: Number(s.customer_debts_total) || 0 },
    { name: 'مستحقات الموردين', value: Number(s.supplier_debts_total) || 0 },
  ]
  const COLORS = ['#f97316', '#ef4444']

  const quickActions = [
    { label: 'المنتجات', icon: Package, path: '/products', color: 'bg-blue-500 hover:bg-blue-600' },
    { label: 'العملاء', icon: Users, path: '/customers', color: 'bg-green-500 hover:bg-green-600' },
    { label: 'فاتورة بيع جديدة', icon: Plus, path: '/sales/new', color: 'bg-purple-500 hover:bg-purple-600' },
    { label: 'التقارير', icon: BarChart3, path: '/reports', color: 'bg-orange-500 hover:bg-orange-600' },
  ]

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    )
  }

  return (
    <div className="space-y-6" dir="rtl">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <StatsCard
          title="مبيعات اليوم"
          value={Number(s.daily_sales)}
          icon={TrendingUp}
          color="green"
          isCurrency
        />
        <StatsCard
          title="المبيعات الشهرية"
          value={Number(s.monthly_sales)}
          icon={DollarSign}
          color="blue"
          isCurrency
        />
        <StatsCard
          title="المشتريات الشهرية"
          value={Number(s.total_purchases)}
          icon={ShoppingCart}
          color="purple"
          isCurrency
        />
        <StatsCard
          title="صافي الأرباح"
          value={Number(s.net_profit)}
          icon={TrendingUp}
          color={s.net_profit >= 0 ? 'green' : 'red'}
          isCurrency
        />
        <StatsCard
          title="رصيد الخزنة"
          value={Number(s.cashbox_balance)}
          icon={Wallet}
          color="emerald"
          isCurrency
        />
        <StatsCard
          title="مديونيات العملاء"
          value={Number(s.customer_debts_total)}
          icon={Users}
          color="orange"
          isCurrency
        />
        <StatsCard
          title="مستحقات الموردين"
          value={Number(s.supplier_debts_total)}
          icon={Truck}
          color="red"
          isCurrency
        />
        <StatsCard
          title="عدد الفواتير"
          value={Number(s.invoice_count)}
          icon={FileText}
          color="indigo"
        />
        <StatsCard
          title="المنتجات"
          value={Number(s.total_products)}
          icon={Package}
          color="blue"
        />
        <StatsCard
          title="المنتجات الناقصة"
          value={Number(s.low_stock_items)}
          icon={AlertTriangle}
          color="orange"
        />
        <StatsCard
          title="الطلبات المعلقة"
          value={Number(s.pending_orders)}
          icon={Clock}
          color="red"
        />
        <StatsCard
          title="التنبيهات"
          value={Number(s.low_stock_items) + Number(s.pending_orders)}
          icon={Bell}
          color="yellow"
        />
      </div>

      {/* Chart + Recent Activities */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Bar Chart */}
        <div className="lg:col-span-2 bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold mb-4">مبيعات vs مشتريات الشهر</h3>
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={chartData} layout="vertical" margin={{ right: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis type="number" tick={{ fontSize: 12 }} tickFormatter={(v: number) => v.toLocaleString('ar-EG')} />
              <YAxis type="category" dataKey="name" width={100} tick={{ fontSize: 13 }} />
              <Tooltip
                formatter={(value: number) => [formatCurrency(value), '']}
                contentStyle={{ direction: 'rtl', textAlign: 'right' }}
              />
              <Bar dataKey="value" radius={[0, 6, 6, 0]} barSize={40}>
                {chartData.map((entry, idx) => (
                  <rect key={idx} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Recent Activities */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">آخر العمليات</h3>
            <Clock size={18} className="text-gray-400" />
          </div>
          <div className="space-y-3 max-h-[320px] overflow-y-auto">
            {s.recent_activities.length === 0 ? (
              <p className="text-gray-400 text-sm text-center py-8">لا توجد عمليات حديثة</p>
            ) : (
              s.recent_activities.map((activity, idx) => {
                const status = statusConfig[activity.status] || statusConfig.draft
                return (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-3 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors"
                  >
                    <div className="flex flex-col gap-1">
                      <span className="text-sm font-medium">{activity.order_number}</span>
                      <span className="text-xs text-gray-500">{timeAgo(activity.created_at)}</span>
                    </div>
                    <div className="flex flex-col items-end gap-1">
                      <span className="text-sm font-semibold">{formatCurrency(activity.total)}</span>
                      <span className={`text-xs px-2 py-0.5 rounded-full ${status.className}`}>
                        {status.label}
                      </span>
                    </div>
                  </div>
                )
              })
            )}
          </div>
        </div>
      </div>

      {/* Debt Comparison + Financial Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold mb-4">مقارنة المديونيات</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie data={debtData} cx="50%" cy="50%" outerRadius={80} dataKey="value" label={({ name, value }) => `${name}: ${formatCurrency(value)}`}>
                {debtData.map((_, idx) => <Cell key={idx} fill={COLORS[idx]} />)}
              </Pie>
              <Tooltip formatter={(value: number) => formatCurrency(value)} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold mb-4">ملخص مالي سريع</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
              <span className="text-sm font-medium">صافي الأرباح</span>
              <span className="font-bold text-green-600">{formatCurrency(Number(s.net_profit))}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
              <span className="text-sm font-medium">رصيد الخزنة</span>
              <span className="font-bold text-blue-600">{formatCurrency(Number(s.cashbox_balance))}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-orange-50 rounded-lg">
              <span className="text-sm font-medium">مديونيات العملاء</span>
              <span className="font-bold text-orange-600">{formatCurrency(Number(s.customer_debts_total))}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-red-50 rounded-lg">
              <span className="text-sm font-medium">مستحقات الموردين</span>
              <span className="font-bold text-red-600">{formatCurrency(Number(s.supplier_debts_total))}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold mb-4">إجراءات سريعة</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {quickActions.map((action) => (
            <button
              key={action.path}
              onClick={() => navigate(action.path)}
              className={`flex items-center justify-center gap-2 p-4 rounded-lg text-white font-medium transition-colors ${action.color}`}
            >
              <action.icon size={20} />
              <span>{action.label}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
