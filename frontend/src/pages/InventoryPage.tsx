import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Package,
  AlertTriangle,
  DollarSign,
  Tag,
  Search,
  FileCheck,
  Plus,
  Warehouse,
  ArrowRightLeft,
  ClipboardList,
  Building2,
} from 'lucide-react'
import api from '../lib/api'
import { formatCurrency } from '../lib/utils'
import PageHeader from '../components/PageHeader'
import LoadingSpinner from '../components/LoadingSpinner'
import Dialog from '../components/Dialog'
import toast from 'react-hot-toast'

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

interface WarehouseItem {
  id: string
  name: string
  location: string
  is_active: boolean
  created_at: string
}

interface WarehouseStock {
  id: string
  warehouse_id: string
  product_id: string
  quantity: number
  product_name?: string
  product_sku?: string
}

interface StockMovement {
  id: string
  movement_number: string
  product_id: string
  warehouse_id: string
  movement_type: string
  quantity: number
  notes: string
  created_at: string
}

interface StockTransfer {
  id: string
  transfer_number: string
  product_id: string
  from_warehouse_id: string
  to_warehouse_id: string
  quantity: number
  status: string
  notes: string
  created_at: string
}

type Tab = 'low-stock' | 'all-products' | 'warehouses' | 'stock-movements' | 'stock-transfers' | 'audit'

function getStockStatus(qty: number, min: number): { label: string; className: string } {
  if (qty <= 0) return { label: 'نفد', className: 'bg-red-100 text-red-700' }
  if (qty <= min) return { label: 'ناقص', className: 'bg-orange-100 text-orange-700' }
  return { label: 'متوفر', className: 'bg-green-100 text-green-700' }
}

function getMovementTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    purchase: 'شراء',
    sale: 'بيع',
    return: 'مرتجع',
    transfer: 'نقل',
    adjustment: 'تعديل',
    damage: 'تلف',
  }
  return labels[type] || type
}

function getTransferStatusLabel(status: string): { label: string; className: string } {
  const map: Record<string, { label: string; className: string }> = {
    pending: { label: 'قيد الانتظار', className: 'bg-yellow-100 text-yellow-700' },
    approved: { label: 'موافق عليه', className: 'bg-blue-100 text-blue-700' },
    completed: { label: 'مكتمل', className: 'bg-green-100 text-green-700' },
    rejected: { label: 'مرفوض', className: 'bg-red-100 text-red-700' },
  }
  return map[status] || { label: status, className: 'bg-gray-100 text-gray-700' }
}

