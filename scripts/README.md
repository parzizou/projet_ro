# Scripts d'Exécution Alternatifs

Ce dossier contient des scripts d'exécution alternatifs pour différents types d'analyses et de résolution du CVRP.

## 📄 Scripts disponibles

### 1. `run_pulp_demo.py`
**Description** : Modélisation exacte du CVRP avec PuLP (programmation linéaire en nombres entiers).

**Objectif** : Démontrer pourquoi une approche heuristique (GA) est nécessaire pour des instances de taille réelle.

**Fonctionnalités** :
- Modélisation MIP complète du CVRP
- Support des contraintes :
  - Capacité des véhicules
  - Multi-dépôts
  - Compatibilité/Split
- Utilisation de solveurs exacts (CBC, GLPK, etc.)

**Utilisation** :
```powershell
python scripts\run_pulp_demo.py
```

**Tests inclus** :
1. **Test de Succès** (p03_test.vrp - N=10) : Validation du modèle
2. **Test d'Échec** (p01.vrp - N=50) : Démonstration de la complexité NP-hard

**Résultats attendus** :
- Petites instances (N<20) : Solution optimale en quelques secondes
- Grandes instances (N>50) : Timeout sans solution (justifie l'AG)

**Prérequis** :
```powershell
pip install pulp
```

---

### 2. `multi_depot.py`
**Description** : Extension du système pour gérer des problèmes CVRP avec plusieurs dépôts.

**Fonctionnalités** :
- Gestion de multiples points de départ
- Affectation des clients aux dépôts
- Optimisation des tournées multi-dépôts

**Utilisation** :
```powershell
python scripts\multi_depot.py
```

**Cas d'usage** :
- Problèmes de logistique avec plusieurs entrepôts
- Optimisation de réseaux de distribution
- Validation sur instances multi-dépôts (p01.vrp, p03_test.vrp)

---

### 3. `test.py`
**Description** : Script de test général pour validation rapide.

**Fonctionnalités** :
- Tests unitaires des modules principaux
- Validation du chargement des données
- Vérification de l'algorithme génétique
- Tests de performance

**Utilisation** :
```powershell
python scripts\test.py
```

---

## 🆚 Différences avec les Scripts Principaux

| Script | Localisation | Usage | Complexité |
|--------|--------------|-------|------------|
| **main.py** | Racine | Exécution standard GA | Simple |
| **run_parameter_analysis.py** | Racine | Analyse complète paramètres | Avancé |
| **run_pulp_demo.py** | scripts/ | Résolution exacte (MIP) | Théorique |
| **multi_depot.py** | scripts/ | Variante multi-dépôts | Spécialisé |
| **test.py** | scripts/ | Tests & validation | Debug |

## 🎯 Quand Utiliser Ces Scripts ?

### `run_pulp_demo.py`
- ✅ Analyse théorique de la complexité
- ✅ Validation sur petites instances
- ✅ Comparaison exacte vs heuristique
- ❌ **PAS** pour instances réelles (trop lent)

### `multi_depot.py`
- ✅ Problèmes avec plusieurs dépôts
- ✅ Validation sur p01.vrp, p03_test.vrp
- ⚠️ En développement

### `test.py`
- ✅ Validation après modifications
- ✅ Tests de régression
- ✅ Debug rapide

## 📊 Instances de Test Recommandées

### Pour PuLP (résolution exacte)
- **p03_test.vrp** : N=10, 3 dépôts → Solvable en ~1-5 secondes
- **p01.vrp** : N=50, 4 dépôts → Timeout (démonstration NP-hard)

### Pour Multi-Dépôts
- **p01.vrp** : Instance complexe multi-dépôts
- **p03_test.vrp** : Validation fonctionnelle

### Pour Tests Standards
- **data.vrp** : Instance principale (X-n153-k22)
- **data2-6.vrp** : Instances additionnelles

## 🔬 Contexte Scientifique

### Pourquoi PuLP (Exact) ET GA (Heuristique) ?

**Modélisation Exacte (PuLP)** :
- ✅ Garantie d'optimalité mathématique
- ✅ Validation théorique du modèle
- ❌ Complexité O(2^n) → impossible pour N>50

**Algorithme Génétique (GA)** :
- ✅ Résultats en temps polynomial
- ✅ Scalable pour N>100
- ✅ Gap < 5% selon littérature (Vidal 2012)
- ⚠️ Pas de garantie d'optimalité

**Conclusion** : PuLP valide le modèle, GA résout le problème réel.

---

## 📚 Documentation Associée

- **Modélisation MIP** : Voir `readme.md` (section "Modélisation Exacte")
- **Standards CVRP** : `docs/CVRP_GAP_STANDARDS.md`
- **Protocole expérimental** : `docs/experiment_protocol.md`
- **Multi-threading** : `docs/MULTITHREADING.md`

---

## 🚀 Workflow Recommandé

### 1. Validation Théorique (Nouveau Projet)
```powershell
# Valider le modèle sur petite instance
python scripts\run_pulp_demo.py  # Test p03_test.vrp
```

### 2. Résolution Pratique
```powershell
# Utiliser l'AG pour instances réelles
python main.py
```

### 3. Optimisation des Paramètres
```powershell
# Analyser et optimiser
python run_parameter_analysis.py
```

### 4. Tests & Validation
```powershell
# Vérifier tout fonctionne
python scripts\test.py
```
