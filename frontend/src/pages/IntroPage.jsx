import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function IntroPage() {
  const [showContent, setShowContent] = useState(false)
  const [showLogo, setShowLogo] = useState(false)
  const [showText, setShowText] = useState(false)
  const [showPaw, setShowPaw] = useState(false)
  const [progress, setProgress] = useState(0)
  const navigate = useNavigate()

  useEffect(() => {
    // Mark that the user has already seen the intro
    localStorage.setItem('lanature-visited', 'true')
    
    // Animation sequence
    setTimeout(() => setShowLogo(true), 300)
    setTimeout(() => setShowText(true), 800)
    setTimeout(() => setShowPaw(true), 1200)
    setTimeout(() => setShowContent(true), 1500)
    
    // Progress bar animation
    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(progressInterval)
          return 100
        }
        return prev + 2
      })
    }, 80)
    
    // Redirect to landing page after 4 seconds
    const timer = setTimeout(() => {
      navigate('/home')
    }, 4000)

    return () => {
      clearTimeout(timer)
      clearInterval(progressInterval)
    }
  }, [navigate])

  const handleSkip = () => {
    localStorage.setItem('lanature-visited', 'true')
    navigate('/home')
  }

  return (
    <div className="fixed inset-0 bg-gradient-to-br from-green-400 via-green-500 to-green-600 flex items-center justify-center overflow-hidden">
      {/* Animated background waves */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute bottom-0 left-0 right-0 h-1/3 bg-white/10 animate-wave" />
        <div className="absolute bottom-0 left-0 right-0 h-1/4 bg-white/5 animate-wave-delayed" />
      </div>

      {/* Animated background particles */}
      <div className="absolute inset-0 overflow-hidden">
        {[...Array(15)].map((_, i) => (
          <div
            key={i}
            className="absolute w-2 h-2 bg-white/20 rounded-full animate-float"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 2}s`,
              animationDuration: `${3 + Math.random() * 2}s`,
            }}
          />
        ))}
      </div>

      {/* Main content */}
      <div className="relative z-10 text-center px-4 max-w-4xl mx-auto">
        {/* Logo/Name with animation */}
        <div
          className={`transition-all duration-1000 ease-out ${
            showLogo
              ? 'opacity-100 scale-100 translate-y-0'
              : 'opacity-0 scale-75 translate-y-10'
          }`}
        >
          <div className="text-7xl sm:text-8xl md:text-9xl font-extrabold text-white mb-6 tracking-tight">
            <span className="inline-block animate-slide-in-left">La</span>
            <span className="inline-block text-green-100 animate-slide-in-right ml-2">Nature</span>
          </div>
        </div>

        {/* Animated paw icon */}
        <div
          className={`transition-all duration-700 delay-300 ${
            showPaw
              ? 'opacity-100 scale-100 rotate-0'
              : 'opacity-0 scale-0 rotate-180'
          }`}
        >
          <div className="text-6xl md:text-7xl mb-8 animate-bounce-slow inline-block">
            🐾
          </div>
        </div>

        {/* Presentation text */}
        <div
          className={`transition-all duration-1000 delay-500 ${
            showText
              ? 'opacity-100 translate-y-0'
              : 'opacity-0 translate-y-5'
          }`}
        >
          <p className="text-white text-xl sm:text-2xl md:text-3xl font-semibold mb-4">
            love translates into care
          </p>
          <p className="text-white/95 text-lg sm:text-xl md:text-2xl font-semibold mb-3">
            Take care of your pets with organization
          </p>
          <p className="text-white/80 text-base sm:text-lg md:text-xl font-light mb-8">
            Manage your pet's routine simply and efficiently
          </p>
        </div>

        {/* Progress bar */}
        <div className="w-64 sm:w-80 md:w-96 h-1.5 bg-white/20 rounded-full mx-auto mt-8 overflow-hidden shadow-lg">
          <div
            className="h-full bg-white rounded-full transition-all duration-75 ease-linear shadow-sm"
            style={{ width: `${progress}%` }}
          />
        </div>

        {/* Skip button */}
        <button
          onClick={handleSkip}
          className="mt-8 text-white/80 hover:text-white text-sm font-medium transition-all duration-200 hover:scale-105 active:scale-95"
        >
          Skip introduction →
        </button>
      </div>

      {/* Inline animation styles */}
      <style>{`
        @keyframes float {
          0%, 100% {
            transform: translateY(0) translateX(0);
            opacity: 0.2;
          }
          50% {
            transform: translateY(-30px) translateX(15px);
            opacity: 0.5;
          }
        }
        
        .animate-float {
          animation: float 4s ease-in-out infinite;
        }
        
        @keyframes bounce-slow {
          0%, 100% {
            transform: translateY(0) scale(1);
          }
          50% {
            transform: translateY(-15px) scale(1.1);
          }
        }
        
        .animate-bounce-slow {
          animation: bounce-slow 2.5s ease-in-out infinite;
        }

        @keyframes wave {
          0%, 100% {
            transform: translateX(0) translateY(0);
          }
          50% {
            transform: translateX(-25%) translateY(-10px);
          }
        }

        .animate-wave {
          animation: wave 8s ease-in-out infinite;
        }

        .animate-wave-delayed {
          animation: wave 10s ease-in-out infinite;
          animation-delay: -2s;
        }

        @keyframes slide-in-left {
          0% {
            transform: translateX(-50px);
            opacity: 0;
          }
          100% {
            transform: translateX(0);
            opacity: 1;
          }
        }

        @keyframes slide-in-right {
          0% {
            transform: translateX(50px);
            opacity: 0;
          }
          100% {
            transform: translateX(0);
            opacity: 1;
          }
        }

        .animate-slide-in-left {
          animation: slide-in-left 0.8s ease-out;
        }

        .animate-slide-in-right {
          animation: slide-in-right 0.8s ease-out;
        }
      `}</style>
    </div>
  )
}
