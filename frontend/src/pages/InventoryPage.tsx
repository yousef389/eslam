import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Package, AlertTriangle, DollarSign, Tag, Search, FileCheck } from 'lucide-react'
import api from '../lib/api'
import { formatCurrency } from '../lib/utils'
import PageHeader from '../components/PageHeader'
import LoadingSpinner from '../components/LoadingSpinner'

interface Product {
  id: string
  name: string
  sku: string
  barcode?: string
  category_id?: string
  category_name?: string
  unit_price: number
  cost_price: number
  quantity_in_stock: number
  minimum_stock_level: number
  maximum_stock_level: number
  unit: string
  is_active: boolean
  created_at: string
  updated_at: string
}

interface PaginatedResponse {
  data: Product[]
  meta: { total: number; page: number; per_page: number }
}

type Tab = 'low-stock' | 'all-products' | 'movement' | 'audit'

function getStockStatus(qty: number, min: number): { label: string; className: string } {
  if (qty <= 0) return { label: 'نفد', className: 'bg-red-100 text-red-700' }
  if (qty <= min) return { label: 'ناقص', className: 'bg-orange-100 text-orange-700' }
  return { label: 'متوفر', className: 'bg-green-100 text-green-700' }
}

export default function InventoryPage() {
  const [activeTab, setActiveTab] = useState<Tab>('low-stock')
  const [search, setSearch] = useState('')
  const [auditCounts, setAuditCounts] = useState<Record<string, string>>({})

  const { data: allProductsData, isLoading: loadingAll } = useQuery<PaginatedResponse>({
    queryKey: ['products', 'all-inventory'],
    queryFn: () =>
      api.get('/products', { params: { page: 1, per_page: 1000 } }).then(res => res.data),
  })

  const { data: lowStockData, isLoading: loadingLow } = useQuery<Product[]>({
    queryKey: ['products', 'low-stock'],
    queryFn: () => api.get('/products/low-stock').then(res => res.data.data || res.data),
  })

  const allProducts = allProductsData?.data || []
  const lowStockProducts = lowStockData || []

  const filteredProducts = allProducts.filter(
    p =>
      p.name.toLowerCase().includes(search.toLowerCase()) ||
      p.sku.toLowerCase().includes(search.toLowerCase()) ||
      (p.barcode && p.barcode.toLowerCase().includes(search.toLowerCase())),
  )

  const totalProducts = allProducts.length
  const lowStockCount = lowStockProducts.length
  const inventoryValue = allProducts.reduce((sum, p) => sum + p.quantity_in_stock * p.cost_price, 0)
  const categories = new Set(allProducts.map(p => p.category_id).filter(Boolean)).size

  const tabs: { key: Tab; label: string; icon: typeof Package }[] = [
    { key: 'low-stock', label: 'المنتجات الناقصة', icon: AlertTriangle },
    { key: 'all-products', label: 'المنتجات المتاحة', icon: Package },
    { key: 'movement', label: 'حركة المخزون', icon: FileCheck },
    { key: 'audit', label: 'جرد المخزون', icon: FileCheck },
  ]

  const isLoading = loadingAll || loadingLow

  if (isLoading) return <LoadingSpinner size="lg" />

  return (
    <div className="space-y-6" dir="rtl">
      <PageHeader title="إدارة المخزون" subtitle="تتبع وإدارة مخزون المنتجات" />

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">إجمالي المنتجات</p>
              <p className="text-2xl font-bold mt-1">{totalProducts}</p>
            </div>
            <div className="p-3 rounded-lg bg-blue-50 text-blue-600">
              <Package size={24} />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">المنتجات الناقصة</p>
              <p className="text-2xl font-bold mt-1 text-red-600">{lowStockCount}</p>
            </div>
            <div className="p-3 rounded-lg bg-red-50 text-red-600">
              <AlertTriangle size={24} />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">قيمة المخزون</p>
              <p className="text-2xl font-bold mt-1 text-green-600">{formatCurrency(inventoryValue)}</p>
            </div>
            <div className="p-3 rounded-lg bg-green-50 text-green-600">
              <DollarSign size={24} />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">فئات المنتجات</p>
              <p className="text-2xl font-bold mt-1 text-purple-600">{categories}</p>
            </div>
            <div className="p-3 rounded-lg bg-purple-50 text-purple-600">
              <Tag size={24} />
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="border-b">
          <div className="flex">
            {tabs.map(tab => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`flex items-center gap-2 px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab.key
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <tab.icon size={16} />
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        <div className="p-6">
          {/* Low Stock Tab */}
          {activeTab === 'low-stock' && (
            <div>
              {lowStockProducts.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  لا توجد منتجات ناقصة - المخزون ممتاز
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm text-right">
                    <thead>
                      <tr className="border-b bg-gray-50">
                        <th className="px-4 py-3 font-medium text-gray-600">اسم المنتج</th>
                        <th className="px-4 py-3 font-medium text-gray-600">SKU</th>
                        <th className="px-4 py-3 font-medium text-gray-600">الكمية الحالية</th>
                        <th className="px-4 py-3 font-medium text-gray-600">الحد الأدنى</th>
                        <th className="px-4 py-3 font-medium text-gray-600">الحالة</th>
                      </tr>
                    </thead>
                    <tbody>
                      {lowStockProducts.map(product => {
                        const status = getStockStatus(product.quantity_in_stock, product.minimum_stock_level)
                        return (
                          <tr key={product.id} className="border-b hover:bg-gray-50">
                            <td className="px-4 py-3 font-medium">{product.name}</td>
                            <td className="px-4 py-3 text-gray-500">{product.sku}</td>
                            <td className="px-4 py-3">
                              <span className="font-semibold text-red-600">{product.quantity_in_stock}</span>
                            </td>
                            <td className="px-4 py-3 text-gray-500">{product.minimum_stock_level}</td>
                            <td className="px-4 py-3">
                              <span className={`px-2 py-1 rounded-full text-xs font-medium ${status.className}`}>
                                {status.label}
                              </span>
                            </td>
                          </tr>
                        )
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {/* All Products Tab */}
          {activeTab === 'all-products' && (
            <div>
              <div className="mb-4">
                <div className="relative max-w-md">
                  <Search className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
                  <input
                    type="text"
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                    placeholder="بحث بالاسم أو الكود أو الباركود..."
                    className="w-full pr-10 pl-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm text-right">
                  <thead>
                    <tr className="border-b bg-gray-50">
                      <th className="px-4 py-3 font-medium text-gray-600">اسم المنتج</th>
                      <th className="px-4 py-3 font-medium text-gray-600">SKU</th>
                      <th className="px-4 py-3 font-medium text-gray-600">الباركود</th>
                      <th className="px-4 py-3 font-medium text-gray-600">الفئة</th>
                      <th className="px-4 py-3 font-medium text-gray-600">السعر</th>
                      <th className="px-4 py-3 font-medium text-gray-600">الكمية</th>
                      <th className="px-4 py-3 font-medium text-gray-600">الحالة</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredProducts.length === 0 ? (
                      <tr>
                        <td colSpan={7} className="text-center py-8 text-gray-500">
                          لا توجد منتجات مطابقة
                        </td>
                      </tr>
                    ) : (
                      filteredProducts.map(product => {
                        const status = getStockStatus(product.quantity_in_stock, product.minimum_stock_level)
                        return (
                          <tr key={product.id} className="border-b hover:bg-gray-50">
                            <td className="px-4 py-3 font-medium">{product.name}</td>
                            <td className="px-4 py-3 text-gray-500">{product.sku}</td>
                            <td className="px-4 py-3 text-gray-500">{product.barcode || '-'}</td>
                            <td className="px-4 py-3 text-gray-500">{product.category_name || '-'}</td>
                            <td className="px-4 py-3">{formatCurrency(product.unit_price)}</td>
                            <td className="px-4 py-3">
                              <span
                                className={
                                  product.quantity_in_stock <= product.minimum_stock_level
                                    ? 'font-semibold text-red-600'
                                    : ''
                                }
                              >
                                {product.quantity_in_stock}
                              </span>
                            </td>
                            <td className="px-4 py-3">
                              <span className={`px-2 py-1 rounded-full text-xs font-medium ${status.className}`}>
                                {status.label}
                              </span>
                            </td>
                          </tr>
                        )
                      })
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Stock Movement Tab */}
          {activeTab === 'movement' && (
            <div className="text-center py-12">
              <FileCheck size={48} className="mx-auto text-gray-300 mb-4" />
              <h3 className="text-lg font-medium text-gray-700 mb-2">حركة المخزون</h3>
              <p className="text-gray-500 max-w-md mx-auto">
                سيتم عرض حركة المخزون هنا بناءً على طلبات البيع والمشتريات. تشمل الإضافات والخصومات وتاريخ كل عملية.
              </p>
            </div>
          )}

          {/* Stock Audit Tab */}
          {activeTab === 'audit' && (
            <div>
              <div className="mb-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="text-sm text-yellow-800">
                  أدخل العدد الفعلي لكل منجر عند الجرد. سيتم مقارنته مع الكمية المسجلة في النظام.
                </p>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm text-right">
                  <thead>
                    <tr className="border-b bg-gray-50">
                      <th className="px-4 py-3 font-medium text-gray-600">اسم المنتج</th>
                      <th className="px-4 py-3 font-medium text-gray-600">SKU</th>
                      <th className="px-4 py-3 font-medium text-gray-600">الكمية المسجلة</th>
                      <th className="px-4 py-3 font-medium text-gray-600">العدد الفعلي</th>
                      <th className="px-4 py-3 font-medium text-gray-600">الفرق</th>
                    </tr>
                  </thead>
                  <tbody>
                    {allProducts.map(product => {
                      const auditVal = auditCounts[product.id] || ''
                      const diff =
                        auditVal !== ''
                          ? Number(auditVal) - product.quantity_in_stock
                          : null
                      return (
                        <tr key={product.id} className="border-b hover:bg-gray-50">
                          <td className="px-4 py-3 font-medium">{product.name}</td>
                          <td className="px-4 py-3 text-gray-500">{product.sku}</td>
                          <td className="px-4 py-3">{product.quantity_in_stock}</td>
                          <td className="px-4 py-3">
                            <input
                              type="number"
                              value={auditVal}
                              onChange={e =>
                                setAuditCounts(prev => ({ ...prev, [product.id]: e.target.value }))
                              }
                              placeholder="0"
                              className="w-20 px-2 py-1 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500 text-center"
                            />
                          </td>
                          <td className="px-4 py-3">
                            {diff !== null && (
                              <span
                                className={`font-semibold ${
                                  diff === 0
                                    ? 'text-green-600'
                                    : diff > 0
                                      ? 'text-blue-600'
                                      : 'text-red-600'
                                }`}
                              >
                                {diff > 0 ? `+${diff}` : diff}
                              </span>
                            )}
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
