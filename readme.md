# Projet CVRP - Optimisation par Algorithme Génétique

Projet de résolution du **Capacitated Vehicle Routing Problem (CVRP)** utilisant un algorithme génétique optimisé avec recherche locale 2-opt.

## 🚀 Installation

```bash
git clone <votre-repo>
cd projet_ro
pip install -r requirements.txt
```

## 📁 Structure du projet

```
projet_ro/
├── src/                          # Code source
│   ├── core/                     # Modules CVRP de base
│   │   ├── cvrp_data.py          # Chargement instances
│   │   ├── ga.py                 # Algorithme génétique
│   │   ├── solution.py           # Gestion solutions
│   │   ├── localsearch.py        # Recherche locale
│   │   └── split.py              # Algorithme de split
│   ├── optimization/             # Scripts d'optimisation
│   │   ├── quick_test.py         # Tests complets (2-4h)
│   │   ├── ultra_quick_test.py   # Tests rapides (8-10min)
│   │   └── advanced_optimizer.py # Optimisation avancée
│   └── visualization/            # Graphiques et analyse
│       ├── plot_results.py       # Analyse paramètres
│       └── plot_solution.py      # Visualisation solutions
├── data/                         # Données
│   ├── instances/                # Instances CVRP
│   └── solutions/                # Solutions générées
├── results/                      # Résultats des tests
│   ├── parameter_tests/          # Tests de paramètres
│   ├── optimization_runs/        # Runs d'optimisation
│   └── plots/                    # Graphiques générés
├── docs/                         # Documentation
│   ├── README.md                 # Documentation détaillée
│   └── optimization_guide.md     # Guide d'optimisation
├── main.py                       # Point d'entrée principal
└── requirements.txt              # Dépendances
```

## 🎯 Utilisation rapide

### 1. Résoudre une instance CVRP
```bash
python main.py
```

### 2. Optimiser les paramètres (ultra-rapide)
```bash
cd src/optimization
python ultra_quick_test.py
```

### 3. Analyser les résultats
```bash
cd src/visualization  
python plot_results.py
```

## 📊 Workflow d'optimisation recommandé

1. **Test ultra-rapide** (8-10 min) → identification des tendances
2. **Tests complets** (2-4h) → validation approfondie
3. **Analyse graphique** → compréhension des impacts
4. **Application** → utilisation des meilleurs paramètres

## 📖 Documentation détaillée

- [Documentation complète](docs/README.md)
- [Guide d'optimisation](docs/optimization_guide.md)

## 🛠️ Fonctionnalités principales

- **Algorithme génétique** avec sélection par tournoi et élitisme
- **Recherche locale 2-opt** pour amélioration des solutions
- **Tests automatisés** de 60-150+ configurations de paramètres
- **Visualisations avancées** avec matplotlib
- **Analyse statistique** complète des performances

## 🎯 Paramètres optimisables

- Population, sélection, élitisme
- Probabilités de crossover et mutation
- Optimisation 2-opt (activation/probabilité)
- Critères d'arrêt (temps/générations)

## 🔧 Configuration

Instance par défaut : `data/instances/data.vrp`

Pour utiliser votre propre instance, remplacez le fichier ou modifiez les chemins dans les scripts.

## 📈 Résultats

Les résultats sont automatiquement sauvegardés dans :
- `results/parameter_tests/` : Données des tests
- `results/plots/` : Graphiques générés
- `data/solutions/` : Solutions CVRP

## 🚨 Remarque importante

Les **paramètres de l'instance CVRP** (capacité, coordonnées, demandes) ne sont **jamais modifiés**. Seuls les **paramètres de l'algorithme génétique** sont optimisés.

---

*Développé pour l'optimisation du Capacitated Vehicle Routing Problem*