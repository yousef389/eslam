import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard, Package, Users, Truck, ShoppingCart,
  BarChart3, Brain, LogOut, Menu, X,
  Landmark
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
  {
    name: 'الحسابات', href: '/accounting', icon: Landmark, children: [
      { name: 'حسابات العملاء', href: '/accounting/customers' },
      { name: 'حسابات الموردين', href: '/accounting/suppliers' },
      { name: 'الصندوق', href: '/accounting/cashbox' },
    ]
  },
  { name: 'التقارير', href: '/reports', icon: BarChart3 },
  { name: 'الذكاء الاصطناعي', href: '/ai', icon: Brain },
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
  const location = useLocation()
  const navigate = useNavigate()

  const { data: user } = useQuery({
    queryKey: ['user'],
    queryFn: () => api.get('/auth/me').then(res => res.data),
  })

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
          <div className="flex items-center gap-4">
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
