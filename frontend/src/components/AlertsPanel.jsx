import React from 'react'

function AlertsPanel({ alerts, selectedMachine }) {
  const filteredAlerts = selectedMachine 
    ? alerts.filter(alert => alert.machine_id === selectedMachine.id)
    : alerts

  const activeAlerts = filteredAlerts.filter(alert => alert.is_active)

  const getAlertIcon = (level) => {
    switch (level) {
      case 'CRITICAL': return '🔴'
      case 'WARNING': return '🟡'
      default: return '🟢'
    }
  }

  const getAlertColor = (level) => {
    switch (level) {
      case 'CRITICAL': return 'border-cyber-red text-cyber-red'
      case 'WARNING': return 'border-cyber-orange text-cyber-orange'
      default: return 'border-cyber-green text-cyber-green'
    }
  }

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString()
  }

  return (
    <div className="bg-dark-surface border border-cyber-purple rounded-lg p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-cyber-purple font-bold">SYSTEM ALERTS</h3>
        <div className="text-sm text-gray-400">
          {activeAlerts.length} active
        </div>
      </div>
      
      {activeAlerts.length === 0 ? (
        <div className="text-center text-gray-400 py-8">
          <div className="text-2xl mb-2">✅</div>
          <div>All systems operational</div>
        </div>
      ) : (
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {activeAlerts.map(alert => (
            <div 
              key={alert.id}
              className={`border rounded-lg p-3 ${getAlertColor(alert.level)} bg-opacity-10`}
            >
              <div className="flex items-start gap-3">
                <div className="text-lg">
                  {getAlertIcon(alert.level)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-sm font-bold">
                      {alert.level}
                    </span>
                    <span className="text-xs text-gray-400">
                      {formatTimestamp(alert.created_at)}
                    </span>
                  </div>
                  <div className="text-sm text-gray-300 mb-2">
                    {alert.message}
                  </div>
                  {selectedMachine && (
                    <div className="text-xs text-gray-500">
                      Machine: {selectedMachine.name}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
      
      {filteredAlerts.length > activeAlerts.length && (
        <div className="mt-4 pt-4 border-t border-gray-600">
          <div className="text-xs text-gray-400 text-center">
            {filteredAlerts.length - activeAlerts.length} resolved alerts
          </div>
        </div>
      )}
    </div>
  )
}

export default AlertsPanel
