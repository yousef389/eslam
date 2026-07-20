import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Trash2, Search } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../lib/api'
import { formatCurrency, formatDate } from '../lib/utils'
import PageHeader from '../components/PageHeader'
import DataTable from '../components/DataTable'
import Dialog from '../components/Dialog'

interface SaleReturn {
  id: string
  return_number: string
  order_id: string
  customer_id: string
  user_id: string
  status: string
  subtotal: number
  tax_amount: number
  total: number
  reason: string
  notes: string
  created_at: string
}

interface SaleOrder {
  id: string
  order_number: string
  customer_id: string
}

interface Product {
  id: string
  name: string
  sku: string
  unit_price: number
}

interface ReturnItem {
  product_id: string
  quantity: number
  unit_price: number
}

interface PaginatedResponse {
  data: SaleReturn[]
  meta: { total: number; page: number; per_page: number }
}

const statusColors: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-700',
  approved: 'bg-green-100 text-green-700',
  rejected: 'bg-red-100 text-red-700',
  completed: 'bg-blue-100 text-blue-700',
  cancelled: 'bg-gray-100 text-gray-700',
}

const statusLabels: Record<string, string> = {
  pending: 'قيد المراجعة',
  approved: 'تمت الموافقة',
  rejected: 'مرفوض',
  completed: 'مكتمل',
  cancelled: 'ملغي',
}

