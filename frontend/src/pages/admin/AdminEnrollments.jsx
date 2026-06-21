import { useState, useEffect } from 'react'
import { adminAPI } from '../../services/api'
import { Users } from 'lucide-react'

const statusColors = { ACTIVE: 'badge-green', COMPLETED: 'badge-blue', TERMINATED: 'badge-red' }

export default function AdminEnrollments() {
  const [enrollments, setEnrollments] = useState([])
  const [pagination, setPagination] = useState({ page: 1, pages: 1, total: 0 })
  const [filter, setFilter] = useState('')
  const [supervisors, setSupervisors] = useState([])
  const [loading, setLoading] = useState(true)
  const [assigning, setAssigning] = useState(null)

  const load = async (page = 1) => {
    setLoading(true)
    try {
      const { data } = await adminAPI.getEnrollments({ status: filter || undefined, page, limit: 20 })
      setEnrollments(data.enrollments)
      setPagination(data.pagination)
    } finally { setLoading(false) }
  }

  useEffect(() => { load(1) }, [filter])

  useEffect(() => {
    adminAPI.getInternalSupervisors().then(({ data }) => setSupervisors(data))
  }, [])

  const assignSupervisor = async (enrollmentId, supervisorId) => {
    await adminAPI.assignSupervisor(enrollmentId, { supervisorId })
    setEnrollments((e) => e.map((en) => {
      if (en.id !== enrollmentId) return en
      const sup = supervisors.find((s) => s.id === supervisorId)
      return { ...en, internalSupervisor: sup ? { firstName: sup.firstName, lastName: sup.lastName } : null }
    }))
    setAssigning(null)
  }

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="page-title">Enrollments</h1>
        <span className="text-sm text-gray-500">{pagination.total} total</span>
      </div>

      <div className="flex gap-2">
        {['', 'ACTIVE', 'COMPLETED', 'TERMINATED'].map((s) => (
          <button key={s} onClick={() => setFilter(s)} className={`badge text-xs px-3 py-1.5 cursor-pointer ${filter === s ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}>
            {s || 'All'}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="flex justify-center py-16"><div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" /></div>
      ) : enrollments.length === 0 ? (
        <div className="card p-12 text-center text-gray-400"><Users size={28} className="mx-auto mb-2 opacity-50" /><p>No enrollments found.</p></div>
      ) : (
        <div className="card overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">Student</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase hidden md:table-cell">Internship</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase hidden lg:table-cell">Int. Supervisor</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {enrollments.map((en) => (
                <tr key={en.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <p className="font-medium text-gray-900">{en.student?.firstName} {en.student?.lastName}</p>
                    <p className="text-xs text-gray-400">{new Date(en.startDate).toLocaleDateString()}</p>
                  </td>
                  <td className="px-4 py-3 hidden md:table-cell">
                    <p className="font-medium text-gray-800">{en.internship?.title}</p>
                    <p className="text-xs text-gray-500">{en.internship?.company?.name}</p>
                  </td>
                  <td className="px-4 py-3 hidden lg:table-cell">
                    {en.internalSupervisor ? (
                      <p className="text-gray-700">{en.internalSupervisor.firstName} {en.internalSupervisor.lastName}</p>
                    ) : (
                      <span className="text-gray-400 text-xs">Not assigned</span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <span className={statusColors[en.status] || 'badge-gray'}>{en.status}</span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    {assigning === en.id ? (
                      <div className="flex items-center gap-2">
                        <select className="input text-xs w-44" defaultValue="" onChange={(e) => e.target.value && assignSupervisor(en.id, e.target.value)}>
                          <option value="">Select supervisor…</option>
                          {supervisors.map((s) => <option key={s.id} value={s.id}>{s.firstName} {s.lastName} — {s.college?.name || 'No college'}</option>)}
                        </select>
                        <button onClick={() => setAssigning(null)} className="text-xs text-gray-500 hover:text-gray-700">✕</button>
                      </div>
                    ) : (
                      <button onClick={() => setAssigning(en.id)} className="btn-secondary btn-sm">
                        {en.internalSupervisor ? 'Change Supervisor' : 'Assign Supervisor'}
                      </button>
                    )}
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
