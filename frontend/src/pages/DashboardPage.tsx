import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { Package, Users, ShoppingCart, AlertTriangle, TrendingUp, CreditCard } from 'lucide-react'
import api from '../lib/api'
import StatsCard from '../components/StatsCard'

export default function DashboardPage() {
  const navigate = useNavigate()

  const { data: stats } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => api.get('/dashboard/stats').then(res => res.data.data),
  })

  const statsData = stats || {
    daily_sales: 0,
    monthly_sales: 0,
    total_products: 0,
    total_customers: 0,
    low_stock_items: 0,
    pending_orders: 0,
  }

  const chartData = [
    { name: 'المبيعات', value: Number(statsData.monthly_sales) || 0 },
    { name: 'المشتريات', value: (Number(statsData.monthly_sales) * 0.6) || 0 },
  ]

  const quickActions = [
    { label: 'المنتجات', icon: Package, path: '/products', color: 'bg-blue-500' },
    { label: 'العملاء', icon: Users, path: '/customers', color: 'bg-green-500' },
    { label: 'مبيعات', icon: ShoppingCart, path: '/sales', color: 'bg-purple-500' },
    { label: 'التقارير', icon: TrendingUp, path: '/reports', color: 'bg-orange-500' },
  ]

  return (
    <div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <StatsCard title="مبيعات اليوم" value={Number(statsData.daily_sales)} icon={TrendingUp} color="green" isCurrency />
        <StatsCard title="إجمالي المبيعات الشهرية" value={Number(statsData.monthly_sales)} icon={CreditCard} color="blue" isCurrency />
        <StatsCard title="المنتجات" value={statsData.total_products} icon={Package} color="purple" />
        <StatsCard title="العملاء" value={statsData.total_customers} icon={Users} color="blue" />
        <StatsCard title="تنبيه المخزون" value={statsData.low_stock_items} icon={AlertTriangle} color="orange" />
        <StatsCard title="الطلبات المعلقة" value={statsData.pending_orders} icon={ShoppingCart} color="red" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-2 bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold mb-4">مبيعات الشهر</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip formatter={(value: number) => `${value.toLocaleString('ar-EG')} ج.م`} />
              <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold mb-4">إجراءات سريعة</h3>
          <div className="space-y-3">
            {quickActions.map(action => (
              <button
                key={action.path}
                onClick={() => navigate(action.path)}
                className="w-full flex items-center gap-3 p-3 rounded-lg border hover:bg-gray-50 transition-colors"
              >
                <div className={`p-2 rounded-lg text-white ${action.color}`}>
                  <action.icon size={18} />
                </div>
                <span className="font-medium">{action.label}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
