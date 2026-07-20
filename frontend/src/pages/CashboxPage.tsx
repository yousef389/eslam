import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, ArrowUpCircle, ArrowDownCircle, ArrowRightLeft } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../lib/api'
import { formatCurrency, formatDate } from '../lib/utils'
import PageHeader from '../components/PageHeader'
import DataTable from '../components/DataTable'
import Dialog from '../components/Dialog'

interface Cashbox {
  id: string
  name: string
  balance: number
  is_active: boolean
  created_at: string
  updated_at: string
}

interface Transaction {
  id: string
  cashbox_id: string
  transaction_type: string
  amount: number
  description: string
  reference_id?: string
  user_id: string
  created_at: string
}

interface CashboxTransfer {
  id: string
  transfer_number: string
  from_cashbox_id: string
  to_cashbox_id: string
  amount: number
  description: string
  user_id: string
  created_at: string
}

interface PaginatedResponse {
  data: Cashbox[] | Transaction[] | CashboxTransfer[]
  meta: { total: number; page: number; per_page: number }
}

const typeConfig: Record<string, { icon: typeof ArrowUpCircle; color: string; label: string }> = {
  income: { icon: ArrowUpCircle, color: 'text-green-600', label: 'دخل' },
  expense: { icon: ArrowDownCircle, color: 'text-red-600', label: 'مصروف' },
  transfer: { icon: ArrowRightLeft, color: 'text-blue-600', label: 'تحويل' },
}

