import { useState, useEffect } from 'react'
import { adminAPI } from '../../services/api'
import { Search, CheckCircle, XCircle, Building2 } from 'lucide-react'

export default function AdminCompanies() {
  const [companies, setCompanies] = useState([])
  const [pagination, setPagination] = useState({ page: 1, pages: 1, total: 0 })
  const [filters, setFilters] = useState({ search: '', isVerified: '' })
  const [loading, setLoading] = useState(true)

  const load = async (page = 1) => {
    setLoading(true)
    try {
      const { data } = await adminAPI.getCompanies({ ...filters, page, limit: 20 })
      setCompanies(data.companies)
      setPagination(data.pagination)
    } finally { setLoading(false) }
  }

  useEffect(() => { load(1) }, [filters])

  const toggleVerify = async (id, isVerified) => {
    await adminAPI.verifyCompany(id, { isVerified: !isVerified })
    setCompanies((c) => c.map((x) => x.id === id ? { ...x, isVerified: !isVerified } : x))
  }

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="page-title">Companies</h1>
        <span className="text-sm text-gray-500">{pagination.total} total</span>
      </div>

      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-48">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input className="input pl-9" placeholder="Search companies…" value={filters.search} onChange={(e) => setFilters((f) => ({ ...f, search: e.target.value }))} />
        </div>
        <select className="input w-44" value={filters.isVerified} onChange={(e) => setFilters((f) => ({ ...f, isVerified: e.target.value }))}>
          <option value="">All Companies</option>
          <option value="true">Verified</option>
          <option value="false">Unverified</option>
        </select>
      </div>

      {loading ? (
        <div className="flex justify-center py-16"><div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" /></div>
      ) : (
        <div className="space-y-3">
          {companies.map((c) => (
            <div key={c.id} className="card p-5 flex items-center gap-4">
              {c.logoUrl ? (
                <img src={c.logoUrl} alt="" className="w-12 h-12 rounded-xl object-cover border border-gray-200 flex-shrink-0" />
              ) : (
                <div className="w-12 h-12 bg-indigo-100 rounded-xl flex items-center justify-center flex-shrink-0">
                  <Building2 size={20} className="text-indigo-600" />
                </div>
              )}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <p className="font-semibold text-gray-900">{c.name}</p>
                  {c.isVerified ? <span className="badge-green">Verified</span> : <span className="badge-yellow">Pending</span>}
                </div>
                <p className="text-xs text-gray-500 mt-0.5">{c.user?.email} · {c.industry} · {c.location}</p>
                <p className="text-xs text-gray-400 mt-0.5">{c._count?.internships} internships posted</p>
              </div>
              <button
                onClick={() => toggleVerify(c.id, c.isVerified)}
                className={`btn-sm flex-shrink-0 gap-1.5 ${c.isVerified ? 'btn-danger' : 'btn-success'}`}
              >
                {c.isVerified ? <><XCircle size={13} /> Unverify</> : <><CheckCircle size={13} /> Verify</>}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
