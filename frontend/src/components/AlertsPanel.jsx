import React, { useState, useEffect } from 'react'
import { AlertTriangle, Shield, X, Clock, CheckCircle } from 'lucide-react'

function AlertItem({ alert, onResolve, onDismiss }) {
  const getAlertColor = (level) => {
    switch (level) {
      case 'CRITICAL':
        return 'border-cyber-red bg-cyber-red bg-opacity-10'
      case 'WARNING':
        return 'border-cyber-orange bg-cyber-orange bg-opacity-10'
      default:
        return 'border-cyber-green bg-cyber-green bg-opacity-10'
    }
  }

  const getAlertIcon = (level) => {
    switch (level) {
      case 'CRITICAL':
        return <AlertTriangle className="w-4 h-4 text-cyber-red" />
      case 'WARNING':
        return <Shield className="w-4 h-4 text-cyber-orange" />
      default:
        return <CheckCircle className="w-4 h-4 text-cyber-green" />
    }
  }

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString()
  }

  return (
    <div className={`p-3 rounded border ${getAlertColor(alert.level)} mb-2 animate-pulse-neon`}>
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-2 flex-1">
          {getAlertIcon(alert.level)}
          <div className="flex-1">
            <div className="text-sm font-medium text-white mb-1">
              {alert.message}
            </div>
            <div className="text-xs text-gray-400 space-y-1">
              <div>Machine: {alert.machine_id}</div>
              <div className="flex items-center space-x-2">
                <Clock className="w-3 h-3" />
                <span>{formatTime(alert.created_at)}</span>
              </div>
            </div>
          </div>
        </div>
        
        <div className="flex items-center space-x-1 ml-2">
          {alert.is_active && (
            <>
              <button
                onClick={() => onResolve(alert)}
                className="p-1 text-cyber-green hover:bg-cyber-green hover:text-dark-bg rounded transition-all"
                title="Resolve Alert"
              >
                <CheckCircle className="w-3 h-3" />
              </button>
              <button
                onClick={() => onDismiss(alert)}
                className="p-1 text-gray-400 hover:bg-cyber-red hover:text-white rounded transition-all"
                title="Dismiss Alert"
              >
                <X className="w-3 h-3" />
              </button>
            </>
          )}
        </div>
      </div>
      
      {!alert.is_active && alert.resolved_at && (
        <div className="mt-2 text-xs text-cyber-green">
          Resolved at: {formatTime(alert.resolved_at)}
        </div>
      )}
    </div>
  )
}

function AlertStats({ alerts }) {
  const activeAlerts = alerts.filter(alert => alert.is_active)
  const criticalCount = activeAlerts.filter(alert => alert.level === 'CRITICAL').length
  const warningCount = activeAlerts.filter(alert => alert.level === 'WARNING').length
  const totalResolved = alerts.filter(alert => !alert.is_active).length

  return (
    <div className="bg-dark-surface p-3 rounded border border-gray-600 mb-4">
      <div className="text-sm font-medium text-gray-300 mb-2">Alert Statistics</div>
      <div className="grid grid-cols-2 gap-2 text-xs">
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-cyber-red rounded-full"></div>
          <span className="text-gray-400">Critical: <span className="text-cyber-red font-bold">{criticalCount}</span></span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-cyber-orange rounded-full"></div>
          <span className="text-gray-400">Warning: <span className="text-cyber-orange font-bold">{warningCount}</span></span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-cyber-green rounded-full"></div>
          <span className="text-gray-400">Active: <span className="text-cyber-green font-bold">{activeAlerts.length}</span></span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
          <span className="text-gray-400">Resolved: <span className="text-gray-300 font-bold">{totalResolved}</span></span>
        </div>
      </div>
    </div>
  )
}

function AlertsPanel({ alerts = [], selectedMachine }) {
  const [filter, setFilter] = useState('all') // all, active, resolved
  const [sortBy, setSortBy] = useState('newest') // newest, oldest, severity

  const filteredAlerts = alerts.filter(alert => {
    if (selectedMachine && alert.machine_id !== selectedMachine.id) return false
    
    switch (filter) {
      case 'active':
        return alert.is_active
      case 'resolved':
        return !alert.is_active
      default:
        return true
    }
  })

  const sortedAlerts = [...filteredAlerts].sort((a, b) => {
    switch (sortBy) {
      case 'oldest':
        return new Date(a.created_at) - new Date(b.created_at)
      case 'severity':
        const severityOrder = { 'CRITICAL': 3, 'WARNING': 2, 'NORMAL': 1 }
        return severityOrder[b.level] - severityOrder[a.level]
      default: // newest
        return new Date(b.created_at) - new Date(a.created_at)
    }
  })

  const handleResolveAlert = (alert) => {
    // In a real app, this would call an API
    console.log('Resolving alert:', alert.id)
  }

  const handleDismissAlert = (alert) => {
    // In a real app, this would call an API
    console.log('Dismissing alert:', alert.id)
  }

  return (
    <div className="bg-dark-card p-4 rounded border border-gray-700 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <AlertTriangle className="w-5 h-5 text-cyber-red" />
          <h2 className="text-lg font-bold text-cyber-red">ALERTS</h2>
        </div>
        <div className="text-xs text-gray-400">
          {selectedMachine ? `Machine: ${selectedMachine.name}` : 'All Machines'}
        </div>
      </div>

      {/* Alert Statistics */}
      <AlertStats alerts={alerts} />

      {/* Filters */}
      <div className="flex items-center justify-between">
        <div className="flex space-x-2">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="bg-dark-surface border border-gray-600 rounded px-2 py-1 text-xs text-white"
          >
            <option value="all">All Alerts</option>
            <option value="active">Active Only</option>
            <option value="resolved">Resolved Only</option>
          </select>
          
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="bg-dark-surface border border-gray-600 rounded px-2 py-1 text-xs text-white"
          >
            <option value="newest">Newest First</option>
            <option value="oldest">Oldest First</option>
            <option value="severity">By Severity</option>
          </select>
        </div>
        
        <div className="text-xs text-gray-400">
          {sortedAlerts.length} alert{sortedAlerts.length !== 1 ? 's' : ''}
        </div>
      </div>

      {/* Alerts List */}
      <div className="max-h-96 overflow-y-auto space-y-2">
        {sortedAlerts.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Shield className="w-8 h-8 mx-auto mb-2 opacity-50" />
            <div className="text-sm">No alerts found</div>
            <div className="text-xs">System is running smoothly</div>
          </div>
        ) : (
          sortedAlerts.map((alert) => (
            <AlertItem
              key={alert.id}
              alert={alert}
              onResolve={handleResolveAlert}
              onDismiss={handleDismissAlert}
            />
          ))
        )}
      </div>

      {/* Quick Actions */}
      <div className="flex space-x-2 pt-2 border-t border-gray-700">
        <button className="flex-1 px-3 py-2 bg-cyber-green bg-opacity-20 text-cyber-green border border-cyber-green rounded text-xs hover:bg-opacity-30 transition-all">
          Resolve All
        </button>
        <button className="flex-1 px-3 py-2 bg-cyber-red bg-opacity-20 text-cyber-red border border-cyber-red rounded text-xs hover:bg-opacity-30 transition-all">
          Clear History
        </button>
      </div>
    </div>
  )
}

export default AlertsPanel