# Structure du Projet CVRP

## 📁 Architecture Complète (Mise à jour : 12 nov 2025)

```
projet_ro/
├── 🔧 Fichiers principaux
│   ├── main.py                          # Point d'entrée principal (résolution CVRP avec GA)
│   ├── run_parameter_analysis.py        # Menu interactif pour analyse de paramètres
│   ├── run_pulp_demo.py                 # 🆕 Modélisation exacte avec PuLP (MIP)
│   ├── multi_depot.py                   # 🆕 Support multi-dépôts
│   ├── test.py                          # 🆕 Script de test
│   ├── readme.md                        # Documentation générale du projet
│   ├── requirements.txt                 # Dépendances Python
│   └── STRUCTURE.md                     # Ce fichier (arborescence du projet)
│
├── 📊 Instances VRP
│   ├── data2.vrp                        # 🆕 Instance VRP #2
│   ├── data3.vrp                        # 🆕 Instance VRP #3
│   ├── data4.vrp                        # 🆕 Instance VRP #4
│   ├── data5.vrp                        # 🆕 Instance VRP #5
│   ├── data6.vrp                        # 🆕 Instance VRP #6
│   ├── p01.vrp                          # 🆕 Instance test (N=50, 4 dépôts)
│   ├── p03_test.vrp                     # 🆕 Instance test (N=10, 3 dépôts)
│   └── debug_model.lp                   # 🆕 Fichier de debug LP (PuLP)
│
├── 🧪 Scripts de démonstration
│   ├── demo_gap_calculation.py          # Démo calcul de gap
│   ├── demo_gap_vs_improvement.py       # Démo comparaison gap vs amélioration
│   ├── demo_multithreading.py           # Démo multi-threading
│   └── test_visualizations_with_gap.py  # Test visualisations avec gap
│
├── 📊 data/                             # Données du problème CVRP
│   ├── instances/
│   │   └── data.vrp                    # Instance CVRP principale (X-n153-k22)
│   └── solutions/
│       ├── solution_data.png           # Visualisation de la solution
│       └── solution_data.sol           # Solution optimale (coût: 22901)
│
├── 📖 docs/                             # Documentation complète
│   ├── README.md                       # README documentation
│   ├── experiment_protocol.md          # ✨ Protocole d'expérimentation v2.0 (gap-based)
│   ├── optimization_guide.md           # Guide d'optimisation des paramètres
│   ├── CVRP_GAP_STANDARDS.md          # Standards de qualité CVRP (scientifique)
│   ├── MULTITHREADING.md              # Documentation multi-threading
│   ├── SOLUTION_REFERENCE.md          # Documentation solution de référence
│   ├── VISUALIZATIONS_GAP.md          # Documentation visualisations gap
│   └── exemple_multithreading.py      # Exemple de code multi-threading
│
├── 📈 results/                          # Résultats des expériences
│   ├── parameter_analysis/             # Analyses complètes de paramètres
│   │   └── (fichiers JSON et visualisations PNG générés)
│   └── parameter_tests/                # Tests de paramètres archivés
│       ├── best_results_summary_*.txt  # Résumés des meilleurs résultats
│       ├── parameter_test_results_*.txt # Résultats détaillés des tests
│       └── ultra_quick_results_*.txt   # Résultats tests rapides
│
└── 🐍 src/                              # Code source principal
    ├── __init__.py
    │
    ├── 📁 core/                        # 🎯 ALGORITHMES DE BASE (ESSENTIELS)
    │   ├── __init__.py
    │   ├── cvrp_data.py               # Chargement des données CVRP
    │   ├── ga.py                      # ✨ Algorithme génétique (avec diversification)
    │   ├── localsearch.py             # Recherche locale (2-opt)
    │   ├── solution.py                # Gestion des solutions
    │   ├── solution_loader.py         # Chargement solution de référence
    │   ├── split.py                   # Procédure de split (giant tour → routes)
    │   └── __pycache__/               # Cache Python (ignoré par Git)
    │
    ├── 📁 optimization/                # 🔬 SYSTÈME D'ANALYSE AVANCÉ
    │   ├── __init__.py
    │   ├── ga_parameter_analyzer.py   # ✨ Analyse systématique (multi-threading)
    │   ├── ga_visualizer.py           # ✨ Visualisations (gaps vs optimal)
    │   └── __pycache__/               # Cache Python (ignoré par Git)
    │
    └── 📁 visualization/               # 📊 Visualisation des solutions
        ├── __init__.py
        ├── plot_solution.py           # Affichage graphique des routes CVRP
        └── __pycache__/               # Cache Python (ignoré par Git)
```

## 🎯 Fichiers Essentiels

