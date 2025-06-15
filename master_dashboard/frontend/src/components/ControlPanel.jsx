import React, { useState } from 'react'
import { Settings, Power, RefreshCw, Monitor, Cpu, Database, Globe, Layers, Server } from 'lucide-react'

function MachineCard({ machine, isSelected, onClick }) {
  const getTypeIcon = (type) => {
    switch (type) {
      case 'WEB_SERVER':
        return <Globe className="w-4 h-4" />
      case 'DATABASE_SERVER':
        return <Database className="w-4 h-4" />
      case 'APPLICATION_SERVER':
        return <Server className="w-4 h-4" />
      case 'LOAD_BALANCER':
        return <Layers className="w-4 h-4" />
      case 'CACHE_SERVER':
        return <Cpu className="w-4 h-4" />
      default:
        return <Monitor className="w-4 h-4" />
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'ONLINE':
        return 'text-cyber-green border-cyber-green bg-cyber-green bg-opacity-10'
      case 'OFFLINE':
        return 'text-cyber-red border-cyber-red bg-cyber-red bg-opacity-10'
      case 'MAINTENANCE':
        return 'text-cyber-orange border-cyber-orange bg-cyber-orange bg-opacity-10'
      case 'ERROR':
        return 'text-cyber-red border-cyber-red bg-cyber-red bg-opacity-20'
      default:
        return 'text-gray-400 border-gray-600 bg-gray-600 bg-opacity-10'
    }
  }

  return (
    <div
      onClick={() => onClick(machine)}
      className={`p-3 rounded border cursor-pointer transition-all hover:shadow-neon ${
        isSelected 
          ? 'border-cyber-blue bg-cyber-blue bg-opacity-20 shadow-neon' 
          : 'border-gray-600 bg-dark-surface hover:border-cyber-blue'
      }`}
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          {getTypeIcon(machine.type)}
          <span className="text-sm font-medium text-white truncate">
            {machine.name}
          </span>
        </div>
        <div className={`px-2 py-1 rounded text-xs border ${getStatusColor(machine.status)}`}>
          {machine.status}
        </div>
      </div>
      
      <div className="text-xs text-gray-400 space-y-1">
        <div>Type: {machine.type.replace('_', ' ')}</div>
        <div>ID: {machine.id}</div>
        <div>Position: ({machine.position.x}, {machine.position.z})</div>
      </div>
    </div>
  )
}

