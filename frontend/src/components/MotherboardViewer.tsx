import React, { useRef, useEffect } from 'react'
import { useFrame, useThree } from '@react-three/fiber'
import { Text, Box, Sphere, Cylinder } from '@react-three/drei'
import * as THREE from 'three'
import { Machine, MetricData } from '@/types'
import { getComponentTemperatureColor, getCpuUsageColor, getMemoryUsageColor } from '@/utils/colors'

interface MotherboardViewerProps {
  machine: Machine
  metrics: MetricData[]
}

function CPUComponent({ position, metrics }: { position: [number, number, number], metrics: MetricData[] }) {
  const meshRef = useRef<THREE.Mesh>(null)
  const cpuUsage = metrics.find(m => m.metric_type === 'cpu_usage')?.value || 0
  const cpuTemp = metrics.find(m => m.metric_type === 'cpu_temperature')?.value || 0
  
  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.005 + (cpuUsage / 100) * 0.02
      const scale = 1 + Math.sin(state.clock.elapsedTime * 3) * (cpuUsage / 1000)
      meshRef.current.scale.setScalar(scale)
    }
  })

  return (
    <group position={position}>
      <Box ref={meshRef} args={[1, 0.2, 1]}>
        <meshStandardMaterial 
          color={getCpuUsageColor(cpuUsage)}
          emissive={getCpuUsageColor(cpuUsage)}
          emissiveIntensity={cpuUsage / 200}
        />
      </Box>
      <Text
        position={[0, 0.5, 0]}
        fontSize={0.15}
        color="#00ffff"
        anchorX="center"
      >
        CPU {cpuUsage.toFixed(1)}%
      </Text>
      {/* Temperature indicator */}
      <Cylinder 
        position={[0.6, 0.2, 0]} 
        args={[0.05, 0.05, cpuTemp / 100]}
      >
        <meshBasicMaterial color={getComponentTemperatureColor(cpuTemp)} />
      </Cylinder>
    </group>
  )
}

function GPUComponent({ position, metrics }: { position: [number, number, number], metrics: MetricData[] }) {
  const meshRef = useRef<THREE.Mesh>(null)
  const gpuUsage = metrics.find(m => m.metric_type === 'gpu_usage')?.value || 0
  const gpuTemp = metrics.find(m => m.metric_type === 'gpu_temperature')?.value || 0
  
  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.x += 0.01
      const intensity = gpuUsage / 100
      meshRef.current.position.y = position[1] + Math.sin(state.clock.elapsedTime * 2) * intensity * 0.1
    }
  })

  return (
    <group position={position}>
      <Box ref={meshRef} args={[2, 0.3, 0.8]}>
        <meshStandardMaterial 
          color="#00ff00"
          emissive="#00ff00"
          emissiveIntensity={gpuUsage / 150}
        />
      </Box>
      <Text
        position={[0, 0.6, 0]}
        fontSize={0.12}
        color="#00ff00"
        anchorX="center"
      >
        GPU {gpuUsage.toFixed(1)}%
      </Text>
      {/* Fan simulation */}
      <Cylinder 
        position={[0.8, 0.2, 0]} 
        args={[0.15, 0.15, 0.05]}
        rotation={[0, 0, 0]}
      >
        <meshBasicMaterial color="#333" />
      </Cylinder>
    </group>
  )
}

function RAMModule({ position, index, metrics }: { position: [number, number, number], index: number, metrics: MetricData[] }) {
  const meshRef = useRef<THREE.Mesh>(null)
  const memUsage = metrics.find(m => m.metric_type === 'memory_usage')?.value || 0
  
  useFrame((state) => {
    if (meshRef.current) {
      const offset = index * 0.5
      meshRef.current.position.y = position[1] + Math.sin(state.clock.elapsedTime * 2 + offset) * 0.05
    }
  })

  return (
    <Box ref={meshRef} position={position} args={[0.2, 0.8, 0.05]}>
      <meshStandardMaterial 
        color={getMemoryUsageColor(memUsage)}
        emissive={getMemoryUsageColor(memUsage)}
        emissiveIntensity={memUsage / 300}
      />
    </Box>
  )
}

