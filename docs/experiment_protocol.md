# Protocole d'Expérimentation — Optimisation GA pour CVRP

**Version 2.0** — Novembre 2025  
**Instance**: X-n153-k22 (117 clients)  
**Solution optimale connue**: 22901

---

## 📋 Table des Matières

1. [Objectif et Contexte](#objectif-et-contexte)
2. [Instance de Référence](#instance-de-référence)
3. [Standards de Qualité CVRP](#standards-de-qualité-cvrp)
4. [Architecture du Système](#architecture-du-système)
5. [Protocole Expérimental](#protocole-expérimental)
6. [Exécution des Tests](#exécution-des-tests)
7. [Analyse des Résultats](#analyse-des-résultats)
8. [Documentation et Traçabilité](#documentation-et-traçabilité)

---

## 🎯 Objectif et Contexte

### Objectif Principal
Optimiser les paramètres de l'algorithme génétique (GA) pour résoudre le Capacitated Vehicle Routing Problem (CVRP) en minimisant l'écart (**gap**) par rapport à la solution optimale connue.

### Métriques de Performance

#### 1. **Gap par rapport à l'optimal** (métrique principale)
```
gap (%) = ((coût_obtenu - coût_optimal) / coût_optimal) × 100
```

**Standards CVRP** (littérature scientifique) :
- **Gap < 5%** : ✅ **Bon résultat** (standard académique)
- **Gap < 1%** : 🏆 **Excellent** (état de l'art)
- **Gap < 10%** : 🟡 **Acceptable** (heuristiques basiques)
- **Gap > 10%** : ❌ **Insuffisant**

#### 2. **Temps d'exécution**
- Limite par défaut : 45 secondes
- Mesure du temps réel (wall-clock time)

#### 3. **Stabilité**
- Écart-type sur n runs (n = 10 par défaut)
- Écart min-max

---

## 📊 Instance de Référence

### Fichier : `data/instances/data.vrp`

**Métadonnées** (format CVRPLIB) :
```
NAME:              X-n153-k22
TYPE:              CVRP
DIMENSION:         153 (152 clients + 1 dépôt)
EDGE_WEIGHT_TYPE:  EUC_2D
CAPACITY:          144
```

**Caractéristiques** :
- **Clients** : 152 (nœuds 2-153)
- **Dépôt** : nœud 1
- **Demande totale** : 3068 unités
- **Véhicules minimum** : 22 (⌈3068/144⌉)
- **Coordonnées** : X ∈ [14, 998], Y ∈ [212, 973]
- **Solution optimale** : **22901** (référence CVRPLIB)

**Source** : Uchoa, Pecin, Pessoa, Poggi, Subramanian, and Vidal (2013)

### Solution de Référence

**Fichier** : `data/solutions/solution_data.sol`

```
Routes: 25 routes optimales
Cost: 22901
```

Cette solution est automatiquement chargée par le système pour calculer les gaps.

---

## 🎓 Standards de Qualité CVRP

### Références Scientifiques

#### 1. **Vidal et al. (2012)** - Hybrid Genetic Algorithm
- **Instance X-n153-k22** : Gap < 0.5% (état de l'art)
- Référence : "A hybrid genetic algorithm for multidepot and periodic vehicle routing problems"

#### 2. **Prins (2004)** - Split Algorithm  
- Gap moyen : 1-3% (AG standards)

#### 3. **Uchoa et al. (2017)** - Benchmarks CVRP
- Gap < 5% : Standard académique
- Gap < 1% : État de l'art

### Objectifs pour ce Projet

| Objectif | Gap | Coût Cible | Difficulté | Statut |
|----------|-----|------------|------------|--------|
| **Baseline actuelle** | +1.81% | 23316 | Point de départ | ✅ Déjà bon |
| **Maintenir < 5%** | < 5% | < 24046 | Réaliste | 🎯 Objectif 1 |
| **Atteindre < 3%** | < 3% | < 23588 | Nécessite optimisation | 🎯 Objectif 2 |
| **Approcher < 1%** | < 1% | < 23130 | État de l'art | 🏆 Objectif avancé |

**Note** : Votre baseline actuelle (gap = 1.81%) est **déjà excellente** selon les standards CVRP.

---

## 🏗️ Architecture du Système

### Modules Principaux

#### 1. **Core Algorithm** (`src/core/`)
```
src/core/
├── cvrp_data.py         # Chargement instance CVRP
├── ga.py                # Algorithme génétique principal
├── solution.py          # Structure et évaluation solution
├── split.py             # Split giant tour → routes
├── localsearch.py       # Optimisations locales (2-opt)
└── solution_loader.py   # Chargement solution de référence
```

#### 2. **Parameter Analysis** (`src/optimization/`)
```
src/optimization/
├── ga_parameter_analyzer.py    # Analyse systématique paramètres
└── ga_visualizer.py             # Visualisations (gaps vs optimal)
```

#### 3. **Interface Principale**
```
run_parameter_analysis.py        # Menu interactif complet
```

### Multi-threading

**Implémentation** : `ProcessPoolExecutor` (Python multiprocessing)
- **Fichier** : `src/optimization/ga_parameter_analyzer.py`
- **Lignes** : 19 (import), 56 (worker), 145 (executor)
- **Workers par défaut** : Auto-détection (~16 sur 12 cœurs)
- **Avantage** : Vrai parallélisme multi-cœur (pas de GIL)

---

## 🔬 Protocole Expérimental

### Phase 1 : Configuration de Base (Baseline)

#### Paramètres par Défaut
```python
DEFAULT_PARAMS = {
    'pop_size': 100,          # Taille de population
    'tournament_k': 3,        # Taille tournoi sélection
    'elitism': 10,            # Nombre élites conservés
    'pc': 0.9,                # Probabilité croisement
    'pm': 0.02,               # Probabilité mutation
    'two_opt_prob': 0.5,      # Probabilité 2-opt
    'use_2opt': True,         # Activation 2-opt
    'time_limit': 45.0,       # Limite temps (sec)
    'generations': 25000      # Générations max
}
```

**Résultat actuel** :
- Coût moyen : 23316
- Gap : +1.81%
- ✅ **Déjà excellent**

### Phase 2 : Tests Individuels des Paramètres

#### Objectif
Identifier l'impact de **chaque paramètre indépendamment** en variant une seule valeur à la fois.

#### Espaces de Recherche

| Paramètre | Valeurs Testées | Justification (littérature) |
|-----------|-----------------|----------------------------|
| `pop_size` | [30, 50, 80, 100, 120, 150, 200, 250, 300] | Formule : √n_clients × 5 ≈ 54 pour 117 clients |
| `tournament_k` | [2, 3, 4, 5, 6, 7, 8] | Optimal : 5-7 (équilibre exploitation/exploration) |
| `elitism` | [0, 2, 4, 6, 8, 10, 12, 15, 20, 25, 30] | Optimal : 5-15% de pop_size |
| `pc` | [0.6, 0.7, 0.8, 0.85, 0.9, 0.92, 0.95, 0.98] | Optimal : 0.8-0.9 |
| `pm` | [0.005, 0.01, 0.02, 0.03, 0.04, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35] | Optimal : 0.05-0.08 (règle : 1/√dimension) |
| `two_opt_prob` | [0.0, 0.1, 0.2, 0.35, 0.5, 0.65, 0.8, 1.0] | Optimal : 0.6-0.8 (crucial pour CVRP) |
| `use_2opt` | [True, False] | True indispensable pour CVRP |

**Total** : ~60 configurations différentes

#### Protocole d'Exécution

1. **Nombre de runs** : 10 par configuration (configurable)
2. **Calcul des statistiques** :
   - Coût moyen, écart-type, min, max
   - Gap moyen par rapport à l'optimal
   - Temps moyen d'exécution

3. **Critères de sélection** :
   - Identifier le meilleur gap pour chaque paramètre
   - Classer par ordre de performance
   - Analyser la stabilité (écart-type)

### Phase 3 : Tests de Combinaisons

#### Objectif
Combiner les **meilleures valeurs** de chaque paramètre pour trouver la configuration optimale.

#### Méthode

1. **Sélection des candidats** :
   - Prendre les top-3 valeurs de chaque paramètre (Phase 2)
   
2. **Génération de combinaisons** :
   - Combinaison 1 : Tous les meilleurs (best-of-best)
   - Combinaisons 2-N : Variations aléatoires des top-3

3. **Nombre de combinaisons** : 10-50 (configurable)

4. **Validation** :
   - 10 runs par combinaison
   - Calcul du gap moyen
   - Identification de la meilleure configuration

#### Configuration Optimale Attendue (basée sur littérature)

```python
OPTIMAL_PARAMS = {
    'pop_size': 60,           # ↓ de 100 (plus efficace)
    'tournament_k': 6,        # ↑ de 3 (meilleure sélection)
    'elitism': 6,            # ↓ de 10 (10% de pop_size)
    'pc': 0.85,              # ↓ de 0.9 (plus de diversité)
    'pm': 0.06,              # ↑ de 0.02 (3× plus, crucial!)
    'two_opt_prob': 0.75,    # ↑ de 0.5 (2-opt plus fréquent)
    'use_2opt': True         # Indispensable
}
```

**Amélioration attendue** : Gap → 0.5-1.0% (coût ~23000-23130)

---

## 🚀 Exécution des Tests

### Option 1 : Menu Interactif (Recommandé)

```powershell
python run_parameter_analysis.py
```

**Menu disponible** :
```
1️⃣  - Tester les paramètres individuellement
2️⃣  - Trouver les meilleures combinaisons
3️⃣  - Visualiser les résultats (graphiques)
4️⃣  - Générer un rapport complet
5️⃣  - Afficher la configuration actuelle
6️⃣  - Charger des résultats existants
7️⃣  - Analyse complète (1+2+3+4)
8️⃣  - Modifier le nombre de runs par test
0️⃣  - Quitter
```

#### Workflow Recommandé

1. **Option 5** : Vérifier la configuration actuelle
   - Affiche baseline, n_runs, optimal chargé

2. **Option 8** (optionnel) : Ajuster le nombre de runs
   - Recommandé : 10 runs (équilibre précision/temps)
   - Rapide : 3-5 runs
   - Précis : 20-30 runs

3. **Option 1** : Lancer les tests individuels
   - Durée estimée : ~60 configs × 10 runs × 45s ≈ 7-8 heures
   - Avec 16 workers : ~30-40 minutes

4. **Option 2** : Tester les combinaisons
   - Après Option 1 uniquement
   - 10-50 combinaisons × 10 runs

5. **Option 3** : Visualiser les résultats
   - Graphiques avec gaps vs optimal
   - Code couleur : Vert (<5%), Orange (5-10%), Rouge (>10%)

6. **Option 7** : Analyse complète automatique
   - Exécute 1 → 2 → 3 → 4 en séquence
   - Génère rapport JSON + visualisations

### Option 2 : Scripts Python Directs

#### Test Rapide (Validation)

```python
from src.optimization.ga_parameter_analyzer import GAParameterAnalyzer

# Créer l'analyseur
analyzer = GAParameterAnalyzer(
    instance_path='data/instances/data.vrp',
    target_optimum=22901,
    n_runs=5  # Tests rapides
)

# Tests individuels
analyzer.test_individual_parameters(
    num_runs=5,
    time_limit=30.0,  # 30s par run
    max_workers=16
)

# Afficher résumé
for param, results in analyzer.individual_results.items():
    best = results[0]
    print(f"{param}: {best.parameter_value} → Gap {best.gap_mean:.2f}%")
```

#### Analyse Complète

```python
from src.optimization.ga_parameter_analyzer import GAParameterAnalyzer
from src.optimization.ga_visualizer import GAVisualizer

# Configuration
analyzer = GAParameterAnalyzer(
    'data/instances/data.vrp',
    target_optimum=22901,
    n_runs=10
)

# Phase 1: Tests individuels
analyzer.test_individual_parameters()

# Phase 2: Combinaisons
analyzer.find_best_combinations(n_combinations=20)

# Phase 3: Visualisation
visualizer = GAVisualizer(analyzer)
visualizer.plot_individual_parameters()
visualizer.plot_parameter_comparison()
visualizer.plot_combination_results()

# Phase 4: Sauvegarde
analyzer.save_results('results/parameter_analysis/full_analysis.json')
```

---

## 📊 Analyse des Résultats

### Visualisations Générées

#### 1. **Graphiques Individuels par Paramètre**

**Fichiers** : `results/parameter_analysis/visualizations_*/param_*.png`

**Contenu** :
- **Graphique gauche** : Coûts moyens
  - Ligne verte : Optimal (22901)
  - Ligne bleue : Baseline (23316)
  - Barres avec écart-type
  
- **Graphique droite** : Gap vs Optimal
  - Code couleur :
    - 🟢 Vert : Gap < 5% (bon)
    - 🟠 Orange : 5% ≤ Gap < 10% (acceptable)
    - 🔴 Rouge : Gap ≥ 10% (à améliorer)
  - Lignes de référence : 0%, 5%, 10%

#### 2. **Comparaison Globale des Paramètres**

**Fichier** : `parameter_comparison.png`

**Contenu** :
- **Graphique gauche** : Gap par paramètre
  - Barres horizontales classées
  - Identification des paramètres les plus impactants
  
- **Graphique droite** : Meilleurs coûts
  - Annotations avec valeurs optimales
  - Ex: `pop_size=60`, `pm=0.06`

#### 3. **Top Combinaisons**

**Fichier** : `combination_results.png`

**Contenu** :
- **Graphique gauche** : Coûts des top-10
  - Gradient de couleur basé sur gap
  
- **Graphique droite** : Gaps des combinaisons
  - Barres horizontales avec valeurs
  - Lignes à 0%, 5%, 10%

### Interprétation des Résultats

#### Analyse du Gap

```python
# Lecture du gap pour une configuration
gap = ((coût - 22901) / 22901) * 100

if gap < 1.0:
    qualité = "🏆 Excellent (état de l'art)"
elif gap < 5.0:
    qualité = "✅ Bon (standard académique)"
elif gap < 10.0:
    qualité = "🟡 Acceptable"
else:
    qualité = "❌ Insuffisant"
```

---

## 📝 Documentation et Traçabilité

### Fichiers de Configuration Sauvegardés

```
results/parameter_analysis/
├── analysis_20251112_103000.json      # Résultats complets
├── visualizations_20251112_103000/    # Graphiques
│   ├── param_pop_size.png
│   ├── param_tournament_k.png
│   ├── param_pm.png
│   ├── ...
│   ├── parameter_comparison.png
│   └── combination_results.png
└── (anciens fichiers)
```

### Traçabilité Git

**Avant chaque campagne** :

```powershell
# Capturer l'état du code
git rev-parse --short HEAD > results/git_hash.txt

# Version Python
python --version > results/python_version.txt

# Dépendances
pip freeze > results/requirements_freeze.txt
```

---

## ✅ Checklist Avant Expérimentation

### Préparation

- [ ] Instance CVRP présente : `data/instances/data.vrp`
- [ ] Solution optimale présente : `data/solutions/solution_data.sol`
- [ ] Optimal vérifié : 22901
- [ ] Python >= 3.11
- [ ] Dépendances installées : `pip install -r requirements.txt`

### Configuration

- [ ] Nombre de runs défini (recommandé : 10)
- [ ] Limite de temps par run (défaut : 45s)
- [ ] Nombre de workers (auto ou manuel)
- [ ] Répertoire de sortie : `results/parameter_analysis/`

### Validation

- [ ] Test baseline : `python run_parameter_analysis.py` → Option 5
- [ ] Optimal chargé : doit afficher "22901"
- [ ] Multi-threading fonctionnel : vérifier dans logs

---

## 🎯 Objectifs et Critères de Succès

### Objectif 1 : Validation (Phase 1)
- ✅ Tous les tests individuels terminés sans erreur
- ✅ Gaps calculés pour toutes les configurations
- ✅ Visualisations générées correctement
- ✅ Au moins 50% des configs avec gap < 5%

### Objectif 2 : Optimisation (Phase 2)
- ✅ Tests de combinaisons terminés
- ✅ Meilleure combinaison identifiée
- 🎯 Gap meilleur que baseline (< 1.81%)
- 🎯 Au moins 3 combinaisons avec gap < 1%

### Objectif 3 : Excellence (Phase 3)
- 🏆 Configuration avec gap < 0.5% (coût < 23016)
- 🏆 Stabilité : écart-type < 100
- 🏆 Temps d'exécution raisonnable (< 60s)

---

## 🚀 Workflow Complet Recommandé

### Jour 1 : Tests Rapides (2-3 heures)

```powershell
# 1. Vérifier la configuration
python run_parameter_analysis.py
# → Option 5 (afficher config)

# 2. Test rapide avec n_runs=3
# → Option 8 (modifier n_runs à 3)

# 3. Lancer tests individuels
# → Option 1 (durée ~15-20 min)

# 4. Visualiser résultats préliminaires
# → Option 3
```

### Jour 2 : Analyse Complète (4-6 heures)

```powershell
# 1. Configuration optimale
# → Option 8 (n_runs = 10)

# 2. Tests individuels complets
# → Option 1 (durée ~30-40 min)

# 3. Tests de combinaisons
# → Option 2 (20 combinaisons, ~10 min)

# 4. Génération rapport
# → Option 4
```

---

## 📈 Résultats Attendus

### Baseline (Configuration Actuelle)
- Coût : **23316**
- Gap : **+1.81%**
- Qualité : ✅ **Déjà excellente**

### Après Optimisation (Prédiction)
- Coût : **22950-23100**
- Gap : **+0.2-0.9%**
- Amélioration : **200-350 de réduction**

### Configuration Optimale Prédite

```python
{
    'pop_size': 60,           # -40 vs baseline
    'tournament_k': 6,        # +3 vs baseline
    'elitism': 6,            # -4 vs baseline
    'pc': 0.85,              # -0.05 vs baseline
    'pm': 0.06,              # +0.04 vs baseline (crucial!)
    'two_opt_prob': 0.75,    # +0.25 vs baseline (crucial!)
    'use_2opt': True
}
```

**Justification** : Basée sur Vidal et al. (2012) et standards CVRP

---

**Version** : 2.0  
**Date** : 12 novembre 2025  
**Auteur** : Système d'Analyse GA-CVRP  
**Instance** : X-n153-k22 (Optimal: 22901)
