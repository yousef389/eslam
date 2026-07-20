import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { Settings, Brain, MessageSquare, Globe, Shield, Store, Save, Eye, EyeOff, Database, Download, Upload, FileDown } from 'lucide-react'
import api from '../lib/api'
import PageHeader from '../components/PageHeader'
import LoadingSpinner from '../components/LoadingSpinner'

interface Setting {
  id: string
  key: string
  value: string
  group: string
  description: string
  is_secret: boolean
  updated_at: string
}

const groupConfig: Record<string, { label: string; icon: typeof Brain; color: string }> = {
  ai: { label: 'الذكاء الاصطناعي', icon: Brain, color: 'purple' },
  telegram: { label: 'تيليجرام', icon: MessageSquare, color: 'blue' },
  api: { label: 'API', icon: Globe, color: 'green' },
  security: { label: 'الأمان', icon: Shield, color: 'red' },
  store: { label: 'المحل', icon: Store, color: 'orange' },
  backup: { label: 'النسخ الاحتياطي', icon: Database, color: 'teal' },
}

export default function SettingsPage() {
  const queryClient = useQueryClient()
  const [activeGroup, setActiveGroup] = useState('ai')
  const [editedValues, setEditedValues] = useState<Record<string, string>>({})
  const [showSecrets, setShowSecrets] = useState<Record<string, boolean>>({})

  const { data: settings, isLoading } = useQuery<Setting[]>({
    queryKey: ['settings'],
    queryFn: () => api.get('/settings').then(res => res.data.data),
  })

  const bulkUpdateMutation = useMutation({
    mutationFn: (data: Record<string, string>) =>
      api.put('/settings/', { settings: data }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] })
      toast.success('تم حفظ جميع الإعدادات بنجاح')
      setEditedValues({})
    },
    onError: () => toast.error('حدث خطأ أثناء حفظ الإعدادات'),
  })

  const groupSettings = settings?.filter(s => s.group === activeGroup) || []

  const handleValueChange = (key: string, value: string) => {
    setEditedValues(prev => ({ ...prev, [key]: value }))
  }

  const handleSave = () => {
    if (Object.keys(editedValues).length > 0) {
      bulkUpdateMutation.mutate(editedValues)
    }
  }

  const toggleSecretVisibility = (key: string) => {
    setShowSecrets(prev => ({ ...prev, [key]: !prev[key] }))
  }

  const handleDownload = async (url: string, filename: string) => {
    try {
      const response = await api.get(url, { responseType: 'blob' })
      const blob = new Blob([response.data])
      const link = document.createElement('a')
      link.href = URL.createObjectURL(blob)
      link.download = filename
      link.click()
      URL.revokeObjectURL(link.href)
      toast.success('تم التحميل بنجاح')
    } catch {
      toast.error('حدث خطأ أثناء التحميل')
    }
  }

  const getDisplayValue = (setting: Setting) => {
    if (editedValues[setting.key] !== undefined) {
      return editedValues[setting.key]
    }
    if (setting.is_secret && setting.value) {
      return showSecrets[setting.key] ? setting.value : '••••••••'
    }
    return setting.value
  }

  if (isLoading) return <LoadingSpinner />

  return (
    <div>
      <PageHeader title="إعدادات النظام" subtitle="إدارة إعدادات التطبيق والخدمات" />

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-sm border p-4">
            <nav className="space-y-1">
              {Object.entries(groupConfig).map(([key, config]) => {
                const Icon = config.icon
                const isActive = activeGroup === key
                return (
                  <button
                    key={key}
                    onClick={() => setActiveGroup(key)}
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm transition-colors ${
                      isActive
                        ? 'bg-blue-50 text-blue-700 border-r-4 border-blue-500'
                        : 'hover:bg-gray-50 text-gray-700'
                    }`}
                  >
                    <Icon size={18} />
                    <span className="flex-1 text-right">{config.label}</span>
                  </button>
                )
              })}
            </nav>
          </div>
        </div>

        {/* Content */}
        <div className="lg:col-span-3">
          <div className="bg-white rounded-lg shadow-sm border">
            <div className="p-6 border-b flex items-center justify-between">
              <div className="flex items-center gap-3">
                {(() => {
                  const Icon = groupConfig[activeGroup]?.icon || Settings
                  return <Icon size={24} className="text-blue-600" />
                })()}
                <h2 className="text-lg font-semibold">
                  {groupConfig[activeGroup]?.label || 'إعدادات'}
                </h2>
              </div>
              {Object.keys(editedValues).length > 0 && (
                <button
                  onClick={handleSave}
                  disabled={bulkUpdateMutation.isPending}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  <Save size={16} />
                  {bulkUpdateMutation.isPending ? 'جاري الحفظ...' : 'حفظ التغييرات'}
                </button>
              )}
            </div>

            <div className="p-6">
              {activeGroup === 'backup' ? (
                <div className="space-y-8">
                  {/* Backup Section */}
                  <div>
                    <h3 className="text-md font-semibold mb-4 flex items-center gap-2">
                      <Database size={20} className="text-teal-600" />
                      نسخ احتياطي كامل
                    </h3>
                    <p className="text-sm text-gray-600 mb-4">
                      قم بتحميل نسخة احتياطية كاملة من جميع بيانات النظام
                    </p>
                    <button
                      onClick={() => handleDownload('/settings/backup', 'backup.json')}
                      className="flex items-center gap-2 px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors"
                    >
                      <Download size={16} />
                      تحميل النسخة الاحتياطية
                    </button>
                  </div>

                  <hr className="border-gray-200" />

                  {/* Export Section */}
                  <div>
                    <h3 className="text-md font-semibold mb-4 flex items-center gap-2">
                      <FileDown size={20} className="text-teal-600" />
                      تصدير البيانات
                    </h3>
                    <p className="text-sm text-gray-600 mb-4">
                      قم بتصدير البيانات إلى ملفات CSV
                    </p>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                      <button
                        onClick={() => handleDownload('/settings/export/products', 'products.csv')}
                        className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                      >
                        <Download size={16} />
                        تصدير المنتجات
                      </button>
                      <button
                        onClick={() => handleDownload('/settings/export/customers', 'customers.csv')}
                        className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                      >
                        <Download size={16} />
                        تصدير العملاء
                      </button>
                      <button
                        onClick={() => handleDownload('/settings/export/suppliers', 'suppliers.csv')}
                        className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                      >
                        <Download size={16} />
                        تصدير الموردين
                      </button>
                    </div>
                  </div>

                  <hr className="border-gray-200" />

                  {/* Import Section */}
                  <div>
                    <h3 className="text-md font-semibold mb-4 flex items-center gap-2">
                      <Upload size={20} className="text-teal-600" />
                      استيراد البيانات
                    </h3>
                    <p className="text-sm text-gray-600 mb-4">
                      قم باستيراد البيانات من ملفات CSV
                    </p>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                      <div className="flex items-center gap-2">
                        <input
                          type="file"
                          accept=".csv"
                          id="import-products"
                          className="hidden"
                        />
                        <label
                          htmlFor="import-products"
                          className="flex items-center gap-2 px-4 py-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors cursor-pointer"
                        >
                          <Upload size={16} />
                          استيراد المنتجات
                        </label>
                      </div>
                      <div className="flex items-center gap-2">
                        <input
                          type="file"
                          accept=".csv"
                          id="import-customers"
                          className="hidden"
                        />
                        <label
                          htmlFor="import-customers"
                          className="flex items-center gap-2 px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors cursor-pointer"
                        >
                          <Upload size={16} />
                          استيراد العملاء
                        </label>
                      </div>
                      <div className="flex items-center gap-2">
                        <input
                          type="file"
                          accept=".csv"
                          id="import-suppliers"
                          className="hidden"
                        />
                        <label
                          htmlFor="import-suppliers"
                          className="flex items-center gap-2 px-4 py-2 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition-colors cursor-pointer"
                        >
                          <Upload size={16} />
                          استيراد الموردين
                        </label>
                      </div>
                    </div>
                  </div>
                </div>
              ) : groupSettings.length === 0 ? (
                <p className="text-center text-gray-500 py-8">لا توجد إعدادات في هذا القسم</p>
              ) : (
                <div className="space-y-6">
                  {groupSettings.map((setting) => (
                    <div key={setting.key} className="space-y-2">
                      <label className="block text-sm font-medium text-gray-700">
                        {setting.description}
                        {setting.is_secret && (
                          <span className="mr-2 text-xs bg-yellow-100 text-yellow-800 px-2 py-0.5 rounded">
                           سري
                          </span>
                        )}
                      </label>
                      <div className="relative">
                        <input
                          type={setting.is_secret && !showSecrets[setting.key] ? 'password' : 'text'}
                          value={getDisplayValue(setting)}
                          onChange={(e) => handleValueChange(setting.key, e.target.value)}
                          className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 pr-10"
                          placeholder={setting.description}
                        />
                        {setting.is_secret && (
                          <button
                            type="button"
                            onClick={() => toggleSecretVisibility(setting.key)}
                            className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                          >
                            {showSecrets[setting.key] ? <EyeOff size={18} /> : <Eye size={18} />}
                          </button>
                        )}
                      </div>
                      <p className="text-xs text-gray-400">المفتاح: {setting.key}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
