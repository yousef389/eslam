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

interface Customer {
  id: string
  name: string
  phone: string
  email?: string
  address?: string
  tax_number?: string
  credit_limit: number
  current_balance: number
  is_active: boolean
  notes?: string
  created_at: string
  updated_at: string
}

interface PaginatedResponse {
  data: Customer[]
  meta: { total: number; page: number; per_page: number }
}

const emptyForm = {
  name: '',
  phone: '',
  email: '',
  address: '',
  tax_number: '',
  credit_limit: '',
  notes: '',
}

export default function CustomersPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [showCreate, setShowCreate] = useState(false)
  const [form, setForm] = useState(emptyForm)

  const { data, isLoading } = useQuery<PaginatedResponse>({
    queryKey: ['customers', page, search],
    queryFn: () =>
      api
        .get('/customers', { params: { page, per_page: 20, search: search || undefined } })
        .then(res => res.data),
  })

  const createMutation = useMutation({
    mutationFn: (payload: Record<string, unknown>) => api.post('/customers', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['customers'] })
      toast.success('تم إضافة العميل بنجاح')
      setShowCreate(false)
      setForm(emptyForm)
    },
    onError: () => toast.error('حدث خطأ أثناء إضافة العميل'),
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    createMutation.mutate({
      name: form.name,
      phone: form.phone,
      email: form.email || undefined,
      address: form.address || undefined,
      tax_number: form.tax_number || undefined,
      credit_limit: Number(form.credit_limit) || 0,
      notes: form.notes || undefined,
    })
  }

  const customers = data?.data || []
  const meta = data?.meta

  const columns = [
    {
      key: 'name',
      header: 'اسم العميل',
      render: (item: Customer) => (
        <div>
          <div className="font-medium">{item.name}</div>
          <div className="text-xs text-gray-500">{item.phone}</div>
        </div>
      ),
    },
    {
      key: 'email',
      header: 'البريد الإلكتروني',
      render: (item: Customer) => item.email || '-',
    },
    {
      key: 'credit_limit',
      header: 'حد الائتمان',
      render: (item: Customer) => formatCurrency(item.credit_limit),
    },
    {
      key: 'current_balance',
      header: 'الرصيد الحالي',
      render: (item: Customer) => (
        <span className={item.current_balance < 0 ? 'text-red-600 font-semibold' : ''}>
          {formatCurrency(item.current_balance)}
        </span>
      ),
    },
    {
      key: 'is_active',
      header: 'الحالة',
      render: (item: Customer) => (
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
        title="العملاء"
        subtitle="إدارة بيانات العملاء"
        action={
          <button
            onClick={() => setShowCreate(true)}
            className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            <Plus size={18} />
            إضافة عميل
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
            placeholder="بحث بالاسم أو الهاتف..."
            className="w-full pr-10 pl-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      <DataTable
        columns={columns}
        data={customers as unknown as Record<string, unknown>[]}
        isLoading={isLoading}
        onRowClick={item => navigate(`/customers/${(item as unknown as Customer).id}`)}
        emptyMessage="لا يوجد عملاء"
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

      <Dialog isOpen={showCreate} onClose={() => setShowCreate(false)} title="إضافة عميل جديد" maxWidth="max-w-xl">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">اسم العميل *</label>
              <input
                type="text"
                value={form.name}
                onChange={e => setForm({ ...form, name: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">رقم الهاتف *</label>
              <input
                type="text"
                value={form.phone}
                onChange={e => setForm({ ...form, phone: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">البريد الإلكتروني</label>
              <input
                type="email"
                value={form.email}
                onChange={e => setForm({ ...form, email: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">الرقم الضريبي</label>
              <input
                type="text"
                value={form.tax_number}
                onChange={e => setForm({ ...form, tax_number: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">حد الائتمان</label>
              <input
                type="number"
                step="0.01"
                value={form.credit_limit}
                onChange={e => setForm({ ...form, credit_limit: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div className="col-span-2">
              <label className="block text-sm font-medium mb-1">العنوان</label>
              <input
                type="text"
                value={form.address}
                onChange={e => setForm({ ...form, address: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div className="col-span-2">
              <label className="block text-sm font-medium mb-1">ملاحظات</label>
              <textarea
                value={form.notes}
                onChange={e => setForm({ ...form, notes: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={2}
              />
            </div>
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
