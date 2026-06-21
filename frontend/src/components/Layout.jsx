import { useState, useEffect } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { notificationAPI } from '../services/api'
import {
  LayoutDashboard, Briefcase, FileText, Users, Settings,
  Bell, LogOut, Menu, X, User, Building2, GraduationCap,
  ClipboardList, BookOpen, Award, ChevronRight,
} from 'lucide-react'

const roleNavItems = {
  STUDENT: [
    { to: '/student/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/student/internships', icon: Briefcase, label: 'Find Internships' },
    { to: '/student/applications', icon: FileText, label: 'My Applications' },
    { to: '/student/progress', icon: BookOpen, label: 'Progress Logs' },
    { to: '/student/profile', icon: User, label: 'Profile' },
  ],
  COMPANY: [
    { to: '/company/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/company/internships', icon: Briefcase, label: 'My Internships' },
    { to: '/company/post', icon: FileText, label: 'Post Internship' },
    { to: '/company/applications', icon: ClipboardList, label: 'Applications' },
    { to: '/company/enrollments', icon: Users, label: 'Interns' },
    { to: '/company/profile', icon: Building2, label: 'Company Profile' },
  ],
  INTERNAL_SUPERVISOR: [
    { to: '/supervisor/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/supervisor/students', icon: GraduationCap, label: 'My Students' },
    { to: '/supervisor/profile', icon: User, label: 'Profile' },
  ],
  EXTERNAL_SUPERVISOR: [
    { to: '/supervisor/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/supervisor/students', icon: GraduationCap, label: 'My Students' },
    { to: '/supervisor/profile', icon: User, label: 'Profile' },
  ],
  ADMIN: [
    { to: '/admin/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/admin/users', icon: Users, label: 'Users' },
    { to: '/admin/companies', icon: Building2, label: 'Companies' },
    { to: '/admin/enrollments', icon: Award, label: 'Enrollments' },
  ],
}

const roleLabels = {
  STUDENT: 'Student',
  COMPANY: 'Company',
  INTERNAL_SUPERVISOR: 'Int. Supervisor',
  EXTERNAL_SUPERVISOR: 'Ext. Supervisor',
  ADMIN: 'Administrator',
}

export default function Layout({ children }) {
  const { user, logout } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [unread, setUnread] = useState(0)

  const navItems = roleNavItems[user?.role] || []
  const name = user?.profile?.name || user?.profile?.firstName
    ? `${user?.profile?.firstName || ''} ${user?.profile?.lastName || ''}`.trim() || user?.profile?.name
    : user?.email

  useEffect(() => {
    notificationAPI.getUnreadCount().then(({ data }) => setUnread(data.count)).catch(() => {})
  }, [location.pathname])

  const handleLogout = () => { logout(); navigate('/') }

  const Sidebar = ({ mobile }) => (
    <div className={`flex flex-col h-full ${mobile ? '' : ''}`}>
      <div className="flex items-center gap-3 px-5 py-5 border-b border-gray-100">
        <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center text-white font-bold text-sm">IP</div>
        <span className="font-semibold text-gray-900">InternPortal</span>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
        {navItems.map(({ to, icon: Icon, label }) => {
          const active = location.pathname === to || location.pathname.startsWith(to + '/')
          return (
            <Link
              key={to}
              to={to}
              onClick={() => setSidebarOpen(false)}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                active ? 'bg-indigo-50 text-indigo-700' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`}
            >
              <Icon size={18} />
              {label}
              {active && <ChevronRight size={14} className="ml-auto text-indigo-400" />}
            </Link>
          )
        })}
      </nav>

      <div className="px-3 py-4 border-t border-gray-100">
        <div className="flex items-center gap-3 px-3 py-2 mb-1">
          <div className="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-700 font-semibold text-sm">
            {(name || 'U')[0].toUpperCase()}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 truncate">{name}</p>
            <p className="text-xs text-gray-500">{roleLabels[user?.role]}</p>
          </div>
        </div>
        <button onClick={handleLogout} className="w-full flex items-center gap-3 px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors">
          <LogOut size={16} /> Sign out
        </button>
      </div>
    </div>
  )

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Desktop sidebar */}
      <aside className="hidden lg:flex lg:flex-col w-60 bg-white border-r border-gray-200 flex-shrink-0">
        <Sidebar />
      </aside>

      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="absolute inset-0 bg-black/40" onClick={() => setSidebarOpen(false)} />
          <aside className="relative w-60 h-full bg-white shadow-xl">
            <button onClick={() => setSidebarOpen(false)} className="absolute top-4 right-4 p-1 text-gray-500 hover:text-gray-700">
              <X size={20} />
            </button>
            <Sidebar mobile />
          </aside>
        </div>
      )}

      {/* Main */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top bar */}
        <header className="bg-white border-b border-gray-200 px-4 py-3 flex items-center gap-3 flex-shrink-0">
          <button className="lg:hidden p-1.5 rounded-lg hover:bg-gray-100" onClick={() => setSidebarOpen(true)}>
            <Menu size={20} />
          </button>
          <div className="flex-1" />
          <Link to="/notifications" className="relative p-2 rounded-lg hover:bg-gray-100 text-gray-600">
            <Bell size={20} />
            {unread > 0 && (
              <span className="absolute top-1 right-1 w-4 h-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                {unread > 9 ? '9+' : unread}
              </span>
            )}
          </Link>
        </header>

        {/* Content */}
        <main className="flex-1 overflow-y-auto p-4 lg:p-6">
          {children}
        </main>
      </div>
    </div>
  )
}
