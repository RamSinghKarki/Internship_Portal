import { Link } from 'react-router-dom'
import { MapPin, Clock, DollarSign, Wifi, Building2 } from 'lucide-react'

const modeColors = { ONSITE: 'badge-blue', REMOTE: 'badge-green', HYBRID: 'badge-purple' }

export default function InternshipCard({ internship, actions }) {
  const { id, title, company, location, mode, duration, stipend, isPaid, skills, deadline, _count } = internship

  const deadlineDays = deadline
    ? Math.ceil((new Date(deadline) - new Date()) / (1000 * 60 * 60 * 24))
    : null

  return (
    <div className="card p-5 hover:shadow-md transition-shadow">
      <div className="flex items-start gap-3">
        {company?.logoUrl ? (
          <img src={company.logoUrl} alt={company.name} className="w-12 h-12 rounded-lg object-cover border border-gray-200 flex-shrink-0" />
        ) : (
          <div className="w-12 h-12 rounded-lg bg-indigo-100 flex items-center justify-center flex-shrink-0">
            <Building2 size={22} className="text-indigo-600" />
          </div>
        )}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div>
              <Link to={`/internships/${id}`} className="font-semibold text-gray-900 hover:text-indigo-600 transition-colors line-clamp-1">
                {title}
              </Link>
              <p className="text-sm text-gray-500 mt-0.5">{company?.name}</p>
            </div>
            <span className={modeColors[mode] || 'badge-gray'}>{mode}</span>
          </div>

          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-2 text-sm text-gray-500">
            {location && <span className="flex items-center gap-1"><MapPin size={13} />{location}</span>}
            <span className="flex items-center gap-1"><Clock size={13} />{duration}w</span>
            {isPaid && stipend ? (
              <span className="flex items-center gap-1 text-emerald-600 font-medium">
                <DollarSign size={13} />Rs. {stipend.toLocaleString()}/mo
              </span>
            ) : !isPaid ? (
              <span className="text-gray-400">Unpaid</span>
            ) : null}
          </div>

          {skills?.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mt-3">
              {skills.slice(0, 4).map(({ skill }) => (
                <span key={skill.id} className="badge bg-gray-100 text-gray-600">{skill.name}</span>
              ))}
              {skills.length > 4 && <span className="badge bg-gray-100 text-gray-500">+{skills.length - 4}</span>}
            </div>
          )}

          <div className="flex items-center justify-between mt-3">
            <div className="flex items-center gap-3 text-xs text-gray-400">
              {_count?.applications !== undefined && <span>{_count.applications} applicants</span>}
              {deadlineDays !== null && (
                <span className={deadlineDays < 7 ? 'text-red-500 font-medium' : ''}>
                  {deadlineDays > 0 ? `${deadlineDays}d left` : 'Expired'}
                </span>
              )}
            </div>
            <div className="flex items-center gap-2">
              {actions || (
                <Link to={`/internships/${id}`} className="btn-primary btn-sm">View</Link>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
