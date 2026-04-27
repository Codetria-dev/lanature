import { useState } from 'react'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Input from '../components/ui/Input'
import Alert from '../components/ui/Alert'
import { t } from '../i18n'

export default function Contact() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  })
  const [alert, setAlert] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setAlert(null)

    setTimeout(() => {
      setLoading(false)
      setAlert({ type: 'success', message: t('contact.messageSent') })
      setFormData({
        name: '',
        email: '',
        subject: '',
        message: ''
      })
    }, 1000)
  }

  return (
    <div className="px-4 py-6 min-h-screen">
      <div className="max-w-2xl mx-auto">
        {alert && (
          <div className="mb-4 fixed top-20 left-1/2 transform -translate-x-1/2 z-50 w-full max-w-2xl px-4">
            <Alert variant={alert.type} onClose={() => setAlert(null)}>
              {alert.message}
            </Alert>
          </div>
        )}

        <Card>
          <h1 className="text-3xl font-bold mb-6 text-center">{t('contact.title')}</h1>
          <p className="text-gray-600 mb-6 text-center">
            {t('contact.subtitle')}
          </p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
                {t('name')}
              </label>
              <Input
                id="name"
                name="name"
                type="text"
                value={formData.name}
                onChange={handleChange}
                required
                placeholder={t('forms.fullName')}
              />
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                {t('email')}
              </label>
              <Input
                id="email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                required
                placeholder={t('contact.emailPlaceholder')}
              />
            </div>

            <div>
              <label htmlFor="subject" className="block text-sm font-medium text-gray-700 mb-1">
                {t('contact.subject')}
              </label>
              <Input
                id="subject"
                name="subject"
                type="text"
                value={formData.subject}
                onChange={handleChange}
                required
                placeholder={t('contact.subjectPlaceholder')}
              />
            </div>

            <div>
              <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-1">
                {t('contact.message')}
              </label>
              <textarea
                id="message"
                name="message"
                value={formData.message}
                onChange={handleChange}
                required
                rows={6}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-[#7fa653] focus:border-[#7fa653]"
                placeholder={t('contact.messagePlaceholder')}
              />
            </div>

            <div className="flex justify-end">
              <Button
                type="submit"
                loading={loading}
                loadingText={t('loadingStates.sendingMessage')}
                className="bg-brand-500 hover:bg-brand-600 text-white"
              >
                {t('contact.sendMessage')}
              </Button>
            </div>
          </form>
        </Card>
      </div>
    </div>
  )
}
