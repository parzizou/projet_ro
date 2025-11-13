# 🚀 Script de Benchmark Professionnel

Script complet et autonome pour évaluer les performances de l'algorithme génétique sur l'instance CVRP X-n153-k22.

## 📋 Vue d'Ensemble

**Fichier** : `scripts/benchmark.py`

**Objectif** : Tester systématiquement 69 configurations de paramètres pour identifier les meilleures performances.

**Durée** : ~15 minutes (avec multi-threading)

---

## ✨ Caractéristiques

### 🎯 Fonctionnalités Principales

- ✅ **69 configurations** testées automatiquement
- ✅ **Multi-threading** (tous les CPU utilisés)
- ✅ **Calcul automatique du baseline** avec paramètres par défaut
- ✅ **7 visualisations** professionnelles générées
- ✅ **Export JSON + CSV** des résultats
- ✅ **Statistiques détaillées** (coût, gap, amélioration, temps)
- ✅ **Top 10** des meilleures configurations
- ✅ **Comparaison avec l'optimal** connu (22901)

### 📊 Grille de Paramètres

```python
EXTENDED_GRID = {
    'population_size': [20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100, 
                        120, 150, 180, 200, 250, 300],  # 18 valeurs
    
    'n_elite': [1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 15, 20],  # 12 valeurs
    
    'mutation_rate': [0.01, 0.02, 0.03, 0.05, 0.07, 0.1, 0.12, 0.15, 
                      0.18, 0.2, 0.22, 0.25, 0.28, 0.3, 0.35, 0.4],  # 16 valeurs
    
    'tournament_size': [2, 3, 4, 5, 6, 7, 8, 10, 12, 15],  # 10 valeurs
    
    'n_close': [3, 5, 7, 10, 12, 15, 18, 20, 25, 30, 35, 40, 50]  # 13 valeurs
}
```

**Total** : 18 + 12 + 16 + 10 + 13 = **69 configurations**

---

## 🚀 Utilisation

### Lancement Simple

```powershell
python scripts/benchmark.py
```

### Workflow Interactif

1. **Chargement automatique** de l'instance `data/instances/data.vrp`
2. **Affichage de la configuration** :
   - Nom de l'instance
   - Nombre de clients
   - Optimum connu
3. **Calcul du baseline** avec paramètres par défaut
4. **Confirmation utilisateur** avant lancement
5. **Exécution parallèle** des 69 tests
6. **Génération automatique** des résultats et visualisations

### Exemple de Session

```
================================================================================
     🚀 BENCHMARK PROFESSIONNEL - ALGORITHME GÉNÉTIQUE CVRP
================================================================================

────────────────────────────────────────────────────────────────────────────────
📊 Configuration
────────────────────────────────────────────────────────────────────────────────
📂 Chargement de l'instance: data/instances/data.vrp
   Nom: X-n153-k22
   Clients: 152
   Capacité: 144
   🎯 Optimum connu: 22901

────────────────────────────────────────────────────────────────────────────────
📊 Calcul du Baseline
────────────────────────────────────────────────────────────────────────────────
🔧 Paramètres par défaut: {'population_size': 50, 'n_elite': 5, ...}
   ✅ Coût baseline: 23316.0
   ⏱️  Temps: 58.3s
   🚛 Routes: 22
   📊 Gap vs optimal: +1.81%

────────────────────────────────────────────────────────────────────────────────
📊 Configuration du Benchmark
────────────────────────────────────────────────────────────────────────────────
  • Configurations à tester: 69
  • Runs par configuration: 1
  • Total d'exécutions GA: 69
  • Threads: 16
  • Temps limite par run: 60s
  • Durée estimée: ~4 minutes

⚠️  Lancer le benchmark ? (o/n): o

────────────────────────────────────────────────────────────────────────────────
📊 Test du paramètre: population_size
────────────────────────────────────────────────────────────────────────────────
Valeurs à tester: [20, 25, 30, ..., 300]
✓ [1/18] population_size=20: Coût=23450 | Amélioration=-0.57% | Gap: +2.40%
✓ [2/18] population_size=25: Coût=23380 | Amélioration=-0.27% | Gap: +2.09%
...
✓ [18/18] population_size=300: Coût=23120 | Amélioration=+0.84% | Gap: +0.96%

🏆 Meilleur pour population_size:
   Valeur: 60
   Coût: 23050.0
   Amélioration vs baseline: +1.14%
   Gap vs optimal: +0.65%
   ⏱️  Temps de test: 12.3s

[... tests pour les autres paramètres ...]

────────────────────────────────────────────────────────────────────────────────
📊 Génération des Visualisations
────────────────────────────────────────────────────────────────────────────────
📁 Dossier de visualisations: results/benchmarks/benchmark_20251113_143000_plots

🎨 Génération des histogrammes individuels...
   ✓ [1/5] population_size.png créé
   ✓ [2/5] n_elite.png créé
   ✓ [3/5] mutation_rate.png créé
   ✓ [4/5] tournament_size.png créé
   ✓ [5/5] n_close.png créé

🎨 Génération du graphique comparatif...
   ✓ parameter_comparison.png créé

🎨 Génération du Top 10...
   ✓ top10_best_configs.png créé

✅ 7 visualisations créées

================================================================================
                     📊 RÉSUMÉ FINAL DU BENCHMARK
================================================================================

🎯 Baseline: 23316.0
🎯 Optimal connu: 22901 (Gap baseline: +1.81%)

⏱️  Temps total: 15.2 minutes

📈 Meilleurs résultats par paramètre:

  • population_size     =     60 → Coût: 23050.0 | Amélioration: +1.14% | Gap: +0.65%
  • n_elite             =      8 → Coût: 23080.0 | Amélioration: +1.01% | Gap: +0.78%
  • mutation_rate       =   0.08 → Coût: 23070.0 | Amélioration: +1.06% | Gap: +0.74%
  • tournament_size     =      5 → Coût: 23090.0 | Amélioration: +0.97% | Gap: +0.83%
  • n_close             =     15 → Coût: 23100.0 | Amélioration: +0.93% | Gap: +0.87%

🏆 TOP 3 CONFIGURATIONS GLOBALES:

  🥇 #1: population_size=60 → Coût: 23050.0 | Amélioration: +1.14% | Gap: +0.65%
  🥈 #2: mutation_rate=0.08 → Coût: 23070.0 | Amélioration: +1.06% | Gap: +0.74%
  🥉 #3: n_elite=8 → Coût: 23080.0 | Amélioration: +1.01% | Gap: +0.78%

================================================================================

💾 Tous les résultats sauvegardés dans: results/benchmarks/
📊 Visualisations disponibles dans: results/benchmarks/benchmark_20251113_143000_plots/

✅ Benchmark terminé avec succès!
```

