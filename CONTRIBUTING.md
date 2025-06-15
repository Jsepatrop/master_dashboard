# Contributing to Master Dashboard Revolutionary

Nous sommes ravis que vous souhaitiez contribuer au Master Dashboard Revolutionary ! Ce guide vous aidera à démarrer.

## 📋 Code de Conduite

En participant à ce projet, vous acceptez de respecter notre code de conduite. Soyez respectueux et constructif dans toutes vos interactions.

## 🚀 Comment Contribuer

### Signaler des Bugs

1. Vérifiez que le bug n'a pas déjà été signalé
2. Créez une issue détaillée avec :
   - Description claire du problème
   - Étapes pour reproduire
   - Comportement attendu vs observé
   - Screenshots si applicable
   - Informations système (OS, navigateur, versions)

### Proposer des Fonctionnalités

1. Ouvrez une issue de type "Feature Request"
2. Décrivez clairement :
   - Le problème que la fonctionnalité résout
   - La solution proposée
   - Les alternatives considérées
   - Des mockups si applicable

### Développement

#### Configuration de l'Environnement

```bash
# Cloner le repository
git clone https://github.com/votre-username/master-dashboard-revolutionary.git
cd master-dashboard-revolutionary

# Installer les dépendances
./start.sh
```

#### Workflow de Développement

1. **Fork** le repository
2. **Créer une branche** pour votre fonctionnalité :
   ```bash
   git checkout -b feature/nom-de-la-fonctionnalite
   ```
3. **Développer** votre fonctionnalité
4. **Tester** vos changements
5. **Commiter** avec des messages clairs :
   ```bash
   git commit -m "feat: ajouter visualisation réseau 3D"
   ```
6. **Pousser** votre branche :
   ```bash
   git push origin feature/nom-de-la-fonctionnalite
   ```
7. **Ouvrir une Pull Request**

## 📝 Standards de Code

### Frontend (React/JavaScript)

- Utiliser les hooks React modernes
- Nommer les composants en PascalCase
- Utiliser des noms de props descriptifs
- Commenter le code complexe
- Suivre les conventions ESLint

```jsx
// ✅ Bon exemple
const MetricsPanel = ({ metrics, onRefresh }) => {
  const [isLoading, setIsLoading] = useState(false);
  
  // Rafraîchir les métriques toutes les 5 secondes
  useEffect(() => {
    const interval = setInterval(onRefresh, 5000);
    return () => clearInterval(interval);
  }, [onRefresh]);
  
  return (
    <div className="metrics-panel">
      {/* Contenu du composant */}
    </div>
  );
};
```

### Backend (Python/FastAPI)

- Suivre PEP 8
- Utiliser des type hints
- Documenter les fonctions avec docstrings
- Gérer les erreurs appropriément

```python
# ✅ Bon exemple
async def get_hardware_metrics(machine_id: str) -> HardwareMetrics:
    """
    Récupère les métriques matérielles pour une machine donnée.
    
    Args:
        machine_id: Identifiant unique de la machine
        
    Returns:
        HardwareMetrics: Métriques actuelles de la machine
        
    Raises:
        HTTPException: Si la machine n'existe pas
    """
    try:
        return await hardware_service.get_metrics(machine_id)
    except MachineNotFoundError:
        raise HTTPException(status_code=404, detail="Machine not found")
```

### CSS/Styling

- Utiliser Tailwind CSS en priorité
- Classes CSS personnalisées dans `globals.css` pour les styles complexes
- Maintenir le thème cyberpunk cohérent
- Utiliser les variables CSS pour les couleurs

```css
/* ✅ Bon exemple */
.neon-button {
  @apply bg-transparent border border-cyan-400 text-cyan-400;
  @apply hover:bg-cyan-400 hover:text-black;
  @apply transition-all duration-300;
  box-shadow: 0 0 10px var(--primary-cyan);
}
```

## 🧪 Tests

### Frontend
```bash
cd frontend
npm run test
```

### Backend
```bash
cd backend
pytest
```

## 📖 Documentation

- Mettre à jour le README.md si nécessaire
- Documenter les nouvelles APIs dans le code
- Ajouter des exemples d'utilisation
- Mettre à jour le CHANGELOG.md

## 🏆 Types de Contributions

### 🐛 Corrections de Bugs
- Corrections de dysfonctionnements
- Améliorations de performance
- Corrections de sécurité

### ✨ Nouvelles Fonctionnalités
- Nouveaux types de visualisations 3D
- Intégrations avec d'autres systèmes
- Amélirations de l'interface utilisateur

### 📚 Documentation
- Amélioration du README
- Tutoriels et guides
- Commentaires de code

### 🎨 Design et UX
- Améliorations visuelles
- Nouvelles animations
- Optimisations d'accessibilité

## 📋 Checklist Pull Request

Avant de soumettre votre PR, vérifiez que :

- [ ] Le code compile sans erreurs
- [ ] Tous les tests passent
- [ ] Le code suit les standards établis
- [ ] La documentation est mise à jour
- [ ] Les messages de commit sont clairs
- [ ] La PR a une description détaillée
- [ ] Les changements ont été testés localement

## 🤝 Processus de Review

1. **Review automatique** - CI/CD vérifie le build
2. **Review par les pairs** - Un mainteneur examine le code
3. **Tests** - Vérification du bon fonctionnement
4. **Merge** - Intégration dans la branche principale

## 💬 Communication

- **Issues GitHub** - Pour les bugs et fonctionnalités
- **Discussions** - Pour les questions générales
- **Pull Requests** - Pour les reviews de code

## 🏅 Reconnaissance

Tous les contributeurs sont ajoutés au fichier CONTRIBUTORS.md et mentionnés dans les releases.

---

Merci pour votre contribution au Master Dashboard Revolutionary ! 🚀