import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Search, Plus } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../lib/api'
import { formatCurrency } from '../lib/utils'
import PageHeader from '../components/PageHeader'
import DataTable from '../components/DataTable'
import Dialog from '../components/Dialog'

interface Product {
  id: string
  name: string
  sku: string
  barcode?: string
  description?: string
  category_id?: string
  unit_price: number
  cost_price: number
  quantity_in_stock: number
  minimum_stock_level: number
  maximum_stock_level: number
  unit: string
  is_active: boolean
  image_url?: string
  created_at: string
  updated_at: string
}

interface PaginatedResponse {
  data: Product[]
  meta: { total: number; page: number; per_page: number }
}

const emptyForm = {
  name: '',
  sku: '',
  barcode: '',
  description: '',
  category_id: '',
  unit_price: '',
  cost_price: '',
  quantity_in_stock: '',
  minimum_stock_level: '',
  maximum_stock_level: '',
  unit: 'piece',
}

export default function ProductsPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [showCreate, setShowCreate] = useState(false)
  const [form, setForm] = useState(emptyForm)

  const { data, isLoading } = useQuery<PaginatedResponse>({
    queryKey: ['products', page, search],
    queryFn: () =>
      api
        .get('/products', { params: { page, per_page: 20, search: search || undefined } })
        .then(res => res.data),
  })

  const createMutation = useMutation({
    mutationFn: (payload: Record<string, unknown>) => api.post('/products', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] })
      toast.success('تم إضافة المنتج بنجاح')
      setShowCreate(false)
      setForm(emptyForm)
    },
    onError: () => toast.error('حدث خطأ أثناء إضافة المنتج'),
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    createMutation.mutate({
      name: form.name,
      sku: form.sku,
      barcode: form.barcode || undefined,
      description: form.description || undefined,
      category_id: form.category_id || undefined,
      unit_price: Number(form.unit_price),
      cost_price: Number(form.cost_price),
      quantity_in_stock: Number(form.quantity_in_stock) || 0,
      minimum_stock_level: Number(form.minimum_stock_level) || 0,
      maximum_stock_level: Number(form.maximum_stock_level) || 1000,
      unit: form.unit,
    })
  }

  const products = data?.data || []
  const meta = data?.meta

  const columns = [
    {
      key: 'name',
      header: 'اسم المنتج',
      render: (item: Product) => (
        <div>
          <div className="font-medium">{item.name}</div>
          <div className="text-xs text-gray-500">{item.sku}</div>
        </div>
      ),
    },
    {
      key: 'unit_price',
      header: 'سعر البيع',
      render: (item: Product) => formatCurrency(item.unit_price),
    },
    {
      key: 'quantity_in_stock',
      header: 'المخزون',
      render: (item: Product) => (
        <span
          className={
            item.quantity_in_stock <= item.minimum_stock_level
              ? 'text-red-600 font-semibold'
              : ''
          }
        >
          {item.quantity_in_stock}
          {item.quantity_in_stock <= item.minimum_stock_level && ' ⚠'}
        </span>
      ),
    },
    {
      key: 'is_active',
      header: 'الحالة',
      render: (item: Product) => (
        <span
          className={`px-2 py-1 rounded-full text-xs font-medium ${
            item.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'
          }`}
        >
          {item.is_active ? 'نشط' : 'غير نشط'}
        </span>
      ),
    },
  ]

  return (
    <div>
      <PageHeader
        title="المنتجات"
        subtitle="إدارة المنتجات والمخزون"
        action={
          <button
            onClick={() => setShowCreate(true)}
            className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            <Plus size={18} />
            إضافة منتج
          </button>
        }
      />

      <div className="mb-4">
        <div className="relative max-w-md">
          <Search className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
          <input
            type="text"
            value={search}
            onChange={e => {
              setSearch(e.target.value)
              setPage(1)
            }}
            placeholder="بحث بالاسم أو الكود..."
            className="w-full pr-10 pl-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      <DataTable
        columns={columns}
        data={products as unknown as Record<string, unknown>[]}
        isLoading={isLoading}
        onRowClick={item => navigate(`/products/${(item as unknown as Product).id}`)}
        emptyMessage="لا توجد منتجات"
      />

      {meta && meta.total > 20 && (
        <div className="flex justify-center gap-2 mt-4">
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-3 py-1 border rounded-lg disabled:opacity-50 hover:bg-gray-50"
          >
            السابق
          </button>
          <span className="px-3 py-1">
            صفحة {page} من {Math.ceil(meta.total / 20)}
          </span>
          <button
            onClick={() => setPage(p => p + 1)}
            disabled={page >= Math.ceil(meta.total / 20)}
            className="px-3 py-1 border rounded-lg disabled:opacity-50 hover:bg-gray-50"
          >
            التالي
          </button>
        </div>
      )}

      <Dialog isOpen={showCreate} onClose={() => setShowCreate(false)} title="إضافة منتج جديد" maxWidth="max-w-xl">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">اسم المنتج *</label>
              <input
                type="text"
                value={form.name}
                onChange={e => setForm({ ...form, name: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">كود المنتج (SKU) *</label>
              <input
                type="text"
                value={form.sku}
                onChange={e => setForm({ ...form, sku: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">الباركود</label>
              <input
                type="text"
                value={form.barcode}
                onChange={e => setForm({ ...form, barcode: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">الوحدة</label>
              <select
                value={form.unit}
                onChange={e => setForm({ ...form, unit: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="piece">قطعة</option>
                <option value="box">علبة</option>
                <option value="meter">متر</option>
                <option value="kg">كيلوجرام</option>
                <option value="roll">لفة</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">سعر البيع *</label>
              <input
                type="number"
                step="0.01"
                value={form.unit_price}
                onChange={e => setForm({ ...form, unit_price: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">سعر التكلفة *</label>
              <input
                type="number"
                step="0.01"
                value={form.cost_price}
                onChange={e => setForm({ ...form, cost_price: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">الكمية</label>
              <input
                type="number"
                value={form.quantity_in_stock}
                onChange={e => setForm({ ...form, quantity_in_stock: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">الحد الأدنى</label>
              <input
                type="number"
                value={form.minimum_stock_level}
                onChange={e => setForm({ ...form, minimum_stock_level: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">الحد الأقصى</label>
              <input
                type="number"
                value={form.maximum_stock_level}
                onChange={e => setForm({ ...form, maximum_stock_level: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">الوصف</label>
            <textarea
              value={form.description}
              onChange={e => setForm({ ...form, description: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={2}
            />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={() => setShowCreate(false)}
              className="px-4 py-2 border rounded-lg hover:bg-gray-50"
            >
              إلغاء
            </button>
            <button
              type="submit"
              disabled={createMutation.isPending}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {createMutation.isPending ? 'جاري الحفظ...' : 'حفظ'}
            </button>
          </div>
        </form>
      </Dialog>
    </div>
  )
}
