# Optimisation des Paramètres de l'Algorithme Génétique pour CVRP

Ce dossier contient des scripts pour optimiser les paramètres de l'algorithme génétique afin d'obtenir les meilleures performances sur votre instance CVRP.

## Fichiers d'optimisation

### 1. `quick_parameter_test.py` - Tests complets de paramètres
Ce script teste systématiquement différentes configurations de paramètres (60-150+ configurations).

**Utilisation :**
```bash
python quick_parameter_test.py
```

**Fonctionnalités :**
- **Tests étendus** : 60+ configurations base + 150+ configurations étendues
 - **Optimisé pour vitesse** : 60s par run, détection de stagnation  
- **Sauvegarde automatique** des résultats en format texte analysable
- **Fichier des meilleurs résultats** avec recommandations
- **Support des combinaisons prometteuses** basées sur la littérature

### 2. `ultra_quick_test.py` - Validation ultra-rapide
Script pour une validation rapide des tendances prometteuses (15s par run).

**Utilisation :**
```bash
python ultra_quick_test.py
```

**Avantages :**
- Test de 17 configurations représentatives en ~8-10 minutes
- Validation rapide des tendances
- Idéal pour identifier rapidement les paramètres prometteurs

### 3. `plot_parameter_results.py` - Analyse et visualisation
Script complet pour analyser et visualiser les résultats de tests.

**Utilisation :**
```bash
python plot_parameter_results.py
```

**Fonctionnalités :**
- **Menu interactif** avec 7 types de graphiques différents
- **Analyse par paramètre** avec 4 sous-graphiques détaillés  
- **Grille de comparaison** de tous les paramètres
- **Comparaison meilleure vs pire** configuration
- **Heatmaps de performance** et corrélations
- **Sauvegarde automatique** des graphiques en PNG

### 4. `optimize_ga_parameters.py` - Optimisation avancée
Script d'optimisation avec recherche par grille ou aléatoire.

**Utilisation :**
```bash
python optimize_ga_parameters.py
```

**Méthodes :**
- **Recherche par grille** : Test systématique de combinaisons
- **Recherche aléatoire** : Échantillonnage de l'espace des paramètres
- **Sauvegarde JSON** pour analyses statistiques approfondies

## Paramètres optimisés

**Paramètres de l'algorithme génétique :**
- `pop_size` : Taille de la population (40-200)
- `tournament_k` : Taille du tournoi pour la sélection (2-8)
- `elitism` : Nombre d'individus élites préservés (1-15)
- `pc` : Probabilité de crossover (0.7-0.99)
- `pm` : Probabilité de mutation (0.05-0.4)
- `use_2opt` : Activation/désactivation de l'optimisation 2-opt
- `two_opt_prob` : Probabilité d'application du 2-opt (0.0-0.8)

**Paramètres de contrôle :**
- `time_limit` : Limite de temps par run (15s, 30s, 45s selon le script)
- `time_limit` : Limite de temps par run (15s pour `ultra_quick_test.py`, 60s pour `quick_parameter_test.py` et `advanced_optimizer.py`)
- `generations` : Nombre maximum de générations (50000)

**Note importante :** Les paramètres de l'instance CVRP (capacité, coordonnées, demandes) ne sont JAMAIS modifiés.

## Guide d'utilisation recommandé

### Étape 1 : Test ultra-rapide (8-10 min)
```bash
python ultra_quick_test.py
```
Identifiez rapidement les tendances prometteuses.

### Étape 2 : Test complet (2-4h selon configurations)
```bash
python quick_parameter_test.py
```
Choisissez "1" pour 60 configs ou "2" pour 150+ configs selon vos besoins.

### Étape 3 : Analyse des résultats
```bash
python plot_parameter_results.py
```
Utilisez l'option "7" pour générer tous les graphiques ou explorez individuellement.

### Étape 4 : Optimisation avancée (optionnel)
```bash
python optimize_ga_parameters.py
```
Pour des analyses statistiques poussées avec recherche par grille.

## Interprétation des résultats

### Types de graphiques disponibles

