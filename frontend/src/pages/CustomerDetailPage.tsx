import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { ArrowRight, Phone, Mail, MapPin, CreditCard, Receipt, Edit, Plus } from 'lucide-react'
import api from '../lib/api'
import { formatCurrency, formatDate } from '../lib/utils'
import PageHeader from '../components/PageHeader'
import Dialog from '../components/Dialog'
import LoadingSpinner from '../components/LoadingSpinner'


interface Debt {
  id: string
  customer_id: string
  amount: number
  paid_amount: number
  remaining: number
  status: string
  description: string
  due_date?: string
  created_at: string
}

interface Payment {
  id: string
  debt_id: string
  amount: number
  payment_method: string
  notes?: string
  created_at: string
}

// statement response types inferred from API

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

const paymentMethodLabels: Record<string, string> = {
  cash: 'نقدي',
  bank_transfer: 'تحويل بنكي',
  credit_card: 'بطاقة ائتمان',
  cheque: 'شيك',
}

export default function CustomerDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<'info' | 'debts' | 'payments'>('info')
  const [showPaymentDialog, setShowPaymentDialog] = useState(false)
  const [selectedDebtId, setSelectedDebtId] = useState<string>('')
  const [paymentForm, setPaymentForm] = useState({ amount: '', payment_method: 'cash', notes: '' })

  const { data: customer, isLoading } = useQuery({
    queryKey: ['customer', id],
    queryFn: () => api.get(`/customers/${id}`).then(res => res.data.data),
    enabled: !!id,
  })

  const { data: statement, isLoading: statementLoading } = useQuery({
    queryKey: ['customer-statement', id],
    queryFn: () => api.get(`/customers/${id}/statement`, { params: { page: 1, per_page: 100 } }).then(res => res.data.data),
    enabled: !!id,
  })

  const paymentMutation = useMutation({
    mutationFn: (payload: { debt_id: string; amount: number; payment_method: string; notes?: string }) =>
      api.post('/accounting/customers/payments', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['customer-statement', id] })
      queryClient.invalidateQueries({ queryKey: ['customer', id] })
      toast.success('تم تسجيل الدفعة بنجاح')
      setShowPaymentDialog(false)
      setPaymentForm({ amount: '', payment_method: 'cash', notes: '' })
      setSelectedDebtId('')
    },
    onError: () => toast.error('حدث خطأ أثناء تسجيل الدفعة'),
  })

  const handleOpenPaymentDialog = (debtId?: string) => {
    if (debtId) {
      setSelectedDebtId(debtId)
      const debt = statement?.debts?.find((d: Debt) => d.id === debtId)
      if (debt) {
        setPaymentForm({ ...paymentForm, amount: String(debt.remaining) })
      }
    } else {
      setSelectedDebtId('')
      setPaymentForm({ amount: '', payment_method: 'cash', notes: '' })
    }
    setShowPaymentDialog(true)
  }

  const handleSubmitPayment = (e: React.FormEvent) => {
    e.preventDefault()
    paymentMutation.mutate({
      debt_id: selectedDebtId,
      amount: Number(paymentForm.amount),
      payment_method: paymentForm.payment_method,
      notes: paymentForm.notes || undefined,
    })
  }

  if (isLoading) return <LoadingSpinner />
  if (!customer) return <div className="text-center py-8 text-gray-500">العميل غير موجود</div>

  const debts = statement?.debts || []
  const payments = statement?.payments || []
  const unpaidDebts = debts.filter((d: Debt) => d.status !== 'paid')

  const totalRemaining = debts.reduce((sum: number, d: Debt) => sum + d.remaining, 0)
  const totalPaid = debts.reduce((sum: number, d: Debt) => sum + d.paid_amount, 0)
  const totalDebts = debts.reduce((sum: number, d: Debt) => sum + d.amount, 0)

  const tabs = [
    { key: 'info', label: 'البيانات' },
    { key: 'debts', label: 'المديونيات' },
    { key: 'payments', label: 'سجل المدفوعات' },
  ]

  return (
    <div>
      <PageHeader
        title={customer.name}
        subtitle={customer.phone}
        action={
          <div className="flex gap-2">
            <button
              onClick={() => navigate('/customers')}
              className="flex items-center gap-2 border px-4 py-2 rounded-lg hover:bg-gray-50"
            >
              <ArrowRight size={18} />
              رجوع
            </button>
            <button
              onClick={() => navigate(`/customers/${id}/edit`)}
              className="flex items-center gap-2 border px-4 py-2 rounded-lg hover:bg-gray-50"
            >
              <Edit size={18} />
              تعديل
            </button>
            <button
              onClick={() => handleOpenPaymentDialog()}
              className="flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
            >
              <Plus size={18} />
              تحصيل دفعة
            </button>
          </div>
        }
      />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-white p-5 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-500">الرصيد الحالي</span>
            <div className="p-2 bg-blue-100 rounded-lg">
              <CreditCard size={18} className="text-blue-600" />
            </div>
          </div>
          <p className="text-2xl font-bold text-blue-600">{formatCurrency(customer.current_balance)}</p>
        </div>
        <div className="bg-white p-5 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-500">المبلغ المستحق</span>
            <div className="p-2 bg-red-100 rounded-lg">
              <Receipt size={18} className="text-red-600" />
            </div>
          </div>
          <p className="text-2xl font-bold text-red-600">{formatCurrency(totalDebts)}</p>
        </div>
        <div className="bg-white p-5 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-500">المدفوع</span>
            <div className="p-2 bg-green-100 rounded-lg">
              <CreditCard size={18} className="text-green-600" />
            </div>
          </div>
          <p className="text-2xl font-bold text-green-600">{formatCurrency(totalPaid)}</p>
        </div>
        <div className="bg-white p-5 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-500">المتبقي</span>
            <div className="p-2 bg-orange-100 rounded-lg">
              <Receipt size={18} className="text-orange-600" />
            </div>
          </div>
          <p className="text-2xl font-bold text-orange-600">{formatCurrency(totalRemaining)}</p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border">
        <div className="flex border-b">
          {tabs.map(tab => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as typeof activeTab)}
              className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.key
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div className="p-6">
          {activeTab === 'info' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <h3 className="text-lg font-semibold border-b pb-2">المعلومات الأساسية</h3>
                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-gray-100 rounded-lg"><CreditCard size={16} className="text-gray-600" /></div>
                    <div>
                      <p className="text-xs text-gray-500">الاسم</p>
                      <p className="font-medium">{customer.name}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-gray-100 rounded-lg"><Phone size={16} className="text-gray-600" /></div>
                    <div>
                      <p className="text-xs text-gray-500">الهاتف</p>
                      <p className="font-medium">{customer.phone}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-gray-100 rounded-lg"><Mail size={16} className="text-gray-600" /></div>
                    <div>
                      <p className="text-xs text-gray-500">البريد الإلكتروني</p>
                      <p className="font-medium">{customer.email || '-'}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-gray-100 rounded-lg"><MapPin size={16} className="text-gray-600" /></div>
                    <div>
                      <p className="text-xs text-gray-500">العنوان</p>
                      <p className="font-medium">{customer.address || '-'}</p>
                    </div>
                  </div>
                </div>
              </div>
              <div className="space-y-4">
                <h3 className="text-lg font-semibold border-b pb-2">معلومات مالية</h3>
                <div className="space-y-3">
                  <div className="flex justify-between py-2 border-b">
                    <span className="text-gray-500">الرقم الضريبي</span>
                    <span className="font-medium">{customer.tax_number || '-'}</span>
                  </div>
                  <div className="flex justify-between py-2 border-b">
                    <span className="text-gray-500">حد الائتمان</span>
                    <span className="font-medium">{formatCurrency(customer.credit_limit)}</span>
                  </div>
                  <div className="flex justify-between py-2 border-b">
                    <span className="text-gray-500">الحالة</span>
                    <span className={`font-medium ${customer.is_active ? 'text-green-600' : 'text-gray-500'}`}>
                      {customer.is_active ? 'نشط' : 'غير نشط'}
                    </span>
                  </div>
                  <div className="flex justify-between py-2 border-b">
                    <span className="text-gray-500">تاريخ الإنشاء</span>
                    <span className="font-medium">{formatDate(customer.created_at)}</span>
                  </div>
                  {customer.notes && (
                    <div className="py-2">
                      <p className="text-gray-500 text-sm mb-1">ملاحظات</p>
                      <p className="font-medium">{customer.notes}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'debts' && (
            <div>
              {statementLoading ? (
                <LoadingSpinner />
              ) : debts.length === 0 ? (
                <div className="text-center py-8 text-gray-500">لا توجد مديونيات</div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b bg-gray-50">
                        <th className="text-right py-3 px-4 font-medium text-gray-600">الوصف</th>
                        <th className="text-right py-3 px-4 font-medium text-gray-600">المبلغ</th>
                        <th className="text-right py-3 px-4 font-medium text-gray-600">المدفوع</th>
                        <th className="text-right py-3 px-4 font-medium text-gray-600">المتبقي</th>
                        <th className="text-right py-3 px-4 font-medium text-gray-600">الحالة</th>
                        <th className="text-right py-3 px-4 font-medium text-gray-600">تاريخ الاستحقاق</th>
                        <th className="text-right py-3 px-4 font-medium text-gray-600">إجراءات</th>
                      </tr>
                    </thead>
                    <tbody>
                      {debts.map((debt: Debt) => (
                        <tr key={debt.id} className="border-b hover:bg-gray-50">
                          <td className="py-3 px-4">{debt.description}</td>
                          <td className="py-3 px-4 font-medium">{formatCurrency(debt.amount)}</td>
                          <td className="py-3 px-4 text-green-600">{formatCurrency(debt.paid_amount)}</td>
                          <td className="py-3 px-4 text-red-600 font-medium">{formatCurrency(debt.remaining)}</td>
                          <td className="py-3 px-4">
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[debt.status] || ''}`}>
                              {statusLabels[debt.status] || debt.status}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-gray-500">{debt.due_date ? formatDate(debt.due_date) : '-'}</td>
                          <td className="py-3 px-4">
                            {debt.status !== 'paid' && (
                              <button
                                onClick={() => handleOpenPaymentDialog(debt.id)}
                                className="text-green-600 hover:text-green-700 text-sm font-medium"
                              >
                                تحصيل
                              </button>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {activeTab === 'payments' && (
            <div>
              {statementLoading ? (
                <LoadingSpinner />
              ) : payments.length === 0 ? (
                <div className="text-center py-8 text-gray-500">لا توجد مدفوعات</div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b bg-gray-50">
                        <th className="text-right py-3 px-4 font-medium text-gray-600">المبلغ</th>
                        <th className="text-right py-3 px-4 font-medium text-gray-600">طريقة الدفع</th>
                        <th className="text-right py-3 px-4 font-medium text-gray-600">التاريخ</th>
                        <th className="text-right py-3 px-4 font-medium text-gray-600">ملاحظات</th>
                      </tr>
                    </thead>
                    <tbody>
                      {payments.map((payment: Payment) => (
                        <tr key={payment.id} className="border-b hover:bg-gray-50">
                          <td className="py-3 px-4 font-medium text-green-600">{formatCurrency(payment.amount)}</td>
                          <td className="py-3 px-4">{paymentMethodLabels[payment.payment_method] || payment.payment_method}</td>
                          <td className="py-3 px-4 text-gray-500">{formatDate(payment.created_at)}</td>
                          <td className="py-3 px-4 text-gray-500">{payment.notes || '-'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      <Dialog isOpen={showPaymentDialog} onClose={() => setShowPaymentDialog(false)} title="تحصيل دفعة" maxWidth="max-w-lg">
        <form onSubmit={handleSubmitPayment} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">الدين *</label>
            <select
              value={selectedDebtId}
              onChange={e => {
                setSelectedDebtId(e.target.value)
                const debt = unpaidDebts.find((d: Debt) => d.id === e.target.value)
                if (debt) setPaymentForm({ ...paymentForm, amount: String(debt.remaining) })
              }}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value="">اختر الدين</option>
              {unpaidDebts.map((d: Debt) => (
                <option key={d.id} value={d.id}>
                  {d.description} - متبقي {formatCurrency(d.remaining)}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">المبلغ *</label>
            <input
              type="number"
              step="0.01"
              min="0.01"
              value={paymentForm.amount}
              onChange={e => setPaymentForm({ ...paymentForm, amount: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">طريقة الدفع</label>
            <select
              value={paymentForm.payment_method}
              onChange={e => setPaymentForm({ ...paymentForm, payment_method: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="cash">نقدي</option>
              <option value="bank_transfer">تحويل بنكي</option>
              <option value="credit_card">بطاقة ائتمان</option>
              <option value="cheque">شيك</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">ملاحظات</label>
            <input
              type="text"
              value={paymentForm.notes}
              onChange={e => setPaymentForm({ ...paymentForm, notes: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <button type="button" onClick={() => setShowPaymentDialog(false)} className="px-4 py-2 border rounded-lg hover:bg-gray-50">
              إلغاء
            </button>
            <button
              type="submit"
              disabled={paymentMutation.isPending || !selectedDebtId || !paymentForm.amount}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
            >
              {paymentMutation.isPending ? 'جاري الحفظ...' : 'تسجيل الدفعة'}
            </button>
          </div>
        </form>
      </Dialog>
    </div>
  )
}
