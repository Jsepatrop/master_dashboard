import React from 'react'

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
    
    if (import.meta.env.DEV) {
      console.error('ErrorBoundary caught an error:', error, errorInfo)
    }
  }

  handleRestart = () => {
    this.setState({ hasError: false, error: null, errorInfo: null })
    window.location.reload()
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-dark-bg flex items-center justify-center p-4">
          <div className="max-w-2xl w-full bg-dark-surface border border-cyber-red rounded-lg p-8">
            <div className="text-center mb-8">
              <div className="text-6xl mb-4">⚠️</div>
              <h1 className="text-3xl font-bold text-cyber-red glow-red mb-2">
                SYSTEM MALFUNCTION
              </h1>
              <p className="text-lg text-gray-300">
                The Master Dashboard has encountered a critical error
              </p>
            </div>

            <div className="bg-dark-bg border border-cyber-red rounded p-4 mb-6">
              <h3 className="text-cyber-red font-bold mb-2">Error Details:</h3>
              <div className="text-sm text-gray-300 font-mono">
                {this.state.error && this.state.error.toString()}
              </div>
              {this.state.errorInfo && (
                <div className="mt-4">
                  <h4 className="text-cyber-orange font-bold mb-2">Stack Trace:</h4>
                  <pre className="text-xs text-gray-400 overflow-auto max-h-32">
                    {this.state.errorInfo.componentStack}
                  </pre>
                </div>
              )}
            </div>

            <div className="flex gap-4 justify-center">
              <button
                onClick={this.handleRestart}
                className="px-6 py-3 bg-cyber-blue text-dark-bg font-bold rounded hover:shadow-neon transition-all"
              >
                RESTART SYSTEM
              </button>
              <button
                onClick={() => window.location.href = '/'}
                className="px-6 py-3 bg-cyber-purple text-white font-bold rounded hover:shadow-neon-purple transition-all"
              >
                RETURN HOME
              </button>
            </div>

            <div className="mt-8 text-center text-sm text-gray-400">
              <p>If the problem persists, please check the console for more details</p>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary
