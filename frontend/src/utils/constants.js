// Application constants and configuration
export const MACHINE_TYPES = {
  WEB_SERVER: 'WEB_SERVER',
  DATABASE_SERVER: 'DATABASE_SERVER',
  APPLICATION_SERVER: 'APPLICATION_SERVER',
  LOAD_BALANCER: 'LOAD_BALANCER',
  CACHE_SERVER: 'CACHE_SERVER'
}

export const MACHINE_STATUS = {
  ONLINE: 'ONLINE',
  OFFLINE: 'OFFLINE',
  MAINTENANCE: 'MAINTENANCE',
  ERROR: 'ERROR'
}

export const METRIC_TYPES = {
  CPU_USAGE: 'CPU_USAGE',
  MEMORY_USAGE: 'MEMORY_USAGE',
  DISK_USAGE: 'DISK_USAGE',
  NETWORK_THROUGHPUT: 'NETWORK_THROUGHPUT'
}

export const ALERT_LEVELS = {
  NORMAL: 'NORMAL',
  WARNING: 'WARNING',
  CRITICAL: 'CRITICAL'
}

export const CONNECTION_STATUS = {
  CONNECTING: 'CONNECTING',
  CONNECTED: 'CONNECTED',
  DISCONNECTED: 'DISCONNECTED',
  RECONNECTING: 'RECONNECTING',
  FAILED: 'FAILED',
  ERROR: 'ERROR'
}

// Cyberpunk color palette
export const COLORS = {
  CYBER_BLUE: '#00ffff',
  CYBER_PURPLE: '#8a2be2',
  CYBER_GREEN: '#00ff41',
  CYBER_ORANGE: '#ff8c00',
  CYBER_RED: '#ff0040',
  DARK_BG: '#0a0a0a',
  DARK_SURFACE: '#1a1a1a',
  DARK_CARD: '#2a2a2a',
  NEON_GLOW: '#00ffff80'
}

// Machine type configurations
export const MACHINE_CONFIGS = {
  [MACHINE_TYPES.WEB_SERVER]: {
    name: 'Web Server',
    icon: 'Globe',
    color: COLORS.CYBER_GREEN,
    description: 'HTTP/HTTPS web service',
    typical_metrics: {
      CPU_USAGE: { normal: 30, warning: 70, critical: 90 },
      MEMORY_USAGE: { normal: 4, warning: 12, critical: 14 },
      DISK_USAGE: { normal: 200, warning: 800, critical: 950 },
      NETWORK_THROUGHPUT: { normal: 100, warning: 800, critical: 950 }
    }
  },
  [MACHINE_TYPES.DATABASE_SERVER]: {
    name: 'Database Server',
    icon: 'Database',
    color: COLORS.CYBER_PURPLE,
    description: 'Database management system',
    typical_metrics: {
      CPU_USAGE: { normal: 40, warning: 80, critical: 95 },
      MEMORY_USAGE: { normal: 8, warning: 14, critical: 15 },
      DISK_USAGE: { normal: 500, warning: 900, critical: 980 },
      NETWORK_THROUGHPUT: { normal: 200, warning: 700, critical: 900 }
    }
  },
  [MACHINE_TYPES.APPLICATION_SERVER]: {
    name: 'Application Server',
    icon: 'Server',
    color: COLORS.CYBER_ORANGE,
    description: 'Application runtime environment',
    typical_metrics: {
      CPU_USAGE: { normal: 35, warning: 75, critical: 90 },
      MEMORY_USAGE: { normal: 6, warning: 12, critical: 14 },
      DISK_USAGE: { normal: 300, warning: 750, critical: 900 },
      NETWORK_THROUGHPUT: { normal: 150, warning: 600, critical: 800 }
    }
  },
  [MACHINE_TYPES.LOAD_BALANCER]: {
    name: 'Load Balancer',
    icon: 'Layers',
    color: COLORS.CYBER_BLUE,
    description: 'Traffic distribution system',
    typical_metrics: {
      CPU_USAGE: { normal: 20, warning: 60, critical: 80 },
      MEMORY_USAGE: { normal: 2, warning: 8, critical: 12 },
      DISK_USAGE: { normal: 50, warning: 400, critical: 500 },
      NETWORK_THROUGHPUT: { normal: 500, warning: 900, critical: 1000 }
    }
  },
  [MACHINE_TYPES.CACHE_SERVER]: {
    name: 'Cache Server',
    icon: 'Cpu',
    color: COLORS.CYBER_BLUE,
    description: 'High-speed data caching',
    typical_metrics: {
      CPU_USAGE: { normal: 25, warning: 65, critical: 85 },
      MEMORY_USAGE: { normal: 10, warning: 14, critical: 15 },
      DISK_USAGE: { normal: 100, warning: 300, critical: 400 },
      NETWORK_THROUGHPUT: { normal: 300, warning: 800, critical: 950 }
    }
  }
}

