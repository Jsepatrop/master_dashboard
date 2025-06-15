import React, { useState, useEffect } from 'react'
import { Machine, MetricData } from '@/types'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts'
import { Activity, Cpu, HardDrive, Thermometer, Zap, Monitor } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

interface MetricsPanelProps {
  machine: Machine | null
  metrics: MetricData[]
}

interface MetricCardProps {
  title: string
  value: number
  unit: string
  icon: React.ReactNode
  color: string
  trend?: 'up' | 'down' | 'stable'
  threshold?: number
}

function MetricCard({ title, value, unit, icon, color, trend, threshold }: MetricCardProps) {
  const isOverThreshold = threshold && value > threshold
  
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className={`bg-dark-200/50 backdrop-blur-sm rounded-lg p-4 border transition-all duration-300 ${
        isOverThreshold 
          ? 'border-red-500/50 bg-red-500/10' 
          : 'border-gray-600/30 hover:border-neon-cyan/50'
      }`}
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          <div className={`p-1.5 rounded-md bg-${color}-500/20`}>
            {icon}
          </div>
          <span className="text-sm font-medium text-gray-300">{title}</span>
        </div>
        {trend && (
          <div className={`px-2 py-1 rounded text-xs font-mono ${
            trend === 'up' ? 'text-red-400 bg-red-500/20' :
            trend === 'down' ? 'text-green-400 bg-green-500/20' :
            'text-gray-400 bg-gray-500/20'
          }`}>
            {trend === 'up' ? '↗' : trend === 'down' ? '↘' : '→'}
          </div>
        )}
      </div>
      
      <div className="flex items-baseline space-x-1">
        <span className={`text-2xl font-bold font-mono text-${color}-400`}>
          {value.toFixed(1)}
        </span>
        <span className="text-sm text-gray-400">{unit}</span>
      </div>
      
      {threshold && (
        <div className="mt-2">
          <div className="flex justify-between text-xs text-gray-400 mb-1">
            <span>Threshold</span>
            <span>{threshold}{unit}</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-1">
            <div 
              className={`h-1 rounded-full transition-all duration-500 ${
                isOverThreshold ? 'bg-red-500' : `bg-${color}-500`
              }`}
              style={{ width: `${Math.min((value / threshold) * 100, 100)}%` }}
            />
          </div>
        </div>
      )}
    </motion.div>
  )
}

