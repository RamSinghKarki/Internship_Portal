import { useState, useEffect } from 'react'
import { adminAPI } from '../../services/api'
import { Search, UserCheck, UserX } from 'lucide-react'

const roles = ['', 'STUDENT', 'COMPANY', 'INTERNAL_SUPERVISOR', 'EXTERNAL_SUPERVISOR', 'ADMIN']
const roleColors = {
  STUDENT: 'badge-blue', COMPANY: 'badge-purple', INTERNAL_SUPERVISOR: 'badge-green',
  EXTERNAL_SUPERVISOR: 'badge-yellow', ADMIN: 'badge-red',
}

export default function AdminUsers() {
  const [users, setUsers] = useState([])
  const [pagination, setPagination] = useState({ page: 1, pages: 1, total: 0 })
  const [filters, setFilters] = useState({ role: '', search: '', isActive: '' })
  const [loading, setLoading] = useState(true)

  const load = async (page = 1) => {
    setLoading(true)
    try {
      const { data } = await adminAPI.getUsers({ ...filters, page, limit: 20 })
      setUsers(data.users)
      setPagination(data.pagination)
    } finally { setLoading(false) }
  }

  useEffect(() => { load(1) }, [filters])

  const toggleActive = async (id, isActive) => {
    await adminAPI.updateUser(id, { isActive: !isActive })
    setUsers((u) => u.map((x) => x.id === id ? { ...x, isActive: !isActive } : x))
  }

  const getName = (u) => {
    if (u.student) return `${u.student.firstName} ${u.student.lastName}`
    if (u.company) return u.company.name
    if (u.supervisor) return `${u.supervisor.firstName} ${u.supervisor.lastName}`
    if (u.admin) return `${u.admin.firstName} ${u.admin.lastName}`
    return '—'
  }

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="page-title">Users</h1>
        <span className="text-sm text-gray-500">{pagination.total} total</span>
      </div>

      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-48">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input className="input pl-9" placeholder="Search by email…" value={filters.search} onChange={(e) => setFilters((f) => ({ ...f, search: e.target.value }))} />
        </div>
        <select className="input w-48" value={filters.role} onChange={(e) => setFilters((f) => ({ ...f, role: e.target.value }))}>
          {roles.map((r) => <option key={r} value={r}>{r || 'All Roles'}</option>)}
        </select>
        <select className="input w-36" value={filters.isActive} onChange={(e) => setFilters((f) => ({ ...f, isActive: e.target.value }))}>
          <option value="">All Status</option>
          <option value="true">Active</option>
          <option value="false">Inactive</option>
        </select>
      </div>

      {loading ? (
        <div className="flex justify-center py-16"><div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" /></div>
      ) : (
        <div className="card overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left px-5 py-3 text-xs font-medium text-gray-500 uppercase tracking-wide">User</th>
                <th className="text-left px-5 py-3 text-xs font-medium text-gray-500 uppercase tracking-wide hidden sm:table-cell">Role</th>
                <th className="text-left px-5 py-3 text-xs font-medium text-gray-500 uppercase tracking-wide hidden md:table-cell">Joined</th>
                <th className="text-left px-5 py-3 text-xs font-medium text-gray-500 uppercase tracking-wide">Status</th>
                <th className="px-5 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {users.map((u) => (
                <tr key={u.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-5 py-3">
                    <p className="font-medium text-gray-900">{getName(u)}</p>
                    <p className="text-xs text-gray-500">{u.email}</p>
                    {u.student?.registrationNumber && <p className="text-xs text-gray-400">Reg: {u.student.registrationNumber}</p>}
                    {u.company?.industry && <p className="text-xs text-gray-400">{u.company.industry}</p>}
                  </td>
                  <td className="px-5 py-3 hidden sm:table-cell">
                    <span className={roleColors[u.role] || 'badge-gray'}>{u.role.replace(/_/g, ' ')}</span>
                    {u.company?.isVerified === false && <span className="badge-yellow ml-1">Unverified</span>}
                  </td>
                  <td className="px-5 py-3 text-gray-500 hidden md:table-cell">{new Date(u.createdAt).toLocaleDateString()}</td>
                  <td className="px-5 py-3">
                    <span className={u.isActive ? 'badge-green' : 'badge-red'}>{u.isActive ? 'Active' : 'Inactive'}</span>
                  </td>
                  <td className="px-5 py-3 text-right">
                    <button
                      onClick={() => toggleActive(u.id, u.isActive)}
                      className={`btn-sm ${u.isActive ? 'btn-secondary gap-1.5' : 'btn-success gap-1.5'}`}
                      title={u.isActive ? 'Deactivate' : 'Activate'}
                    >
                      {u.isActive ? <><UserX size={13} /> Deactivate</> : <><UserCheck size={13} /> Activate</>}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {pagination.pages > 1 && (
            <div className="flex justify-center gap-2 p-4 border-t border-gray-100">
              {Array.from({ length: pagination.pages }, (_, i) => i + 1).map((p) => (
                <button key={p} onClick={() => load(p)} className={`w-9 h-9 rounded-lg text-sm font-medium transition-colors ${p === pagination.page ? 'bg-indigo-600 text-white' : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50'}`}>{p}</button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
