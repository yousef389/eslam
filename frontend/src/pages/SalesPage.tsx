import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Trash2 } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../lib/api'
import { formatCurrency, formatDate } from '../lib/utils'
import PageHeader from '../components/PageHeader'
import DataTable from '../components/DataTable'
import Dialog from '../components/Dialog'

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
  created_at: string
  updated_at: string
}

interface Customer {
  id: string
  name: string
}

interface Product {
  id: string
  name: string
  sku: string
  unit_price: number
  quantity_in_stock: number
}

interface OrderItem {
  product_id: string
  quantity: number
  unit_price: number
  discount: number
}

interface PaginatedResponse {
  data: SaleOrder[]
  meta: { total: number; page: number; per_page: number }
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

export default function SalesPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [fromDate, setFromDate] = useState('')
  const [toDate, setToDate] = useState('')
  const [showCreate, setShowCreate] = useState(false)
  const [customerId, setCustomerId] = useState('')
  const [items, setItems] = useState<OrderItem[]>([])
  const [discount, setDiscount] = useState('')
  const [taxRate, setTaxRate] = useState('0.14')
  const [paymentMethod, setPaymentMethod] = useState('cash')
  const [notes, setNotes] = useState('')

  const { data, isLoading } = useQuery<PaginatedResponse>({
    queryKey: ['sales', page, fromDate, toDate],
    queryFn: () => {
      const params: Record<string, unknown> = { page, per_page: 20 }
      if (fromDate) params.from_date = fromDate
      if (toDate) params.to_date = toDate
      return api.get('/sale-orders', { params }).then(res => res.data)
    },
  })

  const { data: customersData } = useQuery({
    queryKey: ['customers-list'],
    queryFn: () => api.get('/customers', { params: { per_page: 100 } }).then(res => res.data.data),
  })

  const { data: productsData } = useQuery({
    queryKey: ['products-list'],
    queryFn: () => api.get('/products', { params: { per_page: 100 } }).then(res => res.data.data),
  })

  const createMutation = useMutation({
    mutationFn: (payload: Record<string, unknown>) => api.post('/sale-orders', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sales'] })
      toast.success('تم إنشاء فاتورة المبيعات بنجاح')
      setShowCreate(false)
      resetForm()
    },
    onError: () => toast.error('حدث خطأ أثناء إنشاء الفاتورة'),
  })

  const resetForm = () => {
    setCustomerId('')
    setItems([])
    setDiscount('')
    setTaxRate('0.14')
    setPaymentMethod('cash')
    setNotes('')
  }

  const addItem = () => {
    setItems([...items, { product_id: '', quantity: 1, unit_price: 0, discount: 0 }])
  }

  const removeItem = (index: number) => {
    setItems(items.filter((_, i) => i !== index))
  }

  const updateItem = (index: number, field: keyof OrderItem, value: string | number) => {
    const updated = [...items]
    if (field === 'product_id') {
      const product = (productsData || []).find((p: Product) => p.id === value)
      updated[index] = { ...updated[index], product_id: value as string, unit_price: product?.unit_price || 0 }
    } else {
      updated[index] = { ...updated[index], [field]: Number(value) }
    }
    setItems(updated)
  }

