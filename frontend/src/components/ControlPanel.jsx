import React from 'react'

function ControlPanel({ machines, selectedMachine, onMachineSelect, isConnected, onRefresh }) {
  const getMachineStatus = (machine) => {
    const statuses = ['ONLINE', 'WARNING', 'CRITICAL', 'MAINTENANCE']
    return statuses[machine.id % statuses.length] || 'ONLINE'
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'ONLINE': return 'text-cyber-green'
      case 'WARNING': return 'text-cyber-orange'
      case 'CRITICAL': return 'text-cyber-red'
      case 'MAINTENANCE': return 'text-cyber-purple'
      default: return 'text-gray-400'
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'ONLINE': return '●'
      case 'WARNING': return '⚠'
      case 'CRITICAL': return '⚠'
      case 'MAINTENANCE': return '🔧'
      default: return '○'
    }
  }

  return (
    <div className="space-y-4">
      {/* Connection Status */}
      <div className="bg-dark-surface border border-cyber-green rounded-lg p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-cyber-green font-bold">CONNECTION</h3>
          <button
            onClick={onRefresh}
            className="text-cyber-blue hover:text-white transition-colors"
            title="Refresh"
          >
            🔄
          </button>
        </div>
        <div className="flex items-center gap-2">
          <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-cyber-green animate-pulse' : 'bg-cyber-red'}`} />
          <span className="text-sm">
            {isConnected ? 'CONNECTED' : 'DISCONNECTED'}
          </span>
        </div>
      </div>

      {/* Machine List */}
      <div className="bg-dark-surface border border-cyber-blue rounded-lg p-4">
        <h3 className="text-cyber-blue font-bold mb-4">MACHINES ({machines.length})</h3>
        
        {machines.length === 0 ? (
          <div className="text-center text-gray-400 py-4">
            No machines available
          </div>
        ) : (
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {machines.map(machine => {
              const status = getMachineStatus(machine)
              const isSelected = selectedMachine?.id === machine.id
              
              return (
                <div
                  key={machine.id}
                  onClick={() => onMachineSelect(machine)}
                  className={`p-3 rounded border cursor-pointer transition-all hover:bg-dark-bg ${
                    isSelected 
                      ? 'border-cyber-blue bg-dark-bg shadow-neon' 
                      : 'border-gray-600 hover:border-cyber-blue'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-white truncate">
                        {machine.name}
                      </div>
                      <div className="text-xs text-gray-400 truncate">
                        {machine.type.replace('_', ' ')}
                      </div>
                    </div>
                    <div className={`text-sm ml-2 ${getStatusColor(status)}`}>
                      <span className="mr-1">{getStatusIcon(status)}</span>
                      {status}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* System Stats */}
      <div className="bg-dark-surface border border-cyber-purple rounded-lg p-4">
        <h3 className="text-cyber-purple font-bold mb-3">SYSTEM STATS</h3>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-400">Total Machines:</span>
            <span className="text-white">{machines.length}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Online:</span>
            <span className="text-cyber-green">
              {machines.filter(m => getMachineStatus(m) === 'ONLINE').length}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Warnings:</span>
            <span className="text-cyber-orange">
              {machines.filter(m => getMachineStatus(m) === 'WARNING').length}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Critical:</span>
            <span className="text-cyber-red">
              {machines.filter(m => getMachineStatus(m) === 'CRITICAL').length}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ControlPanel
