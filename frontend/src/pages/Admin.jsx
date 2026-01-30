import { useState, useEffect } from 'react'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Alert from '../components/ui/Alert'
import Input from '../components/ui/Input'
import api from '../services/api'
import backgroundBg from '@assets/background.png'

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
        setAlert({ type: 'error', message: 'Acesso negado. Apenas superusuários podem acessar esta página.' })
      } else {
        setAlert({ type: 'error', message: error.response?.data?.detail || 'Error loading admin data' })
      }
    } finally {
      setLoading(false)
    }
  }

  const handleToggleUserStatus = async (userId, isActive) => {
    try {
      if (isActive) {
        await api.patch(`/api/v1/admin/users/${userId}/deactivate`)
        setAlert({ type: 'success', message: 'User deactivated successfully' })
      } else {
        await api.patch(`/api/v1/admin/users/${userId}/activate`)
        setAlert({ type: 'success', message: 'User activated successfully' })
      }
      fetchData()
    } catch (error) {
      setAlert({ type: 'error', message: 'Error updating user status' })
    }
  }

  const handleDeleteUser = async (userId) => {
    if (!window.confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
      return
    }

    try {
      await api.delete(`/api/v1/admin/users/${userId}`)
      setAlert({ type: 'success', message: 'User deleted successfully' })
      fetchData()
    } catch (error) {
      setAlert({ type: 'error', message: 'Error deleting user' })
    }
  }

  const handleUpdateSetting = async (key, value) => {
    try {
      await api.patch(`/api/v1/admin/settings/${key}`, { value })
      setAlert({ type: 'success', message: 'Setting updated successfully' })
      fetchData()
    } catch (error) {
      setAlert({ type: 'error', message: 'Error updating setting' })
    }
  }

  if (loading) {
    return (
      <div 
        className="px-4 py-6 min-h-screen relative"
        style={{
          backgroundImage: `url(${backgroundBg})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
        }}
      >
        <div className="absolute inset-0 bg-white/80 backdrop-blur-sm"></div>
        <div className="relative z-10 text-center py-12">Loading...</div>
      </div>
    )
  }

  return (
    <div 
      className="px-4 py-6 min-h-screen relative"
      style={{
        backgroundImage: `url(${backgroundBg})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
      }}
    >
      <div className="absolute inset-0 bg-white/80 backdrop-blur-sm"></div>
      
      <div className="relative z-10 max-w-7xl mx-auto">
        {alert && (
          <div className="mb-4">
            <Alert variant={alert.type} onClose={() => setAlert(null)}>
              {alert.message}
            </Alert>
          </div>
        )}

        <h1 className="text-3xl font-bold mb-6">Admin Panel</h1>

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
            Users
          </button>
          <button
            onClick={() => setActiveTab('stats')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'stats'
                ? 'border-b-2 border-[#7fa653] text-[#7fa653]'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Statistics
          </button>
          <button
            onClick={() => setActiveTab('settings')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'settings'
                ? 'border-b-2 border-[#7fa653] text-[#7fa653]'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Settings
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
                      Email
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Created At
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Pets
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Active Routines
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
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
                        {new Date(user.created_at).toLocaleDateString()}
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
                          {user.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                        <Button
                          size="sm"
                          onClick={() => handleToggleUserStatus(user.id, user.is_active)}
                          className={user.is_active 
                            ? '!bg-[#cfe0bc] hover:!bg-[#b8d09f] text-gray-800'
                            : '!bg-[#7fa653] hover:!bg-[#6a8a45] text-white'
                          }
                        >
                          {user.is_active ? 'Deactivate' : 'Activate'}
                        </Button>
                        <Button
                          size="sm"
                          onClick={() => handleDeleteUser(user.id)}
                          className="!bg-[#cfe0bc] hover:!bg-[#b8d09f] text-gray-800"
                        >
                          Delete
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
              <h3 className="text-lg font-semibold mb-2">Total Users</h3>
              <p className="text-3xl font-bold text-[#7fa653]">{stats.total_users}</p>
            </Card>
            <Card>
              <h3 className="text-lg font-semibold mb-2">Total Pets</h3>
              <p className="text-3xl font-bold text-[#7fa653]">{stats.total_pets}</p>
            </Card>
            <Card>
              <h3 className="text-lg font-semibold mb-2">Active Routines</h3>
              <p className="text-3xl font-bold text-[#7fa653]">{stats.total_active_routines}</p>
            </Card>
            <Card>
              <h3 className="text-lg font-semibold mb-2">Completed Today</h3>
              <p className="text-3xl font-bold text-[#7fa653]">{stats.routines_completed_today}</p>
            </Card>
            <Card>
              <h3 className="text-lg font-semibold mb-2">Active Users (7 days)</h3>
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
                          {setting.value === 'true' ? 'Enabled' : 'Disabled'}
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
                          onClick={() => handleUpdateSetting(setting.key, setting.value)}
                          className="!bg-[#7fa653] hover:!bg-[#6a8a45] text-white"
                        >
                          Save
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
