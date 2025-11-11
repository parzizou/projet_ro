# 📊 Visualisations avec Gap vs Optimal - Documentation

## 🎯 Objectif

Les visualisations ont été modifiées pour afficher le **gap par rapport à la solution optimale (22901)** au lieu de l'amélioration par rapport à la baseline. Cela permet de mieux évaluer la qualité des résultats.

## ✅ Modifications Apportées

### 1. **Graphiques Individuels des Paramètres** (`plot_individual_parameters`)

#### Avant :
- Graphique de droite : Amélioration vs baseline en %
- Couleurs basées sur baseline uniquement

#### Après :
- **Graphique de gauche** :
  - Ligne verte : Solution optimale (22901)
  - Ligne bleue : Baseline (23316)
  - Titre affiche l'optimal
  
- **Graphique de droite** : **Gap vs Optimal en %**
  - Formule : `gap = ((coût - 22901) / 22901) × 100`
  - Ligne verte à 0% (optimal)
  - Ligne orange à +1% (seuil d'excellence)
  - **Code couleur intelligent** :
    - 🟢 Vert : gap < 1% (excellent)
    - 🟠 Orange : 1% ≤ gap < 2% (bon)
    - 🔴 Rouge : gap ≥ 2% (à améliorer)

### 2. **Comparaison des Paramètres** (`plot_parameter_comparison`)

#### Avant :
- Amélioration vs baseline uniquement

#### Après :
- **Graphique de gauche** : **Gap vs Optimal par paramètre**
  - Montre directement la distance à l'optimal
  - Ligne verte à 0% (optimal)
  - Ligne orange à +1% (seuil)
  
- **Graphique de droite** : **Meilleurs coûts obtenus**
  - Ligne verte : Optimal (22901)
  - Ligne bleue : Baseline (23316)
  - Annotations avec valeurs optimales des paramètres
  - Ex: `pop_size=60`, `pm=0.06`

### 3. **Résultats des Combinaisons** (`plot_combination_results`)

#### Avant :
- Amélioration vs baseline
- Pas de référence à l'optimal

#### Après :
- **Graphique de gauche** : **Coûts des combinaisons**
  - Ligne verte : Optimal (22901)
  - Ligne bleue : Baseline (23316)
  - Couleurs basées sur le gap (gradient)
  
- **Graphique de droite** : **Gap vs Optimal pour chaque combinaison**
  - Barres horizontales avec gaps en %
  - Ligne verte à 0% (optimal)
  - Ligne orange à +1% (seuil d'excellence)
  - Valeurs affichées sur chaque barre

## 📐 Formules Utilisées

### Gap vs Optimal
```python
gap = ((coût_obtenu - coût_optimal) / coût_optimal) × 100
```

**Interprétation** :
- `gap = 0%` → Solution optimale trouvée ! 🎯
- `gap < 1%` → Excellent résultat (< 229 de différence)
- `gap < 2%` → Bon résultat (< 458 de différence)
- `gap > 2%` → À améliorer

### Exemple pour votre instance
- **Optimal** : 22901
- **Baseline** : 23316 → gap = +1.81%
- **Objectif** : Trouver gap < 1% (coût < 23130)

## 🎨 Code Couleur

### Pour les barres de coût
```python
if gap < 1.0:
    couleur = 'green'     # Excellent
elif gap < 2.0:
    couleur = 'orange'    # Bon
else:
    couleur = 'red'       # À améliorer
```

### Pour les graphiques de gap
- Gradient du vert (0%) au rouge (>5%)
- Seuils visuels à 0% et 1%

## 🔧 Utilisation

### Option 1 : Test avec données simulées
```bash
python test_visualizations_with_gap.py
```
Ce script génère des résultats simulés et affiche les visualisations.

### Option 2 : Analyse réelle
```bash
python run_parameter_analysis.py
```
1. Option 1 : Tester les paramètres individuellement
2. Option 3 : Visualiser les résultats (affiche gaps vs optimal)

### Option 3 : Code personnalisé
```python
from src.optimization.ga_parameter_analyzer import GAParameterAnalyzer
from src.optimization.ga_visualizer import GAVisualizer

# Créer l'analyseur avec optimal
analyzer = GAParameterAnalyzer(
    'data/instances/data.vrp',
    target_optimum=22901,
    n_runs=10
)

# Lancer les tests
analyzer.test_individual_parameters()

# Visualiser avec gaps
visualizer = GAVisualizer(analyzer)
visualizer.plot_individual_parameters()
visualizer.plot_parameter_comparison()
```

## 📊 Interprétation des Résultats

### Scénario 1 : Gap négatif
```
gap = -0.5%  → Coût trouvé < optimal
```
**Interprétation** : Impossible ou erreur (l'optimal est par définition le minimum)

### Scénario 2 : Gap < 1%
```
gap = +0.5%  → Coût = 23015
```
**Interprétation** : Excellent ! Configuration très performante ✅

### Scénario 3 : Gap entre 1% et 2%
```
gap = +1.5%  → Coût = 23244
```
**Interprétation** : Bon résultat, peut être amélioré 🟡

### Scénario 4 : Gap > 2%
```
gap = +3.0%  → Coût = 23588
```
**Interprétation** : Configuration sous-optimale, à éviter ❌

## 🎯 Avantages du Gap vs Optimal

### Avant (amélioration vs baseline)
- ✗ Relatif à une baseline arbitraire (23316)
- ✗ Difficile à interpréter absolument
- ✗ Dépend de la qualité de la baseline

### Après (gap vs optimal)
- ✅ **Référence absolue** (22901)
- ✅ **Interprétation claire** : distance au meilleur possible
- ✅ **Objectif précis** : gap < 1%
- ✅ **Comparable entre instances** (si optimal connu)
- ✅ **Standard en recherche opérationnelle**

## 📈 Exemple de Lecture

### Graphique "Gap vs Optimal"
```
pop_size=60   ▓▓░ +0.65%  ← Excellent
pop_size=80   ▓▓▓░ +0.87%  ← Très bon
pop_size=100  ▓▓▓▓▓ +1.81% ← À améliorer (baseline)
pop_size=120  ▓▓▓▓▓▓ +2.18% ← Sous-optimal
```

**Conclusion** : `pop_size=60` est optimal pour ce paramètre.

## 🔬 Recommandations Basées sur les Visualisations

Après avoir lancé l'analyse complète, cherchez :

1. **Paramètres individuels avec gap < 1%**
   - Ces valeurs sont excellentes individuellement
   
2. **Combinaisons avec gap < 0.5%**
   - Configuration quasi-optimale !
   
3. **Cohérence entre paramètres**
   - Si plusieurs paramètres montrent gap < 1%, leur combinaison devrait être encore meilleure

## 🚀 Prochaines Étapes

1. **Lancer l'analyse complète** :
   ```bash
   python run_parameter_analysis.py
   # Choisir option 7 (Analyse complète)
   ```

2. **Identifier les configurations avec gap < 1%**

3. **Tester ces configurations** sur d'autres instances

4. **Documenter les meilleures combinaisons**

## 📝 Notes Techniques

### Fallback si optimal non disponible
Si `target_optimum = None`, le système revient automatiquement à l'affichage de l'amélioration vs baseline.

### Performance
Les visualisations utilisent matplotlib avec :
- Backend TkAgg pour affichage interactif
- DPI 150 pour sauvegarde haute qualité
- Seaborn pour palettes de couleurs

### Sauvegarde automatique
Lors de la génération du rapport complet (option 4 ou 7), tous les graphiques sont sauvegardés en PNG dans `results/parameter_analysis/`.

---

**Créé le** : 11 novembre 2025  
**Version** : 2.0 - Visualisations avec gap vs optimal