function SystemStats({ machines, isConnected }) {
  const onlineCount = machines.filter(m => m.status === 'ONLINE').length
  const offlineCount = machines.filter(m => m.status === 'OFFLINE').length
  const maintenanceCount = machines.filter(m => m.status === 'MAINTENANCE').length

  return (
    <div className="bg-dark-surface p-3 rounded border border-gray-600">
      <div className="text-sm font-medium text-gray-300 mb-3">System Overview</div>
      
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs text-gray-400 flex items-center space-x-2">
            <div className="w-2 h-2 bg-cyber-green rounded-full"></div>
            <span>Online</span>
          </span>
          <span className="text-cyber-green font-bold">{onlineCount}</span>
        </div>
        
        <div className="flex items-center justify-between">
          <span className="text-xs text-gray-400 flex items-center space-x-2">
            <div className="w-2 h-2 bg-cyber-red rounded-full"></div>
            <span>Offline</span>
          </span>
          <span className="text-cyber-red font-bold">{offlineCount}</span>
        </div>
        
        <div className="flex items-center justify-between">
          <span className="text-xs text-gray-400 flex items-center space-x-2">
            <div className="w-2 h-2 bg-cyber-orange rounded-full"></div>
            <span>Maintenance</span>
          </span>
          <span className="text-cyber-orange font-bold">{maintenanceCount}</span>
        </div>
        
        <div className="border-t border-gray-700 pt-2 mt-2">
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-400">Connection</span>
            <span className={`text-xs font-bold ${isConnected ? 'text-cyber-green' : 'text-cyber-red'}`}>
              {isConnected ? 'LIVE' : 'OFFLINE'}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

function ViewControls({ viewMode, setViewMode, autoRotate, setAutoRotate }) {
  return (
    <div className="bg-dark-surface p-3 rounded border border-gray-600">
      <div className="text-sm font-medium text-gray-300 mb-3">View Controls</div>
      
      <div className="space-y-3">
        <div>
          <label className="text-xs text-gray-400 block mb-1">Camera Mode</label>
          <select
            value={viewMode}
            onChange={(e) => setViewMode(e.target.value)}
            className="w-full bg-dark-bg border border-gray-600 rounded px-2 py-1 text-xs text-white"
          >
            <option value="free">Free Camera</option>
            <option value="follow">Follow Selected</option>
            <option value="overview">Overview</option>
          </select>
        </div>
        
        <div className="flex items-center justify-between">
          <span className="text-xs text-gray-400">Auto Rotate</span>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={autoRotate}
              onChange={(e) => setAutoRotate(e.target.checked)}
              className="sr-only peer"
            />
            <div className="w-9 h-5 bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-cyber-blue"></div>
          </label>
        </div>
      </div>
    </div>
  )
}

function ControlPanel({ 
  machines = [], 
  selectedMachine, 
  onMachineSelect, 
  isConnected, 
  onRefresh 
}) {
  const [viewMode, setViewMode] = useState('free')
  const [autoRotate, setAutoRotate] = useState(false)
  const [showSettings, setShowSettings] = useState(false)

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="bg-dark-card p-4 rounded border border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Settings className="w-5 h-5 text-cyber-blue" />
            <h2 className="text-lg font-bold text-cyber-blue">CONTROL PANEL</h2>
          </div>
          <button
            onClick={onRefresh}
            className="p-2 text-gray-400 hover:text-cyber-blue hover:bg-cyber-blue hover:bg-opacity-20 rounded transition-all"
            title="Refresh System"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>

        {/* System Stats */}
        <SystemStats machines={machines} isConnected={isConnected} />
      </div>

      {/* View Controls */}
      <div className="bg-dark-card p-4 rounded border border-gray-700">
        <ViewControls
          viewMode={viewMode}
          setViewMode={setViewMode}
          autoRotate={autoRotate}
          setAutoRotate={setAutoRotate}
        />
      </div>

      {/* Machine List */}
      <div className="bg-dark-card p-4 rounded border border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-bold text-cyber-purple">MACHINES</h3>
          <span className="text-xs text-gray-400">{machines.length} total</span>
        </div>
        
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {machines.length === 0 ? (
            <div className="text-center py-4 text-gray-500">
              <Monitor className="w-6 h-6 mx-auto mb-2 opacity-50" />
              <div className="text-xs">No machines detected</div>
            </div>
          ) : (
            machines.map((machine) => (
              <MachineCard
                key={machine.id}
                machine={machine}
                isSelected={selectedMachine?.id === machine.id}
                onClick={onMachineSelect}
              />
            ))
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-dark-card p-4 rounded border border-gray-700">
        <h3 className="text-sm font-bold text-cyber-green mb-3">QUICK ACTIONS</h3>
        
        <div className="space-y-2">
          <button className="w-full px-3 py-2 bg-cyber-green bg-opacity-20 text-cyber-green border border-cyber-green rounded text-xs hover:bg-opacity-30 transition-all flex items-center justify-center space-x-2">
            <Power className="w-3 h-3" />
            <span>Start All Machines</span>
          </button>
          
          <button className="w-full px-3 py-2 bg-cyber-orange bg-opacity-20 text-cyber-orange border border-cyber-orange rounded text-xs hover:bg-opacity-30 transition-all flex items-center justify-center space-x-2">
            <Settings className="w-3 h-3" />
            <span>Maintenance Mode</span>
          </button>
          
          <button className="w-full px-3 py-2 bg-cyber-red bg-opacity-20 text-cyber-red border border-cyber-red rounded text-xs hover:bg-opacity-30 transition-all flex items-center justify-center space-x-2">
            <Power className="w-3 h-3" />
            <span>Emergency Shutdown</span>
          </button>
        </div>
      </div>

      {/* System Info */}
      <div className="bg-dark-card p-4 rounded border border-gray-700">
        <h3 className="text-sm font-bold text-gray-300 mb-3">SYSTEM INFO</h3>
        
        <div className="text-xs text-gray-400 space-y-1">
          <div>Version: v1.0.0</div>
          <div>Uptime: 99.9%</div>
          <div>Last Update: {new Date().toLocaleString()}</div>
          <div>Performance: Optimal</div>
        </div>
      </div>
    </div>
  )
}

export default ControlPanel