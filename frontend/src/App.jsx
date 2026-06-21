import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import Layout from './components/Layout'

import LandingPage from './pages/LandingPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import NotificationsPage from './pages/NotificationsPage'

import StudentDashboard from './pages/student/StudentDashboard'
import StudentProfile from './pages/student/StudentProfile'
import StudentApplications from './pages/student/StudentApplications'
import InternshipSearch from './pages/student/InternshipSearch'
import InternshipDetail from './pages/student/InternshipDetail'
import StudentProgress from './pages/student/StudentProgress'

import CompanyDashboard from './pages/company/CompanyDashboard'
import CompanyProfile from './pages/company/CompanyProfile'
import PostInternship from './pages/company/PostInternship'
import CompanyInternships from './pages/company/CompanyInternships'
import CompanyApplications from './pages/company/CompanyApplications'
import CompanyEnrollments from './pages/company/CompanyEnrollments'

import SupervisorDashboard from './pages/supervisor/SupervisorDashboard'
import SupervisorStudents from './pages/supervisor/SupervisorStudents'
import SupervisorProfile from './pages/supervisor/SupervisorProfile'

import AdminDashboard from './pages/admin/AdminDashboard'
import AdminUsers from './pages/admin/AdminUsers'
import AdminCompanies from './pages/admin/AdminCompanies'
import AdminEnrollments from './pages/admin/AdminEnrollments'

function RoleRedirect() {
  const { user } = useAuth()
  if (!user) return <Navigate to="/" replace />
  const map = {
    STUDENT: '/student/dashboard',
    COMPANY: '/company/dashboard',
    INTERNAL_SUPERVISOR: '/supervisor/dashboard',
    EXTERNAL_SUPERVISOR: '/supervisor/dashboard',
    ADMIN: '/admin/dashboard',
  }
  return <Navigate to={map[user.role] || '/'} replace />
}

function WithLayout({ children }) {
  return <Layout>{children}</Layout>
}

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        {/* Public */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/internships/:id" element={<InternshipDetail />} />

        {/* Role redirect */}
        <Route path="/dashboard" element={<ProtectedRoute />}>
          <Route index element={<RoleRedirect />} />
        </Route>

        {/* Notifications (all roles) */}
        <Route element={<ProtectedRoute />}>
          <Route path="/notifications" element={<WithLayout><NotificationsPage /></WithLayout>} />
        </Route>

        {/* Student */}
        <Route element={<ProtectedRoute roles={['STUDENT']} />}>
          <Route path="/student/dashboard" element={<WithLayout><StudentDashboard /></WithLayout>} />
          <Route path="/student/profile" element={<WithLayout><StudentProfile /></WithLayout>} />
          <Route path="/student/applications" element={<WithLayout><StudentApplications /></WithLayout>} />
          <Route path="/student/internships" element={<WithLayout><InternshipSearch /></WithLayout>} />
          <Route path="/student/progress" element={<WithLayout><StudentProgress /></WithLayout>} />
        </Route>

        {/* Company */}
        <Route element={<ProtectedRoute roles={['COMPANY']} />}>
          <Route path="/company/dashboard" element={<WithLayout><CompanyDashboard /></WithLayout>} />
          <Route path="/company/profile" element={<WithLayout><CompanyProfile /></WithLayout>} />
          <Route path="/company/post" element={<WithLayout><PostInternship /></WithLayout>} />
          <Route path="/company/post/:id" element={<WithLayout><PostInternship /></WithLayout>} />
          <Route path="/company/internships" element={<WithLayout><CompanyInternships /></WithLayout>} />
          <Route path="/company/applications" element={<WithLayout><CompanyApplications /></WithLayout>} />
          <Route path="/company/enrollments" element={<WithLayout><CompanyEnrollments /></WithLayout>} />
        </Route>

        {/* Supervisor */}
        <Route element={<ProtectedRoute roles={['INTERNAL_SUPERVISOR', 'EXTERNAL_SUPERVISOR']} />}>
          <Route path="/supervisor/dashboard" element={<WithLayout><SupervisorDashboard /></WithLayout>} />
          <Route path="/supervisor/students" element={<WithLayout><SupervisorStudents /></WithLayout>} />
          <Route path="/supervisor/profile" element={<WithLayout><SupervisorProfile /></WithLayout>} />
        </Route>

        {/* Admin */}
        <Route element={<ProtectedRoute roles={['ADMIN']} />}>
          <Route path="/admin/dashboard" element={<WithLayout><AdminDashboard /></WithLayout>} />
          <Route path="/admin/users" element={<WithLayout><AdminUsers /></WithLayout>} />
          <Route path="/admin/companies" element={<WithLayout><AdminCompanies /></WithLayout>} />
          <Route path="/admin/enrollments" element={<WithLayout><AdminEnrollments /></WithLayout>} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  )
}
