import React from 'react'

function MetricsPanel({ machine, metrics, isConnected }) {
  if (!machine) {
    return (
      <div className="bg-dark-surface border border-cyber-blue rounded-lg p-4">
        <h3 className="text-cyber-blue font-bold mb-4">SYSTEM METRICS</h3>
        <div className="text-center text-gray-400 py-8">
          Select a machine to view metrics
        </div>
      </div>
    )
  }

  const getLatestMetric = (type) => {
    const filtered = metrics.filter(m => m.metric_type === type)
    return filtered.length > 0 ? filtered[filtered.length - 1] : null
  }

  const formatValue = (value, unit) => {
    if (typeof value === 'number') {
      return `${value.toFixed(1)}${unit}`
    }
    return `${value}${unit}`
  }

  const getStatusColor = (value, type) => {
    const thresholds = {
      CPU_USAGE: { warning: 70, critical: 90 },
      MEMORY_USAGE: { warning: 12, critical: 14 },
      DISK_USAGE: { warning: 800, critical: 950 }
    }
    
    const threshold = thresholds[type]
    if (!threshold) return 'text-cyber-green'
    
    if (value >= threshold.critical) return 'text-cyber-red'
    if (value >= threshold.warning) return 'text-cyber-orange'
    return 'text-cyber-green'
  }

  const metricTypes = ['CPU_USAGE', 'MEMORY_USAGE', 'DISK_USAGE', 'NETWORK_THROUGHPUT']

  return (
    <div className="bg-dark-surface border border-cyber-blue rounded-lg p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-cyber-blue font-bold">SYSTEM METRICS</h3>
        <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-cyber-green animate-pulse' : 'bg-cyber-red'}`} />
      </div>
      
      <div className="space-y-4">
        <div className="text-sm text-gray-300 mb-2">
          Machine: {machine.name}
        </div>
        
        {metricTypes.map(type => {
          const metric = getLatestMetric(type)
          const displayName = type.replace('_', ' ')
          
          return (
            <div key={type} className="bg-dark-bg border border-gray-600 rounded p-3">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-300">{displayName}</span>
                {metric && (
                  <span className={`text-sm font-bold ${getStatusColor(metric.value, type)}`}>
                    {formatValue(metric.value, metric.unit)}
                  </span>
                )}
              </div>
              
              {metric && (
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full transition-all duration-300 ${
                      getStatusColor(metric.value, type).includes('red') ? 'bg-cyber-red' :
                      getStatusColor(metric.value, type).includes('orange') ? 'bg-cyber-orange' :
                      'bg-cyber-green'
                    }`}
                    style={{ 
                      width: `${Math.min(100, (metric.value / (type === 'CPU_USAGE' ? 100 : type === 'MEMORY_USAGE' ? 16 : 1000)) * 100)}%` 
                    }}
                  />
                </div>
              )}
              
              {!metric && (
                <div className="text-xs text-gray-500">No data available</div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default MetricsPanel