export default function SaleReturnsPage() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [showCreate, setShowCreate] = useState(false)
  const [orderId, setOrderId] = useState('')
  const [items, setItems] = useState<ReturnItem[]>([])
  const [reason, setReason] = useState('')
  const [notes, setNotes] = useState('')

  const { data, isLoading } = useQuery<PaginatedResponse>({
    queryKey: ['sale-returns', page, search],
    queryFn: () => {
      const params: Record<string, unknown> = { page, per_page: 20 }
      if (search) params.search = search
      return api.get('/sale-returns', { params }).then(res => res.data)
    },
  })

  const { data: ordersData } = useQuery({
    queryKey: ['sale-orders-list'],
    queryFn: () => api.get('/sale-orders', { params: { per_page: 100 } }).then(res => res.data.data),
  })

  const { data: productsData } = useQuery({
    queryKey: ['products-list'],
    queryFn: () => api.get('/products', { params: { per_page: 100 } }).then(res => res.data.data),
  })

  const createMutation = useMutation({
    mutationFn: (payload: Record<string, unknown>) => api.post('/sale-returns', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sale-returns'] })
      toast.success('تم إنشاء مرتجع المبيعات بنجاح')
      setShowCreate(false)
      resetForm()
    },
    onError: () => toast.error('حدث خطأ أثناء إنشاء المرتجع'),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.delete(`/sale-returns/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sale-returns'] })
      toast.success('تم حذف المرتجع بنجاح')
    },
    onError: () => toast.error('حدث خطأ أثناء حذف المرتجع'),
  })

  const resetForm = () => {
    setOrderId('')
    setItems([])
    setReason('')
    setNotes('')
  }

  const addItem = () => {
    setItems([...items, { product_id: '', quantity: 1, unit_price: 0 }])
  }

  const removeItem = (index: number) => {
    setItems(items.filter((_, i) => i !== index))
  }

  const updateItem = (index: number, field: keyof ReturnItem, value: string | number) => {
    const updated = [...items]
    if (field === 'product_id') {
      const product = (productsData || []).find((p: Product) => p.id === value)
      updated[index] = { ...updated[index], product_id: value as string, unit_price: product?.unit_price || 0 }
    } else {
      updated[index] = { ...updated[index], [field]: Number(value) }
    }
    setItems(updated)
  }

  const subtotal = items.reduce((sum, item) => sum + item.unit_price * item.quantity, 0)
  const taxAmount = subtotal * 0.14
  const total = subtotal + taxAmount

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!orderId) { toast.error('اختر الفاتورة الأصلية'); return }
    if (items.length === 0) { toast.error('أضف منتج واحد على الأقل'); return }
    if (!reason.trim()) { toast.error('أدخل سبب الإرجاع'); return }
    createMutation.mutate({
      order_id: orderId,
      items: items.map(i => ({ product_id: i.product_id, quantity: i.quantity, unit_price: i.unit_price })),
      reason: reason,
      notes: notes || undefined,
    })
  }

  const returns = data?.data || []
  const meta = data?.meta
  const orders = ordersData || []
  const products = productsData || []

  const columns = [
    { key: 'return_number', header: 'رقم المرتجع', render: (item: SaleReturn) => <span className="font-mono font-medium">{item.return_number}</span> },
    { key: 'order_id', header: 'رقم الفاتورة', render: (item: SaleReturn) => orders.find((o: SaleOrder) => o.id === item.order_id)?.order_number || '-' },
    { key: 'total', header: 'الإجمالي', render: (item: SaleReturn) => formatCurrency(item.total) },
    {
      key: 'status', header: 'الحالة', render: (item: SaleReturn) => (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[item.status] || ''}`}>
          {statusLabels[item.status] || item.status}
        </span>
      ),
    },
    { key: 'reason', header: 'السبب', render: (item: SaleReturn) => <span className="truncate max-w-[200px] block">{item.reason || '-'}</span> },
    { key: 'created_at', header: 'التاريخ', render: (item: SaleReturn) => formatDate(item.created_at) },
    {
      key: 'actions', header: 'إجراءات', render: (item: SaleReturn) => (
        <button onClick={(e) => { e.stopPropagation(); if (confirm('هل أنت متأكد من حذف هذا المرتجع؟')) deleteMutation.mutate(item.id) }} className="p-1 text-red-600 hover:bg-red-50 rounded">
          <Trash2 size={16} />
        </button>
      )
    },
  ]

  return (
    <div>
      <PageHeader
        title="مرتجعات المبيعات"
        subtitle="إدارة مرتجعات المبيعات"
        action={
          <button onClick={() => setShowCreate(true)} className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
            <Plus size={18} />مرتجع جديد
          </button>
        }
      />

      <div className="flex gap-4 mb-4">
        <div className="flex-1">
          <label className="block text-sm font-medium mb-1">بحث</label>
          <div className="relative">
            <Search className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
            <input
              type="text"
              placeholder="بحث برقم المرتجع أو رقم الفاتورة..."
              value={search}
              onChange={e => { setSearch(e.target.value); setPage(1) }}
              className="w-full pr-10 pl-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      </div>

      <DataTable columns={columns} data={returns as unknown as Record<string, unknown>[]} isLoading={isLoading} emptyMessage="لا توجد مرتجعات مبيعات" />

      {meta && meta.total > 20 && (
        <div className="flex justify-center gap-2 mt-4">
          <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1} className="px-3 py-1 border rounded-lg disabled:opacity-50 hover:bg-gray-50">السابق</button>
          <span className="px-3 py-1">صفحة {page} من {Math.ceil(meta.total / 20)}</span>
          <button onClick={() => setPage(p => p + 1)} disabled={page >= Math.ceil(meta.total / 20)} className="px-3 py-1 border rounded-lg disabled:opacity-50 hover:bg-gray-50">التالي</button>
        </div>
      )}

      <Dialog isOpen={showCreate} onClose={() => { setShowCreate(false); resetForm() }} title="مرتجع مبيعات جديد" maxWidth="max-w-3xl">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">الفاتورة الأصلية *</label>
            <select value={orderId} onChange={e => setOrderId(e.target.value)} className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" required>
              <option value="">اختر الفاتورة</option>
              {orders.map((o: SaleOrder) => <option key={o.id} value={o.id}>{o.order_number}</option>)}
            </select>
          </div>

          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="font-medium">المنتجات المرتجعة</label>
              <button type="button" onClick={addItem} className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-700">
                <Plus size={16} />إضافة منتج
              </button>
            </div>
            {items.length === 0 && <p className="text-gray-500 text-sm">لم تتم إضافة أي منتجات</p>}
            {items.map((item, index) => (
              <div key={index} className="grid grid-cols-12 gap-2 mb-2 items-end">
                <div className="col-span-5">
                  <select value={item.product_id} onChange={e => updateItem(index, 'product_id', e.target.value)} className="w-full px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" required>
                    <option value="">اختر المنتج</option>
                    {products.map((p: Product) => <option key={p.id} value={p.id}>{p.name} ({p.sku})</option>)}
                  </select>
                </div>
                <div className="col-span-3">
                  <input type="number" min="1" value={item.quantity} onChange={e => updateItem(index, 'quantity', e.target.value)} className="w-full px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" required />
                </div>
                <div className="col-span-3">
                  <input type="number" step="0.01" value={item.unit_price} onChange={e => updateItem(index, 'unit_price', e.target.value)} className="w-full px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" required />
                </div>
                <div className="col-span-1">
                  <button type="button" onClick={() => removeItem(index)} className="p-2 text-red-600 hover:bg-red-50 rounded-lg">
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">سبب الإرجاع *</label>
              <input type="text" value={reason} onChange={e => setReason(e.target.value)} className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" required />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">ملاحظات</label>
              <input type="text" value={notes} onChange={e => setNotes(e.target.value)} className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
          </div>

          <div className="border-t pt-4 space-y-1 text-left">
            <div className="flex justify-between"><span>المجموع الفرعي:</span><span>{formatCurrency(subtotal)}</span></div>
            <div className="flex justify-between"><span>الضريبة (14%):</span><span>{formatCurrency(taxAmount)}</span></div>
            <div className="flex justify-between font-bold text-lg border-t pt-1"><span>الإجمالي:</span><span>{formatCurrency(total)}</span></div>
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <button type="button" onClick={() => { setShowCreate(false); resetForm() }} className="px-4 py-2 border rounded-lg hover:bg-gray-50">إلغاء</button>
            <button type="submit" disabled={createMutation.isPending} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50">
              {createMutation.isPending ? 'جاري الحفظ...' : 'إنشاء المرتجع'}
            </button>
          </div>
        </form>
      </Dialog>
    </div>
  )
}
