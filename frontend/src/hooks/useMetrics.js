import { useState, useCallback } from 'react'

export function useMetrics() {
  const [metrics, setMetrics] = useState({})
  const [alerts, setAlerts] = useState([])
  const [lastUpdate, setLastUpdate] = useState(null)

  const updateMetrics = useCallback((machineId, newMetric) => {
    setMetrics(prev => {
      const machineMetrics = prev[machineId] || []
      const updatedMetrics = [...machineMetrics, newMetric]
      const trimmedMetrics = updatedMetrics.slice(-50)
      
      return {
        ...prev,
        [machineId]: trimmedMetrics
      }
    })
    
    setLastUpdate(new Date())
    checkForAlerts(machineId, newMetric)
  }, [])

  const checkForAlerts = useCallback((machineId, metric) => {
    const alertConditions = {
      CPU_USAGE: { warning: 70, critical: 90 },
      MEMORY_USAGE: { warning: 12, critical: 14 },
      DISK_USAGE: { warning: 800, critical: 950 },
      NETWORK_THROUGHPUT: { warning: 800, critical: 950 }
    }

    const condition = alertConditions[metric.metric_type]
    if (!condition) return

    let alertLevel = 'NORMAL'
    let message = ''

    if (metric.value >= condition.critical) {
      alertLevel = 'CRITICAL'
      message = `${metric.metric_type.replace('_', ' ')} is critically high: ${metric.value}${metric.unit}`
    } else if (metric.value >= condition.warning) {
      alertLevel = 'WARNING'
      message = `${metric.metric_type.replace('_', ' ')} is elevated: ${metric.value}${metric.unit}`
    }

    if (alertLevel !== 'NORMAL') {
      const alertId = `alert-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      const newAlert = {
        id: alertId,
        machine_id: machineId,
        metric_id: metric.id,
        level: alertLevel,
        message: message,
        created_at: new Date().toISOString(),
        resolved_at: null,
        is_active: true
      }

      setAlerts(prev => {
        const existingAlert = prev.find(alert => 
          alert.machine_id === machineId && 
          alert.level === alertLevel && 
          alert.is_active &&
          alert.message.includes(metric.metric_type.replace('_', ' '))
        )

        if (existingAlert) {
          return prev
        }

        return [newAlert, ...prev]
      })
    }
  }, [])

  const addAlert = useCallback((alert) => {
    setAlerts(prev => {
      const exists = prev.some(existing => existing.id === alert.id)
      if (exists) return prev
      return [alert, ...prev]
    })
  }, [])

  const resolveAlert = useCallback((alertId) => {
    setAlerts(prev => prev.map(alert => 
      alert.id === alertId 
        ? { ...alert, is_active: false, resolved_at: new Date().toISOString() }
        : alert
    ))
  }, [])

  const dismissAlert = useCallback((alertId) => {
    setAlerts(prev => prev.filter(alert => alert.id !== alertId))
  }, [])

  return {
    metrics,
    alerts,
    lastUpdate,
    updateMetrics,
    addAlert,
    resolveAlert,
    dismissAlert
  }
}
