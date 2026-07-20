import { useState, useRef, useEffect } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard, Package, Users, Truck, ShoppingCart,
  BarChart3, Brain, LogOut, Menu, X,
  Landmark, Settings, Search, Bell
} from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import api from '../lib/api'

interface NavChild {
  name: string
  href: string
}

interface NavItem {
  name: string
  href: string
  icon: typeof LayoutDashboard
  children?: NavChild[]
}

const navigation: NavItem[] = [
  { name: 'لوحة التحكم', href: '/', icon: LayoutDashboard },
  { name: 'المنتجات', href: '/products', icon: Package },
  { name: 'العملاء', href: '/customers', icon: Users },
  { name: 'الموردين', href: '/suppliers', icon: Truck },
  { name: 'مبيعات', href: '/sales', icon: ShoppingCart },
  { name: 'مشتريات', href: '/purchases', icon: ShoppingCart },
  { name: 'المخزون', href: '/inventory', icon: Package },
  {
    name: 'الحسابات', href: '/accounting', icon: Landmark, children: [
      { name: 'حسابات العملاء', href: '/accounting/customers' },
      { name: 'حسابات الموردين', href: '/accounting/suppliers' },
      { name: 'الصندوق', href: '/accounting/cashbox' },
    ]
  },
  { name: 'التقارير', href: '/reports', icon: BarChart3 },
  { name: 'الذكاء الاصطناعي', href: '/ai', icon: Brain },
  { name: 'الإعدادات', href: '/settings', icon: Settings },
]

function findPageName(pathname: string): string {
  for (const item of navigation) {
    if (item.href === pathname) return item.name
    if (item.children) {
      for (const child of item.children) {
        if (child.href === pathname) return item.name
      }
    }
  }
  return 'نظام ERP'
}

