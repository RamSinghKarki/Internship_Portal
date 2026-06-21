import { useState, useEffect } from 'react'
import { supervisorAPI } from '../../services/api'
import { Save } from 'lucide-react'

export default function SupervisorProfile() {
  const [profile, setProfile] = useState(null)
  const [form, setForm] = useState({})
  const [saving, setSaving] = useState(false)
  const [msg, setMsg] = useState('')

  useEffect(() => {
    supervisorAPI.getProfile().then(({ data }) => {
      setProfile(data)
      setForm({ firstName: data.firstName || '', lastName: data.lastName || '', phone: data.phone || '', expertise: data.expertise || '' })
    })
  }, [])

  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }))

  const handleSave = async (e) => {
    e.preventDefault()
    setSaving(true)
    setMsg('')
    try {
      await supervisorAPI.updateProfile(form)
      setMsg('Profile updated successfully!')
    } catch { setMsg('Failed to save.') } finally { setSaving(false) }
  }

  if (!profile) return <div className="flex justify-center py-16"><div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" /></div>

  return (
    <div className="max-w-lg mx-auto space-y-5">
      <h1 className="page-title">My Profile</h1>

      {msg && <div className={`p-3 rounded-lg text-sm ${msg.includes('success') ? 'bg-emerald-50 border border-emerald-200 text-emerald-700' : 'bg-red-50 border border-red-200 text-red-700'}`}>{msg}</div>}

      <div className="card p-5 flex items-center gap-3">
        <div className="w-14 h-14 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-700 font-bold text-xl">
          {(profile.firstName || 'S')[0]}
        </div>
        <div>
          <p className="font-semibold text-gray-900">{profile.firstName} {profile.lastName}</p>
          <p className="text-sm text-gray-500">{profile.user?.email}</p>
          <span className={`badge mt-1 ${profile.type === 'INTERNAL' ? 'badge-blue' : 'badge-purple'}`}>{profile.type} Supervisor</span>
        </div>
      </div>

      <form onSubmit={handleSave} className="card p-5 space-y-4">
        <h2 className="section-title">Personal Information</h2>
        <div className="grid grid-cols-2 gap-3">
          <div><label className="label">First Name</label><input className="input" value={form.firstName} onChange={(e) => set('firstName', e.target.value)} /></div>
          <div><label className="label">Last Name</label><input className="input" value={form.lastName} onChange={(e) => set('lastName', e.target.value)} /></div>
        </div>
        <div><label className="label">Phone</label><input className="input" placeholder="9841XXXXXX" value={form.phone} onChange={(e) => set('phone', e.target.value)} /></div>
        <div><label className="label">Area of Expertise</label><input className="input" placeholder="Software Engineering, Finance…" value={form.expertise} onChange={(e) => set('expertise', e.target.value)} /></div>
        {profile.college && <div className="text-sm text-gray-500">College: <span className="font-medium text-gray-700">{profile.college.name}</span></div>}
        {profile.company && <div className="text-sm text-gray-500">Company: <span className="font-medium text-gray-700">{profile.company.name}</span></div>}
        <button type="submit" disabled={saving} className="btn-primary w-full gap-2"><Save size={16} /> {saving ? 'Saving…' : 'Save'}</button>
      </form>
    </div>
  )
}
