import { useState, useEffect } from 'react'
import { applicationAPI, internshipAPI } from '../../services/api'
import { GraduationCap, Calendar, ChevronDown } from 'lucide-react'

const statuses = ['APPLIED', 'SCREENING', 'SHORTLISTED', 'INTERVIEW', 'SELECTED', 'REJECTED']
const statusColors = {
  APPLIED: 'badge-gray', SCREENING: 'badge-yellow', SHORTLISTED: 'badge-blue',
  INTERVIEW: 'badge-purple', SELECTED: 'badge-green', REJECTED: 'badge-red', WITHDRAWN: 'badge-gray',
}

export default function CompanyApplications() {
  const [applications, setApplications] = useState([])
  const [internships, setInternships] = useState([])
  const [filters, setFilters] = useState({ internshipId: '', status: '' })
  const [pagination, setPagination] = useState({ page: 1, pages: 1, total: 0 })
  const [loading, setLoading] = useState(true)
  const [expanded, setExpanded] = useState(null)
  const [interview, setInterview] = useState({ show: false, appId: null, scheduledAt: '', mode: '', link: '' })

  const load = async (page = 1) => {
    setLoading(true)
    try {
      const { data } = await applicationAPI.getCompanyApps({ ...filters, page, limit: 20 })
      setApplications(data.applications)
      setPagination(data.pagination)
    } finally { setLoading(false) }
  }

  useEffect(() => {
    internshipAPI.getMy().then(({ data }) => setInternships(data))
  }, [])

  useEffect(() => { load(1) }, [filters])

  const changeStatus = async (id, status) => {
    await applicationAPI.updateStatus(id, { status })
    setApplications((a) => a.map((x) => x.id === id ? { ...x, status } : x))
  }

  const scheduleInterview = async (e) => {
    e.preventDefault()
    await applicationAPI.scheduleInterview(interview.appId, {
      scheduledAt: interview.scheduledAt, mode: interview.mode, link: interview.link,
    })
    setInterview({ show: false, appId: null, scheduledAt: '', mode: '', link: '' })
    setApplications((a) => a.map((x) => x.id === interview.appId ? { ...x, status: 'INTERVIEW' } : x))
  }

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="page-title">Applications</h1>
        <span className="text-sm text-gray-500">{pagination.total} total</span>
      </div>

      <div className="flex flex-wrap gap-3">
        <select className="input max-w-xs" value={filters.internshipId} onChange={(e) => setFilters((f) => ({ ...f, internshipId: e.target.value }))}>
          <option value="">All Internships</option>
          {internships.map((i) => <option key={i.id} value={i.id}>{i.title}</option>)}
        </select>
        <select className="input max-w-xs" value={filters.status} onChange={(e) => setFilters((f) => ({ ...f, status: e.target.value }))}>
          <option value="">All Status</option>
          {statuses.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>

      {interview.show && (
        <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
          <div className="card p-6 w-full max-w-sm">
            <h3 className="section-title mb-4">Schedule Interview</h3>
            <form onSubmit={scheduleInterview} className="space-y-3">
              <div><label className="label">Date & Time</label><input required type="datetime-local" className="input" value={interview.scheduledAt} onChange={(e) => setInterview((i) => ({ ...i, scheduledAt: e.target.value }))} /></div>
              <div><label className="label">Mode</label>
                <select className="input" value={interview.mode} onChange={(e) => setInterview((i) => ({ ...i, mode: e.target.value }))}>
                  <option value="">Select</option><option>Online</option><option>In-person</option><option>Phone</option>
                </select>
              </div>
              <div><label className="label">Meeting Link</label><input className="input" placeholder="https://meet.google.com/…" value={interview.link} onChange={(e) => setInterview((i) => ({ ...i, link: e.target.value }))} /></div>
              <div className="flex gap-2 pt-2">
                <button type="submit" className="btn-primary flex-1">Schedule</button>
                <button type="button" onClick={() => setInterview({ show: false, appId: null, scheduledAt: '', mode: '', link: '' })} className="btn-secondary">Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {loading ? (
        <div className="flex justify-center py-16"><div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" /></div>
      ) : applications.length === 0 ? (
        <div className="card p-12 text-center text-gray-400">No applications found.</div>
      ) : (
        <div className="space-y-3">
          {applications.map((app) => (
            <div key={app.id} className="card overflow-hidden">
              <button className="w-full flex items-center gap-4 p-4 text-left hover:bg-gray-50 transition-colors" onClick={() => setExpanded(expanded === app.id ? null : app.id)}>
                <div className="w-10 h-10 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-700 font-semibold text-sm flex-shrink-0">
                  {app.student?.firstName?.[0]}{app.student?.lastName?.[0]}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-gray-900">{app.student?.firstName} {app.student?.lastName}</p>
                  <p className="text-xs text-gray-500">{app.internship?.title} · {app.student?.college?.name || 'No college'}</p>
                </div>
                <span className={statusColors[app.status] || 'badge-gray'}>{app.status}</span>
                <ChevronDown size={16} className="text-gray-400 flex-shrink-0" />
              </button>

              {expanded === app.id && (
                <div className="border-t border-gray-100 p-4 space-y-4">
                  <div className="grid sm:grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-gray-500">Email</p>
                      <p className="font-medium">{app.student?.user?.email}</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Program</p>
                      <p className="font-medium">{app.student?.program?.name || '—'}</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Applied</p>
                      <p className="font-medium">{new Date(app.appliedAt).toLocaleDateString()}</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Skills</p>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {app.student?.skills?.map(({ skill }) => <span key={skill.id} className="badge bg-gray-100 text-gray-600 text-xs">{skill.name}</span>)}
                      </div>
                    </div>
                  </div>
                  {app.coverLetter && (
                    <div>
                      <p className="text-sm text-gray-500 mb-1">Cover Letter</p>
                      <p className="text-sm text-gray-700 bg-gray-50 p-3 rounded-lg">{app.coverLetter}</p>
                    </div>
                  )}
                  <div className="flex flex-wrap gap-2 pt-2 border-t border-gray-100">
                    {statuses.filter((s) => s !== app.status).map((s) => (
                      <button key={s} onClick={() => changeStatus(app.id, s)} className={`btn-sm ${s === 'SELECTED' ? 'btn-success' : s === 'REJECTED' ? 'btn-danger' : 'btn-secondary'}`}>
                        → {s}
                      </button>
                    ))}
                    {app.status !== 'INTERVIEW' && app.status !== 'SELECTED' && app.status !== 'REJECTED' && (
                      <button onClick={() => setInterview({ show: true, appId: app.id, scheduledAt: '', mode: '', link: '' })} className="btn-primary btn-sm gap-1.5">
                        <Calendar size={13} /> Schedule Interview
                      </button>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
