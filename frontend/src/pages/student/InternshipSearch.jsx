import { useState, useEffect, useCallback } from 'react'
import { internshipAPI, skillAPI, applicationAPI } from '../../services/api'
import InternshipCard from '../../components/InternshipCard'
import { Search, Filter, X } from 'lucide-react'
import { useAuth } from '../../context/AuthContext'

export default function InternshipSearch() {
  const { user } = useAuth()
  const [internships, setInternships] = useState([])
  const [pagination, setPagination] = useState({ page: 1, pages: 1, total: 0 })
  const [skills, setSkills] = useState([])
  const [loading, setLoading] = useState(true)
  const [applying, setApplying] = useState({})
  const [applied, setApplied] = useState(new Set())
  const [filters, setFilters] = useState({ search: '', mode: '', location: '', isPaid: '', skills: '' })
  const [showFilters, setShowFilters] = useState(false)

  useEffect(() => {
    skillAPI.getAll().then(({ data }) => setSkills(data)).catch(() => {})
  }, [])

  const fetch = useCallback(async (page = 1) => {
    setLoading(true)
    try {
      const params = { page, limit: 12, status: 'OPEN', ...Object.fromEntries(Object.entries(filters).filter(([, v]) => v)) }
      const { data } = await internshipAPI.getAll(params)
      setInternships(data.internships)
      setPagination(data.pagination)
    } finally {
      setLoading(false)
    }
  }, [filters])

  useEffect(() => { fetch(1) }, [fetch])

  const handleApply = async (internshipId) => {
    setApplying((a) => ({ ...a, [internshipId]: true }))
    try {
      await applicationAPI.apply({ internshipId, coverLetter: '' })
      setApplied((s) => new Set([...s, internshipId]))
    } catch (err) {
      alert(err.response?.data?.error || 'Failed to apply')
    } finally {
      setApplying((a) => ({ ...a, [internshipId]: false }))
    }
  }

  const clearFilters = () => setFilters({ search: '', mode: '', location: '', isPaid: '', skills: '' })
  const hasFilters = Object.values(filters).some(Boolean)

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="page-title">Find Internships</h1>
        <button onClick={() => setShowFilters(!showFilters)} className="btn-secondary btn-sm gap-1.5">
          <Filter size={15} /> Filters {hasFilters && <span className="w-4 h-4 bg-indigo-600 text-white text-xs rounded-full flex items-center justify-center">{Object.values(filters).filter(Boolean).length}</span>}
        </button>
      </div>

      {/* Search bar */}
      <div className="relative">
        <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
        <input
          className="input pl-10"
          placeholder="Search by title, company, or keyword…"
          value={filters.search}
          onChange={(e) => setFilters((f) => ({ ...f, search: e.target.value }))}
        />
      </div>

      {/* Filter panel */}
      {showFilters && (
        <div className="card p-4 grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div>
            <label className="label">Mode</label>
            <select className="input" value={filters.mode} onChange={(e) => setFilters((f) => ({ ...f, mode: e.target.value }))}>
              <option value="">All</option>
              <option value="ONSITE">Onsite</option>
              <option value="REMOTE">Remote</option>
              <option value="HYBRID">Hybrid</option>
            </select>
          </div>
          <div>
            <label className="label">Location</label>
            <input className="input" placeholder="Kathmandu…" value={filters.location} onChange={(e) => setFilters((f) => ({ ...f, location: e.target.value }))} />
          </div>
          <div>
            <label className="label">Stipend</label>
            <select className="input" value={filters.isPaid} onChange={(e) => setFilters((f) => ({ ...f, isPaid: e.target.value }))}>
              <option value="">All</option>
              <option value="true">Paid only</option>
              <option value="false">Unpaid only</option>
            </select>
          </div>
          <div>
            <label className="label">Skill</label>
            <select className="input" value={filters.skills} onChange={(e) => setFilters((f) => ({ ...f, skills: e.target.value }))}>
              <option value="">All Skills</option>
              {skills.map((s) => <option key={s.id} value={s.name}>{s.name}</option>)}
            </select>
          </div>
          {hasFilters && (
            <button onClick={clearFilters} className="col-span-full btn-secondary btn-sm gap-1.5 mt-1 self-start">
              <X size={14} /> Clear filters
            </button>
          )}
        </div>
      )}

      <p className="text-sm text-gray-500">{pagination.total} internships found</p>

      {loading ? (
        <div className="flex justify-center py-16"><div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" /></div>
      ) : internships.length === 0 ? (
        <div className="card p-12 text-center text-gray-400">No internships found. Try adjusting your filters.</div>
      ) : (
        <>
          <div className="space-y-3">
            {internships.map((internship) => (
              <InternshipCard
                key={internship.id}
                internship={internship}
                actions={
                  user?.role === 'STUDENT' && (
                    applied.has(internship.id) ? (
                      <span className="badge-green">Applied</span>
                    ) : (
                      <button
                        onClick={() => handleApply(internship.id)}
                        disabled={applying[internship.id]}
                        className="btn-primary btn-sm"
                      >
                        {applying[internship.id] ? 'Applying…' : 'Quick Apply'}
                      </button>
                    )
                  )
                }
              />
            ))}
          </div>

          {pagination.pages > 1 && (
            <div className="flex justify-center gap-2">
              {Array.from({ length: pagination.pages }, (_, i) => i + 1).map((p) => (
                <button
                  key={p}
                  onClick={() => fetch(p)}
                  className={`w-9 h-9 rounded-lg text-sm font-medium transition-colors ${
                    p === pagination.page ? 'bg-indigo-600 text-white' : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  {p}
                </button>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  )
}
