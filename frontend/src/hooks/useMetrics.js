import { useState, useCallback } from 'react'

export function useMetrics() {
  const [metrics, setMetrics] = useState({})
  const [alerts, setAlerts] = useState([])
  const [lastUpdate, setLastUpdate] = useState(null)

  const updateMetrics = useCallback((machineId, newMetric) => {
    setMetrics(prev => {
      const machineMetrics = prev[machineId] || []
      const updatedMetrics = [...machineMetrics, newMetric]
      
      // Keep only last 50 metrics per machine for performance
      const trimmedMetrics = updatedMetrics.slice(-50)
      
      return {
        ...prev,
        [machineId]: trimmedMetrics
      }
    })
    
    setLastUpdate(new Date())
    
    // Check for alert conditions
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
        // Check if similar alert already exists and is active
        const existingAlert = prev.find(alert => 
          alert.machine_id === machineId && 
          alert.level === alertLevel && 
          alert.is_active &&
          alert.message.includes(metric.metric_type.replace('_', ' '))
        )

        if (existingAlert) {
          return prev // Don't add duplicate alert
        }

        return [newAlert, ...prev]
      })
    }
  }, [])

  const addAlert = useCallback((alert) => {
    setAlerts(prev => {
      // Check for duplicates
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

  const clearMetrics = useCallback((machineId) => {
    if (machineId) {
      setMetrics(prev => ({
        ...prev,
        [machineId]: []
      }))
    } else {
      setMetrics({})
    }
  }, [])

  const getLatestMetric = useCallback((machineId, metricType) => {
    const machineMetrics = metrics[machineId] || []
    const filteredMetrics = machineMetrics.filter(m => m.metric_type === metricType)
    return filteredMetrics.length > 0 ? filteredMetrics[filteredMetrics.length - 1] : null
  }, [metrics])

  const getMetricHistory = useCallback((machineId, metricType, limit = 20) => {
    const machineMetrics = metrics[machineId] || []
    return machineMetrics
      .filter(m => m.metric_type === metricType)
      .slice(-limit)
  }, [metrics])

  const getAverageMetric = useCallback((machineId, metricType, timeWindow = 10) => {
    const history = getMetricHistory(machineId, metricType, timeWindow)
    if (history.length === 0) return 0
    
    const sum = history.reduce((acc, metric) => acc + metric.value, 0)
    return sum / history.length
  }, [getMetricHistory])

  const getMachineStatus = useCallback((machineId) => {
    const activeAlerts = alerts.filter(alert => 
      alert.machine_id === machineId && alert.is_active
    )

    if (activeAlerts.some(alert => alert.level === 'CRITICAL')) {
      return 'CRITICAL'
    } else if (activeAlerts.some(alert => alert.level === 'WARNING')) {
      return 'WARNING'
    } else {
      return 'NORMAL'
    }
  }, [alerts])

  const getSystemOverview = useCallback(() => {
    const totalMachines = Object.keys(metrics).length
    const totalMetrics = Object.values(metrics).reduce((sum, machineMetrics) => sum + machineMetrics.length, 0)
    const activeAlerts = alerts.filter(alert => alert.is_active)
    const criticalAlerts = activeAlerts.filter(alert => alert.level === 'CRITICAL')
    const warningAlerts = activeAlerts.filter(alert => alert.level === 'WARNING')

    return {
      totalMachines,
      totalMetrics,
      totalAlerts: alerts.length,
      activeAlerts: activeAlerts.length,
      criticalAlerts: criticalAlerts.length,
      warningAlerts: warningAlerts.length,
      lastUpdate
    }
  }, [metrics, alerts, lastUpdate])

  return {
    metrics,
    alerts,
    lastUpdate,
    updateMetrics,
    addAlert,
    resolveAlert,
    dismissAlert,
    clearMetrics,
    getLatestMetric,
    getMetricHistory,
    getAverageMetric,
    getMachineStatus,
    getSystemOverview
  }
}