import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import Input from '../components/ui/Input'
import Button from '../components/ui/Button'
import Alert from '../components/ui/Alert'
import { ROUTES } from '../constants'
import { t } from '../i18n'
import backgroundBg from '@assets/background.png'

export default function Register() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { register } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await register(name, email, password)
      // Aguardar um pouco para o user ser atualizado no contexto
      setTimeout(() => {
        // Usuários registrados sempre são usuários comuns, não superusers
        navigate(ROUTES.DASHBOARD)
      }, 200)
    } catch (err) {
      setError(err.response?.data?.detail || t('auth.registerError'))
      setLoading(false)
    }
  }

  return (
    <div 
      className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 relative"
      style={{
        backgroundImage: `url(${backgroundBg})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
      }}
    >
      {/* Overlay for better readability */}
      <div className="absolute inset-0 bg-white/80 backdrop-blur-sm"></div>
      
      <div className="max-w-md w-full space-y-8 relative z-10">
        <div>
          <h1 className="text-center text-4xl font-serif text-gray-800 mb-2">
            Welcome to LaNature
          </h1>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            {t('auth.registerTitle')}
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            {t('auth.registerSubtitle')}{' '}
            <Link
              to={ROUTES.LOGIN}
              className="font-medium text-green-600 hover:text-green-500"
            >
              {t('auth.alreadyHaveAccount')}
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
              label={t('name')}
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder={t('name')}
            />
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
            <Button type="submit" disabled={loading} loading={loading} className="w-full">
              {t('register')}
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}
