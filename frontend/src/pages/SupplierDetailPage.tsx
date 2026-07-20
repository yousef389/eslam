import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { ArrowRight, Phone, Mail, MapPin, CreditCard, Receipt, Edit, Plus, Truck } from 'lucide-react'
import api from '../lib/api'
import { formatCurrency, formatDate } from '../lib/utils'
import PageHeader from '../components/PageHeader'
import Dialog from '../components/Dialog'
import LoadingSpinner from '../components/LoadingSpinner'


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
  const [activeTab, setActiveTab] = useState<'info' | 'debts' | 'orders'>('info')
  const [showPaymentDialog, setShowPaymentDialog] = useState(false)
  const [selectedDebtId, setSelectedDebtId] = useState<string>('')
  const [paymentForm, setPaymentForm] = useState({ amount: '', payment_method: 'cash', notes: '' })

  const { data: supplier, isLoading } = useQuery({
    queryKey: ['supplier', id],
    queryFn: () => api.get(`/suppliers/${id}`).then(res => res.data.data),
    enabled: !!id,
  })

  const { data: statement, isLoading: statementLoading } = useQuery({
    queryKey: ['supplier-statement', id],
    queryFn: () => api.get(`/suppliers/${id}/statement`, { params: { page: 1, per_page: 100 } }).then(res => res.data.data),
    enabled: !!id,
  })

  const { data: purchaseOrders, isLoading: ordersLoading } = useQuery({
    queryKey: ['supplier-purchase-orders', id],
    queryFn: () => api.get('/purchase-orders', { params: { supplier_id: id, per_page: 100 } }).then(res => res.data.data),
    enabled: !!id && activeTab === 'orders',
  })

  const paymentMutation = useMutation({
    mutationFn: (payload: { debt_id: string; amount: number; payment_method: string; notes?: string }) =>
      api.post('/accounting/suppliers/payments', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['supplier-statement', id] })
      queryClient.invalidateQueries({ queryKey: ['supplier', id] })
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
  if (!supplier) return <div className="text-center py-8 text-gray-500">المورد غير موجود</div>

  const debts = statement?.debts || []
  const unpaidDebts = debts.filter((d: Debt) => d.status !== 'paid')

  const totalRemaining = debts.reduce((sum: number, d: Debt) => sum + d.remaining, 0)
  const totalPaid = debts.reduce((sum: number, d: Debt) => sum + d.paid_amount, 0)
  const totalDebts = debts.reduce((sum: number, d: Debt) => sum + d.amount, 0)

  const tabs = [
    { key: 'info', label: 'البيانات' },
    { key: 'debts', label: 'المديونيات' },
    { key: 'orders', label: 'فواتير الشراء' },
  ]

  return (
    <div>
      <PageHeader
        title={supplier.name}
        subtitle={supplier.phone}
        action={
          <div className="flex gap-2">
            <button
              onClick={() => navigate('/suppliers')}
              className="flex items-center gap-2 border px-4 py-2 rounded-lg hover:bg-gray-50"
            >
              <ArrowRight size={18} />
              رجوع
            </button>
            <button
              onClick={() => navigate(`/suppliers/${id}/edit`)}
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
              سداد دفعة
            </button>
          </div>
        }
      />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-white p-5 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-500">إجمالي المستحقات</span>
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
        <div className="bg-white p-5 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-500">عدد الفواتير</span>
            <div className="p-2 bg-blue-100 rounded-lg">
              <Truck size={18} className="text-blue-600" />
            </div>
          </div>
          <p className="text-2xl font-bold text-blue-600">{debts.length}</p>
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
                      <p className="font-medium">{supplier.name}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-gray-100 rounded-lg"><Phone size={16} className="text-gray-600" /></div>
                    <div>
                      <p className="text-xs text-gray-500">الهاتف</p>
                      <p className="font-medium">{supplier.phone}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-gray-100 rounded-lg"><Mail size={16} className="text-gray-600" /></div>
                    <div>
                      <p className="text-xs text-gray-500">البريد الإلكتروني</p>
                      <p className="font-medium">{supplier.email || '-'}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-gray-100 rounded-lg"><MapPin size={16} className="text-gray-600" /></div>
                    <div>
                      <p className="text-xs text-gray-500">العنوان</p>
                      <p className="font-medium">{supplier.address || '-'}</p>
                    </div>
                  </div>
                </div>
              </div>
              <div className="space-y-4">
                <h3 className="text-lg font-semibold border-b pb-2">معلومات مالية وإدارية</h3>
                <div className="space-y-3">
                  <div className="flex justify-between py-2 border-b">
                    <span className="text-gray-500">الرقم الضريبي</span>
                    <span className="font-medium">{supplier.tax_number || '-'}</span>
                  </div>
                  <div className="flex justify-between py-2 border-b">
                    <span className="text-gray-500">أيام شروط الدفع</span>
                    <span className="font-medium">{supplier.payment_terms_days} يوم</span>
                  </div>
                  <div className="flex justify-between py-2 border-b">
                    <span className="text-gray-500">الحالة</span>
                    <span className={`font-medium ${supplier.is_active ? 'text-green-600' : 'text-gray-500'}`}>
                      {supplier.is_active ? 'نشط' : 'غير نشط'}
                    </span>
                  </div>
                  <div className="flex justify-between py-2 border-b">
                    <span className="text-gray-500">تاريخ الإنشاء</span>
                    <span className="font-medium">{formatDate(supplier.created_at)}</span>
                  </div>
                  {supplier.notes && (
                    <div className="py-2">
                      <p className="text-gray-500 text-sm mb-1">ملاحظات</p>
                      <p className="font-medium">{supplier.notes}</p>
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
                                سداد
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

          {activeTab === 'orders' && (
            <div>
              {ordersLoading ? (
                <LoadingSpinner />
              ) : !purchaseOrders || purchaseOrders.length === 0 ? (
                <div className="text-center py-8 text-gray-500">لا توجد فواتير شراء</div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b bg-gray-50">
                        <th className="text-right py-3 px-4 font-medium text-gray-600">رقم الطلب</th>
                        <th className="text-right py-3 px-4 font-medium text-gray-600">التاريخ</th>
                        <th className="text-right py-3 px-4 font-medium text-gray-600">المبلغ</th>
                        <th className="text-right py-3 px-4 font-medium text-gray-600">الحالة</th>
                      </tr>
                    </thead>
                    <tbody>
                      {purchaseOrders.map((order: Record<string, unknown>) => (
                        <tr key={order.id as string} className="border-b hover:bg-gray-50">
                          <td className="py-3 px-4 font-medium">{order.order_number as string || order.id as string}</td>
                          <td className="py-3 px-4 text-gray-500">{formatDate(order.created_at as string)}</td>
                          <td className="py-3 px-4 font-medium">{formatCurrency(order.total_amount as number)}</td>
                          <td className="py-3 px-4">
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                              order.status === 'received' ? 'bg-green-100 text-green-700' :
                              order.status === 'pending' ? 'bg-yellow-100 text-yellow-700' :
                              'bg-gray-100 text-gray-700'
                            }`}>
                              {order.status === 'received' ? 'تم الاستلام' :
                               order.status === 'pending' ? 'قيد الانتظار' :
                               order.status as string}
                            </span>
                          </td>
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

      <Dialog isOpen={showPaymentDialog} onClose={() => setShowPaymentDialog(false)} title="سداد دفعة" maxWidth="max-w-lg">
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
