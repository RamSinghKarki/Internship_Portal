import { Link } from 'react-router-dom'
import { Briefcase, Users, TrendingUp, Shield, ArrowRight, Building2, GraduationCap, Star } from 'lucide-react'

const features = [
  { icon: Briefcase, title: 'Internship Marketplace', desc: 'Browse hundreds of verified internship opportunities across all industries.' },
  { icon: Users, title: 'Dual Supervision', desc: 'Internal college supervisors and external company mentors guide your journey.' },
  { icon: TrendingUp, title: 'Progress Tracking', desc: 'Weekly logs, evaluations, and performance metrics in one place.' },
  { icon: Shield, title: 'Verified Companies', desc: 'All companies are verified by administrators for a safe experience.' },
]

const stats = [
  { value: '500+', label: 'Companies' },
  { value: '2,000+', label: 'Students Placed' },
  { value: '50+', label: 'Colleges' },
  { value: '95%', label: 'Success Rate' },
]

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Navbar */}
      <header className="border-b border-gray-100 sticky top-0 bg-white/95 backdrop-blur z-10">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center text-white font-bold text-sm">IP</div>
            <span className="font-semibold text-gray-900 text-lg">InternPortal</span>
          </div>
          <div className="flex items-center gap-3">
            <Link to="/login" className="btn-secondary btn-sm hidden sm:inline-flex">Sign in</Link>
            <Link to="/register" className="btn-primary btn-sm">Get Started</Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="bg-gradient-to-b from-indigo-50 to-white py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <span className="inline-flex items-center gap-2 bg-indigo-100 text-indigo-700 text-sm font-medium px-4 py-1.5 rounded-full mb-6">
            <Star size={14} /> Nepal's #1 Internship Platform
          </span>
          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 leading-tight mb-5">
            Connect Students with<br />
            <span className="text-indigo-600">Real-World Opportunities</span>
          </h1>
          <p className="text-lg text-gray-600 mb-8 max-w-2xl mx-auto">
            An enterprise platform bridging academia and industry — manage internships, track progress, and build careers.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Link to="/register?role=STUDENT" className="btn-primary text-base px-6 py-3">
              Find Internships <ArrowRight size={18} />
            </Link>
            <Link to="/register?role=COMPANY" className="btn-secondary text-base px-6 py-3">
              Hire Interns
            </Link>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-12 border-y border-gray-100">
        <div className="max-w-4xl mx-auto px-4 grid grid-cols-2 sm:grid-cols-4 gap-6">
          {stats.map(({ value, label }) => (
            <div key={label} className="text-center">
              <p className="text-3xl font-bold text-indigo-600">{value}</p>
              <p className="text-sm text-gray-500 mt-1">{label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="py-16 px-4">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-2xl font-bold text-center text-gray-900 mb-2">Everything you need</h2>
          <p className="text-center text-gray-500 mb-10">One platform for students, companies, colleges and administrators.</p>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map(({ icon: Icon, title, desc }) => (
              <div key={title} className="card p-5">
                <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center text-indigo-600 mb-4">
                  <Icon size={20} />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">{title}</h3>
                <p className="text-sm text-gray-500">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Roles */}
      <section className="py-16 px-4 bg-gray-50">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-2xl font-bold text-center text-gray-900 mb-10">Who uses InternPortal?</h2>
          <div className="grid sm:grid-cols-3 gap-6">
            {[
              { icon: GraduationCap, title: 'Students', desc: 'Apply to internships, track progress, and receive evaluations.', role: 'STUDENT', color: 'indigo' },
              { icon: Building2, title: 'Companies', desc: 'Post internships, screen applicants, and manage interns.', role: 'COMPANY', color: 'emerald' },
              { icon: Users, title: 'Supervisors', desc: 'Monitor student progress and provide professional feedback.', role: 'INTERNAL_SUPERVISOR', color: 'amber' },
            ].map(({ icon: Icon, title, desc, role, color }) => (
              <div key={title} className="card p-6 text-center">
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center mx-auto mb-4 bg-${color}-100 text-${color}-600`}>
                  <Icon size={24} />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">{title}</h3>
                <p className="text-sm text-gray-500 mb-4">{desc}</p>
                <Link to={`/register?role=${role}`} className="text-sm text-indigo-600 font-medium hover:text-indigo-700">
                  Sign up as {title} →
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 px-4 bg-indigo-600">
        <div className="max-w-2xl mx-auto text-center text-white">
          <h2 className="text-2xl font-bold mb-4">Ready to get started?</h2>
          <p className="text-indigo-200 mb-8">Join thousands of students and companies on Nepal's leading internship platform.</p>
          <Link to="/register" className="btn bg-white text-indigo-600 hover:bg-indigo-50 text-base px-8 py-3">
            Create Free Account
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 border-t border-gray-100 text-center text-sm text-gray-400">
        <p>© {new Date().getFullYear()} InternPortal. Internship Management & Academic-Industry Collaboration System.</p>
      </footer>
    </div>
  )
}
