import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Trash2, Search, Printer } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../lib/api'
import { formatCurrency, formatDate } from '../lib/utils'
import PageHeader from '../components/PageHeader'
import DataTable from '../components/DataTable'
import Dialog from '../components/Dialog'

interface PurchaseReturn {
  id: string
  return_number: string
  order_id: string
  supplier_id: string
  user_id: string
  status: string
  subtotal: number
  tax_amount: number
  total: number
  reason: string
  notes: string
  created_at: string
}

interface PurchaseOrder {
  id: string
  order_number: string
}

interface Supplier {
  id: string
  name: string
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
  data: PurchaseReturn[]
  meta: { total: number; page: number; per_page: number }
}

const statusColors: Record<string, string> = {
  draft: 'bg-gray-100 text-gray-700',
  pending: 'bg-yellow-100 text-yellow-700',
  approved: 'bg-blue-100 text-blue-700',
  completed: 'bg-green-100 text-green-700',
  rejected: 'bg-red-100 text-red-700',
}

const statusLabels: Record<string, string> = {
  draft: 'مسودة',
  pending: 'قيد المراجعة',
  approved: 'تمت الموافقة',
  completed: 'تم الإتمام',
  rejected: 'مرفوض',
}

export default function PurchaseReturnsPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [fromDate, setFromDate] = useState('')
  const [toDate, setToDate] = useState('')
  const [showCreate, setShowCreate] = useState(false)
  const [orderId, setOrderId] = useState('')
  const [supplierId, setSupplierId] = useState('')
  const [items, setItems] = useState<ReturnItem[]>([])
  const [reason, setReason] = useState('')
  const [notes, setNotes] = useState('')
  const [deleteId, setDeleteId] = useState<string | null>(null)

  const { data, isLoading } = useQuery<PaginatedResponse>({
    queryKey: ['purchase-returns', page, search, fromDate, toDate],
    queryFn: () => {
      const params: Record<string, unknown> = { page, per_page: 20 }
      if (search) params.search = search
      if (fromDate) params.from_date = fromDate
      if (toDate) params.to_date = toDate
      return api.get('/purchase-returns', { params }).then(res => res.data)
    },
  })

  const { data: ordersData } = useQuery({
    queryKey: ['purchase-orders-list'],
    queryFn: () => api.get('/purchase-orders', { params: { per_page: 100 } }).then(res => res.data.data),
  })

  const { data: suppliersData } = useQuery({
    queryKey: ['suppliers-list'],
    queryFn: () => api.get('/suppliers', { params: { per_page: 100 } }).then(res => res.data.data),
  })

  const { data: productsData } = useQuery({
    queryKey: ['products-list'],
    queryFn: () => api.get('/products', { params: { per_page: 100 } }).then(res => res.data.data),
  })

  const createMutation = useMutation({
    mutationFn: (payload: Record<string, unknown>) => api.post('/purchase-returns', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['purchase-returns'] })
      toast.success('تم إنشاء مرتجع الشراء بنجاح')
      setShowCreate(false)
      resetForm()
    },
    onError: () => toast.error('حدث خطأ أثناء إنشاء المرتجع'),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.delete(`/purchase-returns/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['purchase-returns'] })
      toast.success('تم حذف المرتجع بنجاح')
      setDeleteId(null)
    },
    onError: () => toast.error('حدث خطأ أثناء الحذف'),
  })

  const resetForm = () => {
    setOrderId('')
    setSupplierId('')
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

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!orderId) { toast.error('اختر فاتورة الشراء'); return }
    if (!supplierId) { toast.error('اختر المورد'); return }
    if (items.length === 0) { toast.error('أضف منتج واحد على الأقل'); return }
    if (!reason.trim()) { toast.error('أدخل سبب المرتجع'); return }
    createMutation.mutate({
      order_id: orderId,
      supplier_id: supplierId,
      items: items.map(i => ({ product_id: i.product_id, quantity: i.quantity, unit_price: i.unit_price })),
      reason: reason,
      notes: notes || undefined,
    })
  }

  const returns = data?.data || []
  const meta = data?.meta
  const orders = ordersData || []
  const suppliers = suppliersData || []
  const products = productsData || []

  const columns = [
    { key: 'return_number', header: 'رقم المرتجع', render: (item: PurchaseReturn) => <span className="font-mono font-medium">{item.return_number}</span> },
    { key: 'supplier_id', header: 'المورد', render: (item: PurchaseReturn) => suppliers.find((s: Supplier) => s.id === item.supplier_id)?.name || '-' },
    { key: 'order_id', header: 'رقم الطلب', render: (item: PurchaseReturn) => orders.find((o: PurchaseOrder) => o.id === item.order_id)?.order_number || '-' },
    { key: 'total', header: 'الإجمالي', render: (item: PurchaseReturn) => formatCurrency(item.total) },
    {
      key: 'status', header: 'الحالة', render: (item: PurchaseReturn) => (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[item.status] || ''}`}>
          {statusLabels[item.status] || item.status}
        </span>
      ),
    },
    { key: 'created_at', header: 'التاريخ', render: (item: PurchaseReturn) => formatDate(item.created_at) },
    {
      key: 'actions', header: 'إجراءات', render: (item: PurchaseReturn) => (
        <div className="flex gap-1" onClick={e => e.stopPropagation()}>
          <button onClick={() => navigate(`/purchase-returns/${item.id}`)} className="p-1.5 text-gray-600 hover:bg-gray-100 rounded-lg" title="عرض">
            <Printer size={16} />
          </button>
          <button onClick={() => setDeleteId(item.id)} className="p-1.5 text-red-600 hover:bg-red-50 rounded-lg" title="حذف">
            <Trash2 size={16} />
          </button>
        </div>
      ),
    },
  ]

  return (
    <div>
      <PageHeader
        title="مرتجعات المشتريات"
        subtitle="إدارة مرتجعات المشتريات"
        action={
          <button onClick={() => setShowCreate(true)} className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
            <Plus size={18} />مرتجع جديد
          </button>
        }
      />

      <div className="flex gap-4 mb-4 items-end">
        <div className="flex-1 max-w-sm">
          <label className="block text-sm font-medium mb-1">بحث</label>
          <div className="relative">
            <Search className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
            <input
              type="text"
              placeholder="رقم المرتجع أو اسم المورد..."
              value={search}
              onChange={e => { setSearch(e.target.value); setPage(1) }}
              className="w-full pr-10 pl-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">من تاريخ</label>
          <input type="date" value={fromDate} onChange={e => { setFromDate(e.target.value); setPage(1) }} className="px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">إلى تاريخ</label>
          <input type="date" value={toDate} onChange={e => { setToDate(e.target.value); setPage(1) }} className="px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
      </div>

      <DataTable columns={columns} data={returns as unknown as Record<string, unknown>[]} isLoading={isLoading} onRowClick={item => navigate(`/purchase-returns/${(item as unknown as PurchaseReturn).id}`)} emptyMessage="لا توجد مرتجعات مشتريات" />

      {meta && meta.total > 20 && (
        <div className="flex justify-center gap-2 mt-4">
          <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1} className="px-3 py-1 border rounded-lg disabled:opacity-50 hover:bg-gray-50">السابق</button>
          <span className="px-3 py-1">صفحة {page} من {Math.ceil(meta.total / 20)}</span>
          <button onClick={() => setPage(p => p + 1)} disabled={page >= Math.ceil(meta.total / 20)} className="px-3 py-1 border rounded-lg disabled:opacity-50 hover:bg-gray-50">التالي</button>
        </div>
      )}

      <Dialog isOpen={!!deleteId} onClose={() => setDeleteId(null)} title="تأكيد الحذف" maxWidth="max-w-sm">
        <p className="mb-4">هل أنت متأكد من حذف هذا المرتجع؟</p>
        <div className="flex justify-end gap-2">
          <button onClick={() => setDeleteId(null)} className="px-4 py-2 border rounded-lg hover:bg-gray-50">إلغاء</button>
          <button
            onClick={() => deleteId && deleteMutation.mutate(deleteId)}
            disabled={deleteMutation.isPending}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
          >
            {deleteMutation.isPending ? 'جاري الحذف...' : 'حذف'}
          </button>
        </div>
      </Dialog>

      <Dialog isOpen={showCreate} onClose={() => { setShowCreate(false); resetForm() }} title="مرتجع شراء جديد" maxWidth="max-w-3xl">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">فاتورة الشراء *</label>
              <select value={orderId} onChange={e => setOrderId(e.target.value)} className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" required>
                <option value="">اختر فاتورة الشراء</option>
                {orders.map((o: PurchaseOrder) => <option key={o.id} value={o.id}>{o.order_number}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">المورد *</label>
              <select value={supplierId} onChange={e => setSupplierId(e.target.value)} className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" required>
                <option value="">اختر المورد</option>
                {suppliers.map((s: Supplier) => <option key={s.id} value={s.id}>{s.name}</option>)}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">سبب المرتجع *</label>
            <input type="text" value={reason} onChange={e => setReason(e.target.value)} placeholder="أدخل سبب المرتجع..." className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" required />
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
                <div className="col-span-5">
                  <select value={item.product_id} onChange={e => updateItem(index, 'product_id', e.target.value)} className="w-full px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" required>
                    <option value="">اختر المنتج</option>
                    {products.map((p: Product) => <option key={p.id} value={p.id}>{p.name} ({p.sku})</option>)}
                  </select>
                </div>
                <div className="col-span-3">
                  <input type="number" min="1" value={item.quantity} onChange={e => updateItem(index, 'quantity', e.target.value)} className="w-full px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="الكمية" required />
                </div>
                <div className="col-span-3">
                  <input type="number" step="0.01" value={item.unit_price} onChange={e => updateItem(index, 'unit_price', e.target.value)} className="w-full px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="سعر الوحدة" required />
                </div>
                <div className="col-span-1">
                  <button type="button" onClick={() => removeItem(index)} className="p-2 text-red-600 hover:bg-red-50 rounded-lg">
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div className="border-t pt-4 space-y-1 text-left">
            <div className="flex justify-between font-bold text-lg"><span>الإجمالي:</span><span>{formatCurrency(subtotal)}</span></div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">ملاحظات</label>
            <textarea value={notes} onChange={e => setNotes(e.target.value)} rows={2} className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="ملاحظات إضافية..." />
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
