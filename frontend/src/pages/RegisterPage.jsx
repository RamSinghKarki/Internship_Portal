import { useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Eye, EyeOff } from 'lucide-react'

const roles = [
  { value: 'STUDENT', label: 'Student' },
  { value: 'COMPANY', label: 'Company / Employer' },
  { value: 'INTERNAL_SUPERVISOR', label: 'Internal Supervisor (College)' },
  { value: 'EXTERNAL_SUPERVISOR', label: 'External Supervisor (Company)' },
]

const roleRoutes = {
  STUDENT: '/student/dashboard',
  COMPANY: '/company/dashboard',
  INTERNAL_SUPERVISOR: '/supervisor/dashboard',
  EXTERNAL_SUPERVISOR: '/supervisor/dashboard',
}

export default function RegisterPage() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [params] = useSearchParams()
  const [form, setForm] = useState({
    email: '', password: '', confirmPassword: '',
    role: params.get('role') || 'STUDENT',
    firstName: '', lastName: '',
    companyName: '', industry: '', location: '',
  })
  const [showPw, setShowPw] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    if (form.password !== form.confirmPassword) { setError('Passwords do not match'); return }
    setLoading(true)
    try {
      const user = await register(form)
      navigate(roleRoutes[user.role] || '/student/dashboard')
    } catch (err) {
      setError(err.response?.data?.error || err.response?.data?.errors?.[0]?.msg || 'Registration failed.')
    } finally {
      setLoading(false)
    }
  }

  const isCompany = form.role === 'COMPANY'

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center px-4 py-12">
      <Link to="/" className="flex items-center gap-2 mb-8">
        <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center text-white font-bold text-sm">IP</div>
        <span className="font-semibold text-gray-900 text-lg">InternPortal</span>
      </Link>

      <div className="card p-8 w-full max-w-md">
        <h1 className="text-xl font-bold text-gray-900 mb-1">Create an account</h1>
        <p className="text-sm text-gray-500 mb-6">Join the internship ecosystem</p>

        {error && <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">{error}</div>}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="label">I am a</label>
            <select className="input" value={form.role} onChange={(e) => set('role', e.target.value)}>
              {roles.map(({ value, label }) => <option key={value} value={value}>{label}</option>)}
            </select>
          </div>

          {isCompany ? (
            <div>
              <label className="label">Company Name</label>
              <input className="input" placeholder="TechCorp Nepal" value={form.companyName} onChange={(e) => set('companyName', e.target.value)} required />
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="label">First Name</label>
                <input className="input" placeholder="Sita" value={form.firstName} onChange={(e) => set('firstName', e.target.value)} required />
              </div>
              <div>
                <label className="label">Last Name</label>
                <input className="input" placeholder="Thapa" value={form.lastName} onChange={(e) => set('lastName', e.target.value)} required />
              </div>
            </div>
          )}

          {isCompany && (
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="label">Industry</label>
                <input className="input" placeholder="IT, Finance…" value={form.industry} onChange={(e) => set('industry', e.target.value)} />
              </div>
              <div>
                <label className="label">Location</label>
                <input className="input" placeholder="Kathmandu" value={form.location} onChange={(e) => set('location', e.target.value)} />
              </div>
            </div>
          )}

          <div>
            <label className="label">Email</label>
            <input type="email" className="input" placeholder="you@example.com" value={form.email} onChange={(e) => set('email', e.target.value)} required />
          </div>

          <div>
            <label className="label">Password</label>
            <div className="relative">
              <input type={showPw ? 'text' : 'password'} className="input pr-10" placeholder="Min. 6 characters" value={form.password} onChange={(e) => set('password', e.target.value)} required minLength={6} />
              <button type="button" onClick={() => setShowPw(!showPw)} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">
                {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          <div>
            <label className="label">Confirm Password</label>
            <input type="password" className="input" placeholder="Repeat password" value={form.confirmPassword} onChange={(e) => set('confirmPassword', e.target.value)} required />
          </div>

          <button type="submit" disabled={loading} className="btn-primary w-full mt-2">
            {loading ? 'Creating account…' : 'Create account'}
          </button>
        </form>

        <p className="text-center text-sm text-gray-500 mt-5">
          Already have an account? <Link to="/login" className="text-indigo-600 font-medium">Sign in</Link>
        </p>
      </div>
    </div>
  )
}
