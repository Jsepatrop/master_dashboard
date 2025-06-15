import React, { Suspense, useState, useEffect } from 'react'
import { Toaster } from 'react-hot-toast'
import Dashboard3D from '@/components/Dashboard3D'
import LoadingScreen from '@/components/LoadingScreen'
import MetricsPanel from '@/components/MetricsPanel'
import AlertsPanel from '@/components/AlertsPanel'
import MachineList from '@/components/MachineList'
import ConfigurationPanel from '@/components/ConfigurationPanel'
import { useWebSocket } from '@/hooks/useWebSocket'
import { useApi } from '@/hooks/useApi'
import { Machine, MetricData, Alert } from '@/types'
import { Activity, Settings, Zap, AlertTriangle, Server, Menu, X } from 'lucide-react'

function App() {
  const [selectedMachine, setSelectedMachine] = useState<Machine | null>(null)
  const [activePanel, setActivePanel] = useState<string>('metrics')
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [machines, setMachines] = useState<Machine[]>([])
  const [metrics, setMetrics] = useState<MetricData[]>([])
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)

  const { api } = useApi()
  const { isConnected, lastMessage } = useWebSocket('ws://localhost:8000/ws/dashboard/dashboard-1')

  useEffect(() => {
    loadInitialData()
  }, [])

  useEffect(() => {
    if (lastMessage) {
      handleWebSocketMessage(lastMessage)
    }
  }, [lastMessage])

  const loadInitialData = async () => {
    try {
      const [machinesData, alertsData] = await Promise.all([
        api.get('/machines'),
        api.get('/alerts')
      ])
      
      setMachines(machinesData.machines || [])
      setAlerts(alertsData.alerts || [])
      
      if (machinesData.machines && machinesData.machines.length > 0) {
        setSelectedMachine(machinesData.machines[0])
      }
    } catch (error) {
      console.error('Failed to load initial data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleWebSocketMessage = (message: any) => {
    if (message.type === 'metrics_update') {
      setMetrics(prev => [...prev.slice(-100), ...message.data])
    } else if (message.type === 'machine_registered') {
      loadInitialData()
    } else if (message.type === 'alert_triggered') {
      setAlerts(prev => [message.alert, ...prev])
    }
  }

  const renderPanel = () => {
    switch (activePanel) {
      case 'metrics':
        return <MetricsPanel machine={selectedMachine} metrics={metrics} />
      case 'alerts':
        return <AlertsPanel alerts={alerts} />
      case 'config':
        return <ConfigurationPanel />
      default:
        return <MetricsPanel machine={selectedMachine} metrics={metrics} />
    }
  }

  if (loading) {
    return <LoadingScreen />
  }

  return (
    <div className="min-h-screen bg-dark-500 text-white font-mono overflow-hidden">
      {/* Matrix Background Effect */}
      <div className="fixed inset-0 bg-gradient-to-br from-dark-500 via-dark-400 to-dark-300" />
      
      {/* Header */}
      <header className="relative z-50 h-16 bg-dark-300/80 backdrop-blur-md border-b border-neon-cyan/20">
        <div className="flex items-center justify-between h-full px-6">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 rounded-lg bg-dark-200/50 hover:bg-dark-200 transition-colors border border-neon-cyan/30"
            >
              {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
            <h1 className="text-2xl font-cyber font-bold text-neon-cyan animate-glow">
              Master Dashboard Revolutionary
            </h1>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className={`flex items-center space-x-2 px-3 py-1 rounded-full text-sm ${
              isConnected 
                ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
                : 'bg-red-500/20 text-red-400 border border-red-500/30'
            }`}>
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`} />
              {isConnected ? 'Connected' : 'Disconnected'}
            </div>
            
            <div className="text-sm text-gray-400">
              {machines.length} Machines
            </div>
          </div>
        </div>
      </header>

      <div className="flex h-[calc(100vh-4rem)]">
        {/* Sidebar */}
        <div className={`relative z-40 transition-all duration-300 ${
          sidebarOpen ? 'w-80' : 'w-0'
        } overflow-hidden`}>
          <div className="h-full bg-dark-300/80 backdrop-blur-md border-r border-neon-cyan/20">
            {/* Machine List */}
            <div className="h-1/2 border-b border-neon-cyan/20">
              <MachineList
                machines={machines}
                selectedMachine={selectedMachine}
                onSelectMachine={setSelectedMachine}
              />
            </div>
            
            {/* Control Panel */}
            <div className="h-1/2 p-4">
              <h3 className="text-lg font-cyber font-semibold text-neon-cyan mb-4">Control Panel</h3>
              <div className="space-y-2">
                {[
                  { id: 'metrics', label: 'Metrics', icon: Activity },
                  { id: 'alerts', label: 'Alerts', icon: AlertTriangle },
                  { id: 'config', label: 'Configuration', icon: Settings }
                ].map(({ id, label, icon: Icon }) => (
                  <button
                    key={id}
                    onClick={() => setActivePanel(id)}
                    className={`w-full flex items-center space-x-3 p-3 rounded-lg transition-all ${
                      activePanel === id
                        ? 'bg-neon-cyan/20 text-neon-cyan border border-neon-cyan/50'
                        : 'bg-dark-200/30 hover:bg-dark-200/50 text-gray-300 hover:text-white border border-transparent'
                    }`}
                  >
                    <Icon size={18} />
                    <span className="font-medium">{label}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 flex">
          {/* 3D Visualization */}
          <div className="flex-1 relative">
            <Suspense fallback={<LoadingScreen />}>
              <Dashboard3D
                machines={machines}
                selectedMachine={selectedMachine}
                onSelectMachine={setSelectedMachine}
                metrics={metrics}
              />
            </Suspense>
          </div>

          {/* Side Panel */}
          <div className="w-96 bg-dark-300/80 backdrop-blur-md border-l border-neon-cyan/20">
            {renderPanel()}
          </div>
        </div>
      </div>

      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#1e1e2e',
            color: '#ffffff',
            border: '1px solid rgba(0, 255, 255, 0.3)',
          },
        }}
      />
    </div>
  )
}

export default App