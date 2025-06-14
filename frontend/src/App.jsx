import React, { useState, useEffect } from 'react'
import Dashboard3D from './components/Dashboard3D'
import MetricsPanel from './components/MetricsPanel'
import AlertsPanel from './components/AlertsPanel'
import ControlPanel from './components/ControlPanel'
import { useWebSocket } from './hooks/useWebSocket'
import { useMetrics } from './hooks/useMetrics'
import { getMachines } from './utils/api'
import './styles/globals.css'

function App() {
  const [machines, setMachines] = useState([])
  const [selectedMachine, setSelectedMachine] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)
  
  const { 
    isConnected, 
    connectionStatus, 
    lastMessage,
    sendMessage 
  } = useWebSocket('ws://localhost:8000/ws/metrics')
  
  const { 
    metrics, 
    alerts, 
    updateMetrics,
    addAlert 
  } = useMetrics()

  useEffect(() => {
    const initializeDashboard = async () => {
      try {
        setIsLoading(true)
        const machinesData = await getMachines()
        setMachines(machinesData)
        
        // Select first machine by default
        if (machinesData.length > 0) {
          setSelectedMachine(machinesData[0])
        }
        
        // Hide loading screen after 2 seconds
        setTimeout(() => {
          const loadingScreen = document.querySelector('.loading-screen')
          if (loadingScreen) {
            loadingScreen.style.opacity = '0'
            setTimeout(() => {
              loadingScreen.style.display = 'none'
              setIsLoading(false)
            }, 500)
          } else {
            setIsLoading(false)
          }
        }, 2000)
        
      } catch (err) {
        console.error('Failed to initialize dashboard:', err)
        setError(err.message)
        setIsLoading(false)
      }
    }

    initializeDashboard()
  }, [])

  // Handle WebSocket messages
  useEffect(() => {
    if (lastMessage) {
      try {
        const message = JSON.parse(lastMessage)
        
        switch (message.type) {
          case 'metrics_batch':
            if (message.data) {
              message.data.forEach(metric => {
                updateMetrics(metric.machine_id, metric)
              })
            }
            break
            
          case 'metric_update':
            updateMetrics(message.machine_id, message.metric)
            break
            
          case 'alert_created':
            addAlert(message.alert)
            break
            
          default:
            console.log('Unknown message type:', message.type)
        }
      } catch (err) {
        console.error('Error processing WebSocket message:', err)
      }
    }
  }, [lastMessage, updateMetrics, addAlert])

  const handleMachineSelect = (machine) => {
    setSelectedMachine(machine)
  }

  const handleMachineHover = (machine) => {
    // Visual feedback for machine hover
    console.log('Machine hovered:', machine?.name)
  }

  if (error) {
    return (
      <div className="min-h-screen bg-dark-bg flex items-center justify-center">
        <div className="text-center">
          <div className="text-cyber-red text-2xl font-bold mb-4">
            SYSTEM ERROR
          </div>
          <div className="text-white text-lg mb-6">
            {error}
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

  return (
    <div className="min-h-screen bg-dark-bg text-white overflow-hidden">
      {/* Header */}
      <header className="absolute top-0 left-0 right-0 z-50 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold text-cyber-blue glow">
              MASTER DASHBOARD
            </h1>
            <div className="text-sm text-gray-400">
              3D Infrastructure Monitoring System
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className={`px-3 py-1 rounded text-sm ${
              isConnected 
                ? 'bg-cyber-green text-dark-bg' 
                : 'bg-cyber-red text-white'
            }`}>
              {connectionStatus}
            </div>
            
            <div className="text-sm text-gray-400">
              Machines: {machines.length}
            </div>
            
            <div className="text-sm text-gray-400">
              Active Alerts: {alerts.filter(a => a.is_active).length}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex h-screen pt-20">
        {/* Left Panel - Controls */}
        <div className="w-80 p-4 space-y-4">
          <ControlPanel 
            machines={machines}
            selectedMachine={selectedMachine}
            onMachineSelect={handleMachineSelect}
            isConnected={isConnected}
            onRefresh={() => window.location.reload()}
          />
        </div>

        {/* Center - 3D Dashboard */}
        <div className="flex-1 relative">
          <Dashboard3D
            machines={machines}
            metrics={metrics}
            selectedMachine={selectedMachine}
            onMachineSelect={handleMachineSelect}
            onMachineHover={handleMachineHover}
            alerts={alerts}
          />
          
          {/* Status overlay */}
          {!isConnected && (
            <div className="absolute top-4 left-1/2 transform -translate-x-1/2 bg-cyber-red px-4 py-2 rounded text-white font-bold animate-pulse">
              CONNECTION LOST - ATTEMPTING RECONNECTION
            </div>
          )}
        </div>

        {/* Right Panel - Metrics & Alerts */}
        <div className="w-96 p-4 space-y-4">
          <MetricsPanel 
            machine={selectedMachine}
            metrics={selectedMachine ? metrics[selectedMachine.id] || [] : []}
            isConnected={isConnected}
          />
          
          <AlertsPanel 
            alerts={alerts}
            selectedMachine={selectedMachine}
          />
        </div>
      </div>

      {/* Footer */}
      <footer className="absolute bottom-0 left-0 right-0 p-4 text-center text-gray-500 text-sm">
        Master Dashboard v1.0.0 | Real-time Infrastructure Monitoring | 
        {new Date().toLocaleString()}
      </footer>
    </div>
  )
}

export default App