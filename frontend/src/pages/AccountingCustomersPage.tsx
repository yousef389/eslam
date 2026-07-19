import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, CreditCard } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../lib/api'
import { formatCurrency, formatDate } from '../lib/utils'
import PageHeader from '../components/PageHeader'
import DataTable from '../components/DataTable'
import Dialog from '../components/Dialog'
import StatsCard from '../components/StatsCard'
import { DollarSign } from 'lucide-react'

interface Debt {
  id: string
  customer_id?: string
  amount: number
  paid_amount: number
  remaining: number
  status: string
  description: string
  due_date?: string
  created_at: string
}

interface Customer {
  id: string
  name: string
}

interface PaginatedResponse {
  data: Debt[]
  meta: { total: number; page: number; per_page: number }
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

export default function AccountingCustomersPage() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [statusFilter, setStatusFilter] = useState('')
  const [showDebt, setShowDebt] = useState(false)
  const [showPayment, setShowPayment] = useState(false)
  const [debtForm, setDebtForm] = useState({ customer_id: '', amount: '', description: '', due_date: '' })
  const [paymentForm, setPaymentForm] = useState({ debt_id: '', amount: '', payment_method: 'cash', notes: '' })

  const { data, isLoading } = useQuery<PaginatedResponse>({
    queryKey: ['customer-debts', page, statusFilter],
    queryFn: () => {
      const params: Record<string, unknown> = { page, per_page: 20 }
      if (statusFilter) params.status = statusFilter
      return api.get('/accounting/customers', { params }).then(res => res.data)
    },
  })

  const { data: customersData } = useQuery({
    queryKey: ['customers-list'],
    queryFn: () => api.get('/customers', { params: { per_page: 100 } }).then(res => res.data.data),
  })

  const createDebtMutation = useMutation({
    mutationFn: (payload: Record<string, unknown>) => api.post('/accounting/customers', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['customer-debts'] })
      toast.success('تم إنشاء الدين بنجاح')
      setShowDebt(false)
      setDebtForm({ customer_id: '', amount: '', description: '', due_date: '' })
    },
    onError: () => toast.error('حدث خطأ أثناء إنشاء الدين'),
  })

  const createPaymentMutation = useMutation({
    mutationFn: (payload: Record<string, unknown>) => api.post('/accounting/customers/payments', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['customer-debts'] })
      toast.success('تم تسجيل الدفعة بنجاح')
      setShowPayment(false)
      setPaymentForm({ debt_id: '', amount: '', payment_method: 'cash', notes: '' })
    },
    onError: () => toast.error('حدث خطأ أثناء تسجيل الدفعة'),
  })

  const debts = data?.data || []
  const meta = data?.meta
  const customers = customersData || []

  const totalReceivable = debts
    .filter((d: Debt) => d.status !== 'paid')
    .reduce((sum: number, d: Debt) => sum + d.remaining, 0)

  const handleCreateDebt = (e: React.FormEvent) => {
    e.preventDefault()
    createDebtMutation.mutate({
      customer_id: debtForm.customer_id,
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

  const columns = [
    {
      key: 'customer_id',
      header: 'العميل',
      render: (item: Debt) => customers.find((c: Customer) => c.id === item.customer_id)?.name || '-',
    },
    { key: 'description', header: 'الوصف', render: (item: Debt) => item.description },
    { key: 'amount', header: 'المبلغ', render: (item: Debt) => formatCurrency(item.amount) },
    { key: 'paid_amount', header: 'المدفوع', render: (item: Debt) => formatCurrency(item.paid_amount) },
    {
      key: 'remaining',
      header: 'المتبقي',
      render: (item: Debt) => <span className="font-semibold">{formatCurrency(item.remaining)}</span>,
    },
    {
      key: 'status',
      header: 'الحالة',
      render: (item: Debt) => (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[item.status] || ''}`}>
          {statusLabels[item.status] || item.status}
        </span>
      ),
    },
    {
      key: 'due_date',
      header: 'تاريخ الاستحقاق',
      render: (item: Debt) => item.due_date ? formatDate(item.due_date) : '-',
    },
  ]

  return (
    <div>
      <PageHeader
        title="حسابات العملاء"
        subtitle="إدارة الحسابات المدينة للعملاء"
        action={
          <div className="flex gap-2">
            <button onClick={() => setShowDebt(true)} className="flex items-center gap-2 bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700">
              <Plus size={18} />دين جديد
            </button>
            <button onClick={() => setShowPayment(true)} className="flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700">
              <CreditCard size={18} />تسجيل دفعة
            </button>
          </div>
        }
      />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <StatsCard title="إجمالي المبالغ المستحقة" value={totalReceivable} icon={DollarSign} color="green" isCurrency />
        <StatsCard title="ديون معلقة" value={debts.filter((d: Debt) => d.status === 'pending').length} icon={DollarSign} color="orange" />
        <StatsCard title="ديون متأخرة" value={debts.filter((d: Debt) => d.status === 'overdue').length} icon={DollarSign} color="red" />
      </div>

      <div className="flex gap-4 mb-4">
        <select value={statusFilter} onChange={e => { setStatusFilter(e.target.value); setPage(1) }} className="px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
          <option value="">جميع الحالات</option>
          <option value="pending">معلق</option>
          <option value="partial">جزئي</option>
          <option value="paid">مدفوع</option>
          <option value="overdue">متأخر</option>
        </select>
      </div>

      <DataTable columns={columns} data={debts as unknown as Record<string, unknown>[]} isLoading={isLoading} emptyMessage="لا توجد ديون" />

      {meta && meta.total > 20 && (
        <div className="flex justify-center gap-2 mt-4">
          <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1} className="px-3 py-1 border rounded-lg disabled:opacity-50 hover:bg-gray-50">السابق</button>
          <span className="px-3 py-1">صفحة {page} من {Math.ceil(meta.total / 20)}</span>
          <button onClick={() => setPage(p => p + 1)} disabled={page >= Math.ceil(meta.total / 20)} className="px-3 py-1 border rounded-lg disabled:opacity-50 hover:bg-gray-50">التالي</button>
        </div>
      )}

      <Dialog isOpen={showDebt} onClose={() => setShowDebt(false)} title="إضافة دين جديد">
        <form onSubmit={handleCreateDebt} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">العميل *</label>
            <select value={debtForm.customer_id} onChange={e => setDebtForm({ ...debtForm, customer_id: e.target.value })} className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" required>
              <option value="">اختر العميل</option>
              {customers.map((c: Customer) => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </div>
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
              {debts.filter((d: Debt) => d.status !== 'paid').map((d: Debt) => {
                const custName = customers.find((c: Customer) => c.id === d.customer_id)?.name || ''
                return <option key={d.id} value={d.id}>{custName} - {d.description} - متبقي {formatCurrency(d.remaining)}</option>
              })}
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