export default function InventoryPage() {
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<Tab>('low-stock')
  const [search, setSearch] = useState('')
  const [auditCounts, setAuditCounts] = useState<Record<string, string>>({})

  const [warehouseDialogOpen, setWarehouseDialogOpen] = useState(false)
  const [warehouseName, setWarehouseName] = useState('')
  const [warehouseLocation, setWarehouseLocation] = useState('')
  const [selectedWarehouseId, setSelectedWarehouseId] = useState<string | null>(null)

  const [stockMovementDialogOpen, setStockMovementDialogOpen] = useState(false)
  const [movementProductId, setMovementProductId] = useState('')
  const [movementWarehouseId, setMovementWarehouseId] = useState('')
  const [movementType, setMovementType] = useState('purchase')
  const [movementQuantity, setMovementQuantity] = useState('')
  const [movementNotes, setMovementNotes] = useState('')

  const [stockTransferDialogOpen, setStockTransferDialogOpen] = useState(false)
  const [transferProductId, setTransferProductId] = useState('')
  const [transferFromWarehouseId, setTransferFromWarehouseId] = useState('')
  const [transferToWarehouseId, setTransferToWarehouseId] = useState('')
  const [transferQuantity, setTransferQuantity] = useState('')
  const [transferNotes, setTransferNotes] = useState('')

  const { data: allProductsData, isLoading: loadingAll } = useQuery<PaginatedResponse>({
    queryKey: ['products', 'all-inventory'],
    queryFn: () =>
      api.get('/products', { params: { page: 1, per_page: 1000 } }).then(res => res.data),
  })

  const { data: lowStockData, isLoading: loadingLow } = useQuery<Product[]>({
    queryKey: ['products', 'low-stock'],
    queryFn: () => api.get('/products/low-stock').then(res => res.data.data || res.data),
  })

  const { data: warehouses, isLoading: loadingWarehouses } = useQuery<WarehouseItem[]>({
    queryKey: ['warehouses'],
    queryFn: () => api.get('/inventory/warehouses').then(res => res.data.data || res.data),
  })

  const { data: warehouseStock, isLoading: loadingWarehouseStock } = useQuery<WarehouseStock[]>({
    queryKey: ['warehouse-stock', selectedWarehouseId],
    queryFn: () =>
      api
        .get(`/inventory/warehouses/${selectedWarehouseId}/stock`)
        .then(res => res.data.data || res.data),
    enabled: !!selectedWarehouseId,
  })

  const { data: stockMovements, isLoading: loadingMovements } = useQuery<StockMovement[]>({
    queryKey: ['stock-movements'],
    queryFn: () =>
      api.get('/inventory/stock-movements').then(res => res.data.data || res.data),
  })

  const { data: stockTransfers, isLoading: loadingTransfers } = useQuery<StockTransfer[]>({
    queryKey: ['stock-transfers'],
    queryFn: () =>
      api.get('/inventory/stock-transfers').then(res => res.data.data || res.data),
  })

  const createWarehouseMutation = useMutation({
    mutationFn: (data: { name: string; location: string }) =>
      api.post('/inventory/warehouses', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['warehouses'] })
      toast.success('تم إضافة المستودع بنجاح')
      setWarehouseDialogOpen(false)
      setWarehouseName('')
      setWarehouseLocation('')
    },
    onError: () => toast.error('فشل إضافة المستودع'),
  })

  const createMovementMutation = useMutation({
    mutationFn: (data: {
      product_id: string
      warehouse_id: string
      movement_type: string
      quantity: number
      notes: string
    }) => api.post('/inventory/stock-movements', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['stock-movements'] })
      toast.success('تم تسجيل حركة المخزون بنجاح')
      setStockMovementDialogOpen(false)
      resetMovementForm()
    },
    onError: () => toast.error('فشل تسجيل حركة المخزون'),
  })

  const createTransferMutation = useMutation({
    mutationFn: (data: {
      product_id: string
      from_warehouse_id: string
      to_warehouse_id: string
      quantity: number
      notes: string
    }) => api.post('/inventory/stock-transfers', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['stock-transfers'] })
      toast.success('تم إنشاء طلب النقل بنجاح')
      setStockTransferDialogOpen(false)
      resetTransferForm()
    },
    onError: () => toast.error('فشل إنشاء طلب النقل'),
  })

  const allProducts = allProductsData?.data || []
  const lowStockProducts = lowStockData || []
  const warehouseList = warehouses || []
  const movementList = stockMovements || []
  const transferList = stockTransfers || []

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
    { key: 'warehouses', label: 'المستودعات', icon: Warehouse },
    { key: 'stock-movements', label: 'حركات المخزون', icon: ArrowRightLeft },
    { key: 'stock-transfers', label: 'نقل المخزون', icon: ClipboardList },
    { key: 'audit', label: 'جرد المخزون', icon: FileCheck },
  ]

  function resetMovementForm() {
    setMovementProductId('')
    setMovementWarehouseId('')
    setMovementType('purchase')
    setMovementQuantity('')
    setMovementNotes('')
  }

  function resetTransferForm() {
    setTransferProductId('')
    setTransferFromWarehouseId('')
    setTransferToWarehouseId('')
    setTransferQuantity('')
    setTransferNotes('')
  }

  const isLoading = loadingAll || loadingLow

  if (isLoading) return <LoadingSpinner size="lg" />

  return (
    <div className="space-y-6" dir="rtl">
      <PageHeader title="إدارة المخزون" subtitle="تتبع وإدارة مخزون المنتجات" />

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

      <div className="bg-white rounded-lg shadow-sm border">
        <div className="border-b">
          <div className="flex overflow-x-auto">
            {tabs.map(tab => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`flex items-center gap-2 px-6 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
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

          {activeTab === 'warehouses' && (
            <div>
              <div className="flex items-center justify-between mb-4">
                <div />
                <button
                  onClick={() => setWarehouseDialogOpen(true)}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <Plus size={16} />
                  إضافة مستودع
                </button>
              </div>

              {loadingWarehouses ? (
                <LoadingSpinner size="md" />
              ) : warehouseList.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <Building2 size={48} className="mx-auto text-gray-300 mb-4" />
                  لا توجد مستودعات مسجلة
                </div>
              ) : (
                <>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
                    {warehouseList.map(warehouse => (
                      <div
                        key={warehouse.id}
                        onClick={() => setSelectedWarehouseId(warehouse.id)}
                        className={`p-4 rounded-lg border cursor-pointer transition-all ${
                          selectedWarehouseId === warehouse.id
                            ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-200'
                            : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'
                        }`}
                      >
                        <div className="flex items-center gap-3">
                          <div className="p-2 rounded-lg bg-blue-50 text-blue-600">
                            <Warehouse size={20} />
                          </div>
                          <div>
                            <h4 className="font-medium">{warehouse.name}</h4>
                            <p className="text-sm text-gray-500">{warehouse.location}</p>
                          </div>
                        </div>
                        <div className="mt-2">
                          <span
                            className={`text-xs px-2 py-1 rounded-full ${
                              warehouse.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'
                            }`}
                          >
                            {warehouse.is_active ? 'نشط' : 'غير نشط'}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>

                  {selectedWarehouseId && (
                    <div>
                      <h3 className="text-lg font-medium mb-3">
                        مخزون{' '}
                        {warehouseList.find(w => w.id === selectedWarehouseId)?.name}
                      </h3>
                      {loadingWarehouseStock ? (
                        <LoadingSpinner size="md" />
                      ) : (
                        <div className="overflow-x-auto">
                          <table className="w-full text-sm text-right">
                            <thead>
                              <tr className="border-b bg-gray-50">
                                <th className="px-4 py-3 font-medium text-gray-600">المنتج</th>
                                <th className="px-4 py-3 font-medium text-gray-600">SKU</th>
                                <th className="px-4 py-3 font-medium text-gray-600">الكمية</th>
                              </tr>
                            </thead>
                            <tbody>
                              {warehouseStock && warehouseStock.length > 0 ? (
                                warehouseStock.map(item => (
                                  <tr key={item.id} className="border-b hover:bg-gray-50">
                                    <td className="px-4 py-3 font-medium">
                                      {item.product_name || item.product_id}
                                    </td>
                                    <td className="px-4 py-3 text-gray-500">
                                      {item.product_sku || '-'}
                                    </td>
                                    <td className="px-4 py-3 font-semibold">{item.quantity}</td>
                                  </tr>
                                ))
                              ) : (
                                <tr>
                                  <td colSpan={3} className="text-center py-8 text-gray-500">
                                    لا توجد منتجات في هذا المستودع
                                  </td>
                                </tr>
                              )}
                            </tbody>
                          </table>
                        </div>
                      )}
                    </div>
                  )}
                </>
              )}
            </div>
          )}

          {activeTab === 'stock-movements' && (
            <div>
              <div className="flex items-center justify-between mb-4">
                <div />
                <button
                  onClick={() => setStockMovementDialogOpen(true)}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <Plus size={16} />
                  تسجيل حركة
                </button>
              </div>

              {loadingMovements ? (
                <LoadingSpinner size="md" />
              ) : movementList.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <ArrowRightLeft size={48} className="mx-auto text-gray-300 mb-4" />
                  لا توجد حركات مخزون مسجلة
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm text-right">
                    <thead>
                      <tr className="border-b bg-gray-50">
                        <th className="px-4 py-3 font-medium text-gray-600">رقم الحركة</th>
                        <th className="px-4 py-3 font-medium text-gray-600">نوع الحركة</th>
                        <th className="px-4 py-3 font-medium text-gray-600">المنتج</th>
                        <th className="px-4 py-3 font-medium text-gray-600">المستودع</th>
                        <th className="px-4 py-3 font-medium text-gray-600">الكمية</th>
                        <th className="px-4 py-3 font-medium text-gray-600">ملاحظات</th>
                        <th className="px-4 py-3 font-medium text-gray-600">التاريخ</th>
                      </tr>
                    </thead>
                    <tbody>
                      {movementList.map(movement => {
                        const product = allProducts.find(p => p.id === movement.product_id)
                        const warehouse = warehouseList.find(w => w.id === movement.warehouse_id)
                        return (
                          <tr key={movement.id} className="border-b hover:bg-gray-50">
                            <td className="px-4 py-3 font-medium">{movement.movement_number}</td>
                            <td className="px-4 py-3">
                              <span className="px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-700">
                                {getMovementTypeLabel(movement.movement_type)}
                              </span>
                            </td>
                            <td className="px-4 py-3 text-gray-500">
                              {product?.name || movement.product_id}
                            </td>
                            <td className="px-4 py-3 text-gray-500">
                              {warehouse?.name || movement.warehouse_id}
                            </td>
                            <td className="px-4 py-3 font-semibold">{movement.quantity}</td>
                            <td className="px-4 py-3 text-gray-500 max-w-[200px] truncate">
                              {movement.notes || '-'}
                            </td>
                            <td className="px-4 py-3 text-gray-500">
                              {new Date(movement.created_at).toLocaleDateString('ar-EG')}
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

          {activeTab === 'stock-transfers' && (
            <div>
              <div className="flex items-center justify-between mb-4">
                <div />
                <button
                  onClick={() => setStockTransferDialogOpen(true)}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <Plus size={16} />
                  طلب نقل جديد
                </button>
              </div>

              {loadingTransfers ? (
                <LoadingSpinner size="md" />
              ) : transferList.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <ClipboardList size={48} className="mx-auto text-gray-300 mb-4" />
                  لا توجد طلبات نقل مسجلة
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm text-right">
                    <thead>
                      <tr className="border-b bg-gray-50">
                        <th className="px-4 py-3 font-medium text-gray-600">رقم الطلب</th>
                        <th className="px-4 py-3 font-medium text-gray-600">المنتج</th>
                        <th className="px-4 py-3 font-medium text-gray-600">من</th>
                        <th className="px-4 py-3 font-medium text-gray-600">إلى</th>
                        <th className="px-4 py-3 font-medium text-gray-600">الكمية</th>
                        <th className="px-4 py-3 font-medium text-gray-600">الحالة</th>
                        <th className="px-4 py-3 font-medium text-gray-600">التاريخ</th>
                      </tr>
                    </thead>
                    <tbody>
                      {transferList.map(transfer => {
                        const product = allProducts.find(p => p.id === transfer.product_id)
                        const fromWarehouse = warehouseList.find(
                          w => w.id === transfer.from_warehouse_id,
                        )
                        const toWarehouse = warehouseList.find(
                          w => w.id === transfer.to_warehouse_id,
                        )
                        const statusStyle = getTransferStatusLabel(transfer.status)
                        return (
                          <tr key={transfer.id} className="border-b hover:bg-gray-50">
                            <td className="px-4 py-3 font-medium">{transfer.transfer_number}</td>
                            <td className="px-4 py-3 text-gray-500">
                              {product?.name || transfer.product_id}
                            </td>
                            <td className="px-4 py-3 text-gray-500">
                              {fromWarehouse?.name || transfer.from_warehouse_id}
                            </td>
                            <td className="px-4 py-3 text-gray-500">
                              {toWarehouse?.name || transfer.to_warehouse_id}
                            </td>
                            <td className="px-4 py-3 font-semibold">{transfer.quantity}</td>
                            <td className="px-4 py-3">
                              <span
                                className={`px-2 py-1 rounded-full text-xs font-medium ${statusStyle.className}`}
                              >
                                {statusStyle.label}
                              </span>
                            </td>
                            <td className="px-4 py-3 text-gray-500">
                              {new Date(transfer.created_at).toLocaleDateString('ar-EG')}
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

          {activeTab === 'audit' && (
            <div>
              <div className="mb-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="text-sm text-yellow-800">
                  أدخل العدد الفعلي لكل منتج عند الجرد. سيتم مقارنته مع الكمية المسجلة في النظام.
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

      {/* Create Warehouse Dialog */}
      <Dialog
        isOpen={warehouseDialogOpen}
        onClose={() => setWarehouseDialogOpen(false)}
        title="إضافة مستودع جديد"
      >
        <form
          onSubmit={e => {
            e.preventDefault()
            if (!warehouseName.trim() || !warehouseLocation.trim()) {
              toast.error('يرجى ملء جميع الحقول المطلوبة')
              return
            }
            createWarehouseMutation.mutate({
              name: warehouseName.trim(),
              location: warehouseLocation.trim(),
            })
          }}
          className="space-y-4"
        >
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">اسم المستودع</label>
            <input
              type="text"
              value={warehouseName}
              onChange={e => setWarehouseName(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">الموقع</label>
            <input
              type="text"
              value={warehouseLocation}
              onChange={e => setWarehouseLocation(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
          <div className="flex justify-end gap-3 pt-4">
            <button
              type="button"
              onClick={() => setWarehouseDialogOpen(false)}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
            >
              إلغاء
            </button>
            <button
              type="submit"
              disabled={createWarehouseMutation.isPending}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              {createWarehouseMutation.isPending ? 'جاري الإضافة...' : 'إضافة'}
            </button>
          </div>
        </form>
      </Dialog>

      {/* Create Stock Movement Dialog */}
      <Dialog
        isOpen={stockMovementDialogOpen}
        onClose={() => setStockMovementDialogOpen(false)}
        title="تسجيل حركة مخزون"
      >
        <form
          onSubmit={e => {
            e.preventDefault()
            if (!movementProductId || !movementWarehouseId || !movementQuantity) {
              toast.error('يرجى ملء جميع الحقول المطلوبة')
              return
            }
            createMovementMutation.mutate({
              product_id: movementProductId,
              warehouse_id: movementWarehouseId,
              movement_type: movementType,
              quantity: Number(movementQuantity),
              notes: movementNotes.trim(),
            })
          }}
          className="space-y-4"
        >
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">المنتج</label>
            <select
              value={movementProductId}
              onChange={e => setMovementProductId(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value="">اختر منتج...</option>
              {allProducts.map(p => (
                <option key={p.id} value={p.id}>
                  {p.name} ({p.sku})
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">المستودع</label>
            <select
              value={movementWarehouseId}
              onChange={e => setMovementWarehouseId(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value="">اختر مستودع...</option>
              {warehouseList.map(w => (
                <option key={w.id} value={w.id}>
                  {w.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">نوع الحركة</label>
            <select
              value={movementType}
              onChange={e => setMovementType(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="purchase">شراء</option>
              <option value="sale">بيع</option>
              <option value="return">مرتجع</option>
              <option value="transfer">نقل</option>
              <option value="adjustment">تعديل</option>
              <option value="damage">تلف</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">الكمية</label>
            <input
              type="number"
              min="1"
              value={movementQuantity}
              onChange={e => setMovementQuantity(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">ملاحظات</label>
            <textarea
              value={movementNotes}
              onChange={e => setMovementNotes(e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="اختياري..."
            />
          </div>
          <div className="flex justify-end gap-3 pt-4">
            <button
              type="button"
              onClick={() => setStockMovementDialogOpen(false)}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
            >
              إلغاء
            </button>
            <button
              type="submit"
              disabled={createMovementMutation.isPending}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              {createMovementMutation.isPending ? 'جاري التسجيل...' : 'تسجيل'}
            </button>
          </div>
        </form>
      </Dialog>

      {/* Create Stock Transfer Dialog */}
      <Dialog
        isOpen={stockTransferDialogOpen}
        onClose={() => setStockTransferDialogOpen(false)}
        title="طلب نقل مخزون"
      >
        <form
          onSubmit={e => {
            e.preventDefault()
            if (
              !transferProductId ||
              !transferFromWarehouseId ||
              !transferToWarehouseId ||
              !transferQuantity
            ) {
              toast.error('يرجى ملء جميع الحقول المطلوبة')
              return
            }
            if (transferFromWarehouseId === transferToWarehouseId) {
              toast.error('يجب أن يكون المستودع المصدري والمقصود مختلفين')
              return
            }
            createTransferMutation.mutate({
              product_id: transferProductId,
              from_warehouse_id: transferFromWarehouseId,
              to_warehouse_id: transferToWarehouseId,
              quantity: Number(transferQuantity),
              notes: transferNotes.trim(),
            })
          }}
          className="space-y-4"
        >
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">المنتج</label>
            <select
              value={transferProductId}
              onChange={e => setTransferProductId(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value="">اختر منتج...</option>
              {allProducts.map(p => (
                <option key={p.id} value={p.id}>
                  {p.name} ({p.sku})
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">من مستودع</label>
            <select
              value={transferFromWarehouseId}
              onChange={e => setTransferFromWarehouseId(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value="">اختر مستودع المصدر...</option>
              {warehouseList.map(w => (
                <option key={w.id} value={w.id}>
                  {w.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">إلى مستودع</label>
            <select
              value={transferToWarehouseId}
              onChange={e => setTransferToWarehouseId(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value="">اختر مستودع الوجهة...</option>
              {warehouseList
                .filter(w => w.id !== transferFromWarehouseId)
                .map(w => (
                  <option key={w.id} value={w.id}>
                    {w.name}
                  </option>
                ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">الكمية</label>
            <input
              type="number"
              min="1"
              value={transferQuantity}
              onChange={e => setTransferQuantity(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">ملاحظات</label>
            <textarea
              value={transferNotes}
              onChange={e => setTransferNotes(e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="اختياري..."
            />
          </div>
          <div className="flex justify-end gap-3 pt-4">
            <button
              type="button"
              onClick={() => setStockTransferDialogOpen(false)}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
            >
              إلغاء
            </button>
            <button
              type="submit"
              disabled={createTransferMutation.isPending}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              {createTransferMutation.isPending ? 'جاري الإنشاء...' : 'إنشاء طلب النقل'}
            </button>
          </div>
        </form>
      </Dialog>
    </div>
  )
}
