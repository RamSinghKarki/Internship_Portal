import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { adminAPI } from '../../services/api'
import StatCard from '../../components/StatCard'
import { Users, Building2, Briefcase, FileText, TrendingUp, UserCheck, ArrowRight } from 'lucide-react'

const roleColors = {
  STUDENT: 'badge-blue', COMPANY: 'badge-purple', INTERNAL_SUPERVISOR: 'badge-green',
  EXTERNAL_SUPERVISOR: 'badge-yellow', ADMIN: 'badge-red',
}

export default function AdminDashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    adminAPI.getStats().then(({ data }) => setData(data)).finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="flex justify-center py-16"><div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" /></div>

  const { stats, recentUsers } = data || {}

  return (
    <div className="space-y-6">
      <div>
        <h1 className="page-title">Admin Dashboard</h1>
        <p className="text-gray-500 mt-1">Platform overview and management</p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Students" value={stats?.students} icon={Users} color="indigo" />
        <StatCard title="Companies" value={stats?.companies} sub={`${stats?.verifiedCompanies} verified`} icon={Building2} color="emerald" />
        <StatCard title="Internships" value={stats?.internships} sub={`${stats?.openInternships} open`} icon={Briefcase} color="amber" />
        <StatCard title="Applications" value={stats?.applications} icon={FileText} color="blue" />
        <StatCard title="Enrollments" value={stats?.enrollments} sub={`${stats?.activeEnrollments} active`} icon={TrendingUp} color="purple" />
        <StatCard title="Verified Companies" value={stats?.verifiedCompanies} icon={UserCheck} color="rose" />
      </div>

      <div className="grid sm:grid-cols-3 gap-4">
        {[
          { label: 'Manage Users', to: '/admin/users', icon: Users, color: 'bg-indigo-50 text-indigo-700' },
          { label: 'Manage Companies', to: '/admin/companies', icon: Building2, color: 'bg-emerald-50 text-emerald-700' },
          { label: 'Enrollments', to: '/admin/enrollments', icon: FileText, color: 'bg-amber-50 text-amber-700' },
        ].map(({ label, to, icon: Icon, color }) => (
          <Link key={to} to={to} className="card p-5 flex items-center gap-3 hover:shadow-md transition-shadow group">
            <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${color}`}><Icon size={20} /></div>
            <span className="font-medium text-gray-700 group-hover:text-gray-900">{label}</span>
            <ArrowRight size={16} className="ml-auto text-gray-300 group-hover:text-gray-500" />
          </Link>
        ))}
      </div>

      <div className="card">
        <div className="flex items-center justify-between p-5 border-b border-gray-100">
          <h2 className="section-title">Recent Registrations</h2>
          <Link to="/admin/users" className="text-sm text-indigo-600 hover:text-indigo-700 font-medium flex items-center gap-1">
            View all <ArrowRight size={14} />
          </Link>
        </div>
        <div className="divide-y divide-gray-50">
          {recentUsers?.map((u) => {
            const name = u.student ? `${u.student.firstName} ${u.student.lastName}` :
              u.company?.name || u.supervisor ? `${u.supervisor.firstName} ${u.supervisor.lastName}` :
              u.admin ? `${u.admin.firstName} ${u.admin.lastName}` : u.email
            return (
              <div key={u.id} className="flex items-center gap-4 px-5 py-3">
                <div className="w-9 h-9 bg-gray-100 rounded-full flex items-center justify-center text-gray-600 font-medium text-sm">
                  {(name || 'U')[0].toUpperCase()}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">{name}</p>
                  <p className="text-xs text-gray-500">{u.email}</p>
                </div>
                <span className={roleColors[u.role] || 'badge-gray'}>{u.role.replace('_', ' ')}</span>
                {!u.isActive && <span className="badge-red">Inactive</span>}
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
