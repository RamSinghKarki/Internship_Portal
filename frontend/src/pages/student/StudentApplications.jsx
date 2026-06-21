import { useState, useEffect } from 'react'
import { applicationAPI } from '../../services/api'
import { Building2, Calendar, ExternalLink } from 'lucide-react'
import { Link } from 'react-router-dom'

const statusColors = {
  APPLIED: 'badge-gray', SCREENING: 'badge-yellow', SHORTLISTED: 'badge-blue',
  INTERVIEW: 'badge-purple', SELECTED: 'badge-green', REJECTED: 'badge-red', WITHDRAWN: 'badge-gray',
}

const statusOrder = ['APPLIED', 'SCREENING', 'SHORTLISTED', 'INTERVIEW', 'SELECTED', 'REJECTED', 'WITHDRAWN']

export default function StudentApplications() {
  const [applications, setApplications] = useState([])
  const [filter, setFilter] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    applicationAPI.getStudentApps().then(({ data }) => setApplications(data)).finally(() => setLoading(false))
  }, [])

  const withdraw = async (id) => {
    if (!confirm('Withdraw this application?')) return
    await applicationAPI.withdraw(id)
    setApplications((a) => a.map((x) => x.id === id ? { ...x, status: 'WITHDRAWN' } : x))
  }

  const filtered = filter ? applications.filter((a) => a.status === filter) : applications

  if (loading) return <div className="flex justify-center py-16"><div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" /></div>

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="page-title">My Applications</h1>
        <Link to="/student/internships" className="btn-primary btn-sm">Find More</Link>
      </div>

      <div className="flex flex-wrap gap-2">
        <button onClick={() => setFilter('')} className={`badge text-xs px-3 py-1 cursor-pointer ${!filter ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}>
          All ({applications.length})
        </button>
        {statusOrder.filter((s) => applications.some((a) => a.status === s)).map((s) => (
          <button key={s} onClick={() => setFilter(s)} className={`badge text-xs px-3 py-1 cursor-pointer ${filter === s ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}>
            {s} ({applications.filter((a) => a.status === s).length})
          </button>
        ))}
      </div>

      {filtered.length === 0 ? (
        <div className="card p-12 text-center text-gray-400">
          No applications found.
          <br />
          <Link to="/student/internships" className="btn-primary btn-sm mt-4 inline-flex">Browse Internships</Link>
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map((app) => (
            <div key={app.id} className="card p-5">
              <div className="flex items-start gap-4">
                {app.internship?.company?.logoUrl ? (
                  <img src={app.internship.company.logoUrl} alt="" className="w-11 h-11 rounded-lg object-cover border border-gray-200" />
                ) : (
                  <div className="w-11 h-11 bg-indigo-50 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Building2 size={18} className="text-indigo-400" />
                  </div>
                )}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <p className="font-semibold text-gray-900">{app.internship?.title}</p>
                      <p className="text-sm text-gray-500">{app.internship?.company?.name} · {app.internship?.location}</p>
                    </div>
                    <span className={statusColors[app.status] || 'badge-gray'}>{app.status}</span>
                  </div>

                  <div className="flex flex-wrap gap-x-4 gap-y-1 mt-2 text-xs text-gray-400">
                    <span className="flex items-center gap-1"><Calendar size={12} />Applied {new Date(app.appliedAt).toLocaleDateString()}</span>
                    {app.internship?.mode && <span>{app.internship.mode}</span>}
                    {app.internship?.stipend ? <span>Rs. {app.internship.stipend.toLocaleString()}/mo</span> : null}
                  </div>

                  {app.interview && (
                    <div className="mt-3 p-3 bg-purple-50 rounded-lg border border-purple-100">
                      <p className="text-xs font-medium text-purple-700">Interview Scheduled</p>
                      <p className="text-xs text-purple-600 mt-0.5">
                        {new Date(app.interview.scheduledAt).toLocaleString()}
                        {app.interview.mode && ` · ${app.interview.mode}`}
                      </p>
                      {app.interview.link && (
                        <a href={app.interview.link} target="_blank" rel="noreferrer" className="text-xs text-indigo-600 flex items-center gap-1 mt-1">
                          <ExternalLink size={11} /> Join Link
                        </a>
                      )}
                    </div>
                  )}

                  {app.notes && (
                    <p className="mt-2 text-xs text-gray-500 bg-gray-50 px-3 py-2 rounded">{app.notes}</p>
                  )}

                  {['APPLIED', 'SCREENING', 'SHORTLISTED'].includes(app.status) && (
                    <div className="mt-3">
                      <button onClick={() => withdraw(app.id)} className="text-xs text-red-600 hover:text-red-700 font-medium">Withdraw</button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