### Core Algorithms (src/core/)
- **cvrp_data.py** : Parser pour fichiers .vrp, structure de données
- **ga.py** ✨ : Implémentation complète de l'algorithme génétique
  - Diversification (random immigrants, mutation adaptative)
  - Détection de doublons
  - Heavy mutation si stagnation
- **localsearch.py** : Optimisation locale 2-opt
- **solution.py** : Manipulation et évaluation des solutions
- **solution_loader.py** : Chargement solution optimale de référence
- **split.py** : Transformation giant tour → routes CVRP

### Système d'Analyse Avancé (src/optimization/)
- **ga_parameter_analyzer.py** ✨ : 
  - Tests individuels de paramètres (60+ configs)
  - Recherche de meilleures combinaisons
  - Multi-threading (ProcessPoolExecutor, ~16 workers)
  - Calcul automatique du gap vs optimal
  - Export/Import JSON avec sauvegarde automatique
  
- **ga_visualizer.py** ✨ :
  - Graphiques matplotlib/seaborn
  - Visualisation gap vs optimal (code couleur)
  - Comparaisons des paramètres
  - Seuils CVRP standards (<5% = bon, <10% = acceptable)

### Visualisation (src/visualization/)
- **plot_solution.py** : 
  - Affichage graphique des routes CVRP
  - Utilise matplotlib pour visualiser les solutions
  - Montre le dépôt et les tournées en couleurs différentes

### Modélisation Exacte (nouveaux fichiers)
- **run_pulp_demo.py** 🆕 : Résolution exacte avec PuLP/MIP
- **multi_depot.py** 🆕 : Support pour problèmes multi-dépôts
- **p01.vrp, p03_test.vrp** 🆕 : Instances de test pour validation

### Scripts d'Interface
- **run_parameter_analysis.py** : Interface menu pour analyses complètes
- **main.py** : Exécution simple de l'algorithme avec imports corrigés

## 🗑️ Fichiers Supprimés (Obsolètes)

### Nettoyage effectué lors du merge
- ❌ `advanced_optimizer.py` - Ancien système sans multi-threading efficace
- ❌ `quick_test.py` - Tests basiques remplacés
- ❌ `ultra_quick_test.py` - Tests ultra-rapides obsolètes
- ❌ `plot_results.py` - Ancien visualiseur de résultats
- ❌ Anciens fichiers de cache `__pycache__/*.cpython-313.pyc`

## 🚀 Utilisation

### Analyse Complète des Paramètres (Recommandé)
```powershell
python run_parameter_analysis.py
```
**Menu disponible** :
- Option 1 : Tests individuels (60 configs × 10 runs)
- Option 2 : Meilleures combinaisons
- Option 3 : Visualisations (graphiques avec gap)
- Option 7 : Analyse complète automatique
- Option 8 : Modifier le nombre de runs (défaut: 10)

### Exécution Simple
```powershell
python main.py
```

### Modélisation Exacte (PuLP)
```powershell
python run_pulp_demo.py
```

## 📊 Fonctionnalités du Système Actuel

### 1. Analyse de Paramètres ✨
- **Tests individuels** : Varie un paramètre à la fois (~60 configs)
- **Combinaisons optimales** : Trouve les meilleures configurations
- **Multi-threading** : ProcessPoolExecutor (~16 workers sur 12 cœurs)
- **10 runs par config** : Statistiques robustes (moyenne, écart-type, min, max)

### 2. Métriques Basées sur le Gap ✨
- **Gap vs optimal** : `((coût - 22901) / 22901) × 100`
- **Standards CVRP** :
  - Gap < 5% : ✅ Bon (vert)
  - Gap < 10% : 🟡 Acceptable (orange)
  - Gap > 10% : ❌ À améliorer (rouge)

### 3. Visualisations Avancées ✨
- Graphiques automatiques (matplotlib/seaborn)
- Code couleur basé sur les standards CVRP
- Comparaisons par paramètre
- Top combinaisons avec gaps

### 4. Documentation Complète 📖
- Protocole d'expérimentation v2.0
- Standards de qualité CVRP (références scientifiques)
- Guides d'optimisation
- Documentation multi-threading

## 🆕 Nouveautés du Merge avec Main

### Fichiers ajoutés
- ✅ 5 nouvelles instances VRP (data2-6.vrp)
- ✅ Instances de test multi-dépôts (p01, p03_test)
- ✅ Modélisation exacte PuLP (run_pulp_demo.py)
- ✅ Support multi-dépôts (multi_depot.py)

### Améliorations conservées de feature-tests-parameters
- ✅ Système d'analyse avancé avec gap vs optimal
- ✅ Visualisations avec code couleur CVRP
- ✅ Multi-threading optimisé
- ✅ Documentation complète (8 fichiers MD)
- ✅ Protocole d'expérimentation v2.0

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
