import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './styles/globals.css'

// Enable concurrent features
const root = ReactDOM.createRoot(document.getElementById('root'))

// Error boundary for better error handling
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null, errorInfo: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true }
  }

  componentDidCatch(error, errorInfo) {
    this.setState({
      error: error,
      errorInfo: errorInfo
    })
    
    // Log error to console for debugging
    console.error('Master Dashboard Error:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-dark-bg flex items-center justify-center">
          <div className="text-center max-w-md mx-auto p-8">
            <div className="text-cyber-red text-6xl font-bold mb-4 glow-red">
              SYSTEM ERROR
            </div>
            <div className="text-white text-xl mb-6">
              Master Dashboard encountered a critical error
            </div>
            <div className="bg-dark-surface p-4 rounded border border-cyber-red mb-6 text-left">
              <div className="text-cyber-red text-sm font-mono">
                {this.state.error && this.state.error.toString()}
              </div>
              {this.state.errorInfo && (
                <div className="text-gray-400 text-xs mt-2 font-mono">
                  {this.state.errorInfo.componentStack}
                </div>
              )}
            </div>
            <button 
              onClick={() => window.location.reload()}
              className="px-6 py-3 bg-cyber-blue text-dark-bg font-bold rounded hover:shadow-neon transition-all"
            >
              RESTART SYSTEM
            </button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

// Performance monitoring
const performanceObserver = new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    if (entry.entryType === 'measure') {
      console.log(`Performance: ${entry.name} took ${entry.duration}ms`)
    }
  }
})

// Observe performance metrics
if (typeof PerformanceObserver !== 'undefined') {
  performanceObserver.observe({ entryTypes: ['measure', 'navigation'] })
}

// Service Worker registration for PWA capabilities
if ('serviceWorker' in navigator && import.meta.env.PROD) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then((registration) => {
        console.log('SW registered: ', registration)
      })
      .catch((registrationError) => {
        console.log('SW registration failed: ', registrationError)
      })
  })
}

// Global error handler
window.addEventListener('error', (event) => {
  console.error('Global error:', event.error)
  
  // Could send to error reporting service
  // errorReportingService.report(event.error)
})

window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason)
  
  // Could send to error reporting service
  // errorReportingService.report(event.reason)
})

// Development helpers
if (import.meta.env.DEV) {
  // Performance marks for development
  performance.mark('app-start')
  
  // React DevTools message
  console.log(
    '%cMaster Dashboard - Development Mode',
    'color: #00ffff; font-size: 16px; font-weight: bold; text-shadow: 0 0 10px #00ffff;'
  )
  
  // Log build info
  console.log('Build Info:', {
    mode: import.meta.env.MODE,
    apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000',
    timestamp: new Date().toISOString()
  })
}

// Initialize app with error boundary
root.render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </React.StrictMode>
)

// Performance measurement
if (import.meta.env.DEV) {
  performance.mark('app-rendered')
  performance.measure('app-initialization', 'app-start', 'app-rendered')
}

// Cleanup function for development hot reload
if (import.meta.hot) {
  import.meta.hot.dispose(() => {
    // Cleanup WebSocket connections, timers, etc.
    console.log('Hot reload: cleaning up resources')
  })
}