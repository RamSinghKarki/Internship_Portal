import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { internshipAPI, skillAPI } from '../../services/api'
import { X, Save } from 'lucide-react'

export default function PostInternship() {
  const { id } = useParams()
  const navigate = useNavigate()
  const isEdit = Boolean(id)
  const [allSkills, setAllSkills] = useState([])
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [form, setForm] = useState({
    title: '', description: '', requirements: '', responsibilities: '',
    stipend: '', isPaid: false, duration: '', vacancies: '1',
    location: '', mode: 'ONSITE', startDate: '', endDate: '', deadline: '',
  })
  const [selectedSkills, setSelectedSkills] = useState([])

  useEffect(() => {
    skillAPI.getAll().then(({ data }) => setAllSkills(data))
    if (isEdit) {
      internshipAPI.getById(id).then(({ data }) => {
        setForm({
          title: data.title || '', description: data.description || '',
          requirements: data.requirements || '', responsibilities: data.responsibilities || '',
          stipend: data.stipend || '', isPaid: data.isPaid || false,
          duration: data.duration || '', vacancies: data.vacancies || '1',
          location: data.location || '', mode: data.mode || 'ONSITE',
          startDate: data.startDate ? data.startDate.split('T')[0] : '',
          endDate: data.endDate ? data.endDate.split('T')[0] : '',
          deadline: data.deadline ? data.deadline.split('T')[0] : '',
        })
        setSelectedSkills(data.skills?.map((s) => s.skillId || s.skill?.id) || [])
      })
    }
  }, [id, isEdit])

  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }))

  const toggleSkill = (skillId) => {
    setSelectedSkills((ss) => ss.includes(skillId) ? ss.filter((s) => s !== skillId) : [...ss, skillId])
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    try {
      const data = {
        ...form,
        duration: parseInt(form.duration),
        vacancies: parseInt(form.vacancies),
        stipend: form.isPaid && form.stipend ? parseFloat(form.stipend) : null,
        skills: selectedSkills,
        startDate: form.startDate || null,
        endDate: form.endDate || null,
        deadline: form.deadline || null,
      }
      if (isEdit) { await internshipAPI.update(id, data) } else { await internshipAPI.create(data) }
      navigate('/company/internships')
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to save internship')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-5">
      <h1 className="page-title">{isEdit ? 'Edit Internship' : 'Post New Internship'}</h1>

      {error && <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">{error}</div>}

      <form onSubmit={handleSubmit} className="space-y-5">
        <div className="card p-5 space-y-4">
          <h2 className="section-title">Basic Details</h2>
          <div><label className="label">Title *</label><input required className="input" placeholder="Full Stack Developer Intern" value={form.title} onChange={(e) => set('title', e.target.value)} /></div>
          <div><label className="label">Description *</label><textarea required className="input h-28 resize-none" placeholder="Describe the internship role…" value={form.description} onChange={(e) => set('description', e.target.value)} /></div>
          <div><label className="label">Requirements</label><textarea className="input h-24 resize-none" placeholder="What qualifications are needed?…" value={form.requirements} onChange={(e) => set('requirements', e.target.value)} /></div>
          <div><label className="label">Responsibilities</label><textarea className="input h-24 resize-none" placeholder="What will the intern do?…" value={form.responsibilities} onChange={(e) => set('responsibilities', e.target.value)} /></div>
        </div>

        <div className="card p-5 space-y-4">
          <h2 className="section-title">Position Details</h2>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="label">Duration (weeks) *</label>
              <input required type="number" min={1} className="input" value={form.duration} onChange={(e) => set('duration', e.target.value)} />
            </div>
            <div>
              <label className="label">Vacancies</label>
              <input type="number" min={1} className="input" value={form.vacancies} onChange={(e) => set('vacancies', e.target.value)} />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="label">Work Mode</label>
              <select className="input" value={form.mode} onChange={(e) => set('mode', e.target.value)}>
                <option value="ONSITE">Onsite</option>
                <option value="REMOTE">Remote</option>
                <option value="HYBRID">Hybrid</option>
              </select>
            </div>
            <div>
              <label className="label">Location</label>
              <input className="input" placeholder="Kathmandu, Nepal" value={form.location} onChange={(e) => set('location', e.target.value)} />
            </div>
          </div>
          <div className="flex items-center gap-3">
            <input type="checkbox" id="isPaid" checked={form.isPaid} onChange={(e) => set('isPaid', e.target.checked)} className="w-4 h-4 text-indigo-600 rounded" />
            <label htmlFor="isPaid" className="text-sm text-gray-700 font-medium">This internship offers a stipend</label>
          </div>
          {form.isPaid && (
            <div>
              <label className="label">Monthly Stipend (NPR)</label>
              <input type="number" min={0} className="input" placeholder="15000" value={form.stipend} onChange={(e) => set('stipend', e.target.value)} />
            </div>
          )}
        </div>

        <div className="card p-5 space-y-4">
          <h2 className="section-title">Dates</h2>
          <div className="grid grid-cols-3 gap-3">
            <div><label className="label">Start Date</label><input type="date" className="input" value={form.startDate} onChange={(e) => set('startDate', e.target.value)} /></div>
            <div><label className="label">End Date</label><input type="date" className="input" value={form.endDate} onChange={(e) => set('endDate', e.target.value)} /></div>
            <div><label className="label">Application Deadline</label><input type="date" className="input" value={form.deadline} onChange={(e) => set('deadline', e.target.value)} /></div>
          </div>
        </div>

        <div className="card p-5 space-y-3">
          <h2 className="section-title">Required Skills</h2>
          <div className="flex flex-wrap gap-2">
            {allSkills.map((skill) => (
              <button
                key={skill.id}
                type="button"
                onClick={() => toggleSkill(skill.id)}
                className={`badge text-xs px-3 py-1.5 cursor-pointer transition-colors ${
                  selectedSkills.includes(skill.id)
                    ? 'bg-indigo-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {selectedSkills.includes(skill.id) && <X size={11} className="mr-1" />}
                {skill.name}
              </button>
            ))}
          </div>
        </div>

        <div className="flex gap-3">
          <button type="submit" disabled={saving} className="btn-primary flex-1 gap-2">
            <Save size={16} /> {saving ? 'Saving…' : isEdit ? 'Update Internship' : 'Post Internship'}
          </button>
          <button type="button" onClick={() => navigate('/company/internships')} className="btn-secondary">Cancel</button>
        </div>
      </form>
    </div>
  )
}
