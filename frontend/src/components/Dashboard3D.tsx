import React, { useRef, useEffect, useState } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { OrbitControls, Environment, PerspectiveCamera, Text } from '@react-three/drei'
import * as THREE from 'three'
import MotherboardViewer from './MotherboardViewer'
import { Machine, MetricData } from '@/types'
import { getMachineColor, getComponentTemperatureColor } from '@/utils/colors'

interface Dashboard3DProps {
  machines: Machine[]
  selectedMachine: Machine | null
  onSelectMachine: (machine: Machine) => void
  metrics: MetricData[]
}

function CameraController({ selectedMachine }: { selectedMachine: Machine | null }) {
  const { camera } = useThree()
  
  useEffect(() => {
    if (selectedMachine) {
      const position = selectedMachine.position_3d
      camera.position.set(
        position.x + 5,
        position.y + 3,
        position.z + 5
      )
      camera.lookAt(position.x, position.y, position.z)
    }
  }, [selectedMachine, camera])

  return null
}

function GridFloor() {
  return (
    <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -1, 0]}>
      <planeGeometry args={[50, 50]} />
      <meshBasicMaterial 
        color="#001122" 
        transparent 
        opacity={0.3}
        wireframe
      />
    </mesh>
  )
}

function ParticleField() {
  const points = useRef<THREE.Points>(null)
  
  const particlesPosition = new Float32Array(1000 * 3)
  
  for (let i = 0; i < 1000; i++) {
    particlesPosition[i * 3] = (Math.random() - 0.5) * 100
    particlesPosition[i * 3 + 1] = Math.random() * 50
    particlesPosition[i * 3 + 2] = (Math.random() - 0.5) * 100
  }

  useFrame((state) => {
    if (points.current) {
      points.current.rotation.y += 0.0005
      points.current.position.y = Math.sin(state.clock.elapsedTime * 0.5) * 0.1
    }
  })

  return (
    <points ref={points}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={1000}
          array={particlesPosition}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial 
        size={0.05} 
        color="#00ffff" 
        transparent 
        opacity={0.6}
        sizeAttenuation={false}
      />
    </points>
  )
}

function MachineNode({ 
  machine, 
  isSelected, 
  onClick, 
  metrics 
}: { 
  machine: Machine
  isSelected: boolean
  onClick: () => void
  metrics: MetricData[]
}) {
  const meshRef = useRef<THREE.Mesh>(null)
  const [hovered, setHovered] = useState(false)
  
  const machineMetrics = metrics.filter(m => m.machine_id === machine.id)
  const color = getMachineColor(machine.status)
  
  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.01
      if (isSelected) {
        meshRef.current.scale.setScalar(1.2 + Math.sin(state.clock.elapsedTime * 2) * 0.1)
      } else if (hovered) {
        meshRef.current.scale.setScalar(1.1)
      } else {
        meshRef.current.scale.setScalar(1.0)
      }
    }
  })

  return (
    <group position={[machine.position_3d.x, machine.position_3d.y, machine.position_3d.z]}>
      <mesh
        ref={meshRef}
        onClick={onClick}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
      >
        <boxGeometry args={[2, 0.2, 3]} />
        <meshStandardMaterial 
          color={color}
          emissive={color}
          emissiveIntensity={isSelected ? 0.5 : 0.2}
          transparent
          opacity={0.8}
        />
      </mesh>
      
      {/* Machine Label */}
      <Text
        position={[0, 1, 0]}
        fontSize={0.3}
        color="#00ffff"
        anchorX="center"
        anchorY="middle"
        font="/fonts/orbitron.woff"
      >
        {machine.name}
      </Text>
      
      {/* Status Indicators */}
      <mesh position={[0, 0.5, 0]}>
        <sphereGeometry args={[0.1]} />
        <meshBasicMaterial color={color} />
      </mesh>
      
      {/* CPU Temperature Visualization */}
      {machineMetrics.length > 0 && (
        <mesh position={[1, 0.3, 0]}>
          <cylinderGeometry args={[0.05, 0.05, 0.5]} />
          <meshBasicMaterial 
            color={getComponentTemperatureColor(
              machineMetrics.find(m => m.metric_type === 'cpu_temperature')?.value || 0
            )}
          />
        </mesh>
      )}
    </group>
  )
}

const Dashboard3D: React.FC<Dashboard3DProps> = ({ 
  machines, 
  selectedMachine, 
  onSelectMachine, 
  metrics 
}) => {
  return (
    <div className="w-full h-full relative">
      {/* FPS Counter */}
      <div className="absolute top-4 right-4 z-10 bg-dark-300/80 backdrop-blur-sm rounded-lg p-2 border border-neon-cyan/30">
        <div className="text-neon-cyan text-sm font-mono">
          FPS: <span className="animate-pulse">60</span>
        </div>
      </div>

      <Canvas
        gl={{ 
          antialias: true, 
          alpha: true,
          powerPreference: "high-performance"
        }}
        dpr={[1, 2]}
        className="bg-transparent"
      >
        <PerspectiveCamera makeDefault position={[0, 5, 10]} />
        <CameraController selectedMachine={selectedMachine} />
        
        {/* Lighting */}
        <ambientLight intensity={0.2} />
        <pointLight position={[10, 10, 10]} intensity={1} color="#00ffff" />
        <pointLight position={[-10, 10, -10]} intensity={0.5} color="#ff00ff" />
        <spotLight
          position={[0, 20, 0]}
          angle={0.3}
          penumbra={1}
          intensity={1}
          color="#ffffff"
          castShadow
        />

        {/* Environment */}
        <Environment preset="night" />
        <fog attach="fog" args={['#050507', 10, 100]} />
        
        {/* Scene Elements */}
        <GridFloor />
        <ParticleField />
        
        {/* Machine Visualizations */}
        {machines.map((machine) => (
          <MachineNode
            key={machine.id}
            machine={machine}
            isSelected={selectedMachine?.id === machine.id}
            onClick={() => onSelectMachine(machine)}
            metrics={metrics}
          />
        ))}
        
        {/* Selected Machine Detail */}
        {selectedMachine && (
          <MotherboardViewer 
            machine={selectedMachine} 
            metrics={metrics.filter(m => m.machine_id === selectedMachine.id)}
          />
        )}

        <OrbitControls
          enablePan={true}
          enableZoom={true}
          enableRotate={true}
          minDistance={3}
          maxDistance={50}
          maxPolarAngle={Math.PI / 2}
        />
      </Canvas>
      
      {/* Machine Info Overlay */}
      {selectedMachine && (
        <div className="absolute bottom-4 left-4 bg-dark-300/90 backdrop-blur-md rounded-lg p-4 border border-neon-cyan/30 max-w-sm">
          <h3 className="text-lg font-cyber font-bold text-neon-cyan mb-2">
            {selectedMachine.name}
          </h3>
          <div className="space-y-1 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Status:</span>
              <span className={`font-semibold ${
                selectedMachine.status === 'online' ? 'text-green-400' : 'text-red-400'
              }`}>
                {selectedMachine.status.toUpperCase()}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Type:</span>
              <span className="text-white">{selectedMachine.machine_type}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">IP:</span>
              <span className="text-white font-mono">{selectedMachine.ip_address}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Dashboard3D