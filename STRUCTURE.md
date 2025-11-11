# Structure du Projet CVRP

## 📁 Architecture Finale

```
projet_ro/
├── 🔧 run_parameter_analysis.py    # Interface principale pour l'analyse des paramètres
├── 📝 main.py                      # Script de base pour exécution simple
├── 📚 readme.md                    # Documentation générale
├── 📦 requirements.txt             # Dépendances Python
│
├── 📊 data/                        # Données du problème
│   ├── instances/                  # Instances CVRP (.vrp)
│   └── solutions/                  # Solutions sauvegardées
│
├── 📖 docs/                        # Documentation
│   ├── README.md
│   └── optimization_guide.md
│
├── 📈 results/                     # Résultats des analyses
│   └── parameter_tests/            # Anciens tests (archive)
│
└── 🐍 src/                         # Code source
    ├── core/                       # 🎯 ALGORITHMES DE BASE (ESSENTIELS)
    │   ├── cvrp_data.py           # Chargement des données CVRP
    │   ├── ga.py                  # Algorithme génétique principal
    │   ├── localsearch.py         # Recherche locale (2-opt)
    │   ├── solution.py            # Gestion des solutions
    │   └── split.py               # Procédure de split
    │
    ├── optimization/               # 🔬 NOUVEAU SYSTÈME D'ANALYSE
    │   ├── ga_parameter_analyzer.py  # Analyse complète des paramètres
    │   └── ga_visualizer.py          # Visualisation graphique
    │
    └── visualization/              # 📊 Visualisation des solutions
        └── plot_solution.py           # Affichage graphique des routes CVRP
```

## 🎯 Fichiers Essentiels Conservés

### Core Algorithms (src/core/)
- **cvrp_data.py** : Parser pour fichiers .vrp, structure de données
- **ga.py** : Implémentation complète de l'algorithme génétique
- **localsearch.py** : Optimisation locale 2-opt
- **solution.py** : Manipulation et évaluation des solutions
- **split.py** : Transformation géant tour → routes CVRP

### Nouveau Système d'Analyse (src/optimization/)
- **ga_parameter_analyzer.py** : 
  - Tests individuels de paramètres
  - Recherche de meilleures combinaisons
  - Multi-threading (ProcessPoolExecutor)
  - Export/Import JSON
  
- **ga_visualizer.py** :
  - Graphiques matplotlib/seaborn
  - Visualisation de l'impact des paramètres
  - Comparaisons et rapports

### Visualisation (src/visualization/)
- **plot_solution.py** : 
  - Affichage graphique des routes CVRP
  - Utilise matplotlib pour visualiser les solutions
  - Montre le dépôt et les tournées en couleurs différentes
- **run_parameter_analysis.py** : Interface menu pour analyses complètes
- **main.py** : Exécution simple de l'algorithme

## 🗑️ Fichiers Supprimés (Obsolètes)

- ❌ `advanced_optimizer.py` - Ancien système sans multi-threading efficace
- ❌ `parameter_analyzer.py` - Première version incomplète
- ❌ `quick_parameter_test.py` - Tests rapides obsolètes
- ❌ `quick_test.py` - Tests basiques remplacés
- ❌ `ultra_quick_test.py` - Tests ultra-rapides obsolètes
- ❌ `parallel_config_test.py` - Ancien système de parallélisation
- ❌ `plot_results.py` - Ancien visualiseur de résultats de tests (1092 lignes)
- ❌ `examples/` - Dossier vide
- ❌ Fichiers .txt de résultats à la racine

## 🚀 Utilisation

### Analyse Complète des Paramètres
```bash
python run_parameter_analysis.py
# Choisir l'option 7 pour une analyse complète automatique
```

### Exécution Simple
```bash
python main.py
```

## 📊 Fonctionnalités du Nouveau Système

1. **Tests Individuels** : Varie un paramètre à la fois (77 configs)
2. **Meilleures Combinaisons** : Trouve les combinaisons optimales
3. **Multi-threading** : Utilise tous vos cores (12 workers)
4. **Visualisation** : Graphiques automatiques (matplotlib/seaborn)
5. **Sauvegarde** : Export JSON + PNG des résultats
6. **Reproductibilité** : Charge des analyses précédentes

## 🔧 Paramètres Analysés

- `pop_size` : Taille de la population (30-300)
- `tournament_k` : Taille du tournoi (2-8)
- `elitism` : Nombre d'élites conservées (0-30)
- `pc` : Probabilité de croisement (0.6-0.98)
- `pm` : Probabilité de mutation (0.005-0.35)
- `two_opt_prob` : Probabilité d'optimisation locale (0.0-1.0)
- `use_2opt` : Activer/désactiver 2-opt (True/False)

---
*Dernière mise à jour : 9 novembre 2025*