function MetricsChart({ data, dataKey, color, title }: {
  data: any[]
  dataKey: string
  color: string
  title: string
}) {
  return (
    <div className="bg-dark-200/30 backdrop-blur-sm rounded-lg p-4 border border-gray-600/30">
      <h4 className="text-sm font-semibold text-gray-300 mb-3">{title}</h4>
      <ResponsiveContainer width="100%" height={120}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id={`gradient-${dataKey}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={color} stopOpacity={0.3}/>
              <stop offset="95%" stopColor={color} stopOpacity={0.1}/>
            </linearGradient>
          </defs>
          <XAxis 
            dataKey="time" 
            axisLine={false}
            tickLine={false}
            tick={{ fontSize: 10, fill: '#9ca3af' }}
          />
          <YAxis hide />
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
          <Tooltip 
            contentStyle={{
              backgroundColor: '#1e1e2e',
              border: '1px solid rgba(0, 255, 255, 0.3)',
              borderRadius: '8px',
              color: '#ffffff'
            }}
          />
          <Area
            type="monotone"
            dataKey={dataKey}
            stroke={color}
            strokeWidth={2}
            fill={`url(#gradient-${dataKey})`}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}

const MetricsPanel: React.FC<MetricsPanelProps> = ({ machine, metrics }) => {
  const [realtimeData, setRealtimeData] = useState<any[]>([])
  
  useEffect(() => {
    if (!machine || !metrics.length) return
    
    const machineMetrics = metrics.filter(m => m.machine_id === machine.id)
    const latest = machineMetrics.slice(-20).map((metric, index) => ({
      time: new Date(metric.timestamp).toLocaleTimeString(),
      cpu: machineMetrics.find(m => m.metric_type === 'cpu_usage')?.value || 0,
      memory: machineMetrics.find(m => m.metric_type === 'memory_usage')?.value || 0,
      temperature: machineMetrics.find(m => m.metric_type === 'cpu_temperature')?.value || 0,
      disk: machineMetrics.find(m => m.metric_type === 'disk_usage')?.value || 0,
    }))
    
    setRealtimeData(latest)
  }, [machine, metrics])

  if (!machine) {
    return (
      <div className="h-full flex items-center justify-center p-6">
        <div className="text-center">
          <Monitor className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-400">Select a machine to view metrics</p>
        </div>
      </div>
    )
  }

  const machineMetrics = metrics.filter(m => m.machine_id === machine.id)
  
  const currentMetrics = {
    cpu: machineMetrics.find(m => m.metric_type === 'cpu_usage')?.value || 0,
    memory: machineMetrics.find(m => m.metric_type === 'memory_usage')?.value || 0,
    temperature: machineMetrics.find(m => m.metric_type === 'cpu_temperature')?.value || 0,
    disk: machineMetrics.find(m => m.metric_type === 'disk_usage')?.value || 0,
    gpu: machineMetrics.find(m => m.metric_type === 'gpu_usage')?.value || 0,
    power: machineMetrics.find(m => m.metric_type === 'power_consumption')?.value || 0,
  }

  return (
    <div className="h-full overflow-y-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-cyber font-bold text-neon-cyan flex items-center">
          <Activity className="w-5 h-5 mr-2" />
          Live Metrics
        </h2>
        <div className="text-sm text-gray-400">
          {machine.name}
        </div>
      </div>

      {/* Current Metrics Grid */}
      <div className="grid grid-cols-2 gap-4">
        <MetricCard
          title="CPU Usage"
          value={currentMetrics.cpu}
          unit="%"
          icon={<Cpu className="w-4 h-4" />}
          color="blue"
          threshold={machine.cpu_threshold}
          trend={currentMetrics.cpu > 80 ? 'up' : currentMetrics.cpu < 20 ? 'down' : 'stable'}
        />
        
        <MetricCard
          title="Memory"
          value={currentMetrics.memory}
          unit="%"
          icon={<Activity className="w-4 h-4" />}
          color="purple"
          threshold={machine.memory_threshold}
          trend={currentMetrics.memory > 85 ? 'up' : 'stable'}
        />
        
        <MetricCard
          title="Temperature"
          value={currentMetrics.temperature}
          unit="°C"
          icon={<Thermometer className="w-4 h-4" />}
          color="red"
          threshold={machine.temperature_threshold}
          trend={currentMetrics.temperature > 70 ? 'up' : 'stable'}
        />
        
        <MetricCard
          title="Disk Usage"
          value={currentMetrics.disk}
          unit="%"
          icon={<HardDrive className="w-4 h-4" />}
          color="orange"
          threshold={machine.disk_threshold}
        />
        
        <MetricCard
          title="GPU Usage"
          value={currentMetrics.gpu}
          unit="%"
          icon={<Monitor className="w-4 h-4" />}
          color="green"
        />
        
        <MetricCard
          title="Power"
          value={currentMetrics.power}
          unit="W"
          icon={<Zap className="w-4 h-4" />}
          color="yellow"
        />
      </div>

      {/* Charts Section */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-200">Performance Trends</h3>
        
        <MetricsChart
          data={realtimeData}
          dataKey="cpu"
          color="#3b82f6"
          title="CPU Usage Over Time"
        />
        
        <MetricsChart
          data={realtimeData}
          dataKey="memory"
          color="#8b5cf6"
          title="Memory Usage Over Time"
        />
        
        <MetricsChart
          data={realtimeData}
          dataKey="temperature"
          color="#ef4444"
          title="Temperature Over Time"
        />
      </div>

      {/* System Information */}
      <div className="bg-dark-200/30 backdrop-blur-sm rounded-lg p-4 border border-gray-600/30">
        <h4 className="text-sm font-semibold text-gray-300 mb-3">System Information</h4>
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div>
            <span className="text-gray-400">OS:</span>
            <span className="ml-2 text-white">{machine.os_name} {machine.os_version}</span>
          </div>
          <div>
            <span className="text-gray-400">Architecture:</span>
            <span className="ml-2 text-white">{machine.architecture}</span>
          </div>
          <div>
            <span className="text-gray-400">Hostname:</span>
            <span className="ml-2 text-white font-mono">{machine.hostname}</span>
          </div>
          <div>
            <span className="text-gray-400">Last Seen:</span>
            <span className="ml-2 text-white">
              {machine.last_seen ? new Date(machine.last_seen).toLocaleString() : 'Never'}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default MetricsPanel