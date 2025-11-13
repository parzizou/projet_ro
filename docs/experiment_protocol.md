# 🔬 Protocole d'Expérimentation — Optimisation GA pour CVRP# Protocole d'Expérimentation — Optimisation GA pour CVRP# Protocole d'Expérimentation — Optimisation GA pour CVRP



**Version 4.0** — 13 novembre 2025  

**Instance de test** : X-n101-k25 (100 clients)  

**Solution optimale** : 27591 (référence CVRPLIB)**Version 4.0** — Novembre 2025  **Version 3.0** — Novembre 2025  



---**Instance de test**: X-n101-k25 (100 clients)  **Instance**: X-n153-k22 (152 clients)  



## 📋 Table des Matières**Solution optimale connue**: 27591**Solution optimale connue**: 22901



1. [Vue d'Ensemble](#-vue-densemble)

2. [Instance de Test](#-instance-de-test)

3. [Métriques et Standards](#-métriques-et-standards)------

4. [Système de Benchmark](#-système-de-benchmark)

5. [Paramètres Testés](#-paramètres-testés)

6. [Exécution](#-exécution)

7. [Résultats et Visualisations](#-résultats-et-visualisations)## 📋 Table des Matières## 📋 Table des Matières

8. [Interprétation](#-interprétation)

9. [Références](#-références)



---1. [Objectif et Contexte](#objectif-et-contexte)1. [Objectif et Contexte](#objectif-et-contexte)



## 🎯 Vue d'Ensemble2. [Instance de Test](#instance-de-test)2. [Instance de Référence](#instance-de-référence)



### Objectif3. [Standards de Qualité CVRP](#standards-de-qualité-cvrp)3. [Standards de Qualité CVRP](#standards-de-qualité-cvrp)



Déterminer la **configuration optimale** des paramètres de l'algorithme génétique pour résoudre efficacement le CVRP en minimisant l'écart (gap) par rapport à la solution optimale connue.4. [Système de Benchmark](#système-de-benchmark)4. [Architecture du Système](#architecture-du-système)



### Approche5. [Paramètres Testés](#paramètres-testés)5. [Protocole Expérimental](#protocole-expérimental)



Le système teste **144 configurations différentes** des 5 paramètres clés de l'algorithme génétique, puis combine automatiquement les meilleures valeurs trouvées pour créer une **configuration optimale combinée**.6. [Exécution des Tests](#exécution-des-tests)6. [Mode Exploration Rapide](#mode-exploration-rapide)



### Méthodologie7. [Visualisations](#visualisations)7. [Exécution des Tests](#exécution-des-tests)



```8. [Interprétation des Résultats](#interprétation-des-résultats)8. [Visualisations et Analyses](#visualisations-et-analyses)

Baseline → Init Comparison → Parameter Testing → Combined Optimal → Analysis

   (1)          (10 runs)         (144 configs)      (5 runs)      (9 graphs)9. [Documentation et Traçabilité](#documentation-et-traçabilité)

  ~1 min         ~2 min             ~18 min           ~5 min        ~1 min

```---



**Durée totale** : ~25 minutes---



---## 🎯 Objectif et Contexte



## 📊 Instance de Test## 🎯 Objectif et Contexte



### Caractéristiques### Objectif Principal



| Propriété | Valeur |Optimiser les paramètres de l'algorithme génétique (GA) pour résoudre le Capacitated Vehicle Routing Problem (CVRP) en minimisant l'écart (**gap**) par rapport à la solution optimale connue.### Objectif Principal

|-----------|--------|

| **Nom** | X-n101-k25 |Optimiser les paramètres de l'algorithme génétique (GA) pour résoudre le Capacitated Vehicle Routing Problem (CVRP) en minimisant l'écart (**gap**) par rapport à la solution optimale connue.

| **Type** | CVRP |

| **Dimension** | 101 nœuds (100 clients + 1 dépôt) |### Métriques de Performance

| **Capacité** | 206 unités |

| **Optimum connu** | 27591 |### Métriques de Performance

| **Source** | CVRPLIB (Uchoa et al. 2017) |

| **Fichier** | `data/instances/data.vrp` |#### 1. **Gap par rapport à l'optimal** (métrique principale)



### Format```#### 1. **Gap par rapport à l'optimal** (métrique principale)



```gap (%) = ((coût_obtenu - coût_optimal) / coût_optimal) × 100```

NAME : X-n101-k25

COMMENT : (Uchoa, 2014)```gap (%) = ((coût_obtenu - coût_optimal) / coût_optimal) × 100

TYPE : CVRP

DIMENSION : 101```

EDGE_WEIGHT_TYPE : EUC_2D

CAPACITY : 206**Standards CVRP** (littérature scientifique) :

NODE_COORD_SECTION

1 3082 1762- **Gap < 5%** : ✅ **Bon résultat** (standard académique)**Standards CVRP** (littérature scientifique) :

2 3662 4134

...- **Gap < 1%** : 🏆 **Excellent** (état de l'art)- **Gap < 5%** : ✅ **Bon résultat** (standard académique)

DEMAND_SECTION

1 0- **Gap < 10%** : 🟡 **Acceptable** (heuristiques basiques)- **Gap < 1%** : 🏆 **Excellent** (état de l'art)

2 11

...- **Gap > 10%** : ❌ **Insuffisant**- **Gap < 10%** : 🟡 **Acceptable** (heuristiques basiques)

DEPOT_SECTION

1- **Gap > 10%** : ❌ **Insuffisant**

-1

EOF#### 2. **Temps d'exécution**

```

- Limite par configuration : 60 secondes#### 2. **Temps d'exécution**

---

- Mesure du temps réel (wall-clock time)- Limite par défaut : 45 secondes

## 📐 Métriques et Standards

- Mesure du temps réel (wall-clock time)

### 1. Gap (Écart à l'Optimal)

#### 3. **Amélioration**

**Formule** :

``````#### 3. **Stabilité**

gap (%) = ((coût_obtenu - optimum) / optimum) × 100

```amélioration (%) = ((coût_baseline - coût_obtenu) / coût_baseline) × 100- Écart-type sur n runs (n = 10 par défaut)



**Standards académiques** :```- Écart min-max



| Gap | Qualité | Niveau |- Valeur positive = amélioration

|-----|---------|--------|

| **< 0.5%** | 🏆 État de l'art | Excellence |- Valeur négative = dégradation---

| **< 1%** | ✅ Excellent | Publication |

| **< 5%** | ✅ Bon | Standard académique |

| **< 10%** | 🟡 Acceptable | Heuristique basique |

| **> 10%** | ❌ Insuffisant | À améliorer |---## 📊 Instance de Référence



**Exemple** :

- Optimum : 27591

- Coût obtenu : 27650## 📊 Instance de Test### Fichier : `data/instances/data.vrp`

- Gap : (27650 - 27591) / 27591 × 100 = **0.21%** ✅ Excellent



### 2. Amélioration (vs Baseline)

### Fichier : `data/instances/data.vrp`**Métadonnées** (format CVRPLIB) :

**Formule** :

``````

amélioration (%) = ((baseline_cost - coût_obtenu) / baseline_cost) × 100

```**Métadonnées** (format CVRPLIB) :NAME:              X-n153-k22



**Interprétation** :```TYPE:              CVRP

- Valeur **positive** = amélioration ✅

- Valeur **négative** = dégradation ❌NAME:              X-n101-k25DIMENSION:         153 (152 clients + 1 dépôt)

- Valeur **nulle** = identique

TYPE:              CVRPEDGE_WEIGHT_TYPE:  EUC_2D

**Exemple** :

- Baseline : 29310DIMENSION:         101 (100 clients + 1 dépôt)CAPACITY:          144

- Coût obtenu : 27650

- Amélioration : (29310 - 27650) / 29310 × 100 = **5.67%** ✅EDGE_WEIGHT_TYPE:  EUC_2D```



### 3. Temps d'ExécutionCAPACITY:          206



- **Limite par configuration** : 60 secondes```**Caractéristiques** :

- **Mesure** : Wall-clock time (temps réel)

- **Critère** : Respecter la limite de temps- **Clients** : 152 (nœuds 2-153)



---**Caractéristiques** :- **Dépôt** : nœud 1



## 🔬 Système de Benchmark- **Clients** : 100 (nœuds 2-101)- **Demande totale** : 3068 unités



### Architecture- **Dépôt** : nœud 1- **Véhicules minimum** : 22 (⌈3068/144⌉)



```- **Capacité véhicules** : 206 unités- **Coordonnées** : X ∈ [14, 998], Y ∈ [212, 973]

benchmarks/benchmark.py

├── Configuration- **Solution optimale** : **27591** (référence CVRPLIB)- **Solution optimale** : **22901** (référence CVRPLIB)

│   ├── Instance CVRP

│   ├── Optimum connu

│   └── Paramètres par défaut

│**Source** : Uchoa et al. (2017) - Benchmarks CVRP**Source** : Uchoa, Pecin, Pessoa, Poggi, Subramanian, and Vidal (2013)

├── Phase 1 : Baseline

│   └── 1 run avec config par défaut

│

├── Phase 2 : Comparaison Initialisation---### Solution de Référence

│   ├── 5 runs "All Random"

│   └── 5 runs "NN + Random"

│

├── Phase 3 : Tests Paramétriques## 🎓 Standards de Qualité CVRP**Fichier** : `data/solutions/solution_data.sol`

│   ├── population_size (33 valeurs)

│   ├── n_elite (24 valeurs)

│   ├── mutation_rate (36 valeurs)

│   ├── tournament_size (21 valeurs)### Références Scientifiques```

│   └── n_close (30 valeurs)

│   → Total : 144 configurationsRoutes: 25 routes optimales

│

├── Phase 4 : Configuration Optimale Combinée#### 1. **Vidal et al. (2012)** - Hybrid Genetic AlgorithmCost: 22901

│   ├── Extraction best value par paramètre

│   ├── Combinaison des meilleurs- Gap < 0.5% (état de l'art)```

│   └── 5 runs de validation

│- Référence : "A hybrid genetic algorithm for multidepot and periodic vehicle routing problems"

└── Phase 5 : Visualisations

    └── Génération de 9 graphiques PNGCette solution est automatiquement chargée par le système pour calculer les gaps.

```

#### 2. **Prins (2004)** - Split Algorithm  

### Pipeline Détaillé

- Gap moyen : 1-3% (AG standards)---

#### Phase 1 : Baseline (1 minute)



**Objectif** : Établir une référence

#### 3. **Uchoa et al. (2017)** - Benchmarks CVRP## 🎓 Standards de Qualité CVRP

```python

default_params = {- Gap < 5% : Standard académique

    'population_size': 100,

    'n_elite': 10,- Gap < 1% : État de l'art### Références Scientifiques

    'mutation_rate': 0.1,

    'tournament_size': 5,

    'n_close': 20,

    'time_limit': 60---#### 1. **Vidal et al. (2012)** - Hybrid Genetic Algorithm

}

```- **Instance X-n153-k22** : Gap < 0.5% (état de l'art)



**Sortie** :## 🔬 Système de Benchmark- Référence : "A hybrid genetic algorithm for multidepot and periodic vehicle routing problems"

- Coût baseline

- Temps d'exécution

- Gap vs optimum

### Script Principal : `benchmarks/benchmark.py`#### 2. **Prins (2004)** - Split Algorithm  

#### Phase 2 : Comparaison Init (2 minutes)

- Gap moyen : 1-3% (AG standards)

**Objectif** : Comparer 2 stratégies d'initialisation

Le système teste systématiquement **144 configurations de paramètres** avec :

| Stratégie | Description | Runs |

|-----------|-------------|------|- Calcul d'une baseline (configuration par défaut)#### 3. **Uchoa et al. (2017)** - Benchmarks CVRP

| **All Random** | Population 100% aléatoire | 5 |

| **NN + Random** | 50% Nearest Neighbor + 50% aléatoire | 5 |- Comparaison de 2 modes d'initialisation (All Random vs NN+Random)- Gap < 5% : Standard académique



**Métriques calculées** :- Test exhaustif de 5 paramètres clés- Gap < 1% : État de l'art

- Coût moyen, min, max, écart-type

- Temps moyen- Création d'une **configuration optimale combinée** (meilleurs paramètres)

- Gap moyen

- Génération de 9 visualisations professionnelles### Objectifs pour ce Projet

#### Phase 3 : Tests Paramétriques (18 minutes)



**Objectif** : Tester exhaustivement 5 paramètres

### Pipeline d'Exécution| Objectif | Gap | Coût Cible | Difficulté | Statut |

Pour chaque paramètre :

1. Fixer les 4 autres à leur valeur par défaut|----------|-----|------------|------------|--------|

2. Tester toutes les valeurs définies

3. Enregistrer coût, temps, gap, amélioration```| **Baseline actuelle** | +1.81% | 23316 | Point de départ | ✅ Déjà bon |



**Total** : 144 configurations × 60s = 144 minutes de calcul GA  1. Baseline (config par défaut)| **Maintenir < 5%** | < 5% | < 24046 | Réaliste | 🎯 Objectif 1 |

(mais optimisé avec arrêt anticipé si convergence)

   ↓| **Atteindre < 3%** | < 3% | < 23588 | Nécessite optimisation | 🎯 Objectif 2 |

#### Phase 4 : Configuration Optimale (5 minutes)

2. Comparaison Init Modes (10 runs)| **Approcher < 1%** | < 1% | < 23130 | État de l'art | 🏆 Objectif avancé |

**Objectif** : Combiner les meilleurs paramètres

   - 5 runs All Random

**Algorithme** :

```python   - 5 runs NN + Random**Note** : Votre baseline actuelle (gap = 1.81%) est **déjà excellente** selon les standards CVRP.

optimal_params = {}

for param in ['population_size', 'n_elite', 'mutation_rate',    ↓

              'tournament_size', 'n_close']:

    # Trouver la valeur donnant le meilleur coût3. Tests Paramétriques (144 configs)---

    best_value = find_best_value(results[param])

    optimal_params[param] = best_value   - population_size: 33 valeurs



# Tester cette combinaison 5 fois   - n_elite: 24 valeurs## 🏗️ Architecture du Système

for i in range(5):

    run_ga(optimal_params)   - mutation_rate: 36 valeurs



# Calculer statistiques   - tournament_size: 21 valeurs### Modules Principaux

mean_cost = moyenne(costs)

best_cost = min(costs)   - n_close: 30 valeurs

worst_cost = max(costs)

```   ↓#### 1. **Core Algorithm** (`src/core/`)



**Validation** :4. Configuration Optimale Combinée (5 runs)```

- 5 runs pour robustesse statistique

- Utilisation de la moyenne (pas le meilleur)   - Extraction des meilleurs paramètressrc/core/

- Comparaison vs meilleure config individuelle

   - Test de la combinaison├── cvrp_data.py         # Chargement instance CVRP

#### Phase 5 : Visualisations (1 minute)

   - Validation statistique├── ga.py                # Algorithme génétique principal

**Objectif** : Générer 9 graphiques pour analyse

   ↓├── solution.py          # Structure et évaluation solution

---

5. Génération de 9 Visualisations├── split.py             # Split giant tour → routes

## ⚙️ Paramètres Testés

   - Histogrammes individuels (5)├── localsearch.py       # Optimisations locales (2-opt)

### 1. Population Size (33 valeurs)

   - Comparaison multi-paramètres (1)└── solution_loader.py   # Chargement solution de référence

**Rôle** : Taille de la population d'individus

   - Top 10 configurations (1)```

**Valeurs testées** :

```python   - Comparaison init modes (1)

[15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100,

 110, 120, 130, 140, 150, 160, 170, 180, 190, 200,   - Comparaison des gaps (1)#### 2. **Parameter Analysis** (`src/optimization/`)

 220, 240, 260, 280, 300, 320, 340, 360, 380, 400]

`````````



**Impact** :src/optimization/

- ↑ Taille → ↑ Diversité, ↑ Temps calcul

- ↓ Taille → ↓ Diversité, ↓ Temps calcul**Temps total** : ~25 minutes├── ga_parameter_analyzer.py    # Analyse systématique paramètres



**Recommandé** : 80-150├── ga_visualizer.py             # Visualisations (gaps vs optimal)



**Par défaut** : 100---├── advanced_optimizer.py        # Tests avancés



---├── quick_test.py                # Tests rapides



### 2. N Elite (24 valeurs)## ⚙️ Paramètres Testés├── ultra_quick_test.py          # Tests ultra-rapides



**Rôle** : Nombre d'individus élitistes conservés à chaque génération└── exploration_helpers.py       # Helpers pour exploration



**Valeurs testées** :### 1. **Population Size** (33 valeurs)```

```python

[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,```python

 16, 18, 20, 22, 24, 26, 30, 35, 40]

```[15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100, #### 3. **Interface Principale**



**Impact** : 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, ```

- ↑ Elite → ↑ Pression sélective, ↓ Diversité

- ↓ Elite → ↓ Pression sélective, ↑ Diversité 220, 240, 260, 280, 300, 320, 340, 360, 380, 400]run_parameter_analysis.py        # Menu interactif complet (10 options)



**Recommandé** : 5-15 (5-15% de la population)``````



**Par défaut** : 10- **Impact** : Diversité vs Temps de calcul



---- **Recommandé** : 80-150### Multi-threading



### 3. Mutation Rate (36 valeurs)



**Rôle** : Probabilité de mutation pour chaque individu### 2. **N Elite** (24 valeurs)**Implémentation** : `ThreadPoolExecutor` (Python concurrent.futures)



**Valeurs testées** :```python- **Fichier** : `run_parameter_analysis.py`, scripts d'exploration

```python

[0.005, 0.01, 0.015, 0.02, 0.025, 0.03, 0.035, 0.04,[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, - **Workers par défaut** : Auto-détection CPU (ex: 16 threads)

 0.045, 0.05, 0.055, 0.06, 0.065, 0.07, 0.075, 0.08,

 0.085, 0.09, 0.095, 0.1, 0.11, 0.12, 0.13, 0.14, 16, 18, 20, 22, 24, 26, 30, 35, 40]- **Avantage** : Parallélisation massive des tests GA

 0.15, 0.16, 0.17, 0.18, 0.19, 0.2, 0.25, 0.3,

 0.35, 0.4, 0.45, 0.5]```- **Utilisation** : Mode exploration rapide (option 9)

```

- **Impact** : Pression sélective

**Impact** :

- ↑ Taux → ↑ Exploration, ↓ Exploitation- **Recommandé** : 5-15---

- ↓ Taux → ↓ Exploration, ↑ Exploitation



**Recommandé** : 0.05-0.15

### 3. **Mutation Rate** (36 valeurs)## 🔬 Protocole Expérimental

**Par défaut** : 0.1

```python

---

[0.005, 0.01, 0.015, 0.02, 0.025, 0.03, 0.035, 0.04, ### Phase 1 : Configuration de Base (Baseline)

### 4. Tournament Size (21 valeurs)

 0.045, 0.05, 0.055, 0.06, 0.065, 0.07, 0.075, 0.08, 

**Rôle** : Nombre d'individus dans chaque tournoi de sélection

 0.085, 0.09, 0.095, 0.1, 0.11, 0.12, 0.13, 0.14, #### Paramètres par Défaut

**Valeurs testées** :

```python 0.15, 0.16, 0.17, 0.18, 0.19, 0.2, 0.25, 0.3, ```python

[2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,

 16, 18, 20, 22, 24, 26, 30] 0.35, 0.4, 0.45, 0.5]DEFAULT_PARAMS = {

```

```    'population_size': 50,    # Taille de population

**Impact** :

- ↑ Taille → ↑ Pression sélective (convergence rapide)- **Impact** : Exploration vs Exploitation    'n_elite': 5,             # Nombre élites conservés

- ↓ Taille → ↓ Pression sélective (exploration)

- **Recommandé** : 0.05-0.15    'mutation_rate': 0.1,     # Probabilité mutation

**Recommandé** : 3-8

    'tournament_size': 3,     # Taille tournoi sélection

**Par défaut** : 5

### 4. **Tournament Size** (21 valeurs)    'n_close': 10,            # Voisins proches pour crossover

---

```python    'time_limit': 60.0        # Limite temps (sec)

### 5. N Close (30 valeurs)

[2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, }

**Rôle** : Nombre de clients proches considérés pour la mutation

 16, 18, 20, 22, 24, 26, 30]```

**Valeurs testées** :

```python```

[2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,

 16, 18, 20, 22, 24, 26, 28, 30, 35, 40, 45, 50,- **Impact** : Intensité de la sélection**Résultat baseline** :

 60, 70, 80, 100]

```- **Recommandé** : 3-8- Coût moyen : ~23300



**Impact** :- Gap : ~1.8%

- ↑ Voisinage → Mutations plus variées

- ↓ Voisinage → Mutations plus locales (intensification)### 5. **N Close** (30 valeurs)- ✅ **Déjà excellent**



**Recommandé** : 10-25```python



**Par défaut** : 20[2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, ### Phase 2 : Tests Individuels des Paramètres



--- 16, 18, 20, 22, 24, 26, 28, 30, 35, 40, 45, 50, 



## 🚀 Exécution 60, 70, 80, 100]#### Objectif



### Prérequis```Identifier l'impact de **chaque paramètre indépendamment** en variant une seule valeur à la fois.



```bash- **Impact** : Localité de la mutation

# Vérifier l'instance

ls data/instances/data.vrp- **Recommandé** : 10-25#### Espaces de Recherche



# Vérifier l'optimum dans le code

# Doit être 27591 pour X-n101-k25

```---| Paramètre | Valeurs Testées | Justification (littérature) |



### Commandes|-----------|-----------------|----------------------------|



#### Test Rapide (Validation système)## 🚀 Exécution des Tests| `population_size` | [20, 30, 40, 50, 60, 80, 100, 120, 150, 200] | Optimal : 50-100 pour 152 clients |



```bash| `n_elite` | [1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20] | Optimal : 5-10% de population_size |

python benchmarks/test_visualizations.py

```### Test Rapide (Validation)| `mutation_rate` | [0.01, 0.02, 0.05, 0.08, 0.1, 0.15, 0.2, 0.25, 0.3] | Optimal : 0.05-0.15 |



**Durée** : ~10 secondes  | `tournament_size` | [2, 3, 4, 5, 6, 7, 8, 10] | Optimal : 3-5 (équilibre exploitation/exploration) |

**Sortie** : 9 PNG dans `test_visualizations/`  

**Utilité** : Vérifier que matplotlib fonctionne```bash| `n_close` | [3, 5, 7, 10, 12, 15, 20, 25, 30, 40, 50] | Optimal : 10-20 pour localité géographique |



#### Benchmark Complet# Test avec données simulées (~10 secondes)



```bashpython benchmarks/test_visualizations.py**Total** : ~50 configurations différentes

python benchmarks/benchmark.py

``````



**Durée** : ~25 minutes  #### Protocole d'Exécution

**Sortie** :

- `results/benchmarks/benchmark_YYYYMMDD_HHMMSS.json`**Sortie** :

- `results/benchmarks/benchmark_YYYYMMDD_HHMMSS.csv`

- `results/benchmarks/benchmark_YYYYMMDD_HHMMSS_plots/` (9 PNG)- 9 visualisations dans `test_visualizations/`1. **Nombre de runs** : 10 par configuration (configurable)



### Suivi en Temps Réel- Validation du système sans benchmark complet2. **Calcul des statistiques** :



Le terminal affiche la progression :   - Coût moyen, écart-type, min, max



```### Benchmark Complet   - Gap moyen par rapport à l'optimal

================================================================================

                        🔬 BENCHMARK SYSTÈME GA - CVRP   - Temps moyen d'exécution

================================================================================

```bash

Instance: X-n101-k25

Optimum connu: 27591# Benchmark production (~25 minutes)3. **Critères de sélection** :

Total configurations: 144

python benchmarks/benchmark.py   - Identifier le meilleur gap pour chaque paramètre

Calcul de la BASELINE...

✓ Baseline: 29310.0 | Gap: +6.23% | Temps: 60.5s```   - Classer par ordre de performance



Comparaison des modes d'initialisation (10 runs)...   - Analyser la stabilité (écart-type)

[1/10] All Random: 28234.0 (60.2s)

[2/10] All Random: 28156.0 (60.1s)**Sortie** :

...

✓ All Random    → Moyenne: 28130.0 | Gap: +1.95%- Résultats dans `results/benchmarks/benchmark_YYYYMMDD_HHMMSS.json`### Phase 3 : Tests de Combinaisons

✓ NN + Random   → Moyenne: 27840.0 | Gap: +0.90%

- CSV dans `results/benchmarks/benchmark_YYYYMMDD_HHMMSS.csv`

Tests paramétriques...

[1/144] population_size=15 → 28450.0 | +3.11% gap | 45.2s- 9 PNG dans `results/benchmarks/benchmark_YYYYMMDD_HHMMSS_plots/`#### Objectif

[2/144] population_size=20 → 28320.0 | +2.64% gap | 46.8s

...Combiner les **meilleures valeurs** de chaque paramètre pour trouver la configuration optimale.



Test de la Configuration Optimale Combinée...---

Meilleurs paramètres:

  - population_size: 120#### Méthode

  - n_elite: 8

  - mutation_rate: 0.08## 📊 Visualisations

  - tournament_size: 5

  - n_close: 151. **Sélection des candidats** :



[1/5] Run 1: 27650.0 (60.3s)Le système génère **9 graphiques professionnels** :   - Prendre les top-3 valeurs de chaque paramètre (Phase 2)

...

✓ Config combinée → Moyenne: 27620.0 | Gap: +0.10%   



Génération des visualisations...### 1-5. Histogrammes Individuels2. **Génération de combinaisons** :

✓ 9 graphiques créés

- `population_size.png` - Impact de la taille de population   - Combinaison 1 : Tous les meilleurs (best-of-best)

================================================================================

                        📊 RÉSUMÉ DES RÉSULTATS- `n_elite.png` - Impact du nombre d'élites   - Combinaisons 2-N : Variations des top-3

================================================================================

```- `mutation_rate.png` - Impact du taux de mutation



---- `tournament_size.png` - Impact de la taille du tournoi3. **Nombre de combinaisons** : 10-50 (configurable)



## 📊 Résultats et Visualisations- `n_close.png` - Impact du voisinage proche



### Fichiers Générés4. **Validation** :



```**Caractéristiques** :   - 10 runs par combinaison

results/benchmarks/benchmark_20251113_160744/

├── benchmark_20251113_160744.json          # Données complètes- Axe X trié par valeur croissante   - Calcul du gap moyen

├── benchmark_20251113_160744.csv           # Format tableur

└── benchmark_20251113_160744_plots/        # Visualisations- Axe Y dynamique (zoom sur zone d'intérêt)   - Identification de la meilleure configuration

    ├── population_size.png                 # [1] Histogramme

    ├── n_elite.png                         # [2] Histogramme- Ligne optimale en vert pointillé

    ├── mutation_rate.png                   # [3] Histogramme

    ├── tournament_size.png                 # [4] Histogramme- Valeur par défaut marquée d'une étoile---

    ├── n_close.png                         # [5] Histogramme

    ├── parameter_comparison.png            # [6] Comparaison 2×3- Coût minimal surligné en vert

    ├── top10_best_configs.png              # [7] Classement

    ├── init_modes_comparison.png           # [8] Init modes## ⚡ Mode Exploration Rapide

    └── gaps_comparison.png                 # [9] Gaps progression

```### 6. Comparaison Multi-Paramètres



### Structure JSON`parameter_comparison.png`### Principe



```json

{

  "metadata": {**Format** : 2 lignes × 3 colonnes**Nouveau mode** (Option 9) : Exploration rapide avec grille très étendue

    "instance": "X-n101-k25",

    "optimum": 27591,- Visualisation côte à côte des 5 paramètres- **1 seul run par configuration** (au lieu de 10)

    "timestamp": "20251113_160744",

    "total_configs": 144,- Permet d'identifier visuellement les tendances- **Multi-threading massif** (tous les CPU)

    "duration_seconds": 1520

  },- 6ème subplot vide (réservé)- **69 configurations** testées en ~15 minutes

  "baseline": {

    "cost": 29310.0,

    "time": 60.5,

    "gap": 6.23,### 7. Top 10 Configurations### Grille Étendue

    "params": { ... }

  },`top10_best_configs.png`

  "init_comparison": {

    "all_random": {```python

      "costs": [28234, 28156, ...],

      "mean_cost": 28130.0,**Contenu** :EXTENDED_GRID = {

      "best_cost": 27980.0,

      "worst_cost": 28350.0,- 10 meilleures configurations classées    'population_size': [20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100, 

      "std_dev": 145.2,

      "mean_gap": 1.95- Médailles : 🥇 🥈 🥉 pour le podium                        120, 150, 180, 200, 250, 300],  # 18 valeurs

    },

    "nn_random": { ... }- Affichage compact des paramètres    

  },

  "parameter_results": [- Coûts et améliorations vs baseline    'n_elite': [1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 15, 20],  # 12 valeurs

    {

      "param_name": "population_size",    

      "default_value": 100,

      "results": [### 8. Comparaison Init Modes    'mutation_rate': [0.01, 0.02, 0.03, 0.05, 0.07, 0.1, 0.12, 0.15, 

        {

          "value": 15,`init_modes_comparison.png`                      0.18, 0.2, 0.22, 0.25, 0.28, 0.3, 0.35, 0.4],  # 16 valeurs

          "cost": 28450.0,

          "time": 45.2,    

          "gap": 3.11,

          "improvement": 2.93**Format** : 3 sous-graphiques    'tournament_size': [2, 3, 4, 5, 6, 7, 8, 10, 12, 15],  # 10 valeurs

        },

        ...- Distribution des coûts (All Random vs NN+Random)    

      ]

    },- Comparaison des statistiques    'n_close': [3, 5, 7, 10, 12, 15, 18, 20, 25, 30, 35, 40, 50]  # 13 valeurs

    ...

  ],- Analyse de stabilité}

  "combined_optimal": {

    "params": {```

      "population_size": 120,

      "n_elite": 8,### 9. Comparaison des Gaps

      "mutation_rate": 0.08,

      "tournament_size": 5,`gaps_comparison.png`**Total** : 69 configurations

      "n_close": 15

    },

    "costs": [27650, 27620, 27605, 27630, 27595],

    "best_cost": 27595.0,**Progression** :### Caractéristiques

    "mean_cost": 27620.0,

    "worst_cost": 27650.0,1. All Random (initialisation aléatoire pure)

    "std_dev": 21.3,

    "gap": 0.102. NN + Random (code actuel)✅ **Rapidité** : ~15 minutes (vs 2-3h pour mode standard)  

  }

}3. Combined Optimal (meilleurs paramètres combinés)✅ **Couverture** : 69 points vs ~50 en mode standard  

```

✅ **Multi-threading** : Tous les CPU utilisés  

### Structure CSV

**Visualise** : L'amélioration progressive du gap✅ **Automatique** : Baseline calculé, visualisations générées  

```csv

param_name,value,cost,time,gap,improvement

population_size,15,28450.0,45.2,3.11,2.93

population_size,20,28320.0,46.8,2.64,3.38---### Limitations

population_size,25,28190.0,48.1,2.17,3.82

...

n_elite,1,28680.0,52.3,3.95,2.15

n_elite,2,28540.0,53.8,3.44,2.63## 🔍 Interprétation des Résultats⚠️ **Moins précis** : 1 run vs 10 runs (pas de moyenne/écart-type)  

...

```⚠️ **Bruit statistique** : Peut manquer la vraie tendance  



### Visualisations (9 graphiques)### Structure des Résultats JSON💡 **Usage recommandé** : Exploration initiale, puis validation en mode standard



#### [1-5] Histogrammes Individuels



**Caractéristiques** :```json### Résultats Générés

- Axe X : Valeurs du paramètre (triées)

- Axe Y : Coût obtenu (zoom dynamique){

- Ligne verte pointillée : Optimum (27591)

- Étoile rouge : Valeur par défaut  "metadata": {1. **Fichiers JSON/CSV** avec tous les résultats

- Barre verte : Meilleure valeur

- Titre : Nom du paramètre + impact    "instance": "X-n101-k25",2. **7 visualisations automatiques** :



**Exemple** : `mutation_rate.png`    "optimum": 27591,   - 5 histogrammes individuels (par paramètre)

```

📊 Impact de mutation_rate sur le Coût    "timestamp": "20251113_160744",   - 1 graphique comparatif 2×3

(Défaut: 0.1 ⭐ | Optimum: 27591)

    "total_configs": 144   - 1 Top 10 des meilleures configurations

Coût

28500 |       },

28000 |  ▓▓▓▓▓▓▓▓

27500 |▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  "baseline": {---

27000 |---------------------- Optimum

      |____________________    "cost": 29310,

       0.05  0.1  0.15  0.2

            mutation_rate    "gap": 6.23,## 🚀 Exécution des Tests

```

    "time": 60.5

#### [6] Comparaison Multi-Paramètres

  },### Menu Interactif Principal

**Format** : 2 lignes × 3 colonnes

  "init_comparison": {

```

┌─────────────────┬─────────────────┬─────────────────┐    "all_random": {```powershell

│ population_size │    n_elite      │  mutation_rate  │

├─────────────────┼─────────────────┼─────────────────┤      "mean_cost": 28130,python run_parameter_analysis.py

│ tournament_size │    n_close      │     (vide)      │

└─────────────────┴─────────────────┴─────────────────┘      "best_cost": 27980,```

```

      "worst_cost": 28350

**Utilité** : Vue d'ensemble rapide des 5 paramètres

    },**Menu disponible (10 options)** :

#### [7] Top 10 Configurations

    "nn_random": {```

**Format** : Barres horizontales classées

      "mean_cost": 27840,╔════════════════════════════════════════════════════════════╗

```

🏆 Top 10 Meilleures Configurations      "best_cost": 27720,║       🧬 ANALYSE DES PARAMÈTRES DE L'ALGORITHME GA        ║



🥇 #1: 27595  mutation_rate=0.08, pop=120, ...      "worst_cost": 28010╚════════════════════════════════════════════════════════════╝

🥈 #2: 27620  mutation_rate=0.075, pop=110, ...

🥉 #3: 27650  mutation_rate=0.09, pop=130, ...    }

   #4: 27680  ...

   ...  },Instance: data/instances/data.vrp

   #10: 27850 ...

```  "combined_optimal": {Optimal connu: 22901



**Utilité** : Identifier les configurations prometteuses    "params": {Nombre de runs par test: 10



#### [8] Comparaison Init Modes      "population_size": 120,



**Format** : 3 sous-graphiques      "n_elite": 8,OPTIONS DISPONIBLES:



```      "mutation_rate": 0.08,─────────────────────────────────────────────────────────────

┌─────────────────────────────────────┐

│  Distribution des Coûts (boxplot)  │      "tournament_size": 5,1️⃣  - Tester les paramètres individuellement

├─────────────────────────────────────┤

│  Comparaison Statistiques (barres)  │      "n_close": 152️⃣  - Trouver les meilleures combinaisons

├─────────────────────────────────────┤

│  Analyse Stabilité (violin plot)    │    },3️⃣  - Visualiser les résultats (graphiques)

└─────────────────────────────────────┘

```    "best_cost": 27600,4️⃣  - Générer un rapport complet



**Métriques affichées** :    "mean_cost": 27620,5️⃣  - Afficher la configuration actuelle

- Coûts min, max, moyenne, médiane

- Écart-type    "worst_cost": 27650,6️⃣  - Charger des résultats existants

- Gap moyen

    "gap": 0.107️⃣  - Analyse complète (1+2+3+4)

#### [9] Comparaison des Gaps

  },8️⃣  - Modifier le nombre de runs par test

**Format** : Barres avec progression

  "parameter_results": [...]9️⃣  - 🚀 Exploration rapide (69 configs, 1 run, ~15min)

```

📈 Progression du Gap vers l'Optimum}0️⃣  - Quitter



Gap (%)```─────────────────────────────────────────────────────────────

6.5 | ████████  +6.23%

    |           All Random```

2.0 | ███       +1.95%

    |           NN+Random### Lecture du Résumé Terminal

1.0 | █         +0.90%

    |           Combined### Option 9 : Exploration Rapide (NOUVEAU)

0.1 | ▌         +0.10% ← Meilleur!

    |___________________________```

      Baseline  Init  Optimal

```================================================================================**Usage recommandé** : Première exploration



**Utilité** : Visualiser l'amélioration progressive                        📊 RÉSUMÉ DES RÉSULTATS



---================================================================================```powershell



## 🔍 Interprétationpython run_parameter_analysis.py



### Lecture du Résumé Terminal📈 BASELINE (configuration par défaut):# → Choisir option 9



```   Coût: 29310.0 | Gap: +6.23% | Temps: 60.5s```

================================================================================

                        📊 RÉSUMÉ DES RÉSULTATS

================================================================================

🎲 COMPARAISON INITIALISATION:**Caractéristiques** :

📈 BASELINE (configuration par défaut):

   Coût: 29310.0 | Gap: +6.23% | Temps: 60.5s   All Random    → Coût moyen: 28130.0 | Gap: +1.95%- ⚡ **Rapide** : ~15 minutes (tous les CPU utilisés)

   → Point de départ

   NN + Random   → Coût moyen: 27840.0 | Gap: +0.90%- 📊 **69 configurations** testées

🎲 COMPARAISON INITIALISATION:

   All Random    → Coût moyen: 28130.0 | Gap: +1.95%   💡 NN+Random est 290.0 coût meilleur (+1.03%)- 🎨 **7 visualisations** générées automatiquement

   NN + Random   → Coût moyen: 27840.0 | Gap: +0.90%

   💡 NN+Random est 290.0 coût meilleur (+1.03%)- 💾 **Sauvegarde automatique** (JSON + CSV)

   → NN+Random recommandé

⭐ MEILLEUR RÉSULTAT INDIVIDUEL:

⭐ MEILLEUR RÉSULTAT INDIVIDUEL:

   mutation_rate=0.08 → Coût: 27650.0 | Amélioration: +5.67% | Gap: +0.21%   mutation_rate=0.08 → Coût: 27650.0 | Amélioration: +5.67% | Gap: +0.21%**Déroulement** :

   → Meilleure config parmi les 144

1. Calcul du baseline automatique

🌟 CONFIGURATION OPTIMALE COMBINÉE:

   ⭐ Meilleurs paramètres combinés → Coût: 27620.0 | Gap: +0.10%🌟 CONFIGURATION OPTIMALE COMBINÉE:2. Tests parallèles des 69 configurations (1 run chacune)

   📈 30.0 coût de mieux que la meilleure config individuelle!

   → Synergie des paramètres confirmée ✅   ⭐ Meilleurs paramètres combinés → Coût: 27620.0 | Amélioration: +5.77% | Gap: +0.10%3. Génération de 7 graphiques :



   Paramètres optimaux:   📈 30.0 coût de mieux que la meilleure config individuelle!   - 5 histogrammes individuels par paramètre

   • population_size: 120 (vs 100 défaut)

   • n_elite: 8 (vs 10 défaut)   - 1 grille comparative 2×3

   • mutation_rate: 0.08 (vs 0.1 défaut)

   • tournament_size: 5 (= défaut)================================================================================   - 1 Top 10 avec médailles 🥇🥈🥉

   • n_close: 15 (vs 20 défaut)

```

📊 STATISTIQUES FINALES:

   Coût moyen config optimale: 27620.0**Résultats** :

   Écart-type: 21.3 (très stable)

   Meilleur run: 27595.0### Critères de Succès```

   Pire run: 27650.0

results/parameter_analysis/

================================================================================

```✅ **Excellent** :├── fast_exploration_YYYYMMDD_HHMMSS.json



### Critères de Succès- Gap combiné < 0.5%├── fast_exploration_YYYYMMDD_HHMMSS.csv



#### ✅ Excellent- Amélioration baseline > 5%└── fast_exploration_YYYYMMDD_HHMMSS_plots/

- Gap combiné < 0.5% ✅

- Amélioration baseline > 5% ✅- Combined meilleur que best individual    ├── population_size.png       # Histogramme vertical

- Combined meilleur que best individual ✅

- Écart-type < 50 ✅    ├── n_elite.png                # Histogramme vertical



#### ✅ Bon✅ **Bon** :    ├── mutation_rate.png          # Histogramme vertical

- Gap combiné < 1%

- Amélioration baseline > 3%- Gap combiné < 1%    ├── tournament_size.png        # Histogramme vertical

- Combined proche du best individual

- Écart-type < 100- Amélioration baseline > 3%    ├── n_close.png                # Histogramme vertical



#### 🟡 Acceptable- Combined proche du best individual    ├── parameter_comparison.png   # Grille 2×3 comparative

- Gap combiné < 3%

- Amélioration baseline > 1%    └── top10_best_configs.png     # Top 10 avec médailles

- Combined testé avec succès

- Écart-type < 200🟡 **Acceptable** :```



### Analyse des Paramètres- Gap combiné < 3%



#### population_size- Amélioration baseline > 1%### Options 1-8 : Mode Standard



**Si meilleur < défaut (100)** :- Combined testé avec succès

→ Instance relativement petite, population réduite suffit

#### Option 1 : Tests Individuels

**Si meilleur > défaut** :

→ Diversité importante, augmenter la population---- **Durée** : 2-3h (10 runs par config)



**Interprétation typique** :- **Statistiques** : Moyenne, écart-type, min, max

- 80-120 : Optimal pour instances 100 clients

- > 150 : Instances plus grandes## 📝 Traçabilité- **Sauvegarde automatique** : Oui



#### n_elite



**Si meilleur < défaut (10)** :### Fichiers Générés#### Option 2 : Tests de Combinaisons

→ Trop d'élitisme nuit à la diversité

- **Pré-requis** : Option 1 complétée

**Si meilleur > défaut** :

→ Besoin de plus de pression sélective```- **Nombre** : 10-50 combinaisons



**Interprétation typique** :results/benchmarks/- **Sauvegarde automatique** : Oui

- 5-10% de population_size

- Exemple : pop=100 → elite=5-10├── benchmark_20251113_160744.json     # Résultats complets



#### mutation_rate├── benchmark_20251113_160744.csv      # Format tableur#### Option 3 : Visualisations



**Si meilleur < défaut (0.1)** :└── benchmark_20251113_160744_plots/   # 9 visualisations- Génère tous les graphiques

→ Trop de perturbations, réduire

    ├── population_size.png- Nécessite résultats existants

**Si meilleur > défaut** :

→ Besoin de plus d'exploration    ├── n_elite.png



**Interprétation typique** :    ├── mutation_rate.png#### Option 7 : Analyse Complète

- 0.05-0.1 : Standard

- < 0.05 : Exploitation dominante    ├── tournament_size.png- Exécute 1 → 2 → 3 → 4 automatiquement

- > 0.15 : Exploration dominante

    ├── n_close.png- **Durée totale** : 3-4h

#### tournament_size

    ├── parameter_comparison.png

**Si meilleur < défaut (5)** :

→ Pression sélective trop forte    ├── top10_best_configs.png### Scripts Standalone



**Si meilleur > défaut** :    ├── init_modes_comparison.png

→ Besoin de convergence plus rapide

    └── gaps_comparison.png#### Exploration Rapide Mono-dépôt

**Interprétation typique** :

- 3-5 : Équilibre standard``````powershell

- 2 : Très peu de pression

- > 7 : Convergence rapide (risque: optimal local)python scripts/fast_exploration.py



#### n_close### Format CSV (pour analyse)```



**Si meilleur < défaut (20)** :

→ Mutations trop larges, intensifier

```csv#### Exploration Rapide Multi-dépôt

**Si meilleur > défaut** :

→ Mutations trop locales, diversifierparam_name,value,cost,time,gap,improvement```powershell



**Interprétation typique** :population_size,15,28450.0,45.2,3.11,2.93python scripts/fast_exploration_multidepot.py

- 10-25 : Standard pour 100 clients

- < 10 : Très local (hill climbing)population_size,20,28320.0,46.8,2.64,3.38# → Demande k_depots et types_alphabet

- > 30 : Proche aléatoire

...```

### Synergie des Paramètres

```

**Configuration Optimale Combinée meilleure ?** ✅

---

→ **Synergie positive** : Les paramètres fonctionnent bien ensemble

**Colonnes** :

Exemple :

```- `param_name` : Nom du paramètre testé## 📊 Visualisations et Analyses

Meilleur individuel: mutation_rate=0.08 → 27650

Combined optimal: tous les bests → 27620 (30 de mieux!)- `value` : Valeur testée

```

- `cost` : Coût obtenu### Type 1 : Histogrammes Individuels (par paramètre)

**Configuration Optimale Combinée moins bonne ?** ⚠️

- `time` : Temps d'exécution (secondes)

→ **Interaction négative** : Certains paramètres s'opposent

- `gap` : Écart vs optimum (%)**Fichiers** : `population_size.png`, `n_elite.png`, etc.

Action :

- Analyser les corrélations- `improvement` : Amélioration vs baseline (%)

- Tester des compromis

- Augmenter le nombre de runs**Caractéristiques** :



------- 📊 **Barres verticales** (hauteur = coût)



## 🔄 Workflow Recommandé- 🎨 **Gradient de couleurs** :



### 1. Préparation (5 min)## 🔄 Workflow Recommandé  - 🟢 Vert : Meilleures configurations



```bash  - 🟡 Jaune : Configurations moyennes

# Vérifier l'instance

cat data/instances/data.vrp | head -20### 1. Validation Initiale  - 🔴 Rouge : Moins bonnes configurations



# Vérifier l'optimum```bash- 📏 **Lignes de référence** :

grep "27591" benchmarks/benchmark.py

python benchmarks/test_visualizations.py  - Rouge pointillée : Baseline

# Test rapide

python benchmarks/test_visualizations.py```  - Verte pointillée : Optimal (22901)

```

→ Vérifier que le système fonctionne- � **Annotations** : Valeurs du paramètre testées

### 2. Exécution Benchmark (25 min)



```bash

# Lancer le benchmark### 2. Benchmark Complet**Interprétation** :

python benchmarks/benchmark.py

```bash- Plus la barre est basse, meilleur est le résultat

# Attendre...

# Suivre la progression dans le terminalpython benchmarks/benchmark.py- Les barres vertes indiquent les meilleures valeurs

```

```- Rechercher les "vallées" dans l'histogramme

### 3. Analyse Initiale (10 min)

→ Attendre ~25 minutes

**Ordre de lecture** :

### Type 2 : Grille Comparative 2×3

1. **Terminal** : Lire le résumé

   - Gap combiné### 3. Analyse des Résultats

   - Amélioration baseline

   - Paramètres optimaux1. Consulter le résumé terminal**Fichier** : `parameter_comparison.png`



2. **gaps_comparison.png** : Vue d'ensemble2. Ouvrir `gaps_comparison.png` → Vue d'ensemble

   - Progression Baseline → All Random → NN+Random → Combined

   - Vérifier amélioration continue3. Examiner `top10_best_configs.png` → Meilleures configs**Contenu** :



3. **top10_best_configs.png** : Meilleures configs4. Analyser les histogrammes individuels → Tendances par paramètre- 6 sous-graphiques (un par paramètre)

   - Identifier patterns communs

   - Comparer podium- **Axe gauche** (bleu) : Coût total



### 4. Analyse Détaillée (15 min)### 4. Configuration Finale- **Axe droit** (orange) : Amélioration % vs baseline



**Pour chaque paramètre** :Utiliser les paramètres de `combined_optimal` :



1. Ouvrir l'histogramme```python**Utilité** :

2. Identifier la tendance (U, croissante, décroissante, plateau)

3. Comparer valeur optimale vs défautbest_params = {- Vue d'ensemble rapide

4. Noter dans un tableau

    'population_size': 120,- Comparaison des impacts relatifs

Exemple de tableau d'analyse :

    'n_elite': 8,- Identification des paramètres les plus influents

| Paramètre | Défaut | Optimal | Tendance | Interprétation |

|-----------|--------|---------|----------|----------------|    'mutation_rate': 0.08,

| pop_size | 100 | 120 | Plateau 80-150 | Peu sensible dans cette plage |

| n_elite | 10 | 8 | Décroissante | Trop d'élitisme nuit |    'tournament_size': 5,### Type 3 : Top 10 des Configurations

| mut_rate | 0.1 | 0.08 | U inversé | Optimal vers 0.08 |

| tourn_size | 5 | 5 | Plateau 3-7 | Défaut déjà optimal |    'n_close': 15

| n_close | 20 | 15 | Décroissante | Mutations trop larges |

}**Fichier** : `top10_best_configs.png`

### 5. Documentation (10 min)

```

```bash

# Copier les paramètres optimaux**Caractéristiques** :

cat results/benchmarks/benchmark_*/benchmark_*.json | grep "combined_optimal" -A 20

### 5. Production- 📊 **Histogramme vertical** avec médailles

# Créer un rapport

echo "# Résultats Benchmark $(date)" > RAPPORT.mdIntégrer la config optimale dans `main.py` ou scripts de production- 🥇 **1er place** : Médaille d'or

echo "" >> RAPPORT.md

echo "## Configuration Optimale" >> RAPPORT.md- 🥈 **2e place** : Médaille d'argent

echo "..." >> RAPPORT.md

```---- 🥉 **3e place** : Médaille de bronze



### 6. Intégration (5 min)- 🎨 **Gradient de couleurs** (vert → rouge)



**Mettre à jour le code de production** :## 📚 Références- 📈 **Annotations** : Coût + gap % au-dessus des barres



```python

# main.py ou votre script principal

GA_PARAMS = {### Documentation Associée**Interprétation** :

    'population_size': 120,  # Optimisé (était 100)

    'n_elite': 8,            # Optimisé (était 10)- `CVRP_GAP_STANDARDS.md` - Standards de calcul du gap```python

    'mutation_rate': 0.08,   # Optimisé (était 0.1)

    'tournament_size': 5,    # Optimal (inchangé)- `SOLUTION_REFERENCE.md` - Solutions de référence# Exemple de lecture

    'n_close': 15,           # Optimisé (était 20)

    'time_limit': 60- `VISUALIZATIONS_GAP.md` - Guide des visualisationsTop 1: population_size=60, Coût=23050 (+0.65%)

}

```- `README.md` - Vue d'ensemble du projetTop 2: mutation_rate=0.08, Coût=23080 (+0.78%)



---Top 3: n_close=15, Coût=23120 (+0.96%)



## 📚 Références### Standards CVRP```



### Standards CVRP- **CVRPLIB** : http://vrp.atd-lab.inf.puc-rio.br/



- **CVRPLIB** : http://vrp.atd-lab.inf.puc-rio.br/- **Uchoa et al. (2017)** : "New benchmark instances for the Capacitated Vehicle Routing Problem"### Codes Couleurs Universels

  - Instances de référence

  - Solutions optimales connues- **Vidal et al. (2012)** : "A hybrid genetic algorithm with adaptive diversity management"

  - Benchmarks académiques

**Pour les gaps** :

- **Uchoa et al. (2017)** : "New benchmark instances for the Capacitated Vehicle Routing Problem"

  - Journal : European Journal of Operational Research---- 🟢 **Vert** : Gap < 1% (excellent)

  - DOI : 10.1016/j.ejor.2016.08.012

- 🟡 **Jaune** : 1% ≤ Gap < 5% (bon)

### Algorithmes Génétiques

## 🆘 Résolution de Problèmes- 🟠 **Orange** : 5% ≤ Gap < 10% (acceptable)

- **Prins (2004)** : "A simple and effective evolutionary algorithm for the vehicle routing problem"

  - Computers & Operations Research- 🔴 **Rouge** : Gap ≥ 10% (insuffisant)

  - Algorithme Split

### Le benchmark plante

- **Vidal et al. (2012)** : "A hybrid genetic algorithm with adaptive diversity management"

  - Management Science- Vérifier que `data/instances/data.vrp` existe**Pour les histogrammes** :

  - État de l'art CVRP

- Vérifier que l'instance est bien X-n101-k25 (optimum 27591)- Gradient **RdYlGn_r** (Red-Yellow-Green reversed)

### Split Dynamique

- Meilleur résultat = Vert foncé

- **Prins (2009)** : "Two memetic algorithms for heterogeneous fleet vehicle routing problems"

  - Engineering Applications of Artificial Intelligence### Résultats incohérents- Résultat moyen = Jaune

  - Programmation dynamique O(n²)

- Gap négatif → Vérifier la valeur optimale- Moins bon résultat = Rouge

---

- Temps trop courts → Augmenter time_limit dans benchmark.py

## 🆘 Dépannage

- Pas de combined_optimal → Vérifier que les 144 configs sont testées---

### Problème : Le benchmark plante



**Symptômes** :

```### Visualisations vides## 📝 Documentation et Traçabilité

Traceback (most recent call last):

  File "benchmarks/benchmark.py", line 123- Vérifier que matplotlib est installé

    ...

FileNotFoundError: data/instances/data.vrp- Vérifier les warnings dans le terminal### Fichiers de Résultats Sauvegardés

```

- Les warnings d'émojis sont normaux (cosmétiques)

**Solutions** :

1. Vérifier que le fichier existe#### Mode Exploration Rapide (Option 9)

2. Vérifier le chemin (relatif vs absolu)

3. Vérifier les permissions---```



### Problème : Gap négatifresults/parameter_analysis/



**Symptômes** :**Dernière mise à jour** : 13 novembre 2025  ├── fast_exploration_20251113_143000.json      # Résultats complets

```

Gap: -2.35%**Auteur** : Équipe Optimisation CVRP├── fast_exploration_20251113_143000.csv       # Format tableur

```

└── fast_exploration_20251113_143000_plots/    # Visualisations

**Causes** :    ├── population_size.png         # Histogramme vertical

- Valeur optimum incorrecte dans le code    ├── n_elite.png                 # Histogramme vertical

- Instance changée mais optimum pas mis à jour    ├── mutation_rate.png           # Histogramme vertical

    ├── tournament_size.png         # Histogramme vertical

**Solution** :    ├── n_close.png                 # Histogramme vertical

```python    ├── parameter_comparison.png    # Grille 2×3

# Vérifier dans benchmark.py    └── top10_best_configs.png      # Top 10 avec médailles

OPTIMUM = 27591  # Pour X-n101-k25```

```

#### Mode Standard (Options 1-8)

### Problème : Temps trop longs```

results/parameter_analysis/

**Symptômes** :├── individual_params_20251113_143000.json

```├── combinations_20251113_143000.json

[12/144] mutation_rate=0.15 → 180.5s (dépasse limite)└── visualizations_20251113_143000/

```    ├── param_population_size.png

    ├── param_n_elite.png

**Causes** :    └── ...

- Paramètres causant convergence lente```

- Limite de temps trop stricte

### Structure JSON

**Solutions** :

1. Augmenter time_limit (ligne ~50 dans benchmark.py)```json

2. Réduire population_size{

3. Ajuster critère d'arrêt  "timestamp": "20251113_143000",

  "instance": "X-n153-k22",

### Problème : Visualisations vides  "mode": "fast_exploration",

  "n_runs": 1,

**Symptômes** :  "baseline_cost": 23316.5,

```  "default_params": {

UserWarning: Glyph missing from font    "population_size": 50,

```    "n_elite": 5,

    "mutation_rate": 0.1,

**Causes** :    "tournament_size": 3,

- Police par défaut ne supporte pas les émojis    "n_close": 10

- matplotlib pas installé  },

  "results": [

**Solutions** :    {

```bash      "param_name": "population_size",

# Installer matplotlib      "results": [

pip install matplotlib        {

          "value": 60,

# Les warnings d'émojis sont cosmétiques, ignorables          "cost": 23050,

```          "time": 58.3,

          "routes": 22,

### Problème : Pas de configuration combinée          "gap_%": 0.65

        }

**Symptômes** :      ]

```    }

KeyError: 'combined_optimal'  ]

```}

```

**Causes** :

- Benchmark pas terminé complètement### Traçabilité Git

- Erreur pendant phase 4

**Avant chaque campagne** :

**Solutions** :

1. Relancer le benchmark```powershell

2. Vérifier les 144 configs dans le JSON# Capturer l'état du code

3. Consulter les logs d'erreurgit rev-parse --short HEAD > results/git_hash.txt



---# Version Python

python --version > results/python_version.txt

## 📝 Checklist Complète

# Dépendances

### Avant le Benchmarkpip freeze > results/requirements_freeze.txt

```

- [ ] Instance `data/instances/data.vrp` présente

- [ ] Optimum correct (27591 pour X-n101-k25)---

- [ ] Python 3.10+ installé

- [ ] Dépendances installées (`pip install -r requirements.txt`)## ✅ Checklist Avant Expérimentation

- [ ] Test rapide fonctionnel (`test_visualizations.py`)

- [ ] Dossier `results/benchmarks/` existe (créé auto sinon)### Préparation Environnement



### Pendant le Benchmark- [ ] Instance CVRP présente : `data/instances/data.vrp`

- [ ] Solution optimale présente : `data/solutions/solution_data.sol`

- [ ] Suivi de la progression dans le terminal- [ ] Optimal vérifié : 22901

- [ ] Vérification des coûts (cohérents avec l'optimum)- [ ] Python >= 3.11

- [ ] Pas d'erreurs Python affichées- [ ] Dépendances installées : `pip install -r requirements.txt`

- [ ] Temps d'exécution raisonnable (<30 min total)- [ ] Répertoire `results/` créé



### Après le Benchmark### Configuration Tests



- [ ] Résumé terminal lu et compris- [ ] Mode choisi :

- [ ] 3 fichiers générés (JSON, CSV, dossier plots/)  - [ ] **Option 9** : Exploration rapide (~15 min)

- [ ] 9 visualisations présentes dans plots/  - [ ] **Option 1-2** : Mode standard (~2-3h)

- [ ] Gap combiné < 1% ✅  - [ ] **Option 7** : Analyse complète (~3-4h)

- [ ] Configuration optimale extraite- [ ] Nombre de runs défini (1 pour rapide, 10 pour standard)

- [ ] Rapport d'analyse rédigé- [ ] Limite de temps par run (60s par défaut)

- [ ] Code de production mis à jour

### Validation Pré-test

---

- [ ] Test baseline : `python run_parameter_analysis.py` → Option 5

## 🎓 Pour Aller Plus Loin- [ ] Optimal chargé : doit afficher "22901"

- [ ] Multi-threading activé : vérifier nombre de CPU détectés

### Expérimentations Avancées

---

1. **Instances multiples**

   - Tester sur différentes tailles (50, 100, 200 clients)## 🎯 Objectifs et Critères de Succès

   - Comparer les paramètres optimaux

   - Étudier la scalabilité### Mode Exploration Rapide (Option 9)



2. **Runs multiples****Objectif** : Identifier rapidement les zones prometteuses

   - 10 runs par configuration (au lieu de 1)- ✅ 69 configurations testées en ~15 minutes

   - Analyse statistique robuste- ✅ 7 visualisations générées

   - Intervalles de confiance- ✅ Top 10 identifié avec gaps < 2%

- 💡 Permet de choisir paramètres pour validation détaillée

3. **Corrélations**

   - Matrice de corrélation entre paramètres### Mode Standard (Options 1-2)

   - Identifier interactions

   - Optimisation multi-objectif**Objectif 1** : Validation complète

- ✅ Tous les tests individuels terminés sans erreur

4. **Tuning automatique**- ✅ Statistiques (moyenne, écart-type) calculées

   - Algorithme d'optimisation bayésienne- ✅ Visualisations avec barres d'erreur

   - Grid search hiérarchique- 🎯 Au moins 50% des configs avec gap < 5%

   - Apprentissage par renforcement

**Objectif 2** : Optimisation

### Publications- ✅ Tests de combinaisons terminés

- ✅ Meilleure combinaison identifiée

Si vous utilisez ce système pour une publication :- 🎯 Gap meilleur que baseline (< 1.81%)

- 🎯 Au moins 3 combinaisons avec gap < 1%

**Citation recommandée** :

```**Objectif 3** : Excellence

Système de benchmark pour algorithme génétique CVRP- 🏆 Configuration avec gap < 0.5% (coût < 23016)

Version 4.0, Novembre 2025- 🏆 Stabilité : écart-type < 100

144 configurations testées, configuration optimale combinée- 🏆 Temps d'exécution raisonnable (< 60s)

Instance : X-n101-k25 (CVRPLIB)

Gap optimal : 0.10% (27620 vs 27591)---

```

## 🚀 Workflows Recommandés

**Figures à inclure** :

- gaps_comparison.png (progression)### Workflow 1 : Exploration Initiale (30 minutes)

- top10_best_configs.png (meilleures configs)

- 1-2 histogrammes clés (mutation_rate, population_size)**Objectif** : Vue d'ensemble rapide



---```powershell

# Étape 1: Exploration rapide

**Dernière mise à jour** : 13 novembre 2025  python run_parameter_analysis.py

**Version** : 4.0  → Option 9

**Auteur** : Équipe Optimisation CVRP  

**Contact** : Voir README.md# Résultats:

# - 69 configs testées en ~15 min

---# - 7 visualisations générées

# - Top 10 identifié

**Pour commencer** : `python benchmarks/benchmark.py` 🚀

# Étape 2: Analyser les graphiques
cd results/parameter_analysis/fast_exploration_*_plots/
# Examiner les 7 PNG générés
```

**Livrables** :
- ✅ Graphiques individuels (5 histogrammes)
- ✅ Grille comparative
- ✅ Top 10 avec médailles
- ✅ Identification des paramètres critiques

### Workflow 2 : Validation Standard (3 heures)

**Objectif** : Validation statistique approfondie

```powershell
# Étape 1: Configuration
python run_parameter_analysis.py
→ Option 8 (définir n_runs=10)

# Étape 2: Tests individuels
→ Option 1 (durée ~1-2h)

# Étape 3: Analyse visuelle intermédiaire
→ Option 3

# Étape 4: Tests de combinaisons
→ Option 2 (durée ~30-60min)

# Étape 5: Rapport final
→ Option 4
```

**Livrables** :
- ✅ Statistiques complètes (moyenne ± écart-type)
- ✅ Graphiques avec barres d'erreur
- ✅ Top combinaisons validées
- ✅ Rapport JSON complet

### Workflow 3 : Analyse Complète (4+ heures)

**Objectif** : Campagne exhaustive

```powershell
# Option automatique tout-en-un
python run_parameter_analysis.py
→ Option 7 (analyse complète)

# Exécute automatiquement:
# - Tests individuels
# - Tests combinaisons
# - Visualisations
# - Génération rapport
```

---

## 📈 Résultats Attendus

### Baseline (Configuration Par Défaut)

```python
DEFAULT_CONFIG = {
    'population_size': 50,
    'n_elite': 5,
    'mutation_rate': 0.1,
    'tournament_size': 3,
    'n_close': 10
}
```

- **Coût** : ~23300
- **Gap** : ~1.8%
- **Qualité** : ✅ **Déjà excellente**

### Après Exploration Rapide (Option 9)

**Configuration optimale attendue** :
```python
FAST_OPTIMAL = {
    'population_size': 60-80,
    'n_elite': 6-8,
    'mutation_rate': 0.08-0.12,
    'tournament_size': 4-5,
    'n_close': 15-20
}
```

- **Coût attendu** : 23000-23100
- **Gap attendu** : 0.5-1.0%
- **Amélioration** : 200-300 points vs baseline

### Après Validation Standard (Options 1-2)

**Configuration optimale validée** :
```python
VALIDATED_OPTIMAL = {
    'population_size': 70,
    'n_elite': 7,
    'mutation_rate': 0.09,
    'tournament_size': 5,
    'n_close': 18
}
```

- **Coût attendu** : 22950-23050
- **Gap attendu** : 0.2-0.7%
- **Stabilité** : Écart-type < 80
- **Amélioration** : 250-350 points vs baseline

---

## 🔧 Dépannage

### Problème 1 : Optimal non chargé

**Symptôme** : `target_optimum=None` dans Option 5

**Solution** :
```powershell
# Vérifier présence du fichier
ls data/solutions/solution_data.sol

# Si absent, le créer manuellement
echo "Cost 22901" > data/solutions/solution_data.sol
```

### Problème 2 : Exploration lente

**Symptôme** : Option 9 prend >30 minutes

**Causes possibles** :
- CPU limités (< 8 threads)
- Temps limite trop élevé (>60s)

**Solution** :
```python
# Réduire time_limit dans le code
time_limit = 45  # Au lieu de 60
```

### Problème 3 : Visualisations non générées

**Symptôme** : Dossier `_plots/` vide

**Solution** :
```powershell
# Installer matplotlib
pip install matplotlib

# Réinstaller dépendances
pip install -r requirements.txt --upgrade
```

---

**Version** : 3.0  
**Date** : 13 novembre 2025  
**Auteur** : Système d'Analyse GA-CVRP  
**Instance** : X-n153-k22 (Optimal: 22901)  
**Nouveautés v3.0** :
- ✨ Mode exploration rapide (Option 9, 69 configs, ~15min)
- 📊 Histogrammes verticaux avec gradient de couleurs
- 🥇 Top 10 avec médailles (or, argent, bronze)
- 🎨 7 visualisations automatiques
- ⚡ Multi-threading optimisé
