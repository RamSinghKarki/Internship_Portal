import { useState, useEffect } from 'react'
import { studentAPI, skillAPI } from '../../services/api'
import { Save, Plus, X, Upload } from 'lucide-react'

export default function StudentProfile() {
  const [profile, setProfile] = useState(null)
  const [allSkills, setAllSkills] = useState([])
  const [saving, setSaving] = useState(false)
  const [msg, setMsg] = useState('')
  const [form, setForm] = useState({})
  const [selectedSkills, setSelectedSkills] = useState([])

  useEffect(() => {
    Promise.all([studentAPI.getProfile(), skillAPI.getAll()]).then(([{ data: p }, { data: s }]) => {
      setProfile(p)
      setAllSkills(s)
      setForm({
        firstName: p.firstName || '', lastName: p.lastName || '', phone: p.phone || '',
        registrationNumber: p.registrationNumber || '', symbolNumber: p.symbolNumber || '',
        semester: p.semester || '', academicYear: p.academicYear || '',
        location: p.location || '', bio: p.bio || '', status: p.status || 'CURRENT',
      })
      setSelectedSkills(p.skills?.map((s) => ({ skillId: s.skill.id, name: s.skill.name, proficiency: s.proficiency })) || [])
    })
  }, [])

  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }))

  const addSkill = (skillId) => {
    const skill = allSkills.find((s) => s.id === skillId)
    if (!skill || selectedSkills.some((s) => s.skillId === skillId)) return
    setSelectedSkills((ss) => [...ss, { skillId, name: skill.name, proficiency: 'BEGINNER' }])
  }

  const removeSkill = (skillId) => setSelectedSkills((ss) => ss.filter((s) => s.skillId !== skillId))

  const handleSave = async (e) => {
    e.preventDefault()
    setSaving(true)
    setMsg('')
    try {
      await studentAPI.updateProfile({ ...form, skills: selectedSkills })
      setMsg('Profile updated successfully!')
    } catch {
      setMsg('Failed to save. Please try again.')
    } finally {
      setSaving(false)
    }
  }

  const handleAvatarUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    try {
      const { data } = await studentAPI.uploadAvatar(file)
      setProfile((p) => ({ ...p, avatarUrl: data.avatarUrl }))
    } catch { alert('Failed to upload avatar') }
  }

  const availableSkills = allSkills.filter((s) => !selectedSkills.some((ss) => ss.skillId === s.id))

  if (!profile) return <div className="flex justify-center py-16"><div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" /></div>

  return (
    <div className="max-w-2xl mx-auto space-y-5">
      <h1 className="page-title">My Profile</h1>

      {msg && <div className={`p-3 rounded-lg text-sm ${msg.includes('success') ? 'bg-emerald-50 border border-emerald-200 text-emerald-700' : 'bg-red-50 border border-red-200 text-red-700'}`}>{msg}</div>}

      {/* Avatar */}
      <div className="card p-5 flex items-center gap-4">
        <div className="relative">
          {profile.avatarUrl ? (
            <img src={profile.avatarUrl} alt="" className="w-20 h-20 rounded-full object-cover border-2 border-gray-200" />
          ) : (
            <div className="w-20 h-20 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-700 text-2xl font-bold">
              {(form.firstName || 'U')[0]}
            </div>
          )}
        </div>
        <div>
          <p className="font-medium text-gray-900">{form.firstName} {form.lastName}</p>
          <p className="text-sm text-gray-500">{profile.user?.email}</p>
          <label className="btn-secondary btn-sm mt-2 cursor-pointer inline-flex gap-1.5">
            <Upload size={14} /> Change Photo
            <input type="file" accept="image/*" className="hidden" onChange={handleAvatarUpload} />
          </label>
        </div>
      </div>

      <form onSubmit={handleSave} className="space-y-5">
        <div className="card p-5 space-y-4">
          <h2 className="section-title">Personal Information</h2>
          <div className="grid grid-cols-2 gap-3">
            <div><label className="label">First Name</label><input className="input" value={form.firstName} onChange={(e) => set('firstName', e.target.value)} /></div>
            <div><label className="label">Last Name</label><input className="input" value={form.lastName} onChange={(e) => set('lastName', e.target.value)} /></div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div><label className="label">Phone</label><input className="input" value={form.phone} onChange={(e) => set('phone', e.target.value)} placeholder="9841XXXXXX" /></div>
            <div><label className="label">Location</label><input className="input" value={form.location} onChange={(e) => set('location', e.target.value)} placeholder="Kathmandu" /></div>
          </div>
          <div><label className="label">Bio</label><textarea className="input h-24 resize-none" value={form.bio} onChange={(e) => set('bio', e.target.value)} placeholder="Tell companies about yourself…" /></div>
        </div>

        <div className="card p-5 space-y-4">
          <h2 className="section-title">Academic Information</h2>
          <div className="grid grid-cols-2 gap-3">
            <div><label className="label">Registration No.</label><input className="input" value={form.registrationNumber} onChange={(e) => set('registrationNumber', e.target.value)} /></div>
            <div><label className="label">Symbol No.</label><input className="input" value={form.symbolNumber} onChange={(e) => set('symbolNumber', e.target.value)} /></div>
          </div>
          <div className="grid grid-cols-3 gap-3">
            <div><label className="label">Semester</label><input type="number" min={1} max={8} className="input" value={form.semester} onChange={(e) => set('semester', e.target.value)} /></div>
            <div><label className="label">Academic Year</label><input className="input" placeholder="2080/81" value={form.academicYear} onChange={(e) => set('academicYear', e.target.value)} /></div>
            <div>
              <label className="label">Status</label>
              <select className="input" value={form.status} onChange={(e) => set('status', e.target.value)}>
                <option value="CURRENT">Current</option>
                <option value="PASSOUT">Passout</option>
              </select>
            </div>
          </div>
        </div>

        <div className="card p-5 space-y-4">
          <h2 className="section-title">Skills</h2>
          <div className="flex gap-2">
            <select className="input" onChange={(e) => { addSkill(e.target.value); e.target.value = '' }} defaultValue="">
              <option value="" disabled>Add a skill…</option>
              {availableSkills.map((s) => <option key={s.id} value={s.id}>{s.name} {s.category ? `(${s.category})` : ''}</option>)}
            </select>
          </div>
          {selectedSkills.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {selectedSkills.map(({ skillId, name, proficiency }) => (
                <div key={skillId} className="flex items-center gap-1.5 bg-indigo-50 text-indigo-700 px-2.5 py-1.5 rounded-lg text-sm">
                  <span>{name}</span>
                  <select
                    value={proficiency || ''}
                    onChange={(e) => setSelectedSkills((ss) => ss.map((s) => s.skillId === skillId ? { ...s, proficiency: e.target.value } : s))}
                    className="text-xs bg-transparent border-none outline-none text-indigo-600 cursor-pointer"
                  >
                    <option value="BEGINNER">Beginner</option>
                    <option value="INTERMEDIATE">Intermediate</option>
                    <option value="ADVANCED">Advanced</option>
                  </select>
                  <button type="button" onClick={() => removeSkill(skillId)} className="text-indigo-400 hover:text-indigo-700">
                    <X size={13} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        <button type="submit" disabled={saving} className="btn-primary w-full gap-2">
          <Save size={16} /> {saving ? 'Saving…' : 'Save Profile'}
        </button>
      </form>
    </div>
  )
}
