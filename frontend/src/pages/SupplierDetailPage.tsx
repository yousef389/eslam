import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ArrowRight, Edit, Trash2, Plus, CreditCard } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../lib/api'
import { formatCurrency, formatDate } from '../lib/utils'
import PageHeader from '../components/PageHeader'
import LoadingSpinner from '../components/LoadingSpinner'
import DataTable from '../components/DataTable'
import Dialog from '../components/Dialog'

interface Supplier {
  id: string
  name: string
  phone: string
  email?: string
  address?: string
  tax_number?: string
  payment_terms_days: number
  is_active: boolean
  notes?: string
  created_at: string
  updated_at: string
}

interface Debt {
  id: string
  amount: number
  paid_amount: number
  remaining: number
  status: string
  description: string
  due_date?: string
  created_at: string
}

const statusColors: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-700',
  partial: 'bg-blue-100 text-blue-700',
  paid: 'bg-green-100 text-green-700',
  overdue: 'bg-red-100 text-red-700',
}

const statusLabels: Record<string, string> = {
  pending: 'معلق',
  partial: 'جزئي',
  paid: 'مدفوع',
  overdue: 'متأخر',
}

export default function SupplierDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [editMode, setEditMode] = useState(false)
  const [showDelete, setShowDelete] = useState(false)
  const [showDebt, setShowDebt] = useState(false)
  const [showPayment, setShowPayment] = useState(false)
  const [form, setForm] = useState<Partial<Supplier>>({})
  const [debtForm, setDebtForm] = useState({ amount: '', description: '', due_date: '' })
  const [paymentForm, setPaymentForm] = useState({ debt_id: '', amount: '', payment_method: 'cash', notes: '' })

  const { data: supplierData, isLoading } = useQuery({
    queryKey: ['supplier', id],
    queryFn: () => api.get(`/suppliers/${id}`).then(res => res.data.data),
    enabled: !!id,
  })

  const { data: debtsData } = useQuery({
    queryKey: ['supplier-debts', id],
    queryFn: () => api.get('/accounting/suppliers', { params: { per_page: 100 } }).then(res => res.data.data),
    enabled: !!id,
  })

  const updateMutation = useMutation({
    mutationFn: (payload: Record<string, unknown>) => api.put(`/suppliers/${id}`, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['supplier', id] })
      toast.success('تم تحديث المورد بنجاح')
      setEditMode(false)
    },
    onError: () => toast.error('حدث خطأ أثناء تحديث المورد'),
  })

  const deleteMutation = useMutation({
    mutationFn: () => api.delete(`/suppliers/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['suppliers'] })
      toast.success('تم حذف المورد بنجاح')
      navigate('/suppliers')
    },
    onError: () => toast.error('حدث خطأ أثناء حذف المورد'),
  })

  const createDebtMutation = useMutation({
    mutationFn: (payload: Record<string, unknown>) => api.post('/accounting/suppliers', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['supplier-statement', id] })
      queryClient.invalidateQueries({ queryKey: ['supplier', id] })
      toast.success('تم إنشاء الدين بنجاح')
      setShowDebt(false)
      setDebtForm({ amount: '', description: '', due_date: '' })
    },
    onError: () => toast.error('حدث خطأ أثناء إنشاء الدين'),
  })

  const createPaymentMutation = useMutation({
    mutationFn: (payload: Record<string, unknown>) => api.post('/accounting/suppliers/payments', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['supplier-statement', id] })
      queryClient.invalidateQueries({ queryKey: ['supplier', id] })
      toast.success('تم تسجيل الدفعة بنجاح')
      setShowPayment(false)
      setPaymentForm({ debt_id: '', amount: '', payment_method: 'cash', notes: '' })
    },
    onError: () => toast.error('حدث خطأ أثناء تسجيل الدفعة'),
  })

  if (isLoading) return <LoadingSpinner />
  if (!supplierData) return <div className="text-center py-8 text-gray-500">المورد غير موجود</div>

  const supplier: Supplier = supplierData
  const debts = (debtsData || []).filter((d: Debt & { supplier_id?: string }) => d.supplier_id === id)

  const handleSave = () => {
    updateMutation.mutate(form as Record<string, unknown>)
  }

  const startEdit = () => {
    setForm({
      name: supplier.name,
      phone: supplier.phone,
      email: supplier.email,
      address: supplier.address,
      tax_number: supplier.tax_number,
      payment_terms_days: supplier.payment_terms_days,
      notes: supplier.notes,
    })
    setEditMode(true)
  }

  const handleCreateDebt = (e: React.FormEvent) => {
    e.preventDefault()
    createDebtMutation.mutate({
      supplier_id: id,
      amount: Number(debtForm.amount),
      description: debtForm.description,
      due_date: debtForm.due_date || undefined,
    })
  }

  const handleCreatePayment = (e: React.FormEvent) => {
    e.preventDefault()
    createPaymentMutation.mutate({
      debt_id: paymentForm.debt_id,
      amount: Number(paymentForm.amount),
      payment_method: paymentForm.payment_method,
      notes: paymentForm.notes || undefined,
    })
  }

  const debtColumns = [
    { key: 'description', header: 'الوصف', render: (item: Debt) => item.description },
    { key: 'amount', header: 'المبلغ', render: (item: Debt) => formatCurrency(item.amount) },
    { key: 'paid_amount', header: 'المدفوع', render: (item: Debt) => formatCurrency(item.paid_amount) },
    { key: 'remaining', header: 'المتبقي', render: (item: Debt) => formatCurrency(item.remaining) },
    {
      key: 'status', header: 'الحالة', render: (item: Debt) => (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[item.status] || ''}`}>
          {statusLabels[item.status] || item.status}
        </span>
      ),
    },
    { key: 'due_date', header: 'تاريخ الاستحقاق', render: (item: Debt) => item.due_date ? formatDate(item.due_date) : '-' },
  ]

  return (
    <div>
      <PageHeader
        title={supplier.name}
        subtitle={supplier.phone}
        action={
          <div className="flex gap-2">
            <button onClick={() => navigate('/suppliers')} className="flex items-center gap-2 border px-4 py-2 rounded-lg hover:bg-gray-50">
              <ArrowRight size={18} />رجوع
            </button>
            <button onClick={() => setShowDebt(true)} className="flex items-center gap-2 bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700">
              <Plus size={18} />دين جديد
            </button>
            <button onClick={() => setShowPayment(true)} className="flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700">
              <CreditCard size={18} />تسجيل دفعة
            </button>
            <button onClick={startEdit} className="flex items-center gap-2 border px-4 py-2 rounded-lg hover:bg-gray-50">
              <Edit size={18} />تعديل
            </button>
            <button onClick={() => setShowDelete(true)} className="flex items-center gap-2 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700">
              <Trash2 size={18} />حذف
            </button>
          </div>
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border space-y-3">
          <h3 className="text-lg font-semibold">معلومات المورد</h3>
          <div className="space-y-2">
            <div><span className="text-sm text-gray-500">الاسم:</span><p className="font-medium">{supplier.name}</p></div>
            <div><span className="text-sm text-gray-500">الهاتف:</span><p className="font-medium">{supplier.phone}</p></div>
            <div><span className="text-sm text-gray-500">البريد:</span><p className="font-medium">{supplier.email || '-'}</p></div>
            <div><span className="text-sm text-gray-500">العنوان:</span><p className="font-medium">{supplier.address || '-'}</p></div>
            <div><span className="text-sm text-gray-500">الرقم الضريبي:</span><p className="font-medium">{supplier.tax_number || '-'}</p></div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border space-y-3">
          <h3 className="text-lg font-semibold">الشروط</h3>
          <div className="space-y-2">
            <div><span className="text-sm text-gray-500">أيام الدفع:</span><p className="font-medium">{supplier.payment_terms_days} يوم</p></div>
            <div><span className="text-sm text-gray-500">الحالة:</span>
              <p className={`font-medium ${supplier.is_active ? 'text-green-600' : 'text-gray-500'}`}>{supplier.is_active ? 'نشط' : 'غير نشط'}</p>
            </div>
            <div><span className="text-sm text-gray-500">تاريخ الإنشاء:</span><p className="font-medium">{formatDate(supplier.created_at)}</p></div>
            {supplier.notes && <div><span className="text-sm text-gray-500">ملاحظات:</span><p className="font-medium">{supplier.notes}</p></div>}
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border space-y-3">
          <h3 className="text-lg font-semibold">ملخص الديون</h3>
          <div className="space-y-2">
            <div><span className="text-sm text-gray-500">إجمالي الديون:</span>
              <p className="font-semibold text-lg text-orange-600">
                {formatCurrency(debts.reduce((sum: number, d: Debt) => sum + d.remaining, 0))}
              </p>
            </div>
            <div><span className="text-sm text-gray-500">عدد الديون:</span><p className="font-medium">{debts.length}</p></div>
            <div><span className="text-sm text-gray-500">ديون معلقة:</span>
              <p className="font-medium text-yellow-600">{debts.filter((d: Debt) => d.status === 'pending').length}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold mb-4">كشف الحساب</h3>
        <DataTable columns={debtColumns} data={debts as unknown as Record<string, unknown>[]} emptyMessage="لا توجد ديون" />
      </div>

      <Dialog isOpen={editMode} onClose={() => setEditMode(false)} title="تعديل المورد" maxWidth="max-w-xl">
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div><label className="block text-sm font-medium mb-1">الاسم</label><input type="text" value={form.name || ''} onChange={e => setForm({ ...form, name: e.target.value })} className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" /></div>
            <div><label className="block text-sm font-medium mb-1">الهاتف</label><input type="text" value={form.phone || ''} onChange={e => setForm({ ...form, phone: e.target.value })} className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" /></div>
            <div><label className="block text-sm font-medium mb-1">البريد</label><input type="email" value={form.email || ''} onChange={e => setForm({ ...form, email: e.target.value })} className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" /></div>
            <div><label className="block text-sm font-medium mb-1">أيام الدفع</label><input type="number" value={form.payment_terms_days || ''} onChange={e => setForm({ ...form, payment_terms_days: Number(e.target.value) })} className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" /></div>
          </div>
          <div className="flex items-center gap-2">
            <input type="checkbox" checked={form.is_active ?? true} onChange={e => setForm({ ...form, is_active: e.target.checked })} className="rounded" />
            <label className="text-sm font-medium">نشط</label>
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <button onClick={() => setEditMode(false)} className="px-4 py-2 border rounded-lg hover:bg-gray-50">إلغاء</button>
            <button onClick={handleSave} disabled={updateMutation.isPending} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50">
              {updateMutation.isPending ? 'جاري الحفظ...' : 'حفظ'}
            </button>
          </div>
        </div>
      </Dialog>

      <Dialog isOpen={showDelete} onClose={() => setShowDelete(false)} title="تأكيد الحذف">
        <p className="mb-4">هل أنت متأكد من حذف المورد "{supplier.name}"؟</p>
        <div className="flex justify-end gap-2">
          <button onClick={() => setShowDelete(false)} className="px-4 py-2 border rounded-lg hover:bg-gray-50">إلغاء</button>
          <button onClick={() => deleteMutation.mutate()} disabled={deleteMutation.isPending} className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50">
            {deleteMutation.isPending ? 'جاري الحذف...' : 'حذف'}
          </button>
        </div>
      </Dialog>

      <Dialog isOpen={showDebt} onClose={() => setShowDebt(false)} title="إضافة دين جديد">
        <form onSubmit={handleCreateDebt} className="space-y-4">
          <div><label className="block text-sm font-medium mb-1">المبلغ *</label><input type="number" step="0.01" value={debtForm.amount} onChange={e => setDebtForm({ ...debtForm, amount: e.target.value })} className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" required /></div>
          <div><label className="block text-sm font-medium mb-1">الوصف *</label><input type="text" value={debtForm.description} onChange={e => setDebtForm({ ...debtForm, description: e.target.value })} className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" required /></div>
          <div><label className="block text-sm font-medium mb-1">تاريخ الاستحقاق</label><input type="date" value={debtForm.due_date} onChange={e => setDebtForm({ ...debtForm, due_date: e.target.value })} className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" /></div>
          <div className="flex justify-end gap-2 pt-2">
            <button type="button" onClick={() => setShowDebt(false)} className="px-4 py-2 border rounded-lg hover:bg-gray-50">إلغاء</button>
            <button type="submit" disabled={createDebtMutation.isPending} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50">
              {createDebtMutation.isPending ? 'جاري الحفظ...' : 'حفظ'}
            </button>
          </div>
        </form>
      </Dialog>

      <Dialog isOpen={showPayment} onClose={() => setShowPayment(false)} title="تسجيل دفعة">
        <form onSubmit={handleCreatePayment} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">الدين *</label>
            <select value={paymentForm.debt_id} onChange={e => setPaymentForm({ ...paymentForm, debt_id: e.target.value })} className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" required>
              <option value="">اختر الدين</option>
              {debts.filter((d: Debt) => d.status !== 'paid').map((d: Debt) => (
                <option key={d.id} value={d.id}>{d.description} - متبقي {formatCurrency(d.remaining)}</option>
              ))}
            </select>
          </div>
          <div><label className="block text-sm font-medium mb-1">المبلغ *</label><input type="number" step="0.01" value={paymentForm.amount} onChange={e => setPaymentForm({ ...paymentForm, amount: e.target.value })} className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" required /></div>
          <div>
            <label className="block text-sm font-medium mb-1">طريقة الدفع</label>
            <select value={paymentForm.payment_method} onChange={e => setPaymentForm({ ...paymentForm, payment_method: e.target.value })} className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="cash">نقدي</option>
              <option value="bank_transfer">تحويل بنكي</option>
              <option value="credit_card">بطاقة ائتمان</option>
              <option value="cheque">شيك</option>
            </select>
          </div>
          <div><label className="block text-sm font-medium mb-1">ملاحظات</label><input type="text" value={paymentForm.notes} onChange={e => setPaymentForm({ ...paymentForm, notes: e.target.value })} className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" /></div>
          <div className="flex justify-end gap-2 pt-2">
            <button type="button" onClick={() => setShowPayment(false)} className="px-4 py-2 border rounded-lg hover:bg-gray-50">إلغاء</button>
            <button type="submit" disabled={createPaymentMutation.isPending} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50">
              {createPaymentMutation.isPending ? 'جاري الحفظ...' : 'حفظ'}
            </button>
          </div>
        </form>
      </Dialog>
    </div>
  )
}
