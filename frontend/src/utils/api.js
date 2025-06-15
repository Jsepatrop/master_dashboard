const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

class APIError extends Error {
  constructor(message, status, data) {
    super(message)
    this.name = 'APIError'
    this.status = status
    this.data = data
  }
}

async function handleResponse(response) {
  if (!response.ok) {
    let errorData
    try {
      errorData = await response.json()
    } catch {
      errorData = { message: 'Network error occurred' }
    }
    
    throw new APIError(
      errorData.message || `HTTP ${response.status}`,
      response.status,
      errorData
    )
  }
  
  try {
    return await response.json()
  } catch {
    return null
  }
}

async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`
  
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    }
  }
  
  const config = { ...defaultOptions, ...options }
  
  try {
    const response = await fetch(url, config)
    return await handleResponse(response)
  } catch (error) {
    if (error instanceof APIError) {
      throw error
    }
    
    console.error(`API request failed: ${url}`, error)
    throw new APIError('Network request failed', 0, { originalError: error })
  }
}

// Machine API functions
export async function getMachines() {
  try {
    return await apiRequest('/api/v1/machines')
  } catch (error) {
    console.warn('Failed to fetch machines, using mock data:', error.message)
    // Return mock data if API is not available
    return [
      {
        id: 1,
        name: "Web Server 01",
        type: "WEB_SERVER",
        status: "ONLINE",
        position: { x: -2, y: 0, z: 2, rotation_x: 0, rotation_y: 0, rotation_z: 0 }
      },
      {
        id: 2,
        name: "Database Server",
        type: "DATABASE_SERVER", 
        status: "ONLINE",
        position: { x: 2, y: 0, z: -2, rotation_x: 0, rotation_y: 0, rotation_z: 0 }
      },
      {
        id: 3,
        name: "Load Balancer",
        type: "LOAD_BALANCER",
        status: "WARNING",
        position: { x: 0, y: 0, z: 0, rotation_x: 0, rotation_y: 0, rotation_z: 0 }
      }
    ]
  }
}

export async function getMachine(machineId) {
  return apiRequest(`/api/v1/machines/${machineId}`)
}

export async function createMachine(machineData) {
  return apiRequest('/api/v1/machines', {
    method: 'POST',
    body: JSON.stringify(machineData)
  })
}

export async function updateMachine(machineId, updateData) {
  return apiRequest(`/api/v1/machines/${machineId}`, {
    method: 'PUT',
    body: JSON.stringify(updateData)
  })
}

export async function deleteMachine(machineId) {
  return apiRequest(`/api/v1/machines/${machineId}`, {
    method: 'DELETE'
  })
}

// Metrics API functions
export async function getLatestMetrics() {
  return apiRequest('/api/v1/metrics/latest')
}

export async function getMachineMetrics(machineId, limit = 100) {
  return apiRequest(`/api/v1/metrics/${machineId}?limit=${limit}`)
}

export async function createMetric(machineId, metricData) {
  return apiRequest(`/api/v1/metrics/${machineId}`, {
    method: 'POST',
    body: JSON.stringify(metricData)
  })
}

// Alerts API functions
export async function getActiveAlerts() {
  return apiRequest('/api/v1/alerts/active')
}

export async function getAllAlerts() {
  return apiRequest('/api/v1/alerts')
}

export async function getMachineAlerts(machineId) {
  return apiRequest(`/api/v1/alerts/${machineId}`)
}

export async function createAlert(alertData) {
  return apiRequest('/api/v1/alerts', {
    method: 'POST',
    body: JSON.stringify(alertData)
  })
}

export async function updateAlert(alertId, updateData) {
  return apiRequest(`/api/v1/alerts/${alertId}`, {
    method: 'PUT',
    body: JSON.stringify(updateData)
  })
}

export async function deleteAlert(alertId) {
  return apiRequest(`/api/v1/alerts/${alertId}`, {
    method: 'DELETE'
  })
}

// Health API functions
export async function getHealthStatus() {
  return apiRequest('/api/v1/health')
}

export async function getReadyStatus() {
  return apiRequest('/api/v1/health/ready')
}

export function generateMockMetric(machineId, metricType) {
  const mockData = {
    CPU_USAGE: { min: 0, max: 100, unit: '%' },
    MEMORY_USAGE: { min: 0, max: 16, unit: 'GB' },
    DISK_USAGE: { min: 0, max: 1000, unit: 'GB' },
    NETWORK_THROUGHPUT: { min: 0, max: 1000, unit: 'Mbps' }
  }
  
  const config = mockData[metricType] || mockData.CPU_USAGE
  const value = Math.random() * (config.max - config.min) + config.min
  
  return {
    id: `metric-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    machine_id: machineId,
    metric_type: metricType,
    value: Math.round(value * 100) / 100,
    unit: config.unit,
    timestamp: new Date().toISOString()
  }
}

export { APIError }
