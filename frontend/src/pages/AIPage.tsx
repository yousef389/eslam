import { useState, useRef, useCallback } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Upload, Check, X, FileText, Clock, CheckCircle, XCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../lib/api'
import { formatDate } from '../lib/utils'
import PageHeader from '../components/PageHeader'
import LoadingSpinner from '../components/LoadingSpinner'

interface Extraction {
  id: string
  image_url?: string
  source: string
  status: string
  raw_text?: string
  extracted_data?: Record<string, unknown>
  review_notes?: string
  reviewed_by?: string
  created_at: string
  updated_at: string
}

interface PaginatedResponse {
  data: Extraction[]
  meta: { total: number; page: number; per_page: number }
}

const statusConfig: Record<string, { icon: typeof Clock; color: string; label: string }> = {
  pending: { icon: Clock, color: 'text-yellow-600 bg-yellow-50', label: 'قيد المراجعة' },
  reviewed: { icon: FileText, color: 'text-blue-600 bg-blue-50', label: 'تمت المراجعة' },
  approved: { icon: CheckCircle, color: 'text-green-600 bg-green-50', label: 'تمت الموافقة' },
  rejected: { icon: XCircle, color: 'text-red-600 bg-red-50', label: 'مرفوض' },
}

export default function AIPage() {
  const queryClient = useQueryClient()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [page, setPage] = useState(1)
  const [selectedExtraction, setSelectedExtraction] = useState<Extraction | null>(null)
  const [reviewNotes, setReviewNotes] = useState('')
  const [isDragging, setIsDragging] = useState(false)

  const { data, isLoading } = useQuery<PaginatedResponse>({
    queryKey: ['extractions', page],
    queryFn: () => api.get('/extractions', { params: { page, per_page: 20 } }).then(res => res.data),
  })

  const uploadMutation = useMutation({
    mutationFn: (file: File) => {
      const formData = new FormData()
      formData.append('file', file)
      return api.post('/extractions', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        params: { source: 'api' },
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['extractions'] })
      toast.success('تم رفع الملف بنجاح')
    },
    onError: () => toast.error('حدث خطأ أثناء رفع الملف'),
  })

  const reviewMutation = useMutation({
    mutationFn: ({ id, status, notes }: { id: string; status: string; notes?: string }) =>
      api.put(`/extractions/${id}/review`, { status, review_notes: notes }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['extractions'] })
      toast.success('تم مراجعة الاستخراج بنجاح')
      setSelectedExtraction(null)
      setReviewNotes('')
    },
    onError: () => toast.error('حدث خطأ أثناء المراجعة'),
  })

  const handleFile = useCallback((file: File) => {
    if (!file.type.startsWith('image/') && file.type !== 'application/pdf') {
      toast.error('يرجى رفع صورة أو ملف PDF')
      return
    }
    uploadMutation.mutate(file)
  }, [uploadMutation])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) handleFile(file)
  }, [handleFile])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback(() => setIsDragging(false), [])

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) handleFile(file)
    if (fileInputRef.current) fileInputRef.current.value = ''
  }, [handleFile])

  const extractions = data?.data || []
  const meta = data?.meta

  const renderExtractedData = (data: Record<string, unknown>) => {
    if (!data) return null

    const sections = [
      { key: 'products', title: 'المنتجات المستخرجة' },
      { key: 'invoice', title: 'تفاصيل الفاتورة' },
      { key: 'debts', title: 'الديون' },
    ]

    return (
      <div className="space-y-4">
        {sections.map(section => {
          const items = data[section.key]
          if (!items) return null

          if (Array.isArray(items)) {
            return (
              <div key={section.key}>
                <h4 className="font-medium text-sm mb-2">{section.title}</h4>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-50">
                      <tr>
                        {items.length > 0 && Object.keys(items[0] as Record<string, unknown>).map(key => (
                          <th key={key} className="px-3 py-2 text-right text-xs font-medium text-gray-500">{key}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {items.map((item, idx) => (
                        <tr key={idx}>
                          {Object.values(item as Record<string, unknown>).map((val, vi) => (
                            <td key={vi} className="px-3 py-2 text-sm">{String(val ?? '')}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )
          }

          if (typeof items === 'object') {
            return (
              <div key={section.key}>
                <h4 className="font-medium text-sm mb-2">{section.title}</h4>
                <div className="bg-gray-50 rounded-lg p-3 space-y-1">
                  {Object.entries(items as Record<string, unknown>).map(([key, val]) => (
                    <div key={key} className="flex justify-between text-sm">
                      <span className="text-gray-600">{key}:</span>
                      <span className="font-medium">{String(val ?? '-')}</span>
                    </div>
                  ))}
                </div>
              </div>
            )
          }

          return null
        })}
      </div>
    )
  }

  return (
    <div>
      <PageHeader title="الذكاء الاصطناعي" subtitle="تحليل الفواتير والمستندات" />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-2">
          <div
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors ${isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'}`}
          >
            <input ref={fileInputRef} type="file" accept="image/*,application/pdf" onChange={handleInputChange} className="hidden" />
            <Upload className="mx-auto text-gray-400 mb-4" size={48} />
            <p className="text-lg font-medium text-gray-700">اسحب وأفلت ملفاً هنا</p>
            <p className="text-sm text-gray-500 mt-1">أو انقر لاختيار صورة أو ملف PDF</p>
            <p className="text-xs text-gray-400 mt-2">الصيغ المدعومة: JPG, PNG, PDF</p>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="font-semibold mb-4">إحصائيات</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">إجمالي الاستخراجات</span>
              <span className="font-bold">{meta?.total || 0}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">قيد المراجعة</span>
              <span className="font-bold text-yellow-600">{extractions.filter((e: Extraction) => e.status === 'pending').length}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">تمت الموافقة</span>
              <span className="font-bold text-green-600">{extractions.filter((e: Extraction) => e.status === 'approved').length}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">مرفوض</span>
              <span className="font-bold text-red-600">{extractions.filter((e: Extraction) => e.status === 'rejected').length}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="font-semibold mb-4">سجل الاستخراجات</h3>
        {isLoading ? (
          <LoadingSpinner />
        ) : extractions.length === 0 ? (
          <div className="text-center py-8 text-gray-500">لا توجد استخراجات بعد</div>
        ) : (
          <div className="space-y-3">
            {extractions.map((ext: Extraction) => {
              const config = statusConfig[ext.status] || statusConfig.pending
              const Icon = config.icon
              return (
                <div key={ext.id} className="border rounded-lg p-4 hover:bg-gray-50 cursor-pointer" onClick={() => setSelectedExtraction(ext)}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`p-2 rounded-lg ${config.color}`}>
                        <Icon size={18} />
                      </div>
                      <div>
                        <p className="font-medium">{ext.source === 'api' ? 'رفع يدوي' : ext.source}</p>
                        <p className="text-sm text-gray-500">{formatDate(ext.created_at)}</p>
                      </div>
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${config.color}`}>{config.label}</span>
                  </div>
                </div>
              )
            })}
          </div>
        )}

        {meta && meta.total > 20 && (
          <div className="flex justify-center gap-2 mt-4">
            <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1} className="px-3 py-1 border rounded-lg disabled:opacity-50 hover:bg-gray-50">السابق</button>
            <span className="px-3 py-1">صفحة {page} من {Math.ceil(meta.total / 20)}</span>
            <button onClick={() => setPage(p => p + 1)} disabled={page >= Math.ceil(meta.total / 20)} className="px-3 py-1 border rounded-lg disabled:opacity-50 hover:bg-gray-50">التالي</button>
          </div>
        )}
      </div>

      {selectedExtraction && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="fixed inset-0 bg-black/50" onClick={() => setSelectedExtraction(null)} />
          <div className="relative bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-4 border-b">
              <h3 className="text-lg font-semibold">تفاصيل الاستخراج</h3>
              <button onClick={() => setSelectedExtraction(null)} className="p-1 hover:bg-gray-100 rounded">
                <X size={20} />
              </button>
            </div>
            <div className="p-4">
              {selectedExtraction.raw_text && (
                <div className="mb-4">
                  <h4 className="font-medium text-sm mb-2">النص المستخرج:</h4>
                  <pre className="bg-gray-50 p-3 rounded-lg text-sm whitespace-pre-wrap">{selectedExtraction.raw_text}</pre>
                </div>
              )}

              {selectedExtraction.extracted_data && (
                <div className="mb-4">
                  {renderExtractedData(selectedExtraction.extracted_data)}
                </div>
              )}

              {selectedExtraction.status === 'pending' && (
                <div className="border-t pt-4 space-y-3">
                  <div>
                    <label className="block text-sm font-medium mb-1">ملاحظات المراجعة</label>
                    <textarea
                      value={reviewNotes}
                      onChange={e => setReviewNotes(e.target.value)}
                      className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      rows={2}
                      placeholder="ملاحظات اختيارية..."
                    />
                  </div>
                  <div className="flex justify-end gap-2">
                    <button
                      onClick={() => reviewMutation.mutate({ id: selectedExtraction.id, status: 'rejected', notes: reviewNotes })}
                      disabled={reviewMutation.isPending}
                      className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
                    >
                      <X size={16} />رفض
                    </button>
                    <button
                      onClick={() => reviewMutation.mutate({ id: selectedExtraction.id, status: 'approved', notes: reviewNotes })}
                      disabled={reviewMutation.isPending}
                      className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
                    >
                      <Check size={16} />موافقة
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