---

## 📊 Résultats Générés

### 1. Fichiers de Données

```
results/benchmarks/
├── benchmark_YYYYMMDD_HHMMSS.json      # Résultats complets (structure)
├── benchmark_YYYYMMDD_HHMMSS.csv       # Résultats tabulaires (Excel)
└── benchmark_YYYYMMDD_HHMMSS_plots/    # Dossier des visualisations
    ├── population_size.png             # Histogramme individuel
    ├── n_elite.png                     # Histogramme individuel
    ├── mutation_rate.png               # Histogramme individuel
    ├── tournament_size.png             # Histogramme individuel
    ├── n_close.png                     # Histogramme individuel
    ├── parameter_comparison.png        # Grille comparative 2×3
    └── top10_best_configs.png          # Top 10 avec médailles
```

### 2. Structure JSON

```json
{
  "timestamp": "20251113_143000",
  "instance": "X-n153-k22",
  "dimension": 153,
  "capacity": 144,
  "n_runs": 1,
  "baseline_cost": 23316.0,
  "target_optimum": 22901,
  "default_params": {
    "population_size": 50,
    "n_elite": 5,
    "mutation_rate": 0.1,
    "tournament_size": 3,
    "n_close": 10
  },
  "parameter_spaces": { ... },
  "total_configs": 69,
  "results": [
    {
      "param_name": "population_size",
      "results": [
        {
          "param": "population_size",
          "value": 60,
          "cost": 23050.0,
          "time": 58.3,
          "routes": 22,
          "params": { ... }
        },
        ...
      ]
    },
    ...
  ]
}
```

### 3. Structure CSV

```csv
parameter,value,cost,time_sec,routes,improvement_%,gap_%
population_size,20,23450,57.2,23,-0.57,2.40
population_size,25,23380,58.1,22,-0.27,2.09
population_size,30,23320,59.4,22,0.02,1.83
...
```

---

## 🎨 Visualisations

### 1. Histogrammes Individuels (5 graphiques)

**Fichiers** : `population_size.png`, `n_elite.png`, etc.

**Caractéristiques** :
- 📊 Barres verticales avec gradient de couleurs
- 🟢 Vert : Meilleures valeurs
- 🔴 Rouge : Moins bonnes valeurs
- 📏 Lignes de référence (baseline, optimal)
- 🎨 Gradient RdYlGn_r (Red-Yellow-Green reversed)

**Interprétation** :
- Plus la barre est basse et verte, meilleur est le résultat
- Identifier les "vallées" pour trouver les valeurs optimales

### 2. Graphique Comparatif 2×3

**Fichier** : `parameter_comparison.png`

**Caractéristiques** :
- 📊 6 sous-graphiques (un par paramètre)
- ⭐ Étoile dorée sur la meilleure configuration
- 🟢 Barre verte pour le meilleur résultat
- 💬 Bulle jaune avec annotation du meilleur
- 📈 Gradient de couleurs selon performance

