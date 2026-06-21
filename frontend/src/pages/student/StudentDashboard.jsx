import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { studentAPI } from '../../services/api'
import StatCard from '../../components/StatCard'
import { Briefcase, FileText, BookOpen, Clock, Building2, ArrowRight } from 'lucide-react'

const statusColors = {
  APPLIED: 'badge-gray', SCREENING: 'badge-yellow', SHORTLISTED: 'badge-blue',
  INTERVIEW: 'badge-purple', SELECTED: 'badge-green', REJECTED: 'badge-red', WITHDRAWN: 'badge-gray',
}

export default function StudentDashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    studentAPI.getDashboard().then(({ data }) => setData(data)).finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="flex justify-center py-16"><div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" /></div>

  const { stats, recentApplications, activeEnrollment } = data || {}

  return (
    <div className="space-y-6">
      <div>
        <h1 className="page-title">Dashboard</h1>
        <p className="text-gray-500 mt-1">Your internship journey at a glance</p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
        <StatCard title="Applications" value={stats?.applications} icon={FileText} color="indigo" />
        <StatCard title="Enrollments" value={stats?.enrollments} icon={Briefcase} color="emerald" />
        <StatCard title="Progress Logs" value={stats?.progressLogs} icon={BookOpen} color="amber" />
      </div>

      {activeEnrollment && (
        <div className="card p-5">
          <div className="flex items-center justify-between mb-3">
            <h2 className="section-title">Active Internship</h2>
            <Link to="/student/progress" className="text-sm text-indigo-600 hover:text-indigo-700 font-medium flex items-center gap-1">
              View Progress <ArrowRight size={14} />
            </Link>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center flex-shrink-0">
              <Building2 size={18} className="text-indigo-600" />
            </div>
            <div>
              <p className="font-medium text-gray-900">{activeEnrollment.internship?.title}</p>
              <p className="text-sm text-gray-500">{activeEnrollment.internship?.company?.name}</p>
              <div className="flex items-center gap-4 mt-2 text-sm text-gray-500">
                <span className="flex items-center gap-1">
                  <Clock size={13} /> Started {new Date(activeEnrollment.startDate).toLocaleDateString()}
                </span>
                <span>{activeEnrollment._count?.progressLogs} logs submitted</span>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="card">
        <div className="flex items-center justify-between p-5 border-b border-gray-100">
          <h2 className="section-title">Recent Applications</h2>
          <Link to="/student/applications" className="text-sm text-indigo-600 hover:text-indigo-700 font-medium flex items-center gap-1">
            View all <ArrowRight size={14} />
          </Link>
        </div>
        {!recentApplications?.length ? (
          <div className="p-8 text-center text-gray-400">
            <Briefcase size={28} className="mx-auto mb-2 opacity-50" />
            <p className="text-sm">No applications yet.</p>
            <Link to="/student/internships" className="btn-primary btn-sm mt-3 inline-flex">Browse Internships</Link>
          </div>
        ) : (
          <div className="divide-y divide-gray-50">
            {recentApplications.map((app) => (
              <div key={app.id} className="flex items-center gap-4 px-5 py-3">
                {app.internship?.company?.logoUrl ? (
                  <img src={app.internship.company.logoUrl} alt="" className="w-9 h-9 rounded-lg object-cover border border-gray-200" />
                ) : (
                  <div className="w-9 h-9 bg-indigo-50 rounded-lg flex items-center justify-center">
                    <Building2 size={16} className="text-indigo-400" />
                  </div>
                )}
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">{app.internship?.title}</p>
                  <p className="text-xs text-gray-500">{app.internship?.company?.name}</p>
                </div>
                <span className={statusColors[app.status] || 'badge-gray'}>{app.status}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {!activeEnrollment && (
        <div className="card p-6 bg-indigo-50 border-indigo-100 text-center">
          <Briefcase size={28} className="mx-auto mb-3 text-indigo-500" />
          <h3 className="font-semibold text-gray-900 mb-1">Start your internship journey</h3>
          <p className="text-sm text-gray-600 mb-4">Browse internships that match your skills and interests.</p>
          <Link to="/student/internships" className="btn-primary btn-sm inline-flex">Find Internships</Link>
        </div>
      )}
    </div>
  )
}
