# 🚛 CVRP — Résolution par Algorithme Génétique# 🚛 CVRP — Résolution par Algorithme Génétique# 🚛 CVRP — Résolution par Algorithme Génétique# 🚛 CVRP — Résolution par Algorithme Génétique



Système d'optimisation pour le Capacitated Vehicle Routing Problem (CVRP) utilisant un algorithme génétique hybride avec split dynamique et recherche locale.



---Ce projet résout un problème de tournées de véhicules avec capacité (Capacitated Vehicle Routing Problem). L'objectif est de livrer tous les clients en partant du dépôt, sans dépasser la capacité des camions, en minimisant le temps de trajet total.



## 🎯 Objectif



Résoudre efficacement des problèmes de tournées de véhicules avec contraintes de capacité en minimisant la distance totale parcourue.## 📋 Points ClésCe projet résout un problème de tournées de véhicules avec capacité (Capacitated Vehicle Routing Problem). L'objectif est de livrer tous les clients en partant du dépôt, sans dépasser la capacité des camions, en minimisant le temps de trajet total.Ce projet résout un problème de tournées de véhicules avec capacité (Capacitated Vehicle Routing Problem). L'objectif est de livrer tous les clients en partant du dépôt, sans dépasser la capacité des camions, en minimisant le temps de trajet total.



**Standards de qualité** :