**Légende** :
- **Vert** = Meilleur résultat
- **★ Étoile dorée** = Configuration optimale
- **Rouge** = Moins bon résultat

### 3. Top 10 avec Médailles

**Fichier** : `top10_best_configs.png`

**Caractéristiques** :
- 🏆 Histogramme vertical du top 10
- 🥇 Médaille d'or pour le 1er
- 🥈 Médaille d'argent pour le 2e
- 🥉 Médaille de bronze pour le 3e
- 📊 Annotations avec coût et gap %
- 🎨 Gradient de couleurs

---

## 🔧 Configuration Avancée

### Modifier la Grille de Paramètres

Éditer `scripts/benchmark.py`, lignes ~380-395 :

```python
extended_spaces = {
    'population_size': [20, 30, 40, 50, 60, 80, 100],  # Réduire les valeurs
    'n_elite': [2, 4, 6, 8, 10],                       # Simplifier
    # ...
}
```

### Modifier le Temps Limite

Ligne ~440 et ~560 :

```python
baseline_cost, baseline_time, baseline_routes = run_ga_single(
    instance, default_params, time_limit=45  # Changer de 60 à 45
)
```

### Changer l'Instance

Ligne ~370 :

```python
instance_path = "data/instances/autre_instance.vrp"
```

---

## 📈 Interprétation des Résultats

### Métriques Clés

**Gap** : Écart par rapport à l'optimal connu
```
gap (%) = ((coût_obtenu - optimal) / optimal) × 100
```

**Amélioration** : Gain par rapport au baseline
```
amélioration (%) = ((baseline - coût_obtenu) / baseline) × 100
```

### Standards CVRP

| Gap | Qualité | Interprétation |
|-----|---------|----------------|
| < 1% | 🏆 Excellent | État de l'art |
| 1-5% | ✅ Bon | Standard académique |
| 5-10% | 🟡 Acceptable | Heuristiques basiques |
| > 10% | ❌ Insuffisant | À améliorer |

### Analyse des Résultats

1. **Identifier les paramètres critiques** :
   - Ceux avec le plus d'amélioration
   - Ceux avec variation significative

2. **Comparer au baseline** :
   - Amélioration positive = Meilleur que défaut
   - Amélioration négative = Moins bon

3. **Analyser le Top 10** :
   - Configurations les plus performantes
   - Patterns communs entre les meilleures

4. **Valider avec l'optimal** :
   - Gap < 1% = Excellent
   - Gap < 5% = Très bon

---

## 🎯 Cas d'Usage

### 1. Benchmark Initial
**Objectif** : Première exploration des paramètres

```powershell
python scripts/benchmark.py
```

**Durée** : ~15 minutes  
**Résultat** : Vue d'ensemble des performances

### 2. Validation de Configuration
**Objectif** : Tester une configuration spécifique

1. Modifier `default_params` dans le script
2. Exécuter le benchmark
3. Comparer avec le baseline d'origine

### 3. Comparaison d'Instances
**Objectif** : Benchmarker plusieurs instances

1. Exécuter pour `data.vrp`
2. Modifier `instance_path`
3. Exécuter pour `data2.vrp`, etc.
4. Comparer les résultats

---

## 🚨 Dépannage

### Problème 1 : Instance non trouvée

**Symptôme** :
```
❌ Instance introuvable: data/instances/data.vrp
```

**Solution** :
```powershell
# Vérifier l'existence
ls data/instances/data.vrp

# Créer le dossier si nécessaire
mkdir data/instances
```

### Problème 2 : Visualisations non générées

**Symptôme** :
```
⚠️  Erreur lors de la génération des visualisations
```

**Solution** :
```powershell
# Installer matplotlib
pip install matplotlib numpy

# Ou réinstaller dépendances
pip install -r requirements.txt --upgrade
```

### Problème 3 : Benchmark trop lent

**Symptôme** : Durée > 30 minutes

**Solution** :
- Réduire la grille de paramètres
- Diminuer `time_limit` de 60 à 45 secondes
- Vérifier le nombre de CPU utilisés

---

## 📚 Références

- **Protocole expérimental** : `docs/experiment_protocol.md`
- **Guide d'optimisation** : `docs/optimization_guide.md`
- **Standards CVRP** : Vidal et al. (2012)

---

## ✅ Checklist Pre-Benchmark

Avant de lancer le benchmark :

- [ ] Instance présente : `data/instances/data.vrp`
- [ ] Solution optimale connue : 22901
- [ ] Python >= 3.11 installé
- [ ] Dépendances installées : `matplotlib`, `numpy`
- [ ] ~20 Go de RAM disponibles
- [ ] ~15-20 minutes de temps disponible
- [ ] Répertoire `results/benchmarks/` créé

---

**Version** : 1.0  
**Date** : 13 novembre 2025  
**Instance testée** : X-n153-k22 (152 clients)  
**Optimal connu** : 22901
