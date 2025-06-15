# Architecture du Master Dashboard Revolutionary

## 🏗️ Vue d'ensemble

Le Master Dashboard Revolutionary est une application web moderne composée de deux parties principales :

- **Frontend** : Application React avec rendu 3D
- **Backend** : API FastAPI avec WebSocket temps réel

## 🎯 Architecture Générale

```
┌─────────────────┐    WebSocket/HTTP     ┌─────────────────┐
│                 │◄──────────────────────►│                 │
│   Frontend      │        API Calls       │    Backend      │
│   (React)       │◄──────────────────────►│   (FastAPI)     │
│                 │                        │                 │
└─────────────────┘                        └─────────────────┘
         │                                           │
         ▼                                           ▼
┌─────────────────┐                        ┌─────────────────┐
│   Three.js      │                        │   SQLAlchemy    │
│   WebGL         │                        │   Database      │
│   Rendering     │                        │   Layer         │
└─────────────────┘                        └─────────────────┘
```

## 🎨 Frontend Architecture

### Structure des Composants

```
App.jsx
├── ErrorBoundary
└── Dashboard3D
    ├── Scene3D (Three.js Canvas)
    │   ├── MotherboardModel
    │   ├── Lights
    │   └── Controls
    ├── MetricsPanel
    │   ├── CPUMetrics
    │   ├── RAMMetrics
    │   ├── StorageMetrics
    │   └── TemperatureMetrics
    ├── AlertsPanel
    │   ├── AlertList
    │   └── AlertItem
    └── ControlPanel
        ├── MachineSelector
        └── ViewControls
```

### Hooks Personnalisés

#### useWebSocket.js
```javascript
// Gestion des connexions WebSocket temps réel
const useWebSocket = (url) => {
  // État de connexion
  // Messages entrants/sortants
  // Reconnexion automatique
  // Gestion des erreurs
}
```

#### useMetrics.js
```javascript
// Gestion des métriques système
const useMetrics = () => {
  // Données temps réel
  // Historique des métriques
  // Calculs et agrégations
  // Cache local
}
```

### Flux de Données

```
Component Mount
      ↓
WebSocket Connection
      ↓
Subscribe to Metrics
      ↓
Receive Real-time Data
      ↓
Update UI State
      ↓
Render 3D Scene
```

## ⚙️ Backend Architecture

### Structure des Modules

```
app/
├── main.py              # Point d'entrée FastAPI
├── core/                # Configuration et utilitaires
│   ├── config.py        # Variables d'environnement
│   ├── database.py      # Connexion base de données
│   └── websocket.py     # Gestionnaire WebSocket
├── api/                 # Endpoints REST
│   └── v1/
│       ├── endpoints/
│       │   ├── machines.py
│       │   ├── metrics.py
│       │   ├── alerts.py
│       │   └── config.py
│       └── api.py       # Router principal
├── models/              # Modèles de données
│   ├── base.py
│   ├── machine.py
│   ├── metrics.py
│   └── alert.py
├── schemas/             # Schémas Pydantic
│   ├── machine.py
│   ├── metrics.py
│   └── alert.py
└── services/            # Logique métier
    ├── hardware.py      # Service métriques
    ├── alert.py         # Service alertes
    └── websocket.py     # Service WebSocket
```

### API Endpoints

```
GET  /api/v1/machines           # Liste des machines
GET  /api/v1/machines/{id}      # Détails d'une machine
GET  /api/v1/metrics/{id}       # Métriques d'une machine
GET  /api/v1/alerts             # Liste des alertes
POST /api/v1/alerts/{id}/ack    # Acquitter une alerte
WS   /ws                        # WebSocket temps réel
```

### Flux WebSocket

```
Client Connection
      ↓
Authentication (optionnel)
      ↓
Subscription Setup
      ↓
Periodic Data Broadcast
      ↓
Real-time Updates
```

## 🔄 Communication Frontend-Backend

