import { useState } from 'react'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Input from '../components/ui/Input'
import Alert from '../components/ui/Alert'
import backgroundBg from '@assets/background.png'

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

    // Simular envio (você pode integrar com um serviço de email ou API)
    setTimeout(() => {
      setLoading(false)
      setAlert({ type: 'success', message: 'Mensagem enviada com sucesso! Entraremos em contato em breve.' })
      setFormData({
        name: '',
        email: '',
        subject: '',
        message: ''
      })
    }, 1000)
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
      
      <div className="relative z-10 max-w-2xl mx-auto">
        {alert && (
          <div className="mb-4">
            <Alert variant={alert.type} onClose={() => setAlert(null)}>
              {alert.message}
            </Alert>
          </div>
        )}

        <Card>
          <h1 className="text-3xl font-bold mb-6 text-center">Entre em Contato</h1>
          <p className="text-gray-600 mb-6 text-center">
            Tem alguma dúvida ou sugestão? Entre em contato conosco!
          </p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
                Nome
              </label>
              <Input
                id="name"
                name="name"
                type="text"
                value={formData.name}
                onChange={handleChange}
                required
                placeholder="Seu nome completo"
              />
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                Email
              </label>
              <Input
                id="email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                required
                placeholder="seu@email.com"
              />
            </div>

            <div>
              <label htmlFor="subject" className="block text-sm font-medium text-gray-700 mb-1">
                Assunto
              </label>
              <Input
                id="subject"
                name="subject"
                type="text"
                value={formData.subject}
                onChange={handleChange}
                required
                placeholder="Assunto da mensagem"
              />
            </div>

            <div>
              <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-1">
                Mensagem
              </label>
              <textarea
                id="message"
                name="message"
                value={formData.message}
                onChange={handleChange}
                required
                rows={6}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-[#7fa653] focus:border-[#7fa653]"
                placeholder="Sua mensagem aqui..."
              />
            </div>

            <div className="flex justify-end">
              <Button
                type="submit"
                disabled={loading}
                className="!bg-[#7fa653] hover:!bg-[#6a8a45] text-white"
              >
                {loading ? 'Enviando...' : 'Enviar Mensagem'}
              </Button>
            </div>
          </form>
        </Card>
      </div>
    </div>
  )
}
