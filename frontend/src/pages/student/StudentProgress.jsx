import { useState, useEffect } from 'react'
import { studentAPI, progressAPI } from '../../services/api'
import { BookOpen, Plus, Star, Clock, ChevronDown, ChevronUp } from 'lucide-react'

export default function StudentProgress() {
  const [enrollments, setEnrollments] = useState([])
  const [logs, setLogs] = useState([])
  const [selectedEnrollment, setSelectedEnrollment] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [expandedLog, setExpandedLog] = useState(null)
  const [form, setForm] = useState({ weekNumber: 1, title: '', description: '', tasksCompleted: '', challenges: '', nextWeekPlan: '', hoursWorked: '' })
  const [msg, setMsg] = useState('')

  useEffect(() => {
    studentAPI.getEnrollments().then(({ data }) => {
      setEnrollments(data)
      const active = data.find((e) => e.status === 'ACTIVE') || data[0]
      if (active) setSelectedEnrollment(active)
    }).finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (!selectedEnrollment) return
    progressAPI.getEnrollmentLogs(selectedEnrollment.id).then(({ data }) => {
      setLogs(data)
      const maxWeek = data.length > 0 ? Math.max(...data.map((l) => l.weekNumber)) : 0
      setForm((f) => ({ ...f, weekNumber: maxWeek + 1 }))
    })
  }, [selectedEnrollment])

  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    setMsg('')
    try {
      await progressAPI.submit({ ...form, enrollmentId: selectedEnrollment.id })
      setMsg('Progress log submitted!')
      setShowForm(false)
      const { data } = await progressAPI.getEnrollmentLogs(selectedEnrollment.id)
      setLogs(data)
    } catch (err) {
      setMsg(err.response?.data?.error || 'Failed to submit')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) return <div className="flex justify-center py-16"><div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" /></div>

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="page-title">Progress Logs</h1>
        {selectedEnrollment?.status === 'ACTIVE' && (
          <button onClick={() => setShowForm(!showForm)} className="btn-primary btn-sm gap-1.5">
            <Plus size={15} /> New Log
          </button>
        )}
      </div>

      {enrollments.length === 0 ? (
        <div className="card p-12 text-center text-gray-400">
          <BookOpen size={32} className="mx-auto mb-3 opacity-50" />
          <p>No active internships yet.</p>
        </div>
      ) : (
        <>
          {enrollments.length > 1 && (
            <select className="input max-w-xs" value={selectedEnrollment?.id || ''} onChange={(e) => setSelectedEnrollment(enrollments.find((en) => en.id === e.target.value))}>
              {enrollments.map((en) => (
                <option key={en.id} value={en.id}>{en.internship?.title} – {en.status}</option>
              ))}
            </select>
          )}

          {msg && <div className={`p-3 rounded-lg text-sm ${msg.includes('submitted') ? 'bg-emerald-50 border border-emerald-200 text-emerald-700' : 'bg-red-50 border border-red-200 text-red-700'}`}>{msg}</div>}

          {showForm && (
            <div className="card p-5">
              <h2 className="section-title mb-4">Week {form.weekNumber} Progress Log</h2>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-2 gap-3">
                  <div><label className="label">Week #</label><input type="number" min={1} className="input" value={form.weekNumber} onChange={(e) => set('weekNumber', e.target.value)} required /></div>
                  <div><label className="label">Hours Worked</label><input type="number" min={0} className="input" value={form.hoursWorked} onChange={(e) => set('hoursWorked', e.target.value)} /></div>
                </div>
                <div><label className="label">Log Title</label><input className="input" placeholder="Week summary…" value={form.title} onChange={(e) => set('title', e.target.value)} /></div>
                <div><label className="label">Description *</label><textarea required className="input h-24 resize-none" placeholder="Describe what you did this week…" value={form.description} onChange={(e) => set('description', e.target.value)} /></div>
                <div><label className="label">Tasks Completed</label><textarea className="input h-20 resize-none" placeholder="List tasks completed…" value={form.tasksCompleted} onChange={(e) => set('tasksCompleted', e.target.value)} /></div>
                <div><label className="label">Challenges Faced</label><textarea className="input h-20 resize-none" placeholder="What challenges did you face?…" value={form.challenges} onChange={(e) => set('challenges', e.target.value)} /></div>
                <div><label className="label">Next Week Plan</label><textarea className="input h-20 resize-none" placeholder="Plan for next week…" value={form.nextWeekPlan} onChange={(e) => set('nextWeekPlan', e.target.value)} /></div>
                <div className="flex gap-2">
                  <button type="submit" disabled={submitting} className="btn-primary">{submitting ? 'Submitting…' : 'Submit Log'}</button>
                  <button type="button" onClick={() => setShowForm(false)} className="btn-secondary">Cancel</button>
                </div>
              </form>
            </div>
          )}

          <div className="space-y-3">
            {logs.length === 0 ? (
              <div className="card p-8 text-center text-gray-400 text-sm">No progress logs yet. Submit your first weekly log!</div>
            ) : (
              logs.map((log) => (
                <div key={log.id} className="card overflow-hidden">
                  <button className="w-full flex items-center gap-4 p-4 text-left hover:bg-gray-50 transition-colors" onClick={() => setExpandedLog(expandedLog === log.id ? null : log.id)}>
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0 ${log.status === 'REVIEWED' ? 'bg-emerald-100 text-emerald-700' : 'bg-indigo-100 text-indigo-700'}`}>
                      W{log.weekNumber}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <p className="font-medium text-gray-900 truncate">{log.title || `Week ${log.weekNumber} Log`}</p>
                        <span className={`badge flex-shrink-0 ${log.status === 'REVIEWED' ? 'badge-green' : 'badge-yellow'}`}>{log.status}</span>
                      </div>
                      <div className="flex items-center gap-3 mt-0.5 text-xs text-gray-400">
                        <span>{new Date(log.submittedAt).toLocaleDateString()}</span>
                        {log.hoursWorked && <span className="flex items-center gap-1"><Clock size={11} />{log.hoursWorked}h</span>}
                        {log.rating && <span className="flex items-center gap-1"><Star size={11} className="text-amber-400" />{log.rating}/5</span>}
                      </div>
                    </div>
                    {expandedLog === log.id ? <ChevronUp size={16} className="text-gray-400" /> : <ChevronDown size={16} className="text-gray-400" />}
                  </button>

                  {expandedLog === log.id && (
                    <div className="px-5 pb-5 border-t border-gray-100 space-y-3 pt-4">
                      {log.description && <div><p className="label mb-1">Description</p><p className="text-sm text-gray-600 whitespace-pre-line">{log.description}</p></div>}
                      {log.tasksCompleted && <div><p className="label mb-1">Tasks Completed</p><p className="text-sm text-gray-600 whitespace-pre-line">{log.tasksCompleted}</p></div>}
                      {log.challenges && <div><p className="label mb-1">Challenges</p><p className="text-sm text-gray-600 whitespace-pre-line">{log.challenges}</p></div>}
                      {log.nextWeekPlan && <div><p className="label mb-1">Next Week Plan</p><p className="text-sm text-gray-600 whitespace-pre-line">{log.nextWeekPlan}</p></div>}
                      {log.supervisorFeedback && (
                        <div className="p-3 bg-purple-50 border border-purple-100 rounded-lg">
                          <p className="text-xs font-medium text-purple-700 mb-1">Supervisor Feedback</p>
                          <p className="text-sm text-purple-800">{log.supervisorFeedback}</p>
                          {log.rating && (
                            <div className="flex items-center gap-1 mt-1">
                              {[1,2,3,4,5].map((n) => <Star key={n} size={14} className={n <= log.rating ? 'text-amber-400 fill-amber-400' : 'text-gray-300'} />)}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </>
      )}
    </div>
  )
}