### REST API
```javascript
// Configuration initiale
GET /api/v1/machines
↓
// Sélection d'une machine
GET /api/v1/machines/server-01
↓
// Récupération des métriques
GET /api/v1/metrics/server-01
```

### WebSocket
```javascript
// Connexion temps réel
ws://localhost:8000/ws
↓
// Messages bidirectionnels
{
  "type": "metrics_update",
  "machine_id": "server-01",
  "data": { ... }
}
```

## 🎮 Rendu 3D (Three.js)

### Pipeline de Rendu

```
Scene Setup
├── Camera (PerspectiveCamera)
├── Lights (AmbientLight + DirectionalLight)
├── Models (GLTF/GLB ou géométries custom)
└── Materials (MeshStandardMaterial avec effets)
      ↓
Render Loop
├── Update Animations
├── Process User Input
├── Update Materials (couleurs selon métriques)
└── Render Frame
```

### Composants 3D

```javascript
// MotherboardModel.jsx
const MotherboardModel = ({ metrics }) => {
  // Géométrie de la carte mère
  // Composants (CPU, RAM, GPU)
  // Matériaux dynamiques
  // Animations basées sur les données
}
```

## 📊 Gestion des États

### État Global
```javascript
// Contexte principal
const AppContext = {
  selectedMachine: 'server-01',
  metrics: { ... },
  alerts: [ ... ],
  connectionStatus: 'connected',
  theme: 'cyberpunk'
}
```

### État Local des Composants
```javascript
// Exemple MetricsPanel
const [metrics, setMetrics] = useState(null);
const [loading, setLoading] = useState(true);
const [error, setError] = useState(null);
```

## 🔒 Sécurité

### Frontend
- Validation des données entrantes
- Sanitisation des entrées utilisateur
- Gestion des erreurs et états d'exception
- Protection contre les injections XSS

### Backend
- Validation Pydantic des schémas
- Gestion des erreurs HTTP appropriées
- Rate limiting (à implémenter)
- CORS configuré

## 🚀 Performance

### Frontend
- React.memo pour éviter les re-renders
- useMemo et useCallback pour l'optimisation
- Lazy loading des composants
- Debouncing des interactions utilisateur
- Optimisation Three.js (geometry caching, material reuse)

### Backend
- Async/await pour la concurrence
- Connection pooling SQLAlchemy
- Cache en mémoire pour les données fréquentes
- Compression des réponses HTTP

## 📱 Responsive Design

### Breakpoints
```css
/* Mobile First */
@media (min-width: 640px)  { /* sm */ }
@media (min-width: 768px)  { /* md */ }
@media (min-width: 1024px) { /* lg */ }
@media (min-width: 1280px) { /* xl */ }
```

### Adaptations
- Layout flexible avec CSS Grid/Flexbox
- Contrôles tactiles pour mobile
- Menu burger sur petits écrans
- Panneaux empilables sur mobile

## 🔧 Configuration

### Variables d'Environnement

#### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
VITE_DEBUG=true
```

#### Backend
```env
DATABASE_URL=sqlite:///./dashboard.db
SECRET_KEY=your-secret-key
ALLOWED_ORIGINS=http://localhost:3000
WEBSOCKET_HEARTBEAT_INTERVAL=30
```

## 🔍 Monitoring et Debugging

### Frontend
- React DevTools support
- Console logging avec niveaux
- Error boundaries pour crash recovery
- Performance monitoring hooks

### Backend
- Logging structuré avec Python logging
- Health check endpoints
- Métriques d'utilisation internes
- Error tracking et reporting

## 🔄 Déploiement

### Développement
```bash
./start.sh  # Démarre frontend + backend
```

### Production
```bash
# Build frontend
npm run build

# Servir avec nginx/apache
# Backend avec gunicorn/uvicorn
```

### Docker (Futur)
```dockerfile
# Multi-stage build
# Frontend -> Static files
# Backend -> Python app
# Nginx -> Reverse proxy
```

Cette architecture modulaire permet une maintenance facile, des tests isolés, et une scalabilité future.