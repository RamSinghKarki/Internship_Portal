import { useState, useEffect } from 'react'
import { companyAPI, progressAPI, evaluationAPI } from '../../services/api'
import { Users, BookOpen, Star, ChevronDown, ChevronUp, ClipboardList } from 'lucide-react'

const statusColors = { ACTIVE: 'badge-green', COMPLETED: 'badge-blue', TERMINATED: 'badge-red' }

export default function CompanyEnrollments() {
  const [enrollments, setEnrollments] = useState([])
  const [loading, setLoading] = useState(true)
  const [expanded, setExpanded] = useState(null)
  const [logs, setLogs] = useState({})
  const [showEval, setShowEval] = useState(null)
  const [evalForm, setEvalForm] = useState({ technicalScore: '', communicationScore: '', teamworkScore: '', punctualityScore: '', overallScore: '', feedback: '', grade: '', isRecommended: true })
  const [savingEval, setSavingEval] = useState(false)

  useEffect(() => {
    companyAPI.getEnrollments().then(({ data }) => setEnrollments(data)).finally(() => setLoading(false))
  }, [])

  const loadLogs = async (enrollmentId) => {
    if (logs[enrollmentId]) return
    try {
      const { data } = await progressAPI.getEnrollmentLogs(enrollmentId)
      setLogs((l) => ({ ...l, [enrollmentId]: data }))
    } catch {}
  }

  const toggleExpand = (id) => {
    const next = expanded === id ? null : id
    setExpanded(next)
    if (next) loadLogs(next)
  }

  const saveEval = async (enrollmentId) => {
    setSavingEval(true)
    try {
      await evaluationAPI.createOrUpdate({ ...evalForm, enrollmentId })
      setShowEval(null)
      setEnrollments((e) => e.map((en) => en.id === enrollmentId ? { ...en, evaluation: evalForm } : en))
    } catch { alert('Failed to save evaluation') } finally { setSavingEval(false) }
  }

  if (loading) return <div className="flex justify-center py-16"><div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" /></div>

  return (
    <div className="space-y-5">
      <h1 className="page-title">Active Interns</h1>

      {enrollments.length === 0 ? (
        <div className="card p-12 text-center text-gray-400">
          <Users size={32} className="mx-auto mb-3 opacity-50" />
          <p>No enrolled interns yet.</p>
        </div>
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
                  <p className="text-xs text-gray-500">{en.internship?.title} · {en.student?.college?.name || '—'}</p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-400">{en._count?.progressLogs} logs</span>
                  <span className={statusColors[en.status] || 'badge-gray'}>{en.status}</span>
                  {expanded === en.id ? <ChevronUp size={16} className="text-gray-400" /> : <ChevronDown size={16} className="text-gray-400" />}
                </div>
              </button>

              {expanded === en.id && (
                <div className="border-t border-gray-100 p-4 space-y-4">
                  <div className="grid sm:grid-cols-3 gap-3 text-sm">
                    <div><p className="text-gray-500">Started</p><p className="font-medium">{new Date(en.startDate).toLocaleDateString()}</p></div>
                    <div><p className="text-gray-500">Internal Supervisor</p><p className="font-medium">{en.internalSupervisor ? `${en.internalSupervisor.firstName} ${en.internalSupervisor.lastName}` : 'Not assigned'}</p></div>
                    <div><p className="text-gray-500">External Supervisor</p><p className="font-medium">{en.externalSupervisor ? `${en.externalSupervisor.firstName} ${en.externalSupervisor.lastName}` : 'Not assigned'}</p></div>
                  </div>

                  {logs[en.id] && (
                    <div>
                      <p className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-1.5"><BookOpen size={15} /> Progress Logs ({logs[en.id].length})</p>
                      <div className="space-y-2 max-h-48 overflow-y-auto">
                        {logs[en.id].map((log) => (
                          <div key={log.id} className="flex items-center gap-3 p-2.5 bg-gray-50 rounded-lg text-sm">
                            <span className="w-8 h-8 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center text-xs font-bold">W{log.weekNumber}</span>
                            <div className="flex-1 min-w-0">
                              <p className="font-medium text-gray-800 truncate">{log.title || `Week ${log.weekNumber}`}</p>
                              <p className="text-xs text-gray-400">{log.hoursWorked && `${log.hoursWorked}h · `}{log.status}</p>
                            </div>
                            {log.rating && <span className="flex items-center gap-1 text-xs text-amber-600"><Star size={12} className="fill-amber-400" />{log.rating}</span>}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {en.evaluation ? (
                    <div className="p-3 bg-emerald-50 border border-emerald-100 rounded-lg">
                      <p className="text-sm font-medium text-emerald-800">Evaluation Submitted</p>
                      <p className="text-sm text-emerald-700">Overall: {en.evaluation.overallScore}/10 · Grade: {en.evaluation.grade}</p>
                    </div>
                  ) : (
                    <button onClick={() => setShowEval(en.id)} className="btn-primary btn-sm gap-1.5">
                      <ClipboardList size={14} /> Add Evaluation
                    </button>
                  )}

                  {showEval === en.id && (
                    <div className="border border-gray-200 rounded-lg p-4 space-y-3">
                      <h3 className="font-medium text-gray-900">Final Evaluation</h3>
                      <div className="grid grid-cols-2 gap-3">
                        {['technicalScore', 'communicationScore', 'teamworkScore', 'punctualityScore', 'overallScore'].map((k) => (
                          <div key={k}>
                            <label className="label capitalize">{k.replace('Score', '').replace(/([A-Z])/g, ' $1')}</label>
                            <input type="number" min={0} max={10} step={0.5} className="input" placeholder="0–10" value={evalForm[k]} onChange={(e) => setEvalForm((f) => ({ ...f, [k]: e.target.value }))} />
                          </div>
                        ))}
                        <div>
                          <label className="label">Grade</label>
                          <select className="input" value={evalForm.grade} onChange={(e) => setEvalForm((f) => ({ ...f, grade: e.target.value }))}>
                            <option value="">—</option>
                            {['A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'F'].map((g) => <option key={g}>{g}</option>)}
                          </select>
                        </div>
                      </div>
                      <div><label className="label">Feedback</label><textarea className="input h-20 resize-none" value={evalForm.feedback} onChange={(e) => setEvalForm((f) => ({ ...f, feedback: e.target.value }))} /></div>
                      <label className="flex items-center gap-2 text-sm">
                        <input type="checkbox" checked={evalForm.isRecommended} onChange={(e) => setEvalForm((f) => ({ ...f, isRecommended: e.target.checked }))} className="w-4 h-4 text-indigo-600 rounded" />
                        Recommend for future internships
                      </label>
                      <div className="flex gap-2">
                        <button onClick={() => saveEval(en.id)} disabled={savingEval} className="btn-primary btn-sm">{savingEval ? 'Saving…' : 'Save Evaluation'}</button>
                        <button onClick={() => setShowEval(null)} className="btn-secondary btn-sm">Cancel</button>
                      </div>
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