// WebSocket configuration
export const WEBSOCKET_CONFIG = {
  RECONNECT_INTERVAL: 3000,
  MAX_RECONNECT_ATTEMPTS: 5,
  HEARTBEAT_INTERVAL: 30000,
  MESSAGE_QUEUE_SIZE: 100
}

// 3D Scene configuration
export const SCENE_CONFIG = {
  CAMERA: {
    FOV: 60,
    NEAR: 0.1,
    FAR: 1000,
    POSITION: [5, 5, 5]
  },
  LIGHTING: {
    AMBIENT_INTENSITY: 0.3,
    DIRECTIONAL_INTENSITY: 1,
    POINT_LIGHTS: [
      { position: [0, 5, 0], intensity: 0.5, color: COLORS.CYBER_PURPLE },
      { position: [-5, 2, -5], intensity: 0.3, color: COLORS.CYBER_GREEN },
      { position: [5, 2, 5], intensity: 0.3, color: COLORS.CYBER_ORANGE }
    ]
  },
  GRID: {
    SIZE: 20,
    DIVISIONS: 20,
    CELL_SIZE: 1,
    COLORS: {
      CELL: COLORS.CYBER_BLUE,
      SECTION: COLORS.CYBER_PURPLE
    }
  },
  PARTICLES: {
    COUNT: 200,
    SPREAD: 50,
    HEIGHT: 20,
    COLORS: [COLORS.CYBER_BLUE, COLORS.CYBER_PURPLE]
  }
}

// Performance thresholds
export const PERFORMANCE_THRESHOLDS = {
  FRAME_RATE_TARGET: 60,
  FRAME_RATE_WARNING: 30,
  FRAME_RATE_CRITICAL: 15,
  MEMORY_WARNING: 512, // MB
  MEMORY_CRITICAL: 1024, // MB
  NETWORK_TIMEOUT: 10000, // ms
  RENDER_DISTANCE: 50
}

// Animation settings
export const ANIMATION_CONFIG = {
  DURATION: {
    FAST: 0.2,
    NORMAL: 0.5,
    SLOW: 1.0
  },
  EASING: {
    EASE_IN_OUT: 'cubic-bezier(0.4, 0, 0.2, 1)',
    EASE_OUT: 'cubic-bezier(0.0, 0, 0.2, 1)',
    EASE_IN: 'cubic-bezier(0.4, 0, 1, 1)'
  },
  MACHINE_HOVER_SCALE: 1.1,
  SELECTION_RING_ROTATION: 0.02,
  FLOATING_AMPLITUDE: 0.05,
  FLOATING_FREQUENCY: 0.5
}

// UI Configuration
export const UI_CONFIG = {
  SIDEBAR_WIDTH: 320,
  HEADER_HEIGHT: 80,
  FOOTER_HEIGHT: 40,
  PANEL_SPACING: 16,
  BORDER_RADIUS: 8,
  SHADOW_BLUR: 20
}

// Data update intervals
export const UPDATE_INTERVALS = {
  METRICS: 5000,     // 5 seconds
  HEALTH_CHECK: 30000, // 30 seconds
  RECONNECT: 3000,    // 3 seconds
  UI_REFRESH: 100     // 100ms for smooth animations
}

// Error messages
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network connection failed',
  WEBSOCKET_ERROR: 'Real-time connection lost',
  API_ERROR: 'Server communication error',
  AUTHENTICATION_ERROR: 'Authentication required',
  PERMISSION_ERROR: 'Insufficient permissions',
  UNKNOWN_ERROR: 'An unexpected error occurred'
}

// Success messages
export const SUCCESS_MESSAGES = {
  CONNECTION_ESTABLISHED: 'Connected to Master Dashboard',
  DATA_UPDATED: 'System data updated successfully',
  ALERT_RESOLVED: 'Alert resolved successfully',
  MACHINE_UPDATED: 'Machine configuration updated'
}

// Local storage keys
export const STORAGE_KEYS = {
  USER_PREFERENCES: 'master_dashboard_preferences',
  LAST_SELECTED_MACHINE: 'master_dashboard_selected_machine',
  VIEW_SETTINGS: 'master_dashboard_view_settings',
  ALERT_SETTINGS: 'master_dashboard_alert_settings'
}

export default {
  MACHINE_TYPES,
  MACHINE_STATUS,
  METRIC_TYPES,
  ALERT_LEVELS,
  CONNECTION_STATUS,
  COLORS,
  MACHINE_CONFIGS,
  WEBSOCKET_CONFIG,
  SCENE_CONFIG,
  PERFORMANCE_THRESHOLDS,
  ANIMATION_CONFIG,
  UI_CONFIG,
  UPDATE_INTERVALS,
  ERROR_MESSAGES,
  SUCCESS_MESSAGES,
  STORAGE_KEYS
}