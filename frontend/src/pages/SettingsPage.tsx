import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { Settings, Brain, MessageSquare, Globe, Shield, Store, Save, Eye, EyeOff } from 'lucide-react'
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
              {groupSettings.length === 0 ? (
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