function StorageDevice({ position, metrics }: { position: [number, number, number], metrics: MetricData[] }) {
  const meshRef = useRef<THREE.Mesh>(null)
  const diskUsage = metrics.find(m => m.metric_type === 'disk_usage')?.value || 0
  
  useFrame(() => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.02
    }
  })

  return (
    <group position={position}>
      <Box ref={meshRef} args={[0.8, 0.1, 1.2]}>
        <meshStandardMaterial 
          color="#ff6600"
          emissive="#ff6600"
          emissiveIntensity={diskUsage / 400}
        />
      </Box>
      <Text
        position={[0, 0.3, 0]}
        fontSize={0.1}
        color="#ff6600"
        anchorX="center"
      >
        SSD {diskUsage.toFixed(1)}%
      </Text>
    </group>
  )
}

function PowerSupplyUnit({ position }: { position: [number, number, number] }) {
  const meshRef = useRef<THREE.Mesh>(null)
  
  useFrame((state) => {
    if (meshRef.current) {
      const intensity = Math.sin(state.clock.elapsedTime * 4) * 0.5 + 0.5
      ;(meshRef.current.material as THREE.MeshStandardMaterial).emissiveIntensity = intensity * 0.3
    }
  })

  return (
    <Box ref={meshRef} position={position} args={[1.5, 0.8, 1]}>
      <meshStandardMaterial 
        color="#ffff00"
        emissive="#ffff00"
        emissiveIntensity={0.2}
      />
    </Box>
  )
}

const MotherboardViewer: React.FC<MotherboardViewerProps> = ({ machine, metrics }) => {
  const groupRef = useRef<THREE.Group>(null)

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.y += 0.002
      groupRef.current.position.y = Math.sin(state.clock.elapsedTime * 0.5) * 0.1
    }
  })

  return (
    <group ref={groupRef} position={[5, 2, 0]}>
      {/* Motherboard Base */}
      <Box args={[4, 0.05, 3]} position={[0, 0, 0]}>
        <meshStandardMaterial 
          color="#0a4d0a"
          emissive="#0a4d0a"
          emissiveIntensity={0.1}
        />
      </Box>
      
      {/* Circuit traces */}
      {Array.from({ length: 20 }, (_, i) => (
        <Box 
          key={i}
          args={[0.02, 0.001, Math.random() * 2 + 0.5]} 
          position={[
            (Math.random() - 0.5) * 3.5,
            0.026,
            (Math.random() - 0.5) * 2.5
          ]}
        >
          <meshBasicMaterial color="#00ffff" />
        </Box>
      ))}

      {/* Components */}
      <CPUComponent position={[0, 0.2, 0]} metrics={metrics} />
      <GPUComponent position={[0, 0.5, -1.5]} metrics={metrics} />
      
      {/* RAM Modules */}
      {Array.from({ length: 4 }, (_, i) => (
        <RAMModule 
          key={i}
          position={[-1.5 + i * 0.3, 0.4, 1]} 
          index={i}
          metrics={metrics}
        />
      ))}
      
      <StorageDevice position={[1.5, 0.15, 0.5]} metrics={metrics} />
      <PowerSupplyUnit position={[-1.8, 0.4, -1]} />
      
      {/* Machine Label */}
      <Text
        position={[0, 1.5, 0]}
        fontSize={0.3}
        color="#00ffff"
        anchorX="center"
        font="/fonts/orbitron.woff"
      >
        {machine.name} - {machine.motherboard_model}
      </Text>
      
      {/* Performance indicators */}
      <group position={[0, -0.5, 0]}>
        {metrics.slice(0, 5).map((metric, index) => (
          <Sphere key={index} position={[index * 0.3 - 0.6, 0, 0]} args={[0.05]}>
            <meshBasicMaterial 
              color={getComponentTemperatureColor(metric.value)} 
            />
          </Sphere>
        ))}
      </group>
    </group>
  )
}

export default MotherboardViewer