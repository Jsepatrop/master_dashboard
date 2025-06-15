import React, { useRef, useEffect, useState } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Environment, Grid, Text, Html } from '@react-three/drei'
import * as THREE from 'three'
import MotherboardModel from './MotherboardModel'

function CameraController({ selectedMachine }) {
  const controlsRef = useRef()
  
  useEffect(() => {
    if (selectedMachine && controlsRef.current) {
      const position = selectedMachine.position
      controlsRef.current.setLookAt(
        position.x + 3, position.y + 2, position.z + 3,
        position.x, position.y, position.z,
        true
      )
    }
  }, [selectedMachine])
  
  return (
    <OrbitControls
      ref={controlsRef}
      enablePan={true}
      enableZoom={true}
      enableRotate={true}
      minDistance={2}
      maxDistance={20}
      maxPolarAngle={Math.PI / 2}
      target={[0, 0, 0]}
    />
  )
}

function SceneGrid() {
  return (
    <Grid
      args={[20, 20]}
      cellSize={1}
      cellThickness={0.5}
      cellColor="#00ffff"
      sectionSize={5}
      sectionThickness={1}
      sectionColor="#8a2be2"
      fadeDistance={25}
      fadeStrength={1}
      followCamera={false}
      infiniteGrid={true}
    />
  )
}

function FloatingParticles() {
  const particlesRef = useRef()
  const particleCount = 200
  
  const positions = new Float32Array(particleCount * 3)
  const colors = new Float32Array(particleCount * 3)
  
  for (let i = 0; i < particleCount; i++) {
    positions[i * 3] = (Math.random() - 0.5) * 50
    positions[i * 3 + 1] = Math.random() * 20
    positions[i * 3 + 2] = (Math.random() - 0.5) * 50
    
    // Cyberpunk colors
    const color = new THREE.Color()
    color.setHSL(Math.random() > 0.5 ? 0.5 : 0.8, 1, 0.5)
    colors[i * 3] = color.r
    colors[i * 3 + 1] = color.g
    colors[i * 3 + 2] = color.b
  }
  
  useFrame((state) => {
    if (particlesRef.current) {
      particlesRef.current.rotation.y += 0.001
      particlesRef.current.position.y = Math.sin(state.clock.elapsedTime * 0.5) * 0.1
    }
  })
  
  return (
    <points ref={particlesRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={particleCount}
          array={positions}
          itemSize={3}
        />
        <bufferAttribute
          attach="attributes-color"
          count={particleCount}
          array={colors}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.1}
        vertexColors={true}
        transparent={true}
        opacity={0.6}
        blending={THREE.AdditiveBlending}
      />
    </points>
  )
}

function MachineLabel({ machine, position }) {
  const [hovered, setHovered] = useState(false)
  
  return (
    <Html
      position={[position.x, position.y + 1.5, position.z]}
      center
      distanceFactor={8}
      occlude
    >
      <div 
        className={`px-3 py-1 rounded text-sm font-bold transition-all ${
          hovered 
            ? 'bg-cyber-blue text-dark-bg shadow-neon' 
            : 'bg-dark-surface text-cyber-blue border border-cyber-blue'
        }`}
        onPointerEnter={() => setHovered(true)}
        onPointerLeave={() => setHovered(false)}
      >
        {machine.name}
        <div className="text-xs opacity-75">
          {machine.type.replace('_', ' ')}
        </div>
      </div>
    </Html>
  )
}

function Dashboard3D({ 
  machines = [], 
  metrics = {}, 
  selectedMachine, 
  onMachineSelect, 
  onMachineHover,
  alerts = []
}) {
  const sceneRef = useRef()
  
  return (
    <div className="w-full h-full bg-gradient-to-b from-dark-bg to-dark-surface">
      <Canvas
        ref={sceneRef}
        camera={{ position: [5, 5, 5], fov: 60 }}
        gl={{ 
          antialias: true, 
          alpha: true,
          powerPreference: "high-performance"
        }}
        onCreated={({ gl }) => {
          gl.toneMapping = THREE.ACESFilmicToneMapping
          gl.toneMappingExposure = 1.2
          gl.shadowMap.enabled = true
          gl.shadowMap.type = THREE.PCFSoftShadowMap
        }}
      >
        {/* Lighting */}
        <ambientLight intensity={0.3} color="#00ffff" />
        <directionalLight
          position={[10, 10, 5]}
          intensity={1}
          color="#ffffff"
          castShadow
          shadow-mapSize={[2048, 2048]}
          shadow-camera-far={50}
          shadow-camera-left={-20}
          shadow-camera-right={20}
          shadow-camera-top={20}
          shadow-camera-bottom={-20}
        />
        <pointLight position={[0, 5, 0]} intensity={0.5} color="#8a2be2" />
        <pointLight position={[-5, 2, -5]} intensity={0.3} color="#00ff41" />
        <pointLight position={[5, 2, 5]} intensity={0.3} color="#ff8c00" />

        {/* Environment */}
        <Environment preset="night" />
        <fog attach="fog" args={['#0a0a0a', 10, 50]} />
        
        {/* Scene Elements */}
        <SceneGrid />
        <FloatingParticles />
        
        {/* Machine Motherboards */}
        {machines.map((machine) => {
          const machineMetrics = metrics[machine.id] || []
          const machineAlerts = alerts.filter(alert => alert.machine_id === machine.id && alert.is_active)
          const isSelected = selectedMachine?.id === machine.id
          
          return (
            <group key={machine.id}>
              <MotherboardModel
                machine={machine}
                metrics={machineMetrics}
                alerts={machineAlerts}
                isSelected={isSelected}
                onClick={() => onMachineSelect(machine)}
                onHover={() => onMachineHover(machine)}
              />
              <MachineLabel 
                machine={machine} 
                position={machine.position}
              />
            </group>
          )
        })}
        
        {/* Camera Controls */}
        <CameraController selectedMachine={selectedMachine} />
      </Canvas>
      
      {/* 3D Scene Info Overlay */}
      <div className="absolute bottom-4 left-4 bg-dark-surface bg-opacity-80 p-3 rounded border border-cyber-blue">
        <div className="text-cyber-blue text-sm font-bold mb-1">SCENE INFO</div>
        <div className="text-xs text-gray-300 space-y-1">
          <div>Objects: {machines.length}</div>
          <div>Camera: FREE</div>
          <div>Rendering: WebGL</div>
          <div className="text-cyber-green">60 FPS</div>
        </div>
      </div>
      
      {/* Controls Help */}
      <div className="absolute bottom-4 right-4 bg-dark-surface bg-opacity-80 p-3 rounded border border-cyber-purple">
        <div className="text-cyber-purple text-sm font-bold mb-1">CONTROLS</div>
        <div className="text-xs text-gray-300 space-y-1">
          <div>Left Click + Drag: Rotate</div>
          <div>Right Click + Drag: Pan</div>
          <div>Scroll: Zoom</div>
          <div>Click Machine: Select</div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard3D
