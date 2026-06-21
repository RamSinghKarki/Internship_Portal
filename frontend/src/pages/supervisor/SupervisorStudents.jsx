import { useState, useEffect } from 'react'
import { supervisorAPI, progressAPI } from '../../services/api'
import { ChevronDown, ChevronUp, Star, Send } from 'lucide-react'

export default function SupervisorStudents() {
  const [enrollments, setEnrollments] = useState([])
  const [loading, setLoading] = useState(true)
  const [expanded, setExpanded] = useState(null)
  const [logs, setLogs] = useState({})
  const [reviewing, setReviewing] = useState(null)
  const [reviewForm, setReviewForm] = useState({ feedback: '', rating: '' })
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    supervisorAPI.getEnrollments().then(({ data }) => setEnrollments(data)).finally(() => setLoading(false))
  }, [])

  const loadLogs = async (enrollmentId) => {
    if (logs[enrollmentId]) return
    const { data } = await progressAPI.getEnrollmentLogs(enrollmentId)
    setLogs((l) => ({ ...l, [enrollmentId]: data }))
  }

  const toggleExpand = (id) => {
    const next = expanded === id ? null : id
    setExpanded(next)
    if (next) loadLogs(next)
  }

  const submitReview = async (logId) => {
    setSaving(true)
    try {
      await progressAPI.review(logId, { supervisorFeedback: reviewForm.feedback, rating: reviewForm.rating })
      const enrollmentId = Object.keys(logs).find((k) => logs[k].some((l) => l.id === logId))
      if (enrollmentId) {
        setLogs((l) => ({ ...l, [enrollmentId]: l[enrollmentId].map((log) => log.id === logId ? { ...log, status: 'REVIEWED', supervisorFeedback: reviewForm.feedback, rating: reviewForm.rating } : log) }))
      }
      setReviewing(null)
      setReviewForm({ feedback: '', rating: '' })
    } catch { alert('Failed to submit review') } finally { setSaving(false) }
  }

  if (loading) return <div className="flex justify-center py-16"><div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" /></div>

  return (
    <div className="space-y-5">
      <h1 className="page-title">My Students</h1>

      {enrollments.length === 0 ? (
        <div className="card p-12 text-center text-gray-400">No students assigned yet.</div>
      ) : (
        <div className="space-y-3">
          {enrollments.map((en) => (
            <div key={en.id} className="card overflow-hidden">
              <button className="w-full flex items-center gap-4 p-4 text-left hover:bg-gray-50 transition-colors" onClick={() => toggleExpand(en.id)}>
                <div className="w-10 h-10 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-700 font-semibold text-sm flex-shrink-0">
                  {en.student?.firstName?.[0]}{en.student?.lastName?.[0]}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-gray-900">{en.student?.firstName} {en.student?.lastName}</p>
                  <p className="text-xs text-gray-500">{en.internship?.title} · {en.internship?.company?.name}</p>
                  <p className="text-xs text-gray-400 mt-0.5">{en.student?.college?.name} · {en.student?.program?.name}</p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-400">{en._count?.progressLogs} logs</span>
                  {pending(logs[en.id]) > 0 && <span className="badge-yellow">{pending(logs[en.id])} pending</span>}
                  {expanded === en.id ? <ChevronUp size={16} className="text-gray-400" /> : <ChevronDown size={16} className="text-gray-400" />}
                </div>
              </button>

              {expanded === en.id && (
                <div className="border-t border-gray-100 p-4 space-y-3">
                  <div className="grid sm:grid-cols-2 gap-3 text-sm mb-3">
                    <div><p className="text-gray-500">Email</p><p className="font-medium">{en.student?.user?.email}</p></div>
                    <div><p className="text-gray-500">Started</p><p className="font-medium">{new Date(en.startDate).toLocaleDateString()}</p></div>
                  </div>

                  {!logs[en.id] ? (
                    <p className="text-sm text-gray-400">Loading logs…</p>
                  ) : logs[en.id].length === 0 ? (
                    <p className="text-sm text-gray-400">No progress logs submitted yet.</p>
                  ) : (
                    <div className="space-y-2">
                      {logs[en.id].map((log) => (
                        <div key={log.id} className={`border rounded-lg p-3 ${log.status === 'REVIEWED' ? 'border-emerald-200 bg-emerald-50/50' : 'border-amber-200 bg-amber-50/50'}`}>
                          <div className="flex items-center justify-between">
                            <div>
                              <p className="text-sm font-medium text-gray-900">Week {log.weekNumber}: {log.title || 'Progress Log'}</p>
                              <p className="text-xs text-gray-500 mt-0.5">{log.hoursWorked && `${log.hoursWorked}h worked · `}{new Date(log.submittedAt).toLocaleDateString()}</p>
                            </div>
                            <span className={`badge ${log.status === 'REVIEWED' ? 'badge-green' : 'badge-yellow'}`}>{log.status}</span>
                          </div>

                          <p className="text-sm text-gray-700 mt-2">{log.description?.slice(0, 120)}{log.description?.length > 120 ? '…' : ''}</p>

                          {log.supervisorFeedback && (
                            <div className="mt-2 p-2 bg-white rounded border border-emerald-200 text-xs text-gray-600">
                              <span className="font-medium text-emerald-700">Your feedback: </span>{log.supervisorFeedback}
                              {log.rating && <span className="ml-2 text-amber-600">★ {log.rating}/5</span>}
                            </div>
                          )}

                          {log.status === 'SUBMITTED' && (
                            reviewing === log.id ? (
                              <div className="mt-3 space-y-2">
                                <textarea
                                  className="input h-20 resize-none text-sm"
                                  placeholder="Write your feedback…"
                                  value={reviewForm.feedback}
                                  onChange={(e) => setReviewForm((f) => ({ ...f, feedback: e.target.value }))}
                                />
                                <div className="flex items-center gap-3">
                                  <select className="input w-32" value={reviewForm.rating} onChange={(e) => setReviewForm((f) => ({ ...f, rating: e.target.value }))}>
                                    <option value="">Rating</option>
                                    {[5,4,3,2,1].map((n) => <option key={n} value={n}>{n} ★</option>)}
                                  </select>
                                  <button onClick={() => submitReview(log.id)} disabled={saving} className="btn-primary btn-sm gap-1.5">
                                    <Send size={13} /> {saving ? 'Submitting…' : 'Submit'}
                                  </button>
                                  <button onClick={() => setReviewing(null)} className="btn-secondary btn-sm">Cancel</button>
                                </div>
                              </div>
                            ) : (
                              <button onClick={() => { setReviewing(log.id); setReviewForm({ feedback: '', rating: '' }) }} className="mt-2 text-xs text-indigo-600 font-medium hover:text-indigo-700">
                                + Write Review
                              </button>
                            )
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function pending(logs) {
  return logs?.filter((l) => l.status === 'SUBMITTED').length || 0
}
