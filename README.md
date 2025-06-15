# Master Dashboard Revolutionary 🚀

![Master Dashboard Revolutionary](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![React](https://img.shields.io/badge/React-18.2.0-blue)
![Three.js](https://img.shields.io/badge/Three.js-0.158.0-orange)
![License](https://img.shields.io/badge/License-MIT-green)

## 📋 Description

**Master Dashboard Revolutionary** est un tableau de bord révolutionnaire de surveillance d'infrastructure 3D en temps réel. Cette application web moderne combine la puissance de React, Three.js et WebSocket pour offrir une expérience de monitoring immersive avec un thème cyberpunk futuriste.

### ✨ Fonctionnalités Principales

- 🎮 **Dashboard 3D Interactif** - Visualisation 3D des composants matériels
- 📊 **Surveillance en Temps Réel** - Métriques CPU, RAM, température en direct
- 🚨 **Système d'Alertes** - Notifications intelligentes et gestion des priorités
- 🌐 **WebSocket Integration** - Communication bidirectionnelle temps réel
- 🎨 **Thème Cyberpunk** - Interface futuriste avec effets néon
- 📱 **Design Responsive** - Compatible mobile et desktop
- ⚡ **Performance Optimisée** - Rendu 3D fluide et interactions rapides

## 🏗️ Architecture Technique

### Frontend
- **React 18.2.0** - Framework UI moderne
- **Three.js 0.158.0** - Rendu 3D WebGL
- **@react-three/fiber** - Intégration React/Three.js
- **@react-three/drei** - Helpers 3D avancés
- **Vite 5.0.6** - Build tool ultra-rapide
- **Tailwind CSS 3.3.6** - Framework CSS utilitaire

### Backend
- **FastAPI** - Framework Python moderne
- **WebSocket** - Communication temps réel
- **SQLAlchemy** - ORM base de données
- **Pydantic** - Validation des données
- **Uvicorn** - Serveur ASGI haute performance

## 🚀 Installation

### Prérequis
- Node.js 18+ et npm
- Python 3.8+
- Git

### Installation Rapide

```bash
# 1. Cloner le repository
git clone https://github.com/votre-username/master-dashboard-revolutionary.git
cd master-dashboard-revolutionary

# 2. Démarrer l'application complète
./start.sh
```

### Installation Manuelle

#### Frontend
```bash
cd frontend
npm install --legacy-peer-deps
npm run dev
```

#### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🎯 Utilisation

1. **Démarrer l'application** : `./start.sh`
2. **Accéder au dashboard** : http://localhost:3000
3. **Sélectionner une machine** : Utiliser le panneau de contrôle
4. **Explorer la vue 3D** : Cliquer et faire glisser pour naviguer
5. **Surveiller les métriques** : Visualiser les données en temps réel
6. **Gérer les alertes** : Consulter le panneau d'alertes

## 📁 Structure du Projet

```
master-dashboard-revolutionary/
├── 📁 frontend/                 # Application React
│   ├── 📁 src/
│   │   ├── 📁 components/       # Composants React
│   │   │   ├── Dashboard3D.jsx  # Dashboard 3D principal
│   │   │   ├── MotherboardModel.jsx # Modèles 3D
│   │   │   ├── MetricsPanel.jsx # Panneau métriques
│   │   │   ├── AlertsPanel.jsx  # Panneau alertes
│   │   │   └── ControlPanel.jsx # Panneau contrôle
│   │   ├── 📁 hooks/           # Hooks personnalisés
│   │   │   ├── useWebSocket.js # WebSocket hook
│   │   │   └── useMetrics.js   # Métriques hook
│   │   ├── 📁 utils/           # Utilitaires
│   │   │   └── api.js          # API client
│   │   └── 📁 styles/          # Styles CSS
│   │       └── globals.css     # Styles globaux
│   ├── package.json            # Dépendances npm
│   ├── vite.config.js          # Configuration Vite
│   └── tailwind.config.js      # Configuration Tailwind
├── 📁 backend/                 # API FastAPI
│   ├── 📁 app/
│   │   ├── 📁 api/             # Endpoints API
│   │   ├── 📁 core/            # Configuration core
│   │   ├── 📁 models/          # Modèles données
│   │   ├── 📁 schemas/         # Schémas Pydantic
│   │   ├── 📁 services/        # Services métier
│   │   └── main.py             # Point d'entrée
│   └── requirements.txt        # Dépendances Python
├── start.sh                    # Script démarrage
├── README.md                   # Documentation
└── .gitignore                  # Fichiers ignorés
```

## 🎮 Fonctionnalités Détaillées

### Dashboard 3D
- Navigation intuitive avec contrôles souris/tactile
- Zoom et rotation fluides
- Modèles 3D détaillés des composants hardware
- Animations et transitions cyberpunk

### Surveillance Temps Réel
- Métriques CPU, RAM, stockage, température
- Graphiques animés et indicateurs visuels
- Historique des performances
- Alertes automatiques basées sur seuils

### Interface Utilisateur
- Thème sombre cyberpunk avec effets néon
- Typographie futuriste (Orbitron, Rajdhani)
- Animations CSS avancées
- Design responsive multi-plateforme

## 🛠️ Développement

### Scripts Disponibles

```bash
# Frontend
npm run dev          # Serveur développement
npm run build        # Build production
npm run preview      # Prévisualisation build

# Backend
uvicorn app.main:app --reload  # Serveur développement
pytest                         # Tests unitaires
```

### Configuration

#### Variables d'Environnement

**Frontend (.env.development)**
```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
VITE_APP_TITLE=Master Dashboard Revolutionary
```

**Backend**
```env
DATABASE_URL=sqlite:///./dashboard.db
SECRET_KEY=your-secret-key
ALLOWED_ORIGINS=http://localhost:3000
```

## 🎨 Personnalisation

### Thème Cyberpunk
Modifiez les variables CSS dans `frontend/src/styles/globals.css` :

```css
:root {
  --primary-cyan: #00ffff;
  --primary-purple: #8a2be2;
  --accent-green: #00ff41;
  --warning-orange: #ff8c00;
  --critical-red: #ff0040;
}
```

### Ajout de Nouvelles Métriques
1. Étendre le schéma `HardwareMetrics` dans `backend/app/schemas/`
2. Modifier le service `HardwareService` dans `backend/app/services/`
3. Mettre à jour les composants React dans `frontend/src/components/`

## 🚀 Déploiement

### Production

```bash
# Build frontend
cd frontend && npm run build

# Démarrer backend en production
cd backend && gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Docker (Optionnel)

```dockerfile
# Dockerfile exemple
FROM node:18-alpine as frontend
WORKDIR /app
COPY frontend/ .
RUN npm install --legacy-peer-deps && npm run build

FROM python:3.9-slim as backend
WORKDIR /app
COPY backend/ .
RUN pip install -r requirements.txt
COPY --from=frontend /app/dist ./static
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🤝 Contribution

1. Fork le project
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📝 Changelog

### v1.0.0 (2025-06-15)
- ✅ Dashboard 3D interactif complet
- ✅ Surveillance temps réel
- ✅ Système d'alertes
- ✅ Thème cyberpunk
- ✅ Documentation complète

## 📄 License

Distribué sous la licence MIT. Voir `LICENSE` pour plus d'informations.

## 👨‍💻 Auteur

**Master Dashboard Revolutionary Team**
- Email: support@master-dashboard.dev
- GitHub: [@master-dashboard](https://github.com/master-dashboard)

## 🙏 Remerciements

- [Three.js](https://threejs.org/) - Bibliothèque 3D WebGL
- [React Three Fiber](https://docs.pmnd.rs/react-three-fiber) - Intégration React/Three.js
- [FastAPI](https://fastapi.tiangolo.com/) - Framework Python moderne
- [Tailwind CSS](https://tailwindcss.com/) - Framework CSS utilitaire
- [Vite](https://vitejs.dev/) - Build tool ultra-rapide

---

<div align="center">
  <strong>Master Dashboard Revolutionary - L'avenir du monitoring est arrivé! 🚀</strong>
</div>