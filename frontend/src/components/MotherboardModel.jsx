import React, { useRef, useEffect, useState } from 'react'
import { useFrame } from '@react-three/fiber'
import { Box, Sphere, Cylinder, RoundedBox } from '@react-three/drei'
import * as THREE from 'three'

function PCBComponent({ position, size, color, type, isActive, alertLevel }) {
  const meshRef = useRef()
  const [hovered, setHovered] = useState(false)
  
  useFrame((state) => {
    if (meshRef.current && isActive) {
      const pulse = Math.sin(state.clock.elapsedTime * 2) * 0.05 + 1
      meshRef.current.scale.setScalar(pulse)
      
      if (alertLevel === 'CRITICAL') {
        meshRef.current.material.emissive.setHex(0xff0040)
        meshRef.current.material.emissiveIntensity = Math.sin(state.clock.elapsedTime * 4) * 0.3 + 0.2
      } else if (alertLevel === 'WARNING') {
        meshRef.current.material.emissive.setHex(0xff8c00)
        meshRef.current.material.emissiveIntensity = 0.1
      } else {
        meshRef.current.material.emissive.setHex(color)
        meshRef.current.material.emissiveIntensity = hovered ? 0.3 : 0.1
      }
    }
  })
  
  const getComponentShape = () => {
    switch (type) {
      case 'cpu':
        return (
          <Box
            ref={meshRef}
            args={size}
            position={position}
            onPointerEnter={() => setHovered(true)}
            onPointerLeave={() => setHovered(false)}
          >
            <meshPhongMaterial color={color} transparent opacity={0.9} />
          </Box>
        )
      case 'ram':
        return (
          <RoundedBox
            ref={meshRef}
            args={size}
            position={position}
            radius={0.02}
            smoothness={4}
            onPointerEnter={() => setHovered(true)}
            onPointerLeave={() => setHovered(false)}
          >
            <meshPhongMaterial color={color} transparent opacity={0.8} />
          </RoundedBox>
        )
      case 'capacitor':
        return (
          <Cylinder
            ref={meshRef}
            args={[size[0], size[0], size[2], 8]}
            position={position}
            onPointerEnter={() => setHovered(true)}
            onPointerLeave={() => setHovered(false)}
          >
            <meshPhongMaterial color={color} transparent opacity={0.7} />
          </Cylinder>
        )
      default:
        return (
          <Box
            ref={meshRef}
            args={size}
            position={position}
            onPointerEnter={() => setHovered(true)}
            onPointerLeave={() => setHovered(false)}
          >
            <meshPhongMaterial color={color} transparent opacity={0.6} />
          </Box>
        )
    }
  }
  
  return getComponentShape()
}

function CircuitTraces({ boardSize }) {
  const tracesRef = useRef()
  
  useFrame((state) => {
    if (tracesRef.current) {
      tracesRef.current.material.emissiveIntensity = Math.sin(state.clock.elapsedTime * 3) * 0.1 + 0.2
    }
  })
  
  const tracePoints = []
  const traceColors = []
  
  for (let i = 0; i < 50; i++) {
    const x = (Math.random() - 0.5) * boardSize[0] * 0.8
    const z = (Math.random() - 0.5) * boardSize[2] * 0.8
    const y = boardSize[1] * 0.5 + 0.001
    
    tracePoints.push(x, y, z)
    traceColors.push(0, 1, 1)
  }
  
  return (
    <points ref={tracesRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={tracePoints.length / 3}
          array={new Float32Array(tracePoints)}
          itemSize={3}
        />
        <bufferAttribute
          attach="attributes-color"
          count={traceColors.length / 3}
          array={new Float32Array(traceColors)}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.02}
        vertexColors={true}
        transparent={true}
        opacity={0.8}
        emissive="#00ffff"
        emissiveIntensity={0.2}
      />
    </points>
  )
}