export default function Layout({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [expandedMenus, setExpandedMenus] = useState<Record<string, boolean>>({})
  const [searchQuery, setSearchQuery] = useState('')
  const [showSearch, setShowSearch] = useState(false)
  const [showNotifications, setShowNotifications] = useState(false)
  const searchRef = useRef<HTMLDivElement>(null)
  const notificationRef = useRef<HTMLDivElement>(null)
  const location = useLocation()
  const navigate = useNavigate()

  const { data: user } = useQuery({
    queryKey: ['user'],
    queryFn: () => api.get('/auth/me').then(res => res.data),
  })

  const { data: searchResults } = useQuery({
    queryKey: ['global-search', searchQuery],
    queryFn: () => api.get(`/search/?q=${searchQuery}`).then(res => res.data.data),
    enabled: searchQuery.length >= 2,
  })

  const { data: dashboardStats } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => api.get('/dashboard/stats').then(res => res.data.data),
  })

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setShowSearch(false)
      }
      if (notificationRef.current && !notificationRef.current.contains(event.target as Node)) {
        setShowNotifications(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    navigate('/login')
  }

  const toggleMenu = (href: string) => {
    setExpandedMenus(prev => ({ ...prev, [href]: !prev[href] }))
  }

  const isActive = (href: string) => location.pathname === href
  const isParentActive = (item: NavItem) => {
    if (isActive(item.href)) return true
    if (item.children) return item.children.some(c => isActive(c.href))
    return false
  }

  return (
    <div className="min-h-screen bg-gray-100 flex" dir="rtl">
      {/* Sidebar */}
      <aside className={`${sidebarOpen ? 'w-64' : 'w-16'} bg-gray-900 text-white transition-all duration-300 flex flex-col`}>
        <div className="p-4 flex items-center justify-between">
          {sidebarOpen && <h1 className="text-lg font-bold">ERP الأدوات الصحية</h1>}
          <button onClick={() => setSidebarOpen(!sidebarOpen)} className="p-1 rounded hover:bg-gray-700">
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>

        <nav className="flex-1 overflow-y-auto">
          {navigation.map(item => (
            <div key={item.name}>
              {item.children ? (
                <>
                  <button
                    onClick={() => toggleMenu(item.href)}
                    className={`flex items-center gap-3 px-4 py-3 text-sm hover:bg-gray-800 w-full ${
                      isParentActive(item) ? 'bg-gray-800 border-r-4 border-blue-500' : ''
                    }`}
                  >
                    <item.icon size={20} />
                    {sidebarOpen && <span className="flex-1 text-right">{item.name}</span>}
                    {sidebarOpen && (
                      <span className={`transition-transform ${expandedMenus[item.href] ? 'rotate-180' : ''}`}>
                        <svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor">
                          <path d="M2 4l4 4 4-4" stroke="currentColor" strokeWidth="2" fill="none" />
                        </svg>
                      </span>
                    )}
                  </button>
                  {item.children && sidebarOpen && expandedMenus[item.href] && item.children.map(child => (
                    <Link
                      key={child.href}
                      to={child.href}
                      className={`flex items-center gap-3 px-8 py-2 text-sm hover:bg-gray-800 ${
                        isActive(child.href) ? 'bg-gray-800 border-r-4 border-blue-500' : ''
                      }`}
                    >
                      <span>{child.name}</span>
                    </Link>
                  ))}
                </>
              ) : (
                <Link
                  to={item.href}
                  className={`flex items-center gap-3 px-4 py-3 text-sm hover:bg-gray-800 ${
                    isActive(item.href) ? 'bg-gray-800 border-r-4 border-blue-500' : ''
                  }`}
                >
                  <item.icon size={20} />
                  {sidebarOpen && <span>{item.name}</span>}
                </Link>
              )}
            </div>
          ))}
        </nav>

        <div className="p-4 border-t border-gray-700">
          <button onClick={handleLogout} className="flex items-center gap-2 text-sm text-gray-300 hover:text-white w-full">
            <LogOut size={18} />
            {sidebarOpen && <span>تسجيل الخروج</span>}
          </button>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top bar */}
        <header className="bg-white shadow-sm px-6 py-3 flex justify-between items-center">
          <h2 className="text-lg font-semibold text-gray-700">
            {findPageName(location.pathname)}
          </h2>
          
          {/* Global Search */}
          <div ref={searchRef} className="relative flex-1 max-w-md mx-4">
            <div className="relative">
              <Search size={18} className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="بحث عن منتج، عميل، مورد..."
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value)
                  setShowSearch(e.target.value.length >= 2)
                }}
                onFocus={() => searchQuery.length >= 2 && setShowSearch(true)}
                className="w-full pr-10 pl-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
              />
              {searchQuery && (
                <button
                  onClick={() => {
                    setSearchQuery('')
                    setShowSearch(false)
                  }}
                  className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  <X size={16} />
                </button>
              )}
            </div>
            
            {/* Search Results Dropdown */}
            {showSearch && searchResults && (
              <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-50 max-h-96 overflow-y-auto">
                {(() => {
                  const results = Array.isArray(searchResults) ? searchResults : []
                  if (results.length === 0) return <div className="px-4 py-3 text-sm text-gray-500">لا توجد نتائج</div>
                  const grouped: Record<string, typeof results> = {}
                  results.forEach((r: any) => { if (!grouped[r.type]) grouped[r.type] = []; grouped[r.type].push(r) })
                  const typeLabels: Record<string, string> = {
                    product: 'المنتجات', customer: 'العملاء', supplier: 'الموردين',
                    sale_order: 'فواتير البيع', purchase_order: 'فواتير الشراء',
                  }
                  return Object.entries(grouped).map(([type, items]) => (
                    <div key={type} className="border-b border-gray-100 last:border-b-0">
                      <div className="px-4 py-2 bg-gray-50 text-xs font-semibold text-gray-500">
                        {typeLabels[type] || type}
                      </div>
                      {items.map((item: any) => (
                        <button
                          key={item.id}
                          onClick={() => {
                            navigate(item.link)
                            setShowSearch(false)
                            setSearchQuery('')
                          }}
                          className="w-full px-4 py-3 text-right hover:bg-gray-50 flex flex-col"
                        >
                          <span className="text-sm font-medium text-gray-800">{item.name}</span>
                          {item.subtitle && (
                            <span className="text-xs text-gray-500 mt-0.5">{item.subtitle}</span>
                          )}
                        </button>
                      ))}
                    </div>
                  ))
                  })()}
              </div>
            )}
          </div>

          <div className="flex items-center gap-4">
            {/* Notifications Bell */}
            <div ref={notificationRef} className="relative">
              <button
                onClick={() => setShowNotifications(!showNotifications)}
                className="relative p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg"
              >
                <Bell size={20} />
                {dashboardStats?.low_stock_count > 0 && (
                  <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                    {dashboardStats.low_stock_count}
                  </span>
                )}
              </button>
              
              {/* Notifications Dropdown */}
              {showNotifications && (
                <div className="absolute top-full left-0 mt-1 w-80 bg-white border border-gray-200 rounded-lg shadow-lg z-50">
                  <div className="px-4 py-3 border-b border-gray-200 font-semibold text-sm text-gray-700">
                    الإشعارات
                  </div>
                  <div className="max-h-80 overflow-y-auto">
                    {/* Low Stock Alerts */}
                    {dashboardStats?.low_stock_items && dashboardStats.low_stock_items.length > 0 ? (
                      <div>
                        <div className="px-4 py-2 bg-orange-50 text-xs font-semibold text-orange-600 flex items-center gap-2">
                          <span className="w-2 h-2 bg-orange-500 rounded-full"></span>
                          تنبيه المخزون
                        </div>
                        {dashboardStats.low_stock_items.map((item: any) => (
                          <button
                            key={item.id}
                            onClick={() => {
                              navigate(`/products/${item.id}`)
                              setShowNotifications(false)
                            }}
                            className="w-full px-4 py-3 text-right hover:bg-gray-50 flex flex-col border-b border-gray-100"
                          >
                            <span className="text-sm font-medium text-gray-800">{item.name}</span>
                            <span className="text-xs text-red-500 mt-0.5">
                              المخزون: {item.quantity} {item.unit}
                            </span>
                          </button>
                        ))}
                      </div>
                    ) : (
                      <div className="px-4 py-6 text-center text-gray-500 text-sm">
                        لا توجد إشعارات جديدة
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            <span className="text-sm text-gray-600">
              مرحباً {user?.data?.full_name || 'المستخدم'}
            </span>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  )
}