- ✅ Gap < 1% = Excellent (état de l'art)

- ✅ Gap < 5% = Bon (standard académique)- **Capacité véhicules**: Tous les véhicules ont la même capacité

- 🟡 Gap < 10% = Acceptable

- **Découpage intelligent**: Respect de la capacité via l'algorithme de Split

---

- **Performance**: Solutions de qualité en < 3 minutes## 📋 Points Clés## 📋 Points clés

## 🚀 Démarrage Rapide

- **Benchmarking**: Système professionnel avec **multi-threading** ⚡

### Installation

- **Visualisation**: Graphiques et analyses automatiques

```bash

# Cloner le projet

git clone <repo_url>

cd projet_ro## 🎯 Structure du Projet- **Capacité véhicules**: Tous les véhicules ont la même capacité- **Capacité véhicules**: Tous les véhicules ont la même capacité



# Installer les dépendances

pip install -r requirements.txt

``````- **Découpage intelligent**: Respect de la capacité via l'algorithme de Split- **Découpage intelligent**: Respect de la capacité via l'algorithme de Split



### Utilisationprojet_ro/



```bash├── benchmarks/          # 🔬 Système de benchmark professionnel- **Performance**: Solutions de qualité en < 3 minutes- **Performance**: Solutions de qualité en < 3 minutes

# Exécution simple

python main.py│   ├── benchmark.py     # Script principal (69 configs EN PARALLÈLE)



# Benchmark complet (144 configs, ~25 min)│   ├── test_benchmark.py # Test rapide de validation- **Benchmarking**: Système professionnel de tests de paramètres- **Benchmarking**: Système professionnel de tests de paramètres

python benchmarks/benchmark.py

│   └── README.md        # Documentation complète

# Test rapide des visualisations (~10 sec)

python benchmarks/test_visualizations.py├── scripts/             # 🛠️ Scripts utilitaires- **Visualisation**: Graphiques et analyses automatiques- **Visualisation**: Graphiques et analyses automatiques

```

│   ├── fast_exploration.py  # Exploration rapide (multi-threading)

---

│   └── multi_depot.py       # Support multi-dépôts

## 📂 Structure du Projet

├── src/                 # 📦 Code source principal

```

projet_ro/│   ├── core/           # Algorithmes GA, Split, LocalSearch## 🎯 Structure du Projet## 🎯 Structure du Projet

├── 📖 docs/                        # Documentation complète

│   ├── INDEX.md                    # 🎯 Point d'entrée│   ├── optimization/   # Helpers et optimisations

│   ├── experiment_protocol.md      # Guide benchmark

│   └── ...                         # Standards, références, guides│   └── visualization/  # Graphiques et plots

│

├── 🔬 benchmarks/                  # Système de benchmark└── main.py             # 🚀 Point d'entrée principal

│   ├── benchmark.py                # 144 configs + config combinée

│   └── test_visualizations.py     # Validation visualisations`````````

│

├── 💾 data/                        # Données CVRP

│   ├── instances/                  # Fichiers .vrp (CVRPLIB)

│   └── solutions/                  # Solutions de référence## 🚀 Démarrage Rapideprojet_ro/projet_ro/

│

├── 📊 results/                     # Résultats des benchmarks

│   └── benchmarks/                 # JSON, CSV, visualisations

│### Installation├── benchmarks/          # 🔬 Système de benchmark professionnel├── benchmarks/          # 🔬 Système de benchmark professionnel

├── 🐍 src/                         # Code source

│   ├── core/                       # Algorithme GA```bash

│   │   ├── ga.py                   # Algorithme génétique

│   │   ├── split.py                # Split dynamique# Python 3.10+ requis│   ├── benchmark.py     # Script principal (69 configurations)│   ├── benchmark.py     # Script principal (69 configurations)

│   │   ├── localsearch.py          # Recherche locale (2-opt)

│   │   ├── solution.py             # Gestion solutionspip install -r requirements.txt

│   │   └── cvrp_data.py            # Lecture instances

│   └── visualization/              # Visualisations```│   ├── test_benchmark.py # Test rapide de validation│   ├── test_benchmark.py # Test rapide de validation

│       └── plot_solution.py        # Affichage tournées

│

├── main.py                         # Point d'entrée principal

├── requirements.txt                # Dépendances Python### Exécution Basique│   └── README.md        # Documentation complète│   └── README.md        # Documentation complète

└── README.md                       # Ce fichier

``````bash



---# Lancer avec instance par défaut├── scripts/             # 🛠️ Scripts utilitaires├── scripts/             # 🛠️ Scripts utilitaires



## 🔬 Système de Benchmarkpython main.py



### Caractéristiques│   ├── fast_exploration.py  # Exploration rapide (5 min)│   ├── fast_exploration.py  # Exploration rapide (5 min)



- **144 configurations testées** : 5 paramètres × multiples valeurs# Avec instance personnalisée

- **Configuration optimale combinée** : Extraction automatique des meilleurs paramètres

- **10 runs de comparaison** : All Random vs NN+Randompython main.py --instance data/instances/data.vrp│   └── multi_depot.py       # Support multi-dépôts│   └── multi_depot.py       # Support multi-dépôts

- **9 visualisations professionnelles** : Histogrammes, comparaisons, gaps

- **Temps total** : ~25 minutes



### Pipeline# Charger depuis CVRPLIB├── src/                 # 📦 Code source principal├── src/                 # 📦 Code source principal



```python main.py --name A-n32-k5

1. Baseline (config par défaut)

   ↓```│   ├── core/           # Algorithmes GA, Split, LocalSearch│   ├── core/           # Algorithmes GA, Split, LocalSearch

2. Comparaison Init (10 runs)

   ↓

3. Tests Paramétriques (144 configs)

   - population_size: 33 valeurs### Benchmarking (RECOMMANDÉ) ⚡│   ├── optimization/   # Helpers et optimisations│   ├── optimization/   # Helpers et optimisations

   - n_elite: 24 valeurs

   - mutation_rate: 36 valeurs

   - tournament_size: 21 valeurs

   - n_close: 30 valeurs```bash│   └── visualization/  # Graphiques et plots│   └── visualization/  # Graphiques et plots

   ↓

4. Configuration Optimale Combinée (5 runs)# Test rapide (2-3 min) - Validation du système

   ↓

5. Génération Visualisations (9 PNG)python benchmarks/test_benchmark.py└── main.py             # 🚀 Point d'entrée principal└── main.py             # 🚀 Point d'entrée principal

```



### Résultats

# Benchmark complet (9-15 min) - 69 configurations EN PARALLÈLE``````ésolution par algorithme génétique, simple et clair

Fichiers générés dans `results/benchmarks/` :

- `benchmark_YYYYMMDD_HHMMSS.json` - Résultats completspython benchmarks/benchmark.py

- `benchmark_YYYYMMDD_HHMMSS.csv` - Format tableur

- `benchmark_YYYYMMDD_HHMMSS_plots/` - 9 visualisations```



---



## 📊 Visualisations**Performance** : Le multi-threading réduit le temps de **87%** !  ## 🚀 Démarrage RapideCe projet résout un problème de tournées de véhicules avec capacité (chaque camion a une place limitée). L’objectif est de livrer tous les clients en partant du dépôt, sans dépasser la capacité des camions, en minimisant le temps de trajet total (on l’assimile à la distance totale).



Le système génère automatiquement **9 graphiques** :(9 min au lieu de 69 min sur machine 8 cœurs)



1. **Histogrammes individuels** (5) - Impact de chaque paramètre

2. **Comparaison multi-paramètres** (1) - Vue d'ensemble 2×3

3. **Top 10 configurations** (1) - Classement des meilleures configs### Exploration Rapide

4. **Comparaison init modes** (1) - All Random vs NN+Random

5. **Comparaison des gaps** (1) - Progression All Random → NN+Random → Combined```bash### InstallationPoints importants:



---# Exploration paramètres (1-5 min) - Multi-threading actif



## 🎓 Algorithmepython scripts/fast_exploration.py```bash- Tous les véhicules ont la même capacité.



### Composants Principaux```



1. **Algorithme Génétique** (`ga.py`)# Python 3.10+ requis- On respecte la capacité grâce au “découpage intelligent” des tournées.

   - Population d'individus (permutations de clients)

   - Sélection par tournoi## 📊 Système de Benchmark

   - Croisement OX (Order Crossover)

   - Mutation par échangepip install -r requirements.txt- Limite stricte de temps de calcul: par défaut ~170 secondes (< 3 minutes).

   - Élitisme

Le dossier `benchmarks/` contient un système professionnel de test :

2. **Split Dynamique** (`split.py`)

   - Découpage optimal d'une permutation en tournées faisables```- Fenêtres de temps (ex: livrer entre 8h et 18h): non gérées explicitement dans cette version.

   - Programmation dynamique O(n²)

   - Respect strict de la capacité- **benchmark.py** (RECOMMANDÉ): Test systématique de 69 configurations



3. **Recherche Locale** (`localsearch.py`)  - **Multi-threading automatique** (tous les CPU) ⚡  - On suppose que minimiser la distance revient à minimiser le temps de tournée.

   - 2-opt intra-route

   - Amélioration itérative  - **87% plus rapide** grâce au parallélisme

   - First improvement strategy

  - 7 visualisations professionnelles (histogrammes)### Exécution Basique

### Paramètres Clés

  - Export JSON + CSV

| Paramètre | Rôle | Plage | Recommandé |

|-----------|------|-------|------------|  - Top 10 avec médailles 🥇🥈🥉```bash## Modélisation Exacte (PuLP) - Analyse Théorique

| `population_size` | Diversité | 15-400 | 80-150 |

| `n_elite` | Pression sélective | 1-40 | 5-15 |  - Gap analysis vs baseline

| `mutation_rate` | Exploration | 0.005-0.5 | 0.05-0.15 |

| `tournament_size` | Sélection | 2-30 | 3-8 |  - Durée: ~9 min (8 CPU) ou ~15 min (4 CPU)# Lancer avec instance par défautEn complément de l'algorithme génétique (méthode heuristique), cette section fournit une Modélisation Exacte (MIP) utilisant PuLP.

| `n_close` | Localité mutation | 2-100 | 10-25 |



---

- **test_benchmark.py**: Validation rapide (6 configs, 2-3 min)python main.py

## 📖 Documentation



### Point d'Entrée

**[docs/INDEX.md](docs/INDEX.md)** - Navigation complète de la documentationVoir `benchmarks/README.md` pour la documentation complète.L'objectif de cette partie n'est pas de remplacer le solveur GA, mais de prouver théoriquement et pratiquement pourquoi une approche heuristique est nécessaire pour ce problème complexe (MD-VRPSC).



### Documents Essentiels

- **[experiment_protocol.md](docs/experiment_protocol.md)** - Guide complet du système de benchmark

- **[CVRP_GAP_STANDARDS.md](docs/CVRP_GAP_STANDARDS.md)** - Standards de calcul du gap## ⚡ Performance Multi-Threading# Avec instance personnalisée

- **[VISUALIZATIONS_GAP.md](docs/VISUALIZATIONS_GAP.md)** - Guide des 9 visualisations

- **[CONTRIBUTING.md](docs/CONTRIBUTING.md)** - Guide de contribution



### Workflow Recommandé**Tous les benchmarks utilisent le multi-threading** pour tester les paramètres **EN PARALLÈLE** :python main.py --instance data/instances/data.vrpLe script run_pulp_demo.py modélise le problème complet avec les 3 contraintes (Capacité, Multi-Dépôts, Compatibilité/Split) en utilisant l'astuce de pré-traitement (décomposition des commandes) pour rester dans un modèle polynomial O(n^2v) et éviter l'explosion exponentielle (2^n) des contraintes DFJ.



1. **Débutant** (15 min)

   - Lire README.md (ce fichier)

   - Explorer docs/INDEX.md| Script | Configs | Sans // | Avec // (8 CPU) | Gain |

   - Lancer test_visualizations.py

|--------|---------|---------|-----------------|------|

2. **Intermédiaire** (30 min)

   - Lire experiment_protocol.md| **benchmark.py** | 69 | 69 min | **9 min** | **87%** ⚡ |# Charger depuis CVRPLIBCe que contient cette partierun_pulp_demo.py 

   - Lancer benchmark.py

   - Analyser les résultats| **fast_exploration.py** | 20 | 10 min | **1.5 min** | **85%** ⚡ |



3. **Avancé** (45 min)| **test_benchmark.py** | 6 | 3 min | **30s** | **83%** ⚡ |python main.py --name A-n32-k5

   - Étudier tous les docs/

   - Expérimenter avec les paramètres

   - Contribuer au projet

Voir `PERFORMANCE_MULTI_THREADING.md` pour les détails techniques.```- Le script de modélisation exacte (MIP) et de démonstration.p03_test.vrp — Instance (N=10, 3 dépôts) pour le Test de Succès (validation du modèle).p01.vrp — Instance (N=50, 4 dépôts) pour le Test d'Échec (validation de la complexité NP-hard).Rapport_Modelisation.html — (Ce document) L'analyse théorique complète (Modélisation, Complexité NP-Complet, Analyse O(2^n) vs O(n^2v)).

---



## 🧪 Instance de Test

## 🧬 Composants Principaux

**Fichier** : `data/instances/data.vrp`



```

NAME:              X-n101-k25### Core (`src/core/`)### Benchmarking (RECOMMANDÉ)Lancer la Démonstration PuLP

TYPE:              CVRP

DIMENSION:         101 (100 clients + 1 dépôt)- **cvrp_data.py**: Chargement instances CVRPLIB

CAPACITY:          206

OPTIMAL:           27591 (référence CVRPLIB)- **ga.py**: Algorithme génétique principal```bash

```

- **split.py**: Découpage optimal en tournées (programmation dynamique)

---

- **localsearch.py**: Amélioration locale (2-opt)# Test rapide (2-3 min) - Validation du systèmeCe script démontre la faisabilité (sur petit N) et l'infaisabilité (sur grand N) de la méthode exacte.

## 📈 Résultats Typiques

- **solution.py**: Validation et export solutions

### Configuration par Défaut

```python benchmarks/test_benchmark.py

Coût:           29310

Gap:            +6.23%### Scripts Utilitaires

Temps:          60s

```- **fast_exploration.py**: Exploration paramètres rapide (multi-threading)Prérequis Python 3.10 ou plus PuLP (solveur MIP) : pip install pulp



### Configuration Optimale Combinée- **multi_depot.py**: Support problèmes multi-dépôts

```

Coût:           27620# Benchmark complet (15 min) - 69 configurations + 7 visualisations

Gap:            +0.10%

Amélioration:   +5.77%## 🎨 Visualisations

Temps:          60s

```python benchmarks/benchmark.pyExécution de la Démonstration



**Interprétation** : Gap de 0.10% = Excellent (proche de l'optimal !)Toutes les visualisations utilisent des **histogrammes verticaux** avec:



---- Gradient de couleurs (vert = meilleur, rouge = pire)```



## 🛠️ Technologies- Médailles pour le Top 3 (🥇🥈🥉)



- **Python 3.10+**- Étoiles dorées pour valeurs optimalesLe script est conçu pour exécuter deux tests :

- **NumPy** : Calculs matriciels

- **Matplotlib** : Visualisations- Annotations avec statistiques

- **CSV/JSON** : Sauvegarde résultats

### Exploration Rapide

---

Types de graphiques générés:

## 📚 Références Académiques

1. Top 10 configurations```bash- Test de Succès (Validation du Modèle) Objectif : Prouver que notre modèle mathématique (Étape B) est logiquement correct. Action : Dans run_pulp_demo.py, régler FILE_TO_SOLVE = "p03_test.vrp". Lancer : python run_pulp_demo.py Résultat Attendu : Solver Status: Optimal. Le script trouve la solution optimale en quelques secondes.

### Benchmarks CVRP

- **CVRPLIB** : http://vrp.atd-lab.inf.puc-rio.br/2. Impact de chaque paramètre (5 graphiques)

- **Uchoa et al. (2017)** : "New benchmark instances for the Capacitated Vehicle Routing Problem"

3. Grille comparative (temps vs qualité)# Exploration paramètres (5 min) - Avec visualisations

### Algorithmes

- **Prins (2004)** : "A simple and effective evolutionary algorithm for the vehicle routing problem"

- **Vidal et al. (2012)** : "A hybrid genetic algorithm with adaptive diversity management"

## ⚙️ Configuration des Paramètrespython scripts/fast_exploration.py- Test d'Échec (Validation de la Complexité) Objectif : Prouver en pratique que la méthode exacte est impossible pour des instances de taille réelle dans le temps imparti. Action : Dans run_pulp_demo.py, régler FILE_TO_SOLVE = "p01.vrp". Lancer : python run_pulp_demo.py Résultat Attendu : Solver Status: Not Solved. Le solveur s'arrêtera après la limite de temps (ex: 170s) sans avoir trouvé de solution.

---



## 🆘 Support

Les paramètres de l'algorithme génétique peuvent être ajustés dans `main.py` ou via les scripts de benchmark :```

### Problèmes Courants



**Le benchmark plante**

→ Vérifier que `data/instances/data.vrp` existe- **population_size**: Taille de la population (défaut: 50)L'échec du Test 2 justifie la stratégie principale de ce projet, qui est l'utilisation d'un algorithme heuristique (GA) pour obtenir des solutions de haute qualité en un temps raisonnable.



**Résultats incohérents**- **n_elite**: Nombre d'individus élites préservés (défaut: 5)

→ Consulter [CVRP_GAP_STANDARDS.md](docs/CVRP_GAP_STANDARDS.md)

- **mutation_rate**: Taux de mutation (défaut: 0.1)## 📊 Système de Benchmark

**Visualisations vides**

→ Installer matplotlib : `pip install matplotlib`- **tournament_size**: Taille du tournoi pour la sélection (défaut: 3)



### Documentation Complète- **n_close**: Nombre de voisins proches pour mutations (défaut: 10)## Ce que contient le dépôt

→ Voir [docs/INDEX.md](docs/INDEX.md)

- **crossover_rate**: Probabilité de croisement (défaut: 0.5)

---

- **two_opt_prob**: Probabilité d'appliquer 2-opt (défaut: 0.35)Le dossier `benchmarks/` contient un système professionnel de test :

## 🤝 Contribution



Voir [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) pour :

- Standards de documentation## 📈 Sorties du Programme- `cvrp_data.py` — Lecture des fichiers CVRPLIB `.vrp`, construction de l’instance:

- Workflow de contribution

- Checklist de vérification



---Lors de l'exécution, le programme génère :- **benchmark.py** (RECOMMANDÉ): Test systématique de 69 configurations  - coordonnées des points (clients + dépôt)



## 📝 Licence



Projet académique - Optimisation CVRP1. **Solution texte** (`solution_<instance>.sol`):  - Multi-threading automatique  - demandes des clients



---   - Liste des tournées avec IDs clients



## 🎉 Changelog   - Coût total et nombre de véhicules  - 7 visualisations professionnelles (histogrammes)  - capacité des véhicules



### Version 4.0 (13 novembre 2025)   - Respect des contraintes

- ✨ Configuration optimale combinée

- 📊 9 visualisations (+ init_modes + gaps)  - Export JSON + CSV  - matrice de distances (euclidienne arrondie à la manière TSPLIB)

- 🎯 144 configurations testées

- 📚 Documentation complète et nettoyée2. **Image de la solution** (`solution_<instance>.png`):

- 🧹 Suppression fichiers obsolètes

   - Visualisation graphique des tournées  - Top 10 avec médailles 🥇🥈🥉  - Nouveau: `load_cvrp_from_vrplib(name)` pour charger directement une instance par son nom depuis le package Python `vrplib`, et récupérer le best-known cost si disponible.

### Version 3.x

- Exploration rapide (69 configs)   - Différentes couleurs par route

- Multi-threading expérimental

   - Dépôt clairement marqué  - Gap analysis vs baseline- `split.py` — Découpe une “grande tournée” en plusieurs tournées faisables (respect de la capacité) via une programmation dynamique.

### Version 2.x

- Tests paramétriques basiques



### Version 1.x3. **Statistiques console**:  - Durée: ~15 minutes- `localsearch.py` — Amélioration locale “par inversion de segments” à l’intérieur d’une tournée (souvent appelée 2-opt).

- Implémentation initiale GA

   - Coût total de la solution

---

   - Nombre de véhicules utilisés- `solution.py` — Calcul du coût d’une solution, vérification des contraintes, lecture/écriture de solutions texte.

**Pour commencer** : Lire [docs/INDEX.md](docs/INDEX.md) puis lancer `python benchmarks/benchmark.py` ! 🚀

   - Gap vs optimal (si disponible)

   - Validation des contraintes- **test_benchmark.py**: Validation rapide (6 configs, 2-3 min)- `ga.py` — Le cœur de l’algorithme génétique: population, sélection, croisement, mutation, évaluation, élitisme, limite de temps.



## 🔬 Modélisation Exacte (PuLP)- `plot.py` — Affichage des tournées trouvées (optionnel, nécessite `matplotlib`).



Le dossier contient également une analyse théorique avec modélisation exacte (MIP) utilisant PuLP.Voir `benchmarks/README.md` pour la documentation complète.- `main.py` — Petit lanceur: charge une instance (par chemin local ou par nom CVRPLIB), exécute l’algo, vérifie et écrit la solution, et affiche le tracé.



Cette partie démontre pourquoi une approche heuristique (GA) est nécessaire pour ce problème NP-difficile :

- **Test petit N** (p03_test.vrp): Résolution optimale en quelques secondes

- **Test grand N** (p01.vrp): Infaisable dans le temps imparti## 🧬 Composants Principaux## Nouveautés



Voir `scripts/run_pulp_demo.py` pour plus de détails.



## 📚 Documentation Complète### Core (`src/core/`)- Arrêt propre à la demande:



- **DOC_INDEX.md**: Point d'entrée de la documentation 📍- **cvrp_data.py**: Chargement instances CVRPLIB  - Appuie sur Ctrl+C pendant l’exécution: l’algo s’arrête proprement et garde le meilleur individu courant.

- **QUICK_GUIDE.md**: Guide rapide (START HERE) ⚡

- **benchmarks/README.md**: Guide complet du système de benchmark 🔬- **ga.py**: Algorithme génétique principal  - Option `STOP_SENTINEL_FILE` dans `main.py`: si ce fichier existe, l’algo stoppe proprement à la fin de la génération.

- **scripts/README.md**: Description de tous les scripts utilitaires

- **PERFORMANCE_MULTI_THREADING.md**: Détails techniques du parallélisme ⚡- **split.py**: Découpage optimal en tournées (programmation dynamique)- Gap vs optimal:

- **docs/**: Documentation technique approfondie

- **localsearch.py**: Amélioration locale (2-opt)  - Variable `TARGET_OPTIMUM` dans `main.py`. Lors d’un chargement par nom CVRPLIB (`--name`), si une solution de référence est disponible via `vrplib`, la valeur est automatiquement mise à jour avec le best-known cost.

## 🔧 Dépendances

- **solution.py**: Validation et export solutions- Chargement direct par nom CVRPLIB:

```

numpy>=1.24.0  - Utilise le package `vrplib` pour télécharger/charger les instances et, si possible, la solution de référence.

matplotlib>=3.7.0

vrplib>=1.0.1          # Pour charger instances CVRPLIB### Scripts Utilitaires  - Permet d’appeler: `python main.py --name A-n32-k5`

pulp>=2.7.0            # Pour modélisation exacte (optionnel)

```- **fast_exploration.py**: Exploration paramètres rapide



## 🎯 Workflow Recommandé- **multi_depot.py**: Support problèmes multi-dépôts## Lancer le programme



### Première Utilisation

```bash

# 1. Installer les dépendances## 🎨 VisualisationsPrérequis:

pip install -r requirements.txt

- Python 3.10 ou plus

# 2. Test rapide du système (30s)

python benchmarks/test_benchmark.pyToutes les visualisations utilisent des **histogrammes verticaux** avec:- Optionnel pour l’affichage: `pip install matplotlib`



# 3. Voir la structure- Gradient de couleurs (vert = meilleur, rouge = pire)- Optionnel pour le chargement par nom CVRPLIB: `pip install vrplib`

python show_structure.py

```- Médailles pour le Top 3 (🥇🥈🥉)



### Benchmarking Professionnel- Étoiles dorées pour valeurs optimalesExécutions possibles:

```bash

# Benchmark complet avec multi-threading- Annotations avec statistiques- Avec un fichier `.vrp` local:

python benchmarks/benchmark.py

```

# Résultats dans: results/benchmarks/

```Types de graphiques générés:python main.py --instance /chemin/vers/mon_instance.vrp



### Résolution Simple1. Top 10 configurations```

```bash

# Résoudre une instance spécifique2. Impact de chaque paramètre (5 graphiques)- Directement par le nom d’une instance CVRPLIB (ex: A-n32-k5):

python main.py --instance data/instances/data.vrp

```3. Grille comparative (temps vs qualité)```



## 📝 Licencepip install vrplib



Projet académique de recherche opérationnelle.## ⚙️ Configuration des Paramètrespython main.py --name A-n32-k5



## 🤝 Contribution```



Pour toute question ou amélioration, n'hésitez pas à ouvrir une issue ou proposer une pull request.Les paramètres de l'algorithme génétique peuvent être ajustés dans `main.py` ou via les scripts de benchmark :Dans ce second cas:



---- L’instance est récupérée via `vrplib`.



**⚡ Note importante** : Tous les benchmarks utilisent le **multi-threading** pour tester les paramètres EN PARALLÈLE. Cela réduit le temps d'exécution de **85-87%** par rapport à une exécution séquentielle. Le système détecte automatiquement le nombre de CPU disponibles et les utilise tous pour maximiser les performances !- **population_size**: Taille de la population (défaut: 50)- Si `vrplib` expose une solution de référence, le best-known cost est automatiquement utilisé pour calculer le gap.


- **n_elite**: Nombre d'individus élites préservés (défaut: 5)

- **mutation_rate**: Taux de mutation (défaut: 0.1)Sorties:

- **tournament_size**: Taille du tournoi pour la sélection (défaut: 3)- Affiche le coût total, le nombre de véhicules (nombre de tournées), et la validité des contraintes.

- **n_close**: Nombre de voisins proches pour mutations (défaut: 10)- Si une valeur optimale est connue (`TARGET_OPTIMUM` non nulle): affiche aussi `Gap vs optimal: X.YZ%`.

- **crossover_rate**: Probabilité de croisement (défaut: 0.5)- Écrit un fichier solution texte: `solution_<nom_instance>.sol`

- **two_opt_prob**: Probabilité d'appliquer 2-opt (défaut: 0.35)- Si `matplotlib` est dispo, sauvegarde une image: `solution_<nom_instance>.png`



## 📈 Sorties du Programme## Paramètres utiles (où les changer)



Lors de l'exécution, le programme génère :Dans `ga.py`, la fonction `genetic_algorithm(...)` contient les réglages principaux:

- Taille de population, nombre de générations max

1. **Solution texte** (`solution_<instance>.sol`):- Sélection par tournoi (taille du tournoi)

   - Liste des tournées avec IDs clients- Probabilités de croisement et de mutation

   - Coût total et nombre de véhicules- Activation et probabilité de l’amélioration locale

   - Respect des contraintes- Limite de temps (par défaut 170 secondes)

- Option `target_optimum` (affichage gap), et `stop_on_file` (arrêt propre via fichier sentinelle)

2. **Image de la solution** (`solution_<instance>.png`):

   - Visualisation graphique des tournéesBesoin d’aide pour intégrer des fenêtres de temps ou booster les perfs ? Dis-moi, on itère.
   - Différentes couleurs par route
   - Dépôt clairement marqué

3. **Statistiques console**:
   - Coût total de la solution
   - Nombre de véhicules utilisés
   - Gap vs optimal (si disponible)
   - Validation des contraintes

## 🔬 Modélisation Exacte (PuLP)

Le dossier contient également une analyse théorique avec modélisation exacte (MIP) utilisant PuLP.

Cette partie démontre pourquoi une approche heuristique (GA) est nécessaire pour ce problème NP-difficile :
- **Test petit N** (p03_test.vrp): Résolution optimale en quelques secondes
- **Test grand N** (p01.vrp): Infaisable dans le temps imparti

Voir `scripts/run_pulp_demo.py` pour plus de détails.

## 📚 Documentation Complète

- **benchmarks/README.md**: Guide complet du système de benchmark
- **scripts/README.md**: Description de tous les scripts utilitaires
- **docs/**: Documentation technique approfondie

## 🔧 Dépendances

```
numpy>=1.24.0
matplotlib>=3.7.0
vrplib>=1.0.1          # Pour charger instances CVRPLIB
pulp>=2.7.0            # Pour modélisation exacte (optionnel)
```

## 📝 Licence

Projet académique de recherche opérationnelle.

## 🤝 Contribution

Pour toute question ou amélioration, n'hésitez pas à ouvrir une issue ou proposer une pull request.