function MotherboardModel({ 
  machine, 
  metrics = [], 
  alerts = [], 
  isSelected, 
  onClick, 
  onHover 
}) {
  const groupRef = useRef()
  const boardRef = useRef()
  const [boardHovered, setBoardHovered] = useState(false)
  
  const getMachineConfig = (type) => {
    const configs = {
      WEB_SERVER: {
        boardColor: '#1a4a1a',
        components: [
          { type: 'cpu', position: [0, 0.05, 0], size: [0.3, 0.1, 0.3], color: '#00ff41' },
          { type: 'ram', position: [-0.4, 0.03, 0.2], size: [0.15, 0.06, 0.4], color: '#00ffff' },
          { type: 'ram', position: [-0.4, 0.03, -0.2], size: [0.15, 0.06, 0.4], color: '#00ffff' }
        ]
      },
      DATABASE_SERVER: {
        boardColor: '#4a1a4a',
        components: [
          { type: 'cpu', position: [0, 0.05, 0], size: [0.4, 0.12, 0.4], color: '#8a2be2' },
          { type: 'ram', position: [-0.5, 0.04, 0.3], size: [0.12, 0.08, 0.3], color: '#00ffff' },
          { type: 'storage', position: [0.4, 0.03, 0], size: [0.2, 0.06, 0.6], color: '#ff0040' }
        ]
      },
      LOAD_BALANCER: {
        boardColor: '#4a4a1a',
        components: [
          { type: 'cpu', position: [0, 0.05, 0], size: [0.25, 0.08, 0.25], color: '#ffff00' },
          { type: 'network', position: [-0.3, 0.04, 0.4], size: [0.2, 0.08, 0.15], color: '#00ff41' },
          { type: 'ram', position: [0, 0.03, -0.4], size: [0.4, 0.06, 0.12], color: '#00ffff' }
        ]
      }
    }
    return configs[type] || configs.WEB_SERVER
  }
  
  const config = getMachineConfig(machine.type)
  const position = machine.position
  
  const getAlertLevel = () => {
    if (alerts.some(alert => alert.level === 'CRITICAL')) return 'CRITICAL'
    if (alerts.some(alert => alert.level === 'WARNING')) return 'WARNING'
    return 'NORMAL'
  }
  
  const alertLevel = getAlertLevel()
  
  const getMetricValue = (type) => {
    const latestMetrics = metrics.slice(-4)
    const metric = latestMetrics.find(m => m.metric_type === type)
    return metric ? metric.value : 0
  }
  
  const cpuUsage = getMetricValue('CPU_USAGE')
  const memoryUsage = getMetricValue('MEMORY_USAGE')
  const diskUsage = getMetricValue('DISK_USAGE')
  const networkUsage = getMetricValue('NETWORK_THROUGHPUT')
  
  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.position.y = position.y + Math.sin(state.clock.elapsedTime + position.x) * 0.05
      
      if (isSelected) {
        groupRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.5) * 0.1
      }
    }
    
    if (boardRef.current) {
      const avgActivity = (cpuUsage + memoryUsage + diskUsage + networkUsage) / 400
      boardRef.current.material.emissiveIntensity = avgActivity * 0.2 + 0.05
    }
  })
  
  const boardSize = [1.2, 0.02, 0.8]
  
  return (
    <group
      ref={groupRef}
      position={[position.x, position.y, position.z]}
      rotation={[position.rotation_x, position.rotation_y, position.rotation_z]}
      onClick={(e) => {
        e.stopPropagation()
        onClick()
      }}
      onPointerEnter={(e) => {
        e.stopPropagation()
        setBoardHovered(true)
        onHover()
      }}
      onPointerLeave={(e) => {
        e.stopPropagation()
        setBoardHovered(false)
      }}
    >
      <Box ref={boardRef} args={boardSize} receiveShadow castShadow>
        <meshPhongMaterial
          color={config.boardColor}
          transparent
          opacity={boardHovered ? 0.9 : 0.7}
          emissive={isSelected ? '#00ffff' : config.boardColor}
          emissiveIntensity={isSelected ? 0.3 : 0.05}
        />
      </Box>
      
      <CircuitTraces boardSize={boardSize} />
      
      {config.components.map((component, index) => {
        let isActive = false
        let componentAlertLevel = alertLevel
        
        switch (component.type) {
          case 'cpu':
            isActive = cpuUsage > 10
            break
          case 'ram':
            isActive = memoryUsage > 10
            break
          case 'storage':
            isActive = diskUsage > 5
            break
          case 'network':
            isActive = networkUsage > 1
            break
          default:
            isActive = Math.random() > 0.7
        }
        
        return (
          <PCBComponent
            key={index}
            position={component.position}
            size={component.size}
            color={component.color}
            type={component.type}
            isActive={isActive}
            alertLevel={componentAlertLevel}
          />
        )
      })}
      
      {isSelected && (
        <mesh position={[0, -0.01, 0]} rotation={[-Math.PI / 2, 0, 0]}>
          <ringGeometry args={[0.8, 0.9, 32]} />
          <meshBasicMaterial
            color="#00ffff"
            transparent
            opacity={0.6}
            side={THREE.DoubleSide}
          />
        </mesh>
      )}
      
      {alertLevel !== 'NORMAL' && (
        <Sphere position={[0, 0.5, 0]} args={[0.1, 16, 16]}>
          <meshBasicMaterial
            color={alertLevel === 'CRITICAL' ? '#ff0040' : '#ff8c00'}
            transparent
            opacity={0.8}
          />
        </Sphere>
      )}
    </group>
  )
}

export default MotherboardModel
