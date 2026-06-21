import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { internshipAPI } from '../../services/api'
import { Plus, Edit, Trash2, Users, Clock } from 'lucide-react'

const statusColors = { OPEN: 'badge-green', CLOSED: 'badge-red', DRAFT: 'badge-gray', COMPLETED: 'badge-blue' }

export default function CompanyInternships() {
  const [internships, setInternships] = useState([])
  const [filter, setFilter] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    internshipAPI.getMy({ status: filter || undefined }).then(({ data }) => setInternships(data)).finally(() => setLoading(false))
  }, [filter])

  const handleDelete = async (id) => {
    if (!confirm('Delete this internship? This will also delete all applications.')) return
    await internshipAPI.delete(id)
    setInternships((p) => p.filter((i) => i.id !== id))
  }

  if (loading) return <div className="flex justify-center py-16"><div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" /></div>

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="page-title">My Internships</h1>
        <Link to="/company/post" className="btn-primary btn-sm gap-1.5"><Plus size={15} /> Post New</Link>
      </div>

      <div className="flex gap-2">
        {['', 'OPEN', 'CLOSED', 'DRAFT', 'COMPLETED'].map((s) => (
          <button key={s} onClick={() => setFilter(s)}
            className={`badge text-xs px-3 py-1.5 cursor-pointer ${filter === s ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}>
            {s || 'All'} {s && `(${internships.filter((i) => i.status === s).length})`}
          </button>
        ))}
      </div>

      {internships.length === 0 ? (
        <div className="card p-12 text-center text-gray-400">
          No internships yet. <Link to="/company/post" className="text-indigo-600">Post your first internship.</Link>
        </div>
      ) : (
        <div className="space-y-3">
          {internships.map((i) => (
            <div key={i.id} className="card p-5">
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold text-gray-900">{i.title}</h3>
                    <span className={statusColors[i.status] || 'badge-gray'}>{i.status}</span>
                  </div>
                  <p className="text-sm text-gray-500 mt-0.5">{i.location} · {i.mode} · {i.duration}w</p>
                  <div className="flex items-center gap-4 mt-2 text-xs text-gray-400">
                    <span className="flex items-center gap-1"><Users size={12} />{i._count?.applications} applications</span>
                    <span className="flex items-center gap-1"><Users size={12} />{i._count?.enrollments} enrolled</span>
                    <span className="flex items-center gap-1"><Clock size={12} />
                      {i.deadline ? `Deadline: ${new Date(i.deadline).toLocaleDateString()}` : 'No deadline'}
                    </span>
                  </div>
                  {i.skills?.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mt-2">
                      {i.skills.slice(0, 5).map(({ skill }) => (
                        <span key={skill.id} className="badge bg-gray-100 text-gray-600 text-xs">{skill.name}</span>
                      ))}
                    </div>
                  )}
                </div>
                <div className="flex items-center gap-1.5 flex-shrink-0">
                  <Link to={`/company/post/${i.id}`} className="btn-secondary btn-sm gap-1.5"><Edit size={13} /> Edit</Link>
                  <button onClick={() => handleDelete(i.id)} className="btn-danger btn-sm"><Trash2 size={13} /></button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
