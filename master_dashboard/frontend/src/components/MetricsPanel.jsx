import React, { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, ResponsiveContainer, AreaChart, Area } from 'recharts'
import { Activity, Cpu, HardDrive, Wifi, MemoryStick } from 'lucide-react'

function MetricGauge({ label, value, max, unit, color, icon: Icon }) {
  const percentage = (value / max) * 100
  const isHigh = percentage > 80
  const isMedium = percentage > 60
  
  return (
    <div className="bg-dark-surface p-3 rounded border border-gray-700">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          <Icon className={`w-4 h-4 ${color}`} />
          <span className="text-sm font-medium text-gray-300">{label}</span>
        </div>
        <span className={`text-sm font-bold ${
          isHigh ? 'text-cyber-red' : isMedium ? 'text-cyber-orange' : 'text-cyber-green'
        }`}>
          {value.toFixed(1)}{unit}
        </span>
      </div>
      
      <div className="w-full bg-gray-800 rounded-full h-2">
        <div
          className={`h-2 rounded-full transition-all duration-500 ${
            isHigh ? 'bg-cyber-red shadow-neon' : 
            isMedium ? 'bg-cyber-orange' : 'bg-cyber-green'
          }`}
          style={{ width: `${Math.min(percentage, 100)}%` }}
        />
      </div>
      
      <div className="flex justify-between text-xs text-gray-500 mt-1">
        <span>0</span>
        <span>{max}{unit}</span>
      </div>
    </div>
  )
}

function MetricChart({ data, title, dataKey, color }) {
  if (!data || data.length === 0) {
    return (
      <div className="bg-dark-surface p-4 rounded border border-gray-700">
        <h3 className="text-sm font-medium text-gray-300 mb-4">{title}</h3>
        <div className="h-32 flex items-center justify-center text-gray-500">
          No data available
        </div>
      </div>
    )
  }
  
  return (
    <div className="bg-dark-surface p-4 rounded border border-gray-700">
      <h3 className="text-sm font-medium text-gray-300 mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={120}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id={`gradient-${dataKey}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={color} stopOpacity={0.8}/>
              <stop offset="95%" stopColor={color} stopOpacity={0.1}/>
            </linearGradient>
          </defs>
          <Area
            type="monotone"
            dataKey={dataKey}
            stroke={color}
            strokeWidth={2}
            fill={`url(#gradient-${dataKey})`}
          />
          <CartesianGrid strokeDasharray="3 3" stroke="#333" />
          <XAxis hide />
          <YAxis hide />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}

function MetricsPanel({ machine, metrics = [], isConnected }) {
  const [processedMetrics, setProcessedMetrics] = useState({
    cpu: [],
    memory: [],
    disk: [],
    network: []
  })
  
  const [currentValues, setCurrentValues] = useState({
    cpu: 0,
    memory: 0,
    disk: 0,
    network: 0
  })
  
  useEffect(() => {
    if (metrics.length > 0) {
      // Group metrics by type
      const grouped = {
        cpu: [],
        memory: [],
        disk: [],
        network: []
      }
      
      metrics.forEach(metric => {
        const timestamp = new Date(metric.timestamp).toLocaleTimeString()
        
        switch (metric.metric_type) {
          case 'CPU_USAGE':
            grouped.cpu.push({ time: timestamp, value: metric.value })
            setCurrentValues(prev => ({ ...prev, cpu: metric.value }))
            break
          case 'MEMORY_USAGE':
            grouped.memory.push({ time: timestamp, value: metric.value })
            setCurrentValues(prev => ({ ...prev, memory: metric.value }))
            break
          case 'DISK_USAGE':
            grouped.disk.push({ time: timestamp, value: metric.value })
            setCurrentValues(prev => ({ ...prev, disk: metric.value }))
            break
          case 'NETWORK_THROUGHPUT':
            grouped.network.push({ time: timestamp, value: metric.value })
            setCurrentValues(prev => ({ ...prev, network: metric.value }))
            break
        }
      })
      
      // Keep only last 20 data points for each metric
      Object.keys(grouped).forEach(key => {
        grouped[key] = grouped[key].slice(-20)
      })
      
      setProcessedMetrics(grouped)
    }
  }, [metrics])
  
  if (!machine) {
    return (
      <div className="bg-dark-card p-4 rounded border border-gray-700">
        <div className="flex items-center space-x-2 mb-4">
          <Activity className="w-5 h-5 text-cyber-blue" />
          <h2 className="text-lg font-bold text-cyber-blue">METRICS PANEL</h2>
        </div>
        <div className="text-center text-gray-500 py-8">
          Select a machine to view metrics
        </div>
      </div>
    )
  }
  
  return (
    <div className="bg-dark-card p-4 rounded border border-gray-700 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Activity className="w-5 h-5 text-cyber-blue" />
          <h2 className="text-lg font-bold text-cyber-blue">METRICS</h2>
        </div>
        <div className={`px-2 py-1 rounded text-xs ${
          isConnected ? 'bg-cyber-green text-dark-bg' : 'bg-cyber-red text-white'
        }`}>
          {isConnected ? 'LIVE' : 'OFFLINE'}
        </div>
      </div>
      
      {/* Machine Info */}
      <div className="bg-dark-surface p-3 rounded border border-gray-600">
        <div className="text-cyber-purple font-bold">{machine.name}</div>
        <div className="text-sm text-gray-400">{machine.type.replace('_', ' ')}</div>
        <div className="text-xs text-gray-500">ID: {machine.id}</div>
      </div>
      
      {/* Current Metrics Gauges */}
      <div className="space-y-3">
        <MetricGauge
          label="CPU Usage"
          value={currentValues.cpu}
          max={100}
          unit="%"
          color="text-cyber-blue"
          icon={Cpu}
        />
        
        <MetricGauge
          label="Memory Usage"
          value={currentValues.memory}
          max={16}
          unit="GB"
          color="text-cyber-purple"
          icon={MemoryStick}
        />
        
        <MetricGauge
          label="Disk Usage"
          value={currentValues.disk}
          max={1000}
          unit="GB"
          color="text-cyber-orange"
          icon={HardDrive}
        />
        
        <MetricGauge
          label="Network"
          value={currentValues.network}
          max={1000}
          unit="Mbps"
          color="text-cyber-green"
          icon={Wifi}
        />
      </div>
      
      {/* Historical Charts */}
      <div className="space-y-4">
        <MetricChart
          data={processedMetrics.cpu}
          title="CPU Usage History"
          dataKey="value"
          color="#00ffff"
        />
        
        <MetricChart
          data={processedMetrics.memory}
          title="Memory Usage History"
          dataKey="value"
          color="#8a2be2"
        />
      </div>
      
      {/* Stats Summary */}
      <div className="bg-dark-surface p-3 rounded border border-gray-600">
        <div className="text-sm font-medium text-gray-300 mb-2">Session Stats</div>
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div className="text-gray-400">
            Data Points: <span className="text-cyber-blue">{metrics.length}</span>
          </div>
          <div className="text-gray-400">
            Uptime: <span className="text-cyber-green">99.9%</span>
          </div>
          <div className="text-gray-400">
            Avg CPU: <span className="text-cyber-blue">{(currentValues.cpu).toFixed(1)}%</span>
          </div>
          <div className="text-gray-400">
            Avg RAM: <span className="text-cyber-purple">{(currentValues.memory).toFixed(1)}GB</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default MetricsPanel