import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import Input from '../components/ui/Input'
import Button from '../components/ui/Button'
import Alert from '../components/ui/Alert'
import { ROUTES } from '../constants'
import { t } from '../i18n'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await login(email, password)
      navigate(ROUTES.DASHBOARD)
    } catch (err) {
      setError(err.response?.data?.detail || t('auth.loginError'))
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h1 className="text-center text-4xl font-serif text-gray-800 mb-2">
             LaNature
          </h1>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            {t('auth.loginTitle')}
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            {t('auth.loginSubtitle')}{' '}
            <Link
              to={ROUTES.REGISTER}
              className="font-medium text-brand-500 hover:text-brand-600"
            >
              {t('auth.createAccount')}
            </Link>
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <Alert variant="error" onClose={() => setError('')}>
              {error}
            </Alert>
          )}
          <div className="space-y-4">
            <Input
              label={t('email')}
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder={t('email')}
            />
            <Input
              label={t('password')}
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder={t('password')}
            />
          </div>

          <div>
            <Button 
              type="submit" 
              disabled={loading} 
              loading={loading} 
              loadingText={t('loadingStates.loggingIn')}
              className="w-full"
            >
              {t('enter')}
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}
