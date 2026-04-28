import { useState, useEffect } from 'react'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Alert from '../components/ui/Alert'
import Input from '../components/ui/Input'
import ListSkeleton from '../components/ui/ListSkeleton'
import api from '../services/api'
import { t, formatDateShort } from '../i18n'
import { MESSAGES } from '../constants'

export default function Admin() {
  const [users, setUsers] = useState([])
  const [stats, setStats] = useState(null)
  const [settings, setSettings] = useState([])
  const [loading, setLoading] = useState(true)
  const [alert, setAlert] = useState(null)
  const [activeTab, setActiveTab] = useState('users') // 'users', 'stats', 'settings'

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      const [usersRes, statsRes, settingsRes] = await Promise.all([
        api.get('/api/v1/admin/users'),
        api.get('/api/v1/admin/stats'),
        api.get('/api/v1/admin/settings')
      ])
      setUsers(usersRes.data)
      setStats(statsRes.data)
      setSettings(settingsRes.data)
    } catch (error) {
      if (error.response?.status === 403) {
        setAlert({ type: 'error', message: t('admin.accessDenied') })
      } else {
        setAlert({ type: 'error', message: error.response?.data?.detail || t('admin.errorLoading') })
      }
    } finally {
      setLoading(false)
    }
  }

  const handleToggleUserStatus = async (userId, isActive) => {
    try {
      if (isActive) {
        await api.patch(`/api/v1/admin/users/${userId}/deactivate`)
        setAlert({ type: 'success', message: t('admin.users.userDeactivated') })
      } else {
        await api.patch(`/api/v1/admin/users/${userId}/activate`)
        setAlert({ type: 'success', message: t('admin.users.userActivated') })
      }
      fetchData()
    } catch (error) {
      setAlert({ type: 'error', message: t('admin.users.errorUpdate') })
    }
  }

  const handleDeleteUser = async (userId) => {
    if (!window.confirm(t('admin.users.confirmDelete'))) {
      return
    }

    try {
      await api.delete(`/api/v1/admin/users/${userId}`)
      setAlert({ type: 'success', message: t('admin.users.userDeleted') })
      fetchData()
    } catch (error) {
      setAlert({ type: 'error', message: t('admin.users.errorDelete') })
    }
  }

  const handleUpdateSetting = async (key, value) => {
    try {
      await api.patch(`/api/v1/admin/settings/${key}`, { value })
      setAlert({ type: 'success', message: t('admin.settings.updated') })
      fetchData()
    } catch (error) {
      setAlert({ type: 'error', message: t('admin.settings.errorUpdate') })
    }
  }

  if (loading) {
    return (
      <div className="px-4 py-6 min-h-screen">
        <div className="text-center py-12">
          <div className="text-gray-500 text-sm mb-4">{t('loadingStates.loadingUsers')}</div>
          <ListSkeleton count={5} showActions={true} />
        </div>
      </div>
    )
  }

  return (
    <div className="px-4 py-6 min-h-screen">
      
      <div className="max-w-7xl mx-auto">
        {alert && (
          <div className="mb-4 fixed top-20 left-1/2 transform -translate-x-1/2 z-50 w-full max-w-2xl px-4">
            <Alert variant={alert.type} onClose={() => setAlert(null)}>
              {alert.message}
            </Alert>
          </div>
        )}

        <h1 className="text-3xl font-bold mb-6">{t('admin.title')}</h1>

        {/* Tabs */}
        <div className="flex space-x-4 mb-6 border-b">
          <button
            onClick={() => setActiveTab('users')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'users'
                ? 'border-b-2 border-[#7fa653] text-[#7fa653]'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            {t('admin.tabs.users')}
          </button>
          <button
            onClick={() => setActiveTab('stats')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'stats'
                ? 'border-b-2 border-[#7fa653] text-[#7fa653]'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            {t('admin.tabs.stats')}
          </button>
          <button
            onClick={() => setActiveTab('settings')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'settings'
                ? 'border-b-2 border-[#7fa653] text-[#7fa653]'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            {t('admin.tabs.settings')}
          </button>
        </div>

        {/* Users Tab */}
        {activeTab === 'users' && (
          <Card>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {t('admin.users.email')}
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {t('admin.users.createdAt')}
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {t('admin.users.pets')}
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {t('admin.users.activeRoutines')}
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {t('admin.users.status')}
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {t('admin.users.actions')}
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {users.map((user) => (
                    <tr key={user.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {user.email}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDateShort(user.created_at)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {user.pets_count}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {user.routines_count}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                            user.is_active
                              ? 'bg-green-100 text-green-800'
                              : 'bg-gray-100 text-gray-800'
                          }`}
                        >
                          {user.is_active ? t('status.active') : t('status.inactive')}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                        <Button
                          size="sm"
                          variant={user.is_active ? 'secondary' : 'primary'}
                          onClick={() => handleToggleUserStatus(user.id, user.is_active)}
                        >
                          {user.is_active ? t('admin.users.deactivate') : t('admin.users.activate')}
                        </Button>
                        <Button
                          size="sm"
                          variant="secondary"
                          onClick={() => handleDeleteUser(user.id)}
                        >
                          {t('admin.users.delete')}
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        )}

        {/* Statistics Tab */}
        {activeTab === 'stats' && stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Card>
              <h3 className="text-lg font-semibold mb-2">{t('admin.stats.totalUsers')}</h3>
              <p className="text-3xl font-bold text-[#7fa653]">{stats.total_users}</p>
            </Card>
            <Card>
              <h3 className="text-lg font-semibold mb-2">{t('admin.stats.totalPets')}</h3>
              <p className="text-3xl font-bold text-[#7fa653]">{stats.total_pets}</p>
            </Card>
            <Card>
              <h3 className="text-lg font-semibold mb-2">{t('admin.stats.activeRoutines')}</h3>
              <p className="text-3xl font-bold text-[#7fa653]">{stats.total_active_routines}</p>
            </Card>
            <Card>
              <h3 className="text-lg font-semibold mb-2">{t('admin.stats.completedToday')}</h3>
              <p className="text-3xl font-bold text-[#7fa653]">{stats.routines_completed_today}</p>
            </Card>
            <Card>
              <h3 className="text-lg font-semibold mb-2">{t('admin.stats.activeUsers7Days')}</h3>
              <p className="text-3xl font-bold text-[#7fa653]">{stats.active_users_last_7_days}</p>
            </Card>
          </div>
        )}

        {/* Settings Tab */}
        {activeTab === 'settings' && (
          <Card>
            <div className="space-y-6">
              {settings.map((setting) => (
                <div key={setting.key} className="border-b pb-4 last:border-b-0">
                  <div className="flex items-center justify-between mb-2">
                    <div>
                      <h3 className="text-lg font-semibold">{setting.key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</h3>
                      {setting.description && (
                        <p className="text-sm text-gray-500">{setting.description}</p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    {setting.key === 'registration_enabled' ? (
                      <div className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          checked={setting.value === 'true'}
                          onChange={(e) => handleUpdateSetting(setting.key, e.target.checked ? 'true' : 'false')}
                          className="w-4 h-4 text-[#7fa653] border-gray-300 rounded focus:ring-[#7fa653]"
                        />
                        <span className="text-sm text-gray-700">
                          {setting.value === 'true' ? t('admin.settings.enabled') : t('admin.settings.disabled')}
                        </span>
                      </div>
                    ) : (
                      <>
                        <Input
                          type="number"
                          value={setting.value}
                          onChange={(e) => {
                            const newSettings = settings.map(s => 
                              s.key === setting.key ? { ...s, value: e.target.value } : s
                            )
                            setSettings(newSettings)
                          }}
                          className="w-32"
                        />
                        <Button
                          size="sm"
                          variant="primary"
                          onClick={() => handleUpdateSetting(setting.key, setting.value)}
                        >
                          {t('admin.settings.save')}
                        </Button>
                      </>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </Card>
        )}
      </div>
    </div>
  )
}