1. **Impact par paramètre** : 4 sous-graphiques détaillés
   - Performance moyenne par valeur
   - Points individuels avec tendances  
   - Box plots de distribution
   - Corrélation et ligne de tendance

2. **Grille de comparaison** : Vue d'ensemble de tous paramètres
   - Paramètre en X, Performance en Y (axes corrigés)
   - Marquage des valeurs optimales
   - Comparaison visuelle immédiate

3. **Meilleure vs Pire** : Comparaison détaillée
   - Graphique radar des paramètres
   - Barres de comparaison directe
   - Tableau des différences

### Métriques importantes
- **Coût moyen** : Performance moyenne sur plusieurs runs
- **Écart-type** : Stabilité de l'algorithme (plus faible = plus stable)
- **Meilleur coût** : Meilleure solution trouvée
- **Amélioration %** : Potentiel d'optimisation du paramètre

## Format des fichiers de résultats

### Fichiers texte (format principal)
```
# Format: config_name|param1:value1|param2:value2|...|cost_mean|cost_min|cost_max|...
PopSize_120|pop_size:120|cost_mean:22777.3|cost_min:22769|...
```

### Fichiers de synthèse
- `parameter_test_results_YYYYMMDD_HHMMSS.txt` : Données brutes
- `best_results_summary_YYYYMMDD_HHMMSS.txt` : Top configurations
- `ultra_quick_results_YYYYMMDD_HHMMSS.txt` : Tests rapides
- Graphiques PNG générés automatiquement

## Conseils d'optimisation par type d'instance

### Instances petites (< 50 clients)
- Population plus petite (60-100)
- Plus d'élitisme (6-12)
- 2-opt obligatoire (two_opt_prob: 0.5-0.7)

### Instances moyennes (50-100 clients)  
- Population standard (100-140)
- Élitisme modéré (4-8)
- 2-opt équilibré (two_opt_prob: 0.35-0.5)

### Instances grandes (> 100 clients)
- Population plus grande (140-200)
- Moins d'élitisme (2-6) pour préserver la diversité
- 2-opt réduit (two_opt_prob: 0.2-0.35) pour la vitesse

### Optimisation par critère

**Si le temps d'exécution est critique :**
- Utilisez `ultra_quick_test.py` (15s par run)
- Réduisez `pop_size` et `two_opt_prob`
- Désactivez `use_2opt` si nécessaire

**Si la qualité de solution est prioritaire :**
- Utilisez `quick_parameter_test.py` avec tests étendus
- Augmentez `pop_size` et `two_opt_prob`
- Plus de runs par configuration (modifiez le script)

## Exemples d'utilisation

```bash
# Workflow complet recommandé
python ultra_quick_test.py          # 8-10 min : tendances
python quick_parameter_test.py      # 2-4h : tests complets  
python plot_parameter_results.py    # Analyse graphique

# Pour une analyse rapide
python ultra_quick_test.py
python plot_parameter_results.py    # Choisir option 1-5

# Pour optimisation poussée
python quick_parameter_test.py      # Option 2 (configurations étendues)
python plot_parameter_results.py    # Option 7 (tous graphiques)
python optimize_ga_parameters.py    # Si besoin d'analyses statistiques
```

## Dépendances

**Obligatoires :**
```bash
# Inclus dans le projet
from cvrp_data import load_cvrp_instance  
from ga import genetic_algorithm
from solution import verify_solution
```

**Optionnelles (pour graphiques) :**
```bash
pip install matplotlib numpy
```

## Troubleshooting

**Problème** : "Fichier data.vrp introuvable"  
**Solution** : Vérifiez que `data.vrp` est dans le même dossier

**Problème** : Temps d'exécution trop long  
**Solution** : Utilisez `ultra_quick_test.py` ou réduisez les configurations

**Problème** : Graphiques ne s'affichent pas  
**Solution** : Installez matplotlib avec `pip install matplotlib`

**Problème** : Solutions invalides  
**Solution** : Vérifiez les contraintes de capacité dans l'instance CVRP

**Problème** : Pas d'amélioration  
**Solution** : Augmentez le nombre de configurations ou utilisez les combinaisons prometteuses