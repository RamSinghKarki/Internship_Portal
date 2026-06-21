import { useState, useEffect } from 'react'
import { notificationAPI } from '../services/api'
import { Bell, CheckCheck, Trash2, AlertCircle } from 'lucide-react'

const typeColors = {
  APPLICATION_UPDATE: 'bg-blue-100 text-blue-600',
  SUPERVISOR_FEEDBACK: 'bg-purple-100 text-purple-600',
  DEADLINE_REMINDER: 'bg-amber-100 text-amber-600',
  INTERVIEW_SCHEDULED: 'bg-emerald-100 text-emerald-600',
  SYSTEM: 'bg-gray-100 text-gray-600',
  GENERAL: 'bg-gray-100 text-gray-600',
}

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    notificationAPI.getAll().then(({ data }) => setNotifications(data)).finally(() => setLoading(false))
  }, [])

  const markRead = async (id) => {
    await notificationAPI.markRead(id)
    setNotifications((n) => n.map((x) => x.id === id ? { ...x, isRead: true } : x))
  }

  const markAllRead = async () => {
    await notificationAPI.markAllRead()
    setNotifications((n) => n.map((x) => ({ ...x, isRead: true })))
  }

  const remove = async (id) => {
    await notificationAPI.delete(id)
    setNotifications((n) => n.filter((x) => x.id !== id))
  }

  const unread = notifications.filter((n) => !n.isRead).length

  if (loading) return <div className="flex justify-center py-16"><div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" /></div>

  return (
    <div className="max-w-2xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="page-title">Notifications</h1>
          {unread > 0 && <p className="text-sm text-gray-500 mt-1">{unread} unread</p>}
        </div>
        {unread > 0 && (
          <button onClick={markAllRead} className="btn-secondary btn-sm gap-1.5">
            <CheckCheck size={15} /> Mark all read
          </button>
        )}
      </div>

      {notifications.length === 0 ? (
        <div className="card p-12 text-center text-gray-400">
          <Bell size={32} className="mx-auto mb-3 opacity-50" />
          <p>No notifications yet</p>
        </div>
      ) : (
        <div className="space-y-2">
          {notifications.map((n) => (
            <div key={n.id} className={`card p-4 flex items-start gap-4 transition-colors ${n.isRead ? 'opacity-70' : ''}`}>
              <div className={`w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0 ${typeColors[n.type] || typeColors.GENERAL}`}>
                <AlertCircle size={16} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-2">
                  <p className={`text-sm font-medium ${n.isRead ? 'text-gray-600' : 'text-gray-900'}`}>{n.title}</p>
                  {!n.isRead && <span className="w-2 h-2 bg-indigo-500 rounded-full flex-shrink-0 mt-1.5" />}
                </div>
                <p className="text-sm text-gray-500 mt-0.5">{n.message}</p>
                <p className="text-xs text-gray-400 mt-1">{new Date(n.createdAt).toLocaleString()}</p>
              </div>
              <div className="flex items-center gap-1 flex-shrink-0">
                {!n.isRead && (
                  <button onClick={() => markRead(n.id)} className="p-1.5 hover:bg-gray-100 rounded text-gray-400 hover:text-indigo-600" title="Mark read">
                    <CheckCheck size={14} />
                  </button>
                )}
                <button onClick={() => remove(n.id)} className="p-1.5 hover:bg-red-50 rounded text-gray-400 hover:text-red-600" title="Delete">
                  <Trash2 size={14} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
