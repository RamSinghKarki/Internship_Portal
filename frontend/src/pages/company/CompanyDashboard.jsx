import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { companyAPI } from '../../services/api'
import StatCard from '../../components/StatCard'
import { Briefcase, Users, FileText, TrendingUp, Building2, ArrowRight } from 'lucide-react'

const statusColors = {
  APPLIED: 'badge-gray', SCREENING: 'badge-yellow', SHORTLISTED: 'badge-blue',
  INTERVIEW: 'badge-purple', SELECTED: 'badge-green', REJECTED: 'badge-red',
}

export default function CompanyDashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    companyAPI.getDashboard().then(({ data }) => setData(data)).finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="flex justify-center py-16"><div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" /></div>

  const { stats, recentApplications } = data || {}

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="page-title">Dashboard</h1>
          <p className="text-gray-500 mt-1">Manage your internship programs</p>
        </div>
        <Link to="/company/post" className="btn-primary btn-sm gap-1.5"><Briefcase size={15} /> Post Internship</Link>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Total Internships" value={stats?.totalInternships} icon={Briefcase} color="indigo" />
        <StatCard title="Open Positions" value={stats?.openInternships} icon={TrendingUp} color="emerald" />
        <StatCard title="Applications" value={stats?.totalApplications} icon={FileText} color="amber" />
        <StatCard title="Active Interns" value={stats?.activeEnrollments} icon={Users} color="blue" />
      </div>

      <div className="card">
        <div className="flex items-center justify-between p-5 border-b border-gray-100">
          <h2 className="section-title">Recent Applications</h2>
          <Link to="/company/applications" className="text-sm text-indigo-600 hover:text-indigo-700 font-medium flex items-center gap-1">
            View all <ArrowRight size={14} />
          </Link>
        </div>
        {!recentApplications?.length ? (
          <div className="p-8 text-center text-gray-400 text-sm">
            No applications yet. <Link to="/company/post" className="text-indigo-600">Post an internship</Link> to get started.
          </div>
        ) : (
          <div className="divide-y divide-gray-50">
            {recentApplications.map((app) => (
              <div key={app.id} className="flex items-center gap-4 px-5 py-3">
                <div className="w-9 h-9 bg-indigo-50 rounded-full flex items-center justify-center text-indigo-700 font-semibold text-sm flex-shrink-0">
                  {app.student?.firstName?.[0]}{app.student?.lastName?.[0]}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900">{app.student?.firstName} {app.student?.lastName}</p>
                  <p className="text-xs text-gray-500">{app.internship?.title}</p>
                </div>
                <span className={statusColors[app.status] || 'badge-gray'}>{app.status}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="grid sm:grid-cols-3 gap-4">
        {[
          { label: 'Post New Internship', to: '/company/post', icon: Briefcase, color: 'bg-indigo-50 text-indigo-700' },
          { label: 'Review Applications', to: '/company/applications', icon: FileText, color: 'bg-amber-50 text-amber-700' },
          { label: 'Manage Interns', to: '/company/enrollments', icon: Users, color: 'bg-emerald-50 text-emerald-700' },
        ].map(({ label, to, icon: Icon, color }) => (
          <Link key={to} to={to} className="card p-5 flex items-center gap-3 hover:shadow-md transition-shadow group">
            <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${color}`}><Icon size={20} /></div>
            <span className="font-medium text-gray-700 group-hover:text-gray-900">{label}</span>
            <ArrowRight size={16} className="ml-auto text-gray-300 group-hover:text-gray-500" />
          </Link>
        ))}
      </div>
    </div>
  )
}
