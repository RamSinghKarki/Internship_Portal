import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Eye, EyeOff, LogIn } from 'lucide-react'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', password: '' })
  const [showPw, setShowPw] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const roleRoutes = {
    STUDENT: '/student/dashboard',
    COMPANY: '/company/dashboard',
    INTERNAL_SUPERVISOR: '/supervisor/dashboard',
    EXTERNAL_SUPERVISOR: '/supervisor/dashboard',
    ADMIN: '/admin/dashboard',
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const user = await login(form.email, form.password)
      navigate(roleRoutes[user.role] || '/')
    } catch (err) {
      setError(err.response?.data?.error || 'Login failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const fillDemo = (email, password) => setForm({ email, password })

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center px-4 py-12">
      <Link to="/" className="flex items-center gap-2 mb-8">
        <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center text-white font-bold text-sm">IP</div>
        <span className="font-semibold text-gray-900 text-lg">InternPortal</span>
      </Link>

      <div className="card p-8 w-full max-w-sm">
        <h1 className="text-xl font-bold text-gray-900 mb-1">Welcome back</h1>
        <p className="text-sm text-gray-500 mb-6">Sign in to your account</p>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">{error}</div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="label">Email</label>
            <input
              type="email"
              className="input"
              placeholder="you@example.com"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              required
            />
          </div>
          <div>
            <label className="label">Password</label>
            <div className="relative">
              <input
                type={showPw ? 'text' : 'password'}
                className="input pr-10"
                placeholder="••••••••"
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                required
              />
              <button type="button" onClick={() => setShowPw(!showPw)} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>
          <button type="submit" disabled={loading} className="btn-primary w-full">
            <LogIn size={16} /> {loading ? 'Signing in…' : 'Sign in'}
          </button>
        </form>

        <p className="text-center text-sm text-gray-500 mt-5">
          No account? <Link to="/register" className="text-indigo-600 font-medium hover:text-indigo-700">Register</Link>
        </p>

        {/* Demo credentials */}
        <div className="mt-6 p-3 bg-gray-50 rounded-lg border border-gray-200">
          <p className="text-xs font-medium text-gray-600 mb-2">Demo accounts:</p>
          <div className="space-y-1">
            {[
              ['Admin', 'admin@internportal.com', 'Admin@123'],
              ['Company', 'hr@techcorp.com', 'Company@123'],
              ['Student', 'student@example.com', 'Student@123'],
              ['Supervisor', 'supervisor@kcm.edu.np', 'Supervisor@123'],
            ].map(([label, email, pw]) => (
              <button key={label} type="button" onClick={() => fillDemo(email, pw)}
                className="w-full text-left text-xs px-2 py-1 hover:bg-indigo-50 rounded text-gray-600 hover:text-indigo-700 transition-colors">
                <span className="font-medium">{label}:</span> {email}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
