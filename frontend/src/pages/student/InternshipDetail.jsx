import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { internshipAPI, applicationAPI } from '../../services/api'
import { useAuth } from '../../context/AuthContext'
import { MapPin, Clock, DollarSign, Building2, Users, Calendar, ArrowLeft, Globe, Wifi } from 'lucide-react'

const modeIcons = { ONSITE: Building2, REMOTE: Wifi, HYBRID: Users }

export default function InternshipDetail() {
  const { id } = useParams()
  const { user } = useAuth()
  const [internship, setInternship] = useState(null)
  const [loading, setLoading] = useState(true)
  const [applying, setApplying] = useState(false)
  const [applied, setApplied] = useState(false)
  const [coverLetter, setCoverLetter] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    internshipAPI.getById(id).then(({ data }) => setInternship(data)).finally(() => setLoading(false))
  }, [id])

  const handleApply = async (e) => {
    e.preventDefault()
    setApplying(true)
    setError('')
    try {
      await applicationAPI.apply({ internshipId: id, coverLetter })
      setApplied(true)
      setShowForm(false)
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to apply')
    } finally {
      setApplying(false)
    }
  }

  if (loading) return <div className="flex justify-center py-20"><div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" /></div>
  if (!internship) return <div className="text-center py-20 text-gray-500">Internship not found.</div>

  const { title, company, description, requirements, responsibilities, stipend, isPaid, duration, vacancies, location, mode, deadline, skills, _count } = internship
  const ModeIcon = modeIcons[mode] || Building2
  const deadlineDays = deadline ? Math.ceil((new Date(deadline) - new Date()) / (1000 * 60 * 60 * 24)) : null

  return (
    <div className="max-w-4xl mx-auto space-y-5">
      <Link to={user ? '/student/internships' : '/'} className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700">
        <ArrowLeft size={16} /> Back
      </Link>

      <div className="card p-6">
        <div className="flex items-start gap-4">
          {company?.logoUrl ? (
            <img src={company.logoUrl} alt={company.name} className="w-16 h-16 rounded-xl object-cover border border-gray-200" />
          ) : (
            <div className="w-16 h-16 bg-indigo-100 rounded-xl flex items-center justify-center flex-shrink-0">
              <Building2 size={28} className="text-indigo-600" />
            </div>
          )}
          <div className="flex-1">
            <h1 className="text-xl font-bold text-gray-900">{title}</h1>
            <p className="text-gray-600 mt-0.5">{company?.name}</p>
            {company?.isVerified && <span className="badge-green mt-1">Verified Company</span>}

            <div className="flex flex-wrap gap-x-5 gap-y-2 mt-3 text-sm text-gray-500">
              {location && <span className="flex items-center gap-1.5"><MapPin size={14} />{location}</span>}
              <span className="flex items-center gap-1.5"><ModeIcon size={14} />{mode}</span>
              <span className="flex items-center gap-1.5"><Clock size={14} />{duration} weeks</span>
              {isPaid && stipend ? (
                <span className="flex items-center gap-1.5 text-emerald-600 font-medium"><DollarSign size={14} />Rs. {stipend.toLocaleString()}/month</span>
              ) : <span className="text-gray-400">Unpaid</span>}
              <span className="flex items-center gap-1.5"><Users size={14} />{vacancies} vacancies</span>
              <span className="flex items-center gap-1.5"><Users size={14} />{_count?.applications} applicants</span>
              {deadlineDays !== null && (
                <span className={`flex items-center gap-1.5 ${deadlineDays < 7 ? 'text-red-500 font-medium' : ''}`}>
                  <Calendar size={14} />
                  {deadlineDays > 0 ? `${deadlineDays} days left` : 'Deadline passed'}
                </span>
              )}
            </div>
          </div>
        </div>

        {skills?.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t border-gray-100">
            {skills.map(({ skill }) => <span key={skill.id} className="badge bg-indigo-50 text-indigo-700">{skill.name}</span>)}
          </div>
        )}
      </div>

      <div className="grid lg:grid-cols-3 gap-5">
        <div className="lg:col-span-2 space-y-5">
          {description && (
            <div className="card p-5">
              <h2 className="section-title mb-3">About the Role</h2>
              <p className="text-sm text-gray-600 whitespace-pre-line leading-relaxed">{description}</p>
            </div>
          )}
          {requirements && (
            <div className="card p-5">
              <h2 className="section-title mb-3">Requirements</h2>
              <p className="text-sm text-gray-600 whitespace-pre-line leading-relaxed">{requirements}</p>
            </div>
          )}
          {responsibilities && (
            <div className="card p-5">
              <h2 className="section-title mb-3">Responsibilities</h2>
              <p className="text-sm text-gray-600 whitespace-pre-line leading-relaxed">{responsibilities}</p>
            </div>
          )}
        </div>

        <div className="space-y-4">
          {user?.role === 'STUDENT' && (
            <div className="card p-5">
              {applied ? (
                <div className="text-center">
                  <span className="badge-green text-sm px-3 py-1.5">Application Submitted!</span>
                  <p className="text-xs text-gray-500 mt-2">Track it in <Link to="/student/applications" className="text-indigo-600">My Applications</Link></p>
                </div>
              ) : showForm ? (
                <form onSubmit={handleApply} className="space-y-3">
                  <label className="label">Cover Letter (optional)</label>
                  <textarea className="input h-28 resize-none" placeholder="Why are you interested in this role?…" value={coverLetter} onChange={(e) => setCoverLetter(e.target.value)} />
                  {error && <p className="text-sm text-red-600">{error}</p>}
                  <button type="submit" disabled={applying} className="btn-primary w-full">{applying ? 'Applying…' : 'Submit Application'}</button>
                  <button type="button" onClick={() => setShowForm(false)} className="btn-secondary w-full">Cancel</button>
                </form>
              ) : (
                <button onClick={() => setShowForm(true)} className="btn-primary w-full">Apply Now</button>
              )}
            </div>
          )}

          {company && (
            <div className="card p-5 space-y-3">
              <h2 className="section-title">Company</h2>
              <p className="text-sm text-gray-600">{company.description?.slice(0, 150)}{company.description?.length > 150 ? '…' : ''}</p>
              <div className="text-sm text-gray-500 space-y-1">
                {company.industry && <p>Industry: {company.industry}</p>}
                {company.size && <p>Size: {company.size} employees</p>}
                {company.website && (
                  <a href={company.website} target="_blank" rel="noreferrer" className="flex items-center gap-1.5 text-indigo-600 hover:text-indigo-700">
                    <Globe size={13} /> Website
                  </a>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