  const subtotal = items.reduce((sum, item) => sum + item.unit_price * item.quantity - item.discount, 0)
  const taxAmount = subtotal * Number(taxRate)
  const total = subtotal + taxAmount - Number(discount || 0)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!customerId) { toast.error('اختر العميل'); return }
    if (items.length === 0) { toast.error('أضف منتج واحد على الأقل'); return }
    createMutation.mutate({
      customer_id: customerId,
      items: items.map(i => ({ product_id: i.product_id, quantity: i.quantity, unit_price: i.unit_price, discount: i.discount })),
      discount: Number(discount) || 0,
      tax_rate: Number(taxRate),
      payment_method: paymentMethod,
      notes: notes || undefined,
    })
  }

  const orders = data?.data || []
  const meta = data?.meta
  const customers = customersData || []
  const products = productsData || []

  const columns = [
    { key: 'order_number', header: 'رقم الفاتورة', render: (item: SaleOrder) => <span className="font-mono font-medium">{item.order_number}</span> },
    { key: 'customer_id', header: 'العميل', render: (item: SaleOrder) => customers.find((c: Customer) => c.id === item.customer_id)?.name || '-' },
    { key: 'total', header: 'الإجمالي', render: (item: SaleOrder) => formatCurrency(item.total) },
    {
      key: 'status', header: 'الحالة', render: (item: SaleOrder) => (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[item.status] || ''}`}>
          {statusLabels[item.status] || item.status}
        </span>
      ),
    },
    { key: 'payment_method', header: 'طريقة الدفع', render: (item: SaleOrder) => ({ cash: 'نقدي', bank_transfer: 'تحويل بنكي', credit_card: 'بطاقة ائتمان', cheque: 'شيك' }[item.payment_method] || item.payment_method) },
    { key: 'created_at', header: 'التاريخ', render: (item: SaleOrder) => formatDate(item.created_at) },
  ]

  return (
    <div>
      <PageHeader
        title="مبيعات"
        subtitle="إدارة فواتير المبيعات"
        action={
          <button onClick={() => setShowCreate(true)} className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
            <Plus size={18} />فاتورة جديدة
          </button>
        }
      />

      <div className="flex gap-4 mb-4">
        <div>
          <label className="block text-sm font-medium mb-1">من تاريخ</label>
          <input type="date" value={fromDate} onChange={e => { setFromDate(e.target.value); setPage(1) }} className="px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">إلى تاريخ</label>
          <input type="date" value={toDate} onChange={e => { setToDate(e.target.value); setPage(1) }} className="px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
      </div>

      <DataTable columns={columns} data={orders as unknown as Record<string, unknown>[]} isLoading={isLoading} onRowClick={item => navigate(`/sales/${(item as unknown as SaleOrder).id}`)} emptyMessage="لا توجد فواتير مبيعات" />

      {meta && meta.total > 20 && (
        <div className="flex justify-center gap-2 mt-4">
          <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1} className="px-3 py-1 border rounded-lg disabled:opacity-50 hover:bg-gray-50">السابق</button>
          <span className="px-3 py-1">صفحة {page} من {Math.ceil(meta.total / 20)}</span>
          <button onClick={() => setPage(p => p + 1)} disabled={page >= Math.ceil(meta.total / 20)} className="px-3 py-1 border rounded-lg disabled:opacity-50 hover:bg-gray-50">التالي</button>
        </div>
      )}

      <Dialog isOpen={showCreate} onClose={() => { setShowCreate(false); resetForm() }} title="فاتورة مبيعات جديدة" maxWidth="max-w-3xl">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">العميل *</label>
              <select value={customerId} onChange={e => setCustomerId(e.target.value)} className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" required>
                <option value="">اختر العميل</option>
                {customers.map((c: Customer) => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">طريقة الدفع</label>
              <select value={paymentMethod} onChange={e => setPaymentMethod(e.target.value)} className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="cash">نقدي</option>
                <option value="bank_transfer">تحويل بنكي</option>
                <option value="credit_card">بطاقة ائتمان</option>
                <option value="cheque">شيك</option>
              </select>
            </div>
          </div>

          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="font-medium">المنتجات</label>
              <button type="button" onClick={addItem} className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-700">
                <Plus size={16} />إضافة منتج
              </button>
            </div>
            {items.length === 0 && <p className="text-gray-500 text-sm">لم تتم إضافة أي منتجات</p>}
            {items.map((item, index) => (
              <div key={index} className="grid grid-cols-12 gap-2 mb-2 items-end">
                <div className="col-span-4">
                  <select value={item.product_id} onChange={e => updateItem(index, 'product_id', e.target.value)} className="w-full px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" required>
                    <option value="">اختر المنتج</option>
                    {products.map((p: Product) => <option key={p.id} value={p.id}>{p.name} ({p.sku})</option>)}
                  </select>
                </div>
                <div className="col-span-2">
                  <input type="number" min="1" value={item.quantity} onChange={e => updateItem(index, 'quantity', e.target.value)} className="w-full px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" required />
                </div>
                <div className="col-span-2">
                  <input type="number" step="0.01" value={item.unit_price} onChange={e => updateItem(index, 'unit_price', e.target.value)} className="w-full px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" required />
                </div>
                <div className="col-span-2">
                  <input type="number" step="0.01" value={item.discount} onChange={e => updateItem(index, 'discount', e.target.value)} className="w-full px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="خصم" />
                </div>
                <div className="col-span-2">
                  <button type="button" onClick={() => removeItem(index)} className="p-2 text-red-600 hover:bg-red-50 rounded-lg">
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">خصم</label>
              <input type="number" step="0.01" value={discount} onChange={e => setDiscount(e.target.value)} className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">نسبة الضريبة</label>
              <input type="number" step="0.01" value={taxRate} onChange={e => setTaxRate(e.target.value)} className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">ملاحظات</label>
              <input type="text" value={notes} onChange={e => setNotes(e.target.value)} className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
          </div>

          <div className="border-t pt-4 space-y-1 text-left">
            <div className="flex justify-between"><span>المجموع الفرعي:</span><span>{formatCurrency(subtotal)}</span></div>
            <div className="flex justify-between"><span>الخصم:</span><span>{formatCurrency(Number(discount) || 0)}</span></div>
            <div className="flex justify-between"><span>الضريبة:</span><span>{formatCurrency(taxAmount)}</span></div>
            <div className="flex justify-between font-bold text-lg border-t pt-1"><span>الإجمالي:</span><span>{formatCurrency(total)}</span></div>
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <button type="button" onClick={() => { setShowCreate(false); resetForm() }} className="px-4 py-2 border rounded-lg hover:bg-gray-50">إلغاء</button>
            <button type="submit" disabled={createMutation.isPending} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50">
              {createMutation.isPending ? 'جاري الحفظ...' : 'إنشاء الفاتورة'}
            </button>
          </div>
        </form>
      </Dialog>
    </div>
  )
}
