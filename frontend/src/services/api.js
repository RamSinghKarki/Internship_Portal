import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  getMe: () => api.get('/auth/me'),
  changePassword: (data) => api.put('/auth/change-password', data),
}

export const internshipAPI = {
  getAll: (params) => api.get('/internships', { params }),
  getById: (id) => api.get(`/internships/${id}`),
  getMy: (params) => api.get('/internships/my', { params }),
  create: (data) => api.post('/internships', data),
  update: (id, data) => api.put(`/internships/${id}`, data),
  delete: (id) => api.delete(`/internships/${id}`),
}

export const applicationAPI = {
  apply: (data) => api.post('/applications', data),
  getStudentApps: (params) => api.get('/applications/student', { params }),
  getCompanyApps: (params) => api.get('/applications/company', { params }),
  updateStatus: (id, data) => api.put(`/applications/${id}/status`, data),
  withdraw: (id) => api.put(`/applications/${id}/withdraw`),
  scheduleInterview: (id, data) => api.post(`/applications/${id}/interview`, data),
}

export const studentAPI = {
  getProfile: () => api.get('/students/profile'),
  updateProfile: (data) => api.put('/students/profile', data),
  uploadAvatar: (file) => {
    const fd = new FormData(); fd.append('avatar', file)
    return api.post('/students/avatar', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
  },
  getDocuments: () => api.get('/students/documents'),
  uploadDocument: (file, type, name) => {
    const fd = new FormData(); fd.append('document', file); fd.append('type', type); fd.append('name', name)
    return api.post('/students/documents', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
  },
  deleteDocument: (id) => api.delete(`/students/documents/${id}`),
  getEnrollments: () => api.get('/students/enrollments'),
  getDashboard: () => api.get('/students/dashboard'),
}

export const companyAPI = {
  getProfile: () => api.get('/companies/profile'),
  updateProfile: (data) => api.put('/companies/profile', data),
  uploadLogo: (file) => {
    const fd = new FormData(); fd.append('logo', file)
    return api.post('/companies/logo', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
  },
  getDashboard: () => api.get('/companies/dashboard'),
  getEnrollments: (params) => api.get('/companies/enrollments', { params }),
  assignSupervisor: (enrollmentId, data) => api.put(`/companies/enrollments/${enrollmentId}/supervisor`, data),
}

export const progressAPI = {
  submit: (data) => api.post('/progress', data),
  getMyLogs: (params) => api.get('/progress/my', { params }),
  getEnrollmentLogs: (enrollmentId) => api.get(`/progress/enrollment/${enrollmentId}`),
  review: (id, data) => api.put(`/progress/${id}/review`, data),
}

export const evaluationAPI = {
  createOrUpdate: (data) => api.post('/evaluations', data),
  getByEnrollment: (enrollmentId) => api.get(`/evaluations/enrollment/${enrollmentId}`),
}

export const supervisorAPI = {
  getProfile: () => api.get('/supervisors/profile'),
  updateProfile: (data) => api.put('/supervisors/profile', data),
  getEnrollments: (params) => api.get('/supervisors/enrollments', { params }),
  getDashboard: () => api.get('/supervisors/dashboard'),
}

export const adminAPI = {
  getStats: () => api.get('/admin/stats'),
  getUsers: (params) => api.get('/admin/users', { params }),
  updateUser: (id, data) => api.put(`/admin/users/${id}`, data),
  getCompanies: (params) => api.get('/admin/companies', { params }),
  verifyCompany: (id, data) => api.put(`/admin/companies/${id}/verify`, data),
  getUniversities: () => api.get('/admin/universities'),
  createUniversity: (data) => api.post('/admin/universities', data),
  getColleges: () => api.get('/admin/colleges'),
  createCollege: (data) => api.post('/admin/colleges', data),
  getEnrollments: (params) => api.get('/admin/enrollments', { params }),
  assignSupervisor: (enrollmentId, data) => api.put(`/admin/enrollments/${enrollmentId}/supervisor`, data),
  getInternalSupervisors: () => api.get('/admin/supervisors/internal'),
}

export const notificationAPI = {
  getAll: (params) => api.get('/notifications', { params }),
  getUnreadCount: () => api.get('/notifications/unread-count'),
  markRead: (id) => api.put(`/notifications/${id}/read`),
  markAllRead: () => api.put('/notifications/read-all'),
  delete: (id) => api.delete(`/notifications/${id}`),
}

export const skillAPI = {
  getAll: (params) => api.get('/skills', { params }),
  create: (data) => api.post('/skills', data),
  update: (id, data) => api.put(`/skills/${id}`, data),
  delete: (id) => api.delete(`/skills/${id}`),
}

export default api
