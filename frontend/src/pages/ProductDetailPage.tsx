import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ArrowRight, Edit, Trash2, Package } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../lib/api'
import { formatCurrency, formatDate } from '../lib/utils'
import PageHeader from '../components/PageHeader'
import LoadingSpinner from '../components/LoadingSpinner'
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

export default function ProductDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [editMode, setEditMode] = useState(false)
  const [showDelete, setShowDelete] = useState(false)
  const [form, setForm] = useState<Partial<Product>>({})

  const { data, isLoading } = useQuery({
    queryKey: ['product', id],
    queryFn: () => api.get(`/products/${id}`).then(res => res.data.data),
    enabled: !!id,
  })

  const updateMutation = useMutation({
    mutationFn: (payload: Record<string, unknown>) => api.put(`/products/${id}`, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['product', id] })
      queryClient.invalidateQueries({ queryKey: ['products'] })
      toast.success('تم تحديث المنتج بنجاح')
      setEditMode(false)
    },
    onError: () => toast.error('حدث خطأ أثناء تحديث المنتج'),
  })

  const deleteMutation = useMutation({
    mutationFn: () => api.delete(`/products/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] })
      toast.success('تم حذف المنتج بنجاح')
      navigate('/products')
    },
    onError: () => toast.error('حدث خطأ أثناء حذف المنتج'),
  })

  if (isLoading) return <LoadingSpinner />
  if (!data) return <div className="text-center py-8 text-gray-500">المنتج غير موجود</div>

  const product: Product = data
  const stockPercent = product.maximum_stock_level
    ? (product.quantity_in_stock / product.maximum_stock_level) * 100
    : 0
  const isLowStock = product.quantity_in_stock <= product.minimum_stock_level

  const handleSave = () => {
    updateMutation.mutate(form as Record<string, unknown>)
  }

  const startEdit = () => {
    setForm({
      name: product.name,
      sku: product.sku,
      barcode: product.barcode,
      description: product.description,
      unit_price: product.unit_price,
      cost_price: product.cost_price,
      quantity_in_stock: product.quantity_in_stock,
      minimum_stock_level: product.minimum_stock_level,
      maximum_stock_level: product.maximum_stock_level,
      unit: product.unit,
    })
    setEditMode(true)
  }

  return (
    <div>
      <PageHeader
        title={product.name}
        subtitle={`SKU: ${product.sku}`}
        action={
          <div className="flex gap-2">
            <button
              onClick={() => navigate('/products')}
              className="flex items-center gap-2 border px-4 py-2 rounded-lg hover:bg-gray-50"
            >
              <ArrowRight size={18} />
              رجوع
            </button>
            <button
              onClick={startEdit}
              className="flex items-center gap-2 border px-4 py-2 rounded-lg hover:bg-gray-50"
            >
              <Edit size={18} />
              تعديل
            </button>
            <button
              onClick={() => setShowDelete(true)}
              className="flex items-center gap-2 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700"
            >
              <Trash2 size={18} />
              حذف
            </button>
          </div>
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border space-y-4">
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <Package size={20} />
            معلومات المنتج
          </h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <span className="text-sm text-gray-500">الاسم</span>
              <p className="font-medium">{product.name}</p>
            </div>
            <div>
              <span className="text-sm text-gray-500">SKU</span>
              <p className="font-medium">{product.sku}</p>
            </div>
            <div>
              <span className="text-sm text-gray-500">الباركود</span>
              <p className="font-medium">{product.barcode || '-'}</p>
            </div>
            <div>
              <span className="text-sm text-gray-500">الوحدة</span>
              <p className="font-medium">{product.unit}</p>
            </div>
            <div>
              <span className="text-sm text-gray-500">سعر البيع</span>
              <p className="font-medium">{formatCurrency(product.unit_price)}</p>
            </div>
            <div>
              <span className="text-sm text-gray-500">سعر التكلفة</span>
              <p className="font-medium">{formatCurrency(product.cost_price)}</p>
            </div>
            <div>
              <span className="text-sm text-gray-500">تاريخ الإنشاء</span>
              <p className="font-medium">{formatDate(product.created_at)}</p>
            </div>
            <div>
              <span className="text-sm text-gray-500">آخر تحديث</span>
              <p className="font-medium">{formatDate(product.updated_at)}</p>
            </div>
          </div>
          {product.description && (
            <div>
              <span className="text-sm text-gray-500">الوصف</span>
              <p className="font-medium">{product.description}</p>
            </div>
          )}
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border space-y-4">
          <h3 className="text-lg font-semibold">مستوى المخزون</h3>
          <div className={`p-4 rounded-lg ${isLowStock ? 'bg-red-50 border border-red-200' : 'bg-green-50 border border-green-200'}`}>
            <div className="flex justify-between mb-2">
              <span className={`font-semibold text-lg ${isLowStock ? 'text-red-600' : 'text-green-600'}`}>
                {product.quantity_in_stock} {product.unit}
              </span>
              {isLowStock && (
                <span className="text-red-600 text-sm font-medium">⚠ مخزون منخفض</span>
              )}
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className={`h-3 rounded-full ${isLowStock ? 'bg-red-500' : 'bg-green-500'}`}
                style={{ width: `${Math.min(stockPercent, 100)}%` }}
              />
            </div>
            <div className="flex justify-between text-sm text-gray-500 mt-1">
              <span>الحد الأدنى: {product.minimum_stock_level}</span>
              <span>الحد الأقصى: {product.maximum_stock_level}</span>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="p-3 bg-gray-50 rounded-lg">
              <span className="text-sm text-gray-500">الحالة</span>
              <p className={`font-medium ${product.is_active ? 'text-green-600' : 'text-gray-500'}`}>
                {product.is_active ? 'نشط' : 'غير نشط'}
              </p>
            </div>
            <div className="p-3 bg-gray-50 rounded-lg">
              <span className="text-sm text-gray-500">هامش الربح</span>
              <p className="font-medium">
                {product.unit_price > 0
                  ? `${((1 - product.cost_price / product.unit_price) * 100).toFixed(1)}%`
                  : '-'}
              </p>
            </div>
          </div>
        </div>
      </div>

      <Dialog isOpen={editMode} onClose={() => setEditMode(false)} title="تعديل المنتج" maxWidth="max-w-xl">
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">اسم المنتج</label>
              <input
                type="text"
                value={form.name || ''}
                onChange={e => setForm({ ...form, name: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">SKU</label>
              <input
                type="text"
                value={form.sku || ''}
                onChange={e => setForm({ ...form, sku: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">سعر البيع</label>
              <input
                type="number"
                step="0.01"
                value={form.unit_price || ''}
                onChange={e => setForm({ ...form, unit_price: Number(e.target.value) })}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">سعر التكلفة</label>
              <input
                type="number"
                step="0.01"
                value={form.cost_price || ''}
                onChange={e => setForm({ ...form, cost_price: Number(e.target.value) })}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">الكمية</label>
              <input
                type="number"
                value={form.quantity_in_stock || ''}
                onChange={e => setForm({ ...form, quantity_in_stock: Number(e.target.value) })}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">الحد الأدنى</label>
              <input
                type="number"
                value={form.minimum_stock_level || ''}
                onChange={e => setForm({ ...form, minimum_stock_level: Number(e.target.value) })}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">الحد الأقصى</label>
              <input
                type="number"
                value={form.maximum_stock_level || ''}
                onChange={e => setForm({ ...form, maximum_stock_level: Number(e.target.value) })}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">الوحدة</label>
              <select
                value={form.unit || 'piece'}
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
          </div>
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={form.is_active ?? true}
              onChange={e => setForm({ ...form, is_active: e.target.checked })}
              className="rounded"
            />
            <label className="text-sm font-medium">نشط</label>
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <button
              onClick={() => setEditMode(false)}
              className="px-4 py-2 border rounded-lg hover:bg-gray-50"
            >
              إلغاء
            </button>
            <button
              onClick={handleSave}
              disabled={updateMutation.isPending}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {updateMutation.isPending ? 'جاري الحفظ...' : 'حفظ'}
            </button>
          </div>
        </div>
      </Dialog>

      <Dialog isOpen={showDelete} onClose={() => setShowDelete(false)} title="تأكيد الحذف">
        <p className="mb-4">هل أنت متأكد من حذف المنتج "{product.name}"؟</p>
        <div className="flex justify-end gap-2">
          <button
            onClick={() => setShowDelete(false)}
            className="px-4 py-2 border rounded-lg hover:bg-gray-50"
          >
            إلغاء
          </button>
          <button
            onClick={() => deleteMutation.mutate()}
            disabled={deleteMutation.isPending}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
          >
            {deleteMutation.isPending ? 'جاري الحذف...' : 'حذف'}
          </button>
        </div>
      </Dialog>
    </div>
  )
}
