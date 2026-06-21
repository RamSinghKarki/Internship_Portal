import { useState, useEffect } from 'react'
import { companyAPI } from '../../services/api'
import { Save, Upload, Building2 } from 'lucide-react'

export default function CompanyProfile() {
  const [profile, setProfile] = useState(null)
  const [form, setForm] = useState({})
  const [saving, setSaving] = useState(false)
  const [msg, setMsg] = useState('')

  useEffect(() => {
    companyAPI.getProfile().then(({ data }) => {
      setProfile(data)
      setForm({ name: data.name || '', description: data.description || '', industry: data.industry || '', website: data.website || '', location: data.location || '', size: data.size || '' })
    })
  }, [])

  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }))

  const handleSave = async (e) => {
    e.preventDefault()
    setSaving(true)
    setMsg('')
    try {
      await companyAPI.updateProfile(form)
      setMsg('Profile updated successfully!')
    } catch { setMsg('Failed to save.') } finally { setSaving(false) }
  }

  const handleLogo = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    try {
      const { data } = await companyAPI.uploadLogo(file)
      setProfile((p) => ({ ...p, logoUrl: data.logoUrl }))
    } catch { alert('Failed to upload logo') }
  }

  if (!profile) return <div className="flex justify-center py-16"><div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" /></div>

  return (
    <div className="max-w-2xl mx-auto space-y-5">
      <h1 className="page-title">Company Profile</h1>

      {msg && <div className={`p-3 rounded-lg text-sm ${msg.includes('success') ? 'bg-emerald-50 border border-emerald-200 text-emerald-700' : 'bg-red-50 border border-red-200 text-red-700'}`}>{msg}</div>}

      <div className="card p-5 flex items-center gap-4">
        {profile.logoUrl ? (
          <img src={profile.logoUrl} alt="Logo" className="w-20 h-20 rounded-xl object-cover border border-gray-200" />
        ) : (
          <div className="w-20 h-20 rounded-xl bg-indigo-100 flex items-center justify-center"><Building2 size={32} className="text-indigo-500" /></div>
        )}
        <div>
          <p className="font-medium text-gray-900">{profile.name}</p>
          <p className="text-sm text-gray-500">{profile.user?.email}</p>
          {profile.isVerified ? <span className="badge-green mt-1 inline-block">Verified</span> : <span className="badge-yellow mt-1 inline-block">Pending Verification</span>}
          <label className="btn-secondary btn-sm mt-2 cursor-pointer inline-flex gap-1.5">
            <Upload size={14} /> Upload Logo
            <input type="file" accept="image/*" className="hidden" onChange={handleLogo} />
          </label>
        </div>
      </div>

      <form onSubmit={handleSave} className="space-y-5">
        <div className="card p-5 space-y-4">
          <h2 className="section-title">Company Information</h2>
          <div><label className="label">Company Name</label><input required className="input" value={form.name} onChange={(e) => set('name', e.target.value)} /></div>
          <div><label className="label">Description</label><textarea className="input h-28 resize-none" placeholder="Tell students about your company…" value={form.description} onChange={(e) => set('description', e.target.value)} /></div>
          <div className="grid grid-cols-2 gap-3">
            <div><label className="label">Industry</label><input className="input" placeholder="IT, Finance, Healthcare…" value={form.industry} onChange={(e) => set('industry', e.target.value)} /></div>
            <div>
              <label className="label">Company Size</label>
              <select className="input" value={form.size} onChange={(e) => set('size', e.target.value)}>
                <option value="">Select size</option>
                <option value="1-10">1–10</option>
                <option value="10-50">10–50</option>
                <option value="50-200">50–200</option>
                <option value="200-1000">200–1000</option>
                <option value="1000+">1000+</option>
              </select>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div><label className="label">Website</label><input type="url" className="input" placeholder="https://yourcompany.com" value={form.website} onChange={(e) => set('website', e.target.value)} /></div>
            <div><label className="label">Location</label><input className="input" placeholder="Kathmandu, Nepal" value={form.location} onChange={(e) => set('location', e.target.value)} /></div>
          </div>
        </div>

        <button type="submit" disabled={saving} className="btn-primary w-full gap-2">
          <Save size={16} /> {saving ? 'Saving…' : 'Save Changes'}
        </button>
      </form>
    </div>
  )
}
