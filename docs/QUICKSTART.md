# ⚡ Guide Rapide — Benchmark CVRP

**Pour les pressés** : Tout ce qu'il faut savoir en 5 minutes

---

## 🎯 En Bref

**Objectif** : Trouver les meilleurs paramètres pour l'algorithme génétique

**Méthode** : Tester 144 configurations + créer config optimale combinée

**Durée** : ~25 minutes

**Résultat** : 9 graphiques + paramètres optimaux

---

## 🚀 Commandes Essentielles

```bash
# Test rapide (10s)
python benchmarks/test_visualizations.py

# Benchmark complet (25 min)
python benchmarks/benchmark.py
```

---

## 📊 Lire les Résultats

### 1. Terminal (30 secondes)

Chercher ces lignes :

```
🌟 CONFIGURATION OPTIMALE COMBINÉE:
   ⭐ Coût: 27620.0 | Gap: +0.10%
```

**Si Gap < 1%** ✅ = Excellent !

### 2. Un seul graphique (1 minute)

Ouvrir : `results/benchmarks/*/gaps_comparison.png`

Regarder la dernière barre (Combined Optimal) :
- **Barre courte** = Bon (proche de l'optimal)
- **Barre longue** = À améliorer

### 3. Paramètres optimaux (30 secondes)

Dans le terminal, noter ces 5 valeurs :

```python
OPTIMAL_PARAMS = {
    'population_size': 120,    # ← Noter cette valeur
    'n_elite': 8,              # ← Noter cette valeur
    'mutation_rate': 0.08,     # ← Noter cette valeur
    'tournament_size': 5,      # ← Noter cette valeur
    'n_close': 15              # ← Noter cette valeur
}
```

---

## 📈 Standards de Qualité

| Gap | Signification |
|-----|---------------|
| < 0.5% | 🏆 Excellence (état de l'art) |
| < 1% | ✅ Excellent (publiable) |
| < 5% | ✅ Bon (standard académique) |
| < 10% | 🟡 Acceptable |
| > 10% | ❌ Insuffisant |

---

## 🎯 Workflow Ultra-Rapide

```bash
# 1. Lancer (puis café ☕)
python benchmarks/benchmark.py

# 2. Attendre 25 minutes

# 3. Lire le terminal
#    → Noter le Gap de la config combinée

# 4. Ouvrir gaps_comparison.png
#    → Vérifier amélioration progressive

# 5. Copier les paramètres optimaux
#    → Les utiliser dans votre code
```

---

## 🔧 Utiliser les Résultats

**Modifier votre code** :

```python
# Avant (défaut)
params = {
    'population_size': 100,
    'n_elite': 10,
    'mutation_rate': 0.1,
    'tournament_size': 5,
    'n_close': 20
}

# Après (optimal)
params = {
    'population_size': 120,     # ← Optimisé
    'n_elite': 8,               # ← Optimisé
    'mutation_rate': 0.08,      # ← Optimisé
    'tournament_size': 5,       # ← OK
    'n_close': 15               # ← Optimisé
}
```

---

## 🆘 Problèmes Fréquents

### Le benchmark plante
→ Vérifier que `data/instances/data.vrp` existe

### Gap négatif
→ Vérifier `OPTIMUM = 27591` dans benchmark.py

### Trop lent
→ Normal ! 25 min c'est attendu

### Warnings émojis
→ Ignorables (cosmétiques uniquement)

---

## 📚 Pour en Savoir Plus

**Documentation complète** : `docs/experiment_protocol.md`

**Navigation** : `docs/INDEX.md`

---

**C'est tout !** Vous savez l'essentiel. 🎉

Pour approfondir, lisez le protocole complet (20 min de lecture).
