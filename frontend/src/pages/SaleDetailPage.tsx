import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ArrowRight, ChevronLeft } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../lib/api'
import { formatCurrency, formatDate } from '../lib/utils'
import PageHeader from '../components/PageHeader'
import LoadingSpinner from '../components/LoadingSpinner'

interface SaleOrderItem {
  id: string
  product_id: string
  quantity: number
  unit_price: number
  discount: number
  total: number
}

interface SaleOrder {
  id: string
  order_number: string
  customer_id: string
  status: string
  subtotal: number
  discount: number
  tax_amount: number
  total: number
  payment_method: string
  notes?: string
  items: SaleOrderItem[]
  created_at: string
  updated_at: string
}

interface Product {
  id: string
  name: string
}

interface Customer {
  id: string
  name: string
}

const statusColors: Record<string, string> = {
  draft: 'bg-gray-100 text-gray-700',
  confirmed: 'bg-blue-100 text-blue-700',
  shipped: 'bg-yellow-100 text-yellow-700',
  delivered: 'bg-green-100 text-green-700',
  cancelled: 'bg-red-100 text-red-700',
}

const statusLabels: Record<string, string> = {
  draft: 'مسودة',
  confirmed: 'مؤكد',
  shipped: 'تم الشحن',
  delivered: 'تم التوصيل',
  cancelled: 'ملغي',
}

const nextStatus: Record<string, string> = {
  draft: 'confirmed',
  confirmed: 'shipped',
  shipped: 'delivered',
}

const nextStatusLabel: Record<string, string> = {
  draft: 'تأكيد',
  confirmed: 'شحن',
  shipped: 'توصيل',
}

export default function SaleDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['sale-order', id],
    queryFn: () => api.get(`/sale-orders/${id}`).then(res => res.data.data),
    enabled: !!id,
  })

  const { data: customersData } = useQuery({
    queryKey: ['customers-list'],
    queryFn: () => api.get('/customers', { params: { per_page: 100 } }).then(res => res.data.data),
  })

  const { data: productsData } = useQuery({
    queryKey: ['products-list'],
    queryFn: () => api.get('/products', { params: { per_page: 100 } }).then(res => res.data.data),
  })

  const statusMutation = useMutation({
    mutationFn: (newStatus: string) => api.put(`/sale-orders/${id}/status`, { status: newStatus }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sale-order', id] })
      toast.success('تم تحديث حالة الفاتورة')
    },
    onError: () => toast.error('حدث خطأ أثناء تحديث الحالة'),
  })

  if (isLoading) return <LoadingSpinner />
  if (!data) return <div className="text-center py-8 text-gray-500">الفاتورة غير موجودة</div>

  const order: SaleOrder = data
  const customers = customersData || []
  const products = productsData || []
  const customerName = customers.find((c: Customer) => c.id === order.customer_id)?.name || '-'
  const next = nextStatus[order.status]

  const getProductName = (productId: string) => products.find((p: Product) => p.id === productId)?.name || productId

  return (
    <div>
      <PageHeader
        title={`فاتورة ${order.order_number}`}
        subtitle={formatDate(order.created_at)}
        action={
          <div className="flex gap-2">
            <button onClick={() => navigate('/sales')} className="flex items-center gap-2 border px-4 py-2 rounded-lg hover:bg-gray-50">
              <ArrowRight size={18} />رجوع
            </button>
            {next && (
              <button onClick={() => statusMutation.mutate(next)} disabled={statusMutation.isPending} className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50">
                <ChevronLeft size={18} />{nextStatusLabel[order.status]}
              </button>
            )}
          </div>
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="font-semibold mb-3">معلومات الفاتورة</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between"><span className="text-gray-500">رقم الفاتورة:</span><span className="font-mono font-medium">{order.order_number}</span></div>
            <div className="flex justify-between"><span className="text-gray-500">العميل:</span><span className="font-medium">{customerName}</span></div>
            <div className="flex justify-between"><span className="text-gray-500">التاريخ:</span><span className="font-medium">{formatDate(order.created_at)}</span></div>
            <div className="flex justify-between"><span className="text-gray-500">طريقة الدفع:</span><span className="font-medium">{
              { cash: 'نقدي', bank_transfer: 'تحويل بنكي', credit_card: 'بطاقة ائتمان', cheque: 'شيك' }[order.payment_method] || order.payment_method
            }</span></div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="font-semibold mb-3">الحالة</h3>
          <div className="space-y-2">
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${statusColors[order.status] || ''}`}>
              {statusLabels[order.status] || order.status}
            </span>
            {order.notes && <div className="mt-3"><span className="text-sm text-gray-500">ملاحظات:</span><p className="text-sm">{order.notes}</p></div>}
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="font-semibold mb-3">الإجماليات</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between"><span className="text-gray-500">المجموع الفرعي:</span><span>{formatCurrency(order.subtotal)}</span></div>
            <div className="flex justify-between"><span className="text-gray-500">الخصم:</span><span>{formatCurrency(order.discount)}</span></div>
            <div className="flex justify-between"><span className="text-gray-500">الضريبة:</span><span>{formatCurrency(order.tax_amount)}</span></div>
            <div className="flex justify-between font-bold text-lg border-t pt-2"><span>الإجمالي:</span><span>{formatCurrency(order.total)}</span></div>
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="font-semibold mb-4">المنتجات</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-right text-sm font-semibold text-gray-700">المنتج</th>
                <th className="px-4 py-3 text-right text-sm font-semibold text-gray-700">الكمية</th>
                <th className="px-4 py-3 text-right text-sm font-semibold text-gray-700">سعر الوحدة</th>
                <th className="px-4 py-3 text-right text-sm font-semibold text-gray-700">الخصم</th>
                <th className="px-4 py-3 text-right text-sm font-semibold text-gray-700">الإجمالي</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {order.items.map(item => (
                <tr key={item.id}>
                  <td className="px-4 py-3 text-sm font-medium">{getProductName(item.product_id)}</td>
                  <td className="px-4 py-3 text-sm">{item.quantity}</td>
                  <td className="px-4 py-3 text-sm">{formatCurrency(item.unit_price)}</td>
                  <td className="px-4 py-3 text-sm">{formatCurrency(item.discount)}</td>
                  <td className="px-4 py-3 text-sm font-medium">{formatCurrency(item.total)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