export default function CashboxPage() {
  const queryClient = useQueryClient()
  const [selectedCashbox, setSelectedCashbox] = useState<string>('')
  const [txPage, setTxPage] = useState(1)
  const [showTransaction, setShowTransaction] = useState(false)
  const [txForm, setTxForm] = useState({ amount: '', transaction_type: 'income', description: '' })
  const [activeTab, setActiveTab] = useState<'transactions' | 'transfers'>('transactions')
  const [transferPage, setTransferPage] = useState(1)
  const [showTransfer, setShowTransfer] = useState(false)
  const [transferForm, setTransferForm] = useState({ from_cashbox_id: '', to_cashbox_id: '', amount: '', description: '' })

  const { data: cashboxesData, isLoading: loadingCashboxes } = useQuery<PaginatedResponse>({
    queryKey: ['cashboxes'],
    queryFn: () => api.get('/accounting/cashbox', { params: { per_page: 100 } }).then(res => res.data),
  })

  const { data: txData, isLoading: loadingTx } = useQuery<PaginatedResponse>({
    queryKey: ['cashbox-transactions', selectedCashbox, txPage],
    queryFn: () =>
      api.get(`/accounting/cashbox/${selectedCashbox}/transactions`, { params: { page: txPage, per_page: 20 } }).then(res => res.data),
    enabled: !!selectedCashbox,
  })

  const { data: transfersData, isLoading: loadingTransfers } = useQuery<PaginatedResponse>({
    queryKey: ['cashbox-transfers', transferPage],
    queryFn: () =>
      api.get('/cashbox-transfers/', { params: { page: transferPage, per_page: 20 } }).then(res => res.data),
    enabled: activeTab === 'transfers',
  })

  const createTxMutation = useMutation({
    mutationFn: (payload: Record<string, unknown>) =>
      api.post(`/accounting/cashbox/${selectedCashbox}/transactions`, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cashbox-transactions', selectedCashbox] })
      queryClient.invalidateQueries({ queryKey: ['cashboxes'] })
      toast.success('تم تسجيل المعاملة بنجاح')
      setShowTransaction(false)
      setTxForm({ amount: '', transaction_type: 'income', description: '' })
    },
    onError: () => toast.error('حدث خطأ أثناء تسجيل المعاملة'),
  })

  const createTransferMutation = useMutation({
    mutationFn: (payload: Record<string, unknown>) =>
      api.post('/cashbox-transfers/', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cashbox-transfers'] })
      queryClient.invalidateQueries({ queryKey: ['cashboxes'] })
      toast.success('تم التحويل بنجاح')
      setShowTransfer(false)
      setTransferForm({ from_cashbox_id: '', to_cashbox_id: '', amount: '', description: '' })
    },
    onError: () => toast.error('حدث خطأ أثناء التحويل'),
  })

  const cashboxes = (cashboxesData?.data || []) as Cashbox[]
  const transactions = (txData?.data || []) as Transaction[]
  const txMeta = txData?.meta
  const transfers = (transfersData?.data || []) as CashboxTransfer[]
  const transferMeta = transfersData?.meta

  const selectedBox = cashboxes.find(c => c.id === selectedCashbox)

  const handleCreateTx = (e: React.FormEvent) => {
    e.preventDefault()
    createTxMutation.mutate({
      cashbox_id: selectedCashbox,
      amount: Number(txForm.amount),
      transaction_type: txForm.transaction_type,
      description: txForm.description,
    })
  }

  const handleCreateTransfer = (e: React.FormEvent) => {
    e.preventDefault()
    if (transferForm.from_cashbox_id === transferForm.to_cashbox_id) {
      toast.error('لا يمكن التحويل إلى نفس الصندوق')
      return
    }
    createTransferMutation.mutate({
      from_cashbox_id: transferForm.from_cashbox_id,
      to_cashbox_id: transferForm.to_cashbox_id,
      amount: Number(transferForm.amount),
      description: transferForm.description,
    })
  }

  const txColumns = [
    {
      key: 'transaction_type',
      header: 'النوع',
      render: (item: Transaction) => {
        const config = typeConfig[item.transaction_type] || typeConfig.income
        const Icon = config.icon
        return (
          <div className={`flex items-center gap-2 ${config.color}`}>
            <Icon size={16} />
            <span>{config.label}</span>
          </div>
        )
      },
    },
    {
      key: 'amount',
      header: 'المبلغ',
      render: (item: Transaction) => (
        <span className={`font-semibold ${item.transaction_type === 'income' ? 'text-green-600' : item.transaction_type === 'expense' ? 'text-red-600' : 'text-blue-600'}`}>
          {item.transaction_type === 'expense' ? '-' : '+'}{formatCurrency(item.amount)}
        </span>
      ),
    },
    { key: 'description', header: 'الوصف', render: (item: Transaction) => item.description },
    { key: 'created_at', header: 'التاريخ', render: (item: Transaction) => formatDate(item.created_at) },
  ]

  const transferColumns = [
    {
      key: 'transfer_number',
      header: 'رقم التحويل',
      render: (item: CashboxTransfer) => (
        <span className="font-mono text-sm">{item.transfer_number}</span>
      ),
    },
    {
      key: 'from_cashbox_id',
      header: 'من صندوق',
      render: (item: CashboxTransfer) => {
        const box = cashboxes.find(c => c.id === item.from_cashbox_id)
        return box?.name || item.from_cashbox_id
      },
    },
    {
      key: 'to_cashbox_id',
      header: 'إلى صندوق',
      render: (item: CashboxTransfer) => {
        const box = cashboxes.find(c => c.id === item.to_cashbox_id)
        return box?.name || item.to_cashbox_id
      },
    },
    {
      key: 'amount',
      header: 'المبلغ',
      render: (item: CashboxTransfer) => (
        <span className="font-semibold text-blue-600">{formatCurrency(item.amount)}</span>
      ),
    },
    { key: 'description', header: 'الوصف', render: (item: CashboxTransfer) => item.description },
    { key: 'created_at', header: 'التاريخ', render: (item: CashboxTransfer) => formatDate(item.created_at) },
  ]

  let runningBalance = 0
  const txWithBalance = [...transactions].reverse().map(tx => {
    if (tx.transaction_type === 'income') runningBalance += tx.amount
    else if (tx.transaction_type === 'expense') runningBalance -= tx.amount
    return { ...tx, _balance: runningBalance }
  }).reverse()

  return (
    <div>
      <PageHeader
        title="الصندوق"
        subtitle="إدارة حركات الصندوق"
        action={
          <div className="flex gap-2">
            <button onClick={() => setShowTransfer(true)} className="flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700">
              <ArrowRightLeft size={18} />تحويل بين الصناديق
            </button>
            {selectedCashbox && (
              <button onClick={() => setShowTransaction(true)} className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                <Plus size={18} />معاملة جديدة
              </button>
            )}
          </div>
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="font-semibold mb-4">الصندوق</h3>
          {loadingCashboxes ? (
            <div className="text-center py-4 text-gray-500">جاري التحميل...</div>
          ) : (
            <div className="space-y-2">
              {cashboxes.map(box => (
                <button
                  key={box.id}
                  onClick={() => { setSelectedCashbox(box.id); setTxPage(1) }}
                  className={`w-full p-3 rounded-lg border text-right transition-colors ${selectedCashbox === box.id ? 'bg-blue-50 border-blue-300' : 'hover:bg-gray-50'}`}
                >
                  <div className="flex justify-between items-center">
                    <span className="font-medium">{box.name}</span>
                    <span className={`font-semibold ${box.balance >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {formatCurrency(box.balance)}
                    </span>
                  </div>
                </button>
              ))}
              {cashboxes.length === 0 && <p className="text-gray-500 text-sm">لا توجد صناديق</p>}
            </div>
          )}
        </div>

        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow-sm border">
            <div className="border-b">
              <div className="flex">
                <button
                  onClick={() => setActiveTab('transactions')}
                  className={`px-6 py-3 font-medium border-b-2 transition-colors ${
                    activeTab === 'transactions'
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  المعاملات
                </button>
                <button
                  onClick={() => setActiveTab('transfers')}
                  className={`px-6 py-3 font-medium border-b-2 transition-colors ${
                    activeTab === 'transfers'
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  التحويلات
                </button>
              </div>
            </div>

            <div className="p-6">
              {activeTab === 'transactions' ? (
                selectedCashbox ? (
                  <>
                    <div className="flex justify-between items-center mb-4">
                      <h3 className="font-semibold">معاملات {selectedBox?.name}</h3>
                      {selectedBox && (
                        <div className="flex items-center gap-2">
                          <span className="text-sm text-gray-500">الرصيد الحالي:</span>
                          <span className={`font-bold text-lg ${selectedBox.balance >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {formatCurrency(selectedBox.balance)}
                          </span>
                        </div>
                      )}
                    </div>

                    {loadingTx ? (
                      <div className="text-center py-8 text-gray-500">جاري التحميل...</div>
                    ) : (
                      <>
                        <DataTable columns={txColumns} data={txWithBalance as unknown as Record<string, unknown>[]} emptyMessage="لا توجد معاملات" />

                        {txMeta && txMeta.total > 20 && (
                          <div className="flex justify-center gap-2 mt-4">
                            <button onClick={() => setTxPage(p => Math.max(1, p - 1))} disabled={txPage === 1} className="px-3 py-1 border rounded-lg disabled:opacity-50 hover:bg-gray-50">السابق</button>
                            <span className="px-3 py-1">صفحة {txPage} من {Math.ceil(txMeta.total / 20)}</span>
                            <button onClick={() => setTxPage(p => p + 1)} disabled={txPage >= Math.ceil(txMeta.total / 20)} className="px-3 py-1 border rounded-lg disabled:opacity-50 hover:bg-gray-50">التالي</button>
                          </div>
                        )}
                      </>
                    )}
                  </>
                ) : (
                  <div className="text-center py-12 text-gray-500">
                    اختر صندوقاً لعرض المعاملات
                  </div>
                )
              ) : (
                <>
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="font-semibold">تحويلات الصناديق</h3>
                  </div>

                  {loadingTransfers ? (
                    <div className="text-center py-8 text-gray-500">جاري التحميل...</div>
                  ) : (
                    <>
                      <DataTable columns={transferColumns} data={transfers as unknown as Record<string, unknown>[]} emptyMessage="لا توجد تحويلات" />

                      {transferMeta && transferMeta.total > 20 && (
                        <div className="flex justify-center gap-2 mt-4">
                          <button onClick={() => setTransferPage(p => Math.max(1, p - 1))} disabled={transferPage === 1} className="px-3 py-1 border rounded-lg disabled:opacity-50 hover:bg-gray-50">السابق</button>
                          <span className="px-3 py-1">صفحة {transferPage} من {Math.ceil(transferMeta.total / 20)}</span>
                          <button onClick={() => setTransferPage(p => p + 1)} disabled={transferPage >= Math.ceil(transferMeta.total / 20)} className="px-3 py-1 border rounded-lg disabled:opacity-50 hover:bg-gray-50">التالي</button>
                        </div>
                      )}
                    </>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      <Dialog isOpen={showTransaction} onClose={() => setShowTransaction(false)} title="تسجيل معاملة">
        <form onSubmit={handleCreateTx} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">نوع المعاملة *</label>
            <select value={txForm.transaction_type} onChange={e => setTxForm({ ...txForm, transaction_type: e.target.value })} className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="income">دخل</option>
              <option value="expense">مصروف</option>
              <option value="transfer">تحويل</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">المبلغ *</label>
            <input type="number" step="0.01" min="0.01" value={txForm.amount} onChange={e => setTxForm({ ...txForm, amount: e.target.value })} className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" required />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">الوصف *</label>
            <input type="text" value={txForm.description} onChange={e => setTxForm({ ...txForm, description: e.target.value })} className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" required />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <button type="button" onClick={() => setShowTransaction(false)} className="px-4 py-2 border rounded-lg hover:bg-gray-50">إلغاء</button>
            <button type="submit" disabled={createTxMutation.isPending} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50">
              {createTxMutation.isPending ? 'جاري الحفظ...' : 'حفظ'}
            </button>
          </div>
        </form>
      </Dialog>

      <Dialog isOpen={showTransfer} onClose={() => setShowTransfer(false)} title="تحويل بين الصناديق">
        <form onSubmit={handleCreateTransfer} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">من صندوق *</label>
            <select value={transferForm.from_cashbox_id} onChange={e => setTransferForm({ ...transferForm, from_cashbox_id: e.target.value })} className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" required>
              <option value="">اختر الصندوق المصدر</option>
              {cashboxes.filter(box => box.is_active).map(box => (
                <option key={box.id} value={box.id}>{box.name} ({formatCurrency(box.balance)})</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">إلى صندوق *</label>
            <select value={transferForm.to_cashbox_id} onChange={e => setTransferForm({ ...transferForm, to_cashbox_id: e.target.value })} className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" required>
              <option value="">اختر الصندوق الوجهة</option>
              {cashboxes.filter(box => box.is_active && box.id !== transferForm.from_cashbox_id).map(box => (
                <option key={box.id} value={box.id}>{box.name} ({formatCurrency(box.balance)})</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">المبلغ *</label>
            <input type="number" step="0.01" min="0.01" value={transferForm.amount} onChange={e => setTransferForm({ ...transferForm, amount: e.target.value })} className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" required />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">الوصف *</label>
            <input type="text" value={transferForm.description} onChange={e => setTransferForm({ ...transferForm, description: e.target.value })} className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" required />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <button type="button" onClick={() => setShowTransfer(false)} className="px-4 py-2 border rounded-lg hover:bg-gray-50">إلغاء</button>
            <button type="submit" disabled={createTransferMutation.isPending} className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50">
              {createTransferMutation.isPending ? 'جاري التحويل...' : 'تحويل'}
            </button>
          </div>
        </form>
      </Dialog>
    </div>
  )
}
