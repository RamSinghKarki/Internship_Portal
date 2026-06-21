import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { supervisorAPI } from '../../services/api'
import StatCard from '../../components/StatCard'
import { Users, BookOpen, ClipboardCheck, ArrowRight } from 'lucide-react'

export default function SupervisorDashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    supervisorAPI.getDashboard().then(({ data }) => setData(data)).finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="flex justify-center py-16"><div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" /></div>

  const { stats, recentLogs } = data || {}

  return (
    <div className="space-y-6">
      <h1 className="page-title">Dashboard</h1>

      <div className="grid grid-cols-3 gap-4">
        <StatCard title="Assigned Students" value={stats?.assigned} icon={Users} color="indigo" />
        <StatCard title="Active" value={stats?.active} icon={ClipboardCheck} color="emerald" />
        <StatCard title="Pending Reviews" value={stats?.pendingLogs} icon={BookOpen} color="amber" />
      </div>

      <div className="card">
        <div className="flex items-center justify-between p-5 border-b border-gray-100">
          <h2 className="section-title">Pending Progress Reviews</h2>
          <Link to="/supervisor/students" className="text-sm text-indigo-600 hover:text-indigo-700 font-medium flex items-center gap-1">
            View all <ArrowRight size={14} />
          </Link>
        </div>
        {!recentLogs?.length ? (
          <div className="p-8 text-center text-gray-400 text-sm">No pending reviews.</div>
        ) : (
          <div className="divide-y divide-gray-50">
            {recentLogs.map((log) => (
              <div key={log.id} className="flex items-center gap-4 px-5 py-3">
                <div className="w-9 h-9 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-700 font-semibold text-sm">
                  W{log.weekNumber}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900">{log.enrollment?.student?.firstName} {log.enrollment?.student?.lastName}</p>
                  <p className="text-xs text-gray-500">{log.enrollment?.internship?.title} · Week {log.weekNumber}</p>
                </div>
                <span className="text-xs text-gray-400">{new Date(log.submittedAt).toLocaleDateString()}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
