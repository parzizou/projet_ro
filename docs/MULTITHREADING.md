# 🚀 Multi-Threading dans le Système d'Analyse

## 📍 Localisation du Multi-Threading

Le multi-threading est implémenté dans **`src/optimization/ga_parameter_analyzer.py`**

## 🔧 Architecture du Multi-Threading

### 1. Fonction Worker (`_run_ga_single`)

```python
def _run_ga_single(instance_path: str, params: Dict[str, Any], 
                   time_limit: float, generations: int) -> int:
    """
    Fonction worker pour le multi-threading.
    Exécute l'AG UNE FOIS avec les paramètres donnés.
    """
```

**Ligne 56-79** : Cette fonction est exécutée **en parallèle** par plusieurs processus.

### 2. Méthode de Parallélisation (`_run_multiple_tests`)

```python
def _run_multiple_tests(self, params: Dict[str, Any], num_runs: int,
                       time_limit: float, generations: int,
                       max_workers: Optional[int] = None):
    """
    Exécute plusieurs tests EN PARALLÈLE.
    Utilise ProcessPoolExecutor pour le multi-threading.
    """
    start_time = time.time()
    
    # 🔥 MULTI-THREADING ICI
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(_run_ga_single, self.instance_path, params, 
                          time_limit, generations)
            for _ in range(num_runs)
        ]
        
        # Récupère les résultats au fur et à mesure
        costs = [future.result() for future in as_completed(futures)]
    
    elapsed = time.time() - start_time
    return costs, elapsed
```

**Lignes 130-155** : Crée un pool de processus qui exécute les tests en parallèle.

## 🎯 Comment ça fonctionne ?

### Exemple Concret

Si vous testez une configuration avec `n_runs=5` sur votre machine 12 cores :

```
Configuration: pop_size=100, pc=0.9, pm=0.02...

Sans multi-threading (séquentiel):
├── Run 1: [████████] 30s
├── Run 2: [████████] 30s  
├── Run 3: [████████] 30s
├── Run 4: [████████] 30s
└── Run 5: [████████] 30s
Total: 150 secondes

Avec multi-threading (5 processus en parallèle):
├── Run 1: [████████] 
├── Run 2: [████████] TOUS EN MÊME TEMPS
├── Run 3: [████████] 
├── Run 4: [████████]
└── Run 5: [████████]
Total: ~30 secondes (5x plus rapide!)
```

## ⚙️ Configuration du Multi-Threading

### Paramètre `max_workers`

Dans les méthodes `test_individual_parameters()` et `find_best_combinations()` :

```python
def test_individual_parameters(self, ..., max_workers: Optional[int] = None):
    """
    Args:
        max_workers: Nombre de processus parallèles
                    None = auto (Python détecte le nombre de cores)
                    int = nombre spécifique de workers
    """
```

### Utilisation Automatique

Par défaut, `max_workers=None` signifie que Python utilise :
```python
max_workers = min(32, (os.cpu_count() or 1) + 4)
```

Sur votre machine 12 cores :
- **16 workers** seront utilisés par défaut
- Vous pouvez tester **16 configurations en parallèle** !

### Utilisation Personnalisée

Vous pouvez spécifier manuellement :

```python
# Utiliser exactement 12 workers (1 par core)
analyzer.test_individual_parameters(max_workers=12)

# Utiliser 6 workers (pour laisser des ressources)
analyzer.test_individual_parameters(max_workers=6)

# Utiliser tous les cores disponibles (auto)
analyzer.test_individual_parameters(max_workers=None)
```

## 📊 Où le Multi-Threading est Utilisé

### 1. Tests Individuels (`test_individual_parameters`)

```python
# Ligne 195: Établir la baseline (5 runs en parallèle)
costs, _ = self._run_multiple_tests(self.default_params, num_runs, 
                                   time_limit, generations, max_workers)

# Ligne 226: Tester chaque valeur (num_runs exécutions en parallèle)
costs, elapsed = self._run_multiple_tests(test_params, num_runs,
                                         time_limit, generations, max_workers)
```

**Résultat** : Si vous testez 77 configurations avec 5 runs chaque :
- Sans multi-threading : 77 × 5 × 30s = **32 heures** 😱
- Avec 12 workers : 77 × 5 × 30s ÷ 12 = **~2.7 heures** 🚀

### 2. Tests de Combinaisons (`find_best_combinations`)

```python
# Ligne 314: Tester chaque combinaison
costs, _ = self._run_multiple_tests(combo, combination_runs,
                                   time_limit, generations, max_workers)
```

**Résultat** : 20 combinaisons avec 8 runs chaque :
- Sans multi-threading : 20 × 8 × 45s = **2 heures**
- Avec 12 workers : 20 × 8 × 45s ÷ 12 = **~10 minutes** 🚀

## 🔬 Type de Parallélisme

### ProcessPoolExecutor vs ThreadPoolExecutor

Le code utilise **`ProcessPoolExecutor`** (et non `ThreadPoolExecutor`) :

```python
from concurrent.futures import ProcessPoolExecutor, as_completed
```

**Pourquoi ProcessPoolExecutor ?**
- ✅ Contourne le **GIL** (Global Interpreter Lock) de Python
- ✅ Vraie parallélisation sur **plusieurs cores CPU**
- ✅ Chaque processus a sa propre mémoire
- ✅ Idéal pour calculs intensifs (GA)

**ThreadPoolExecutor** serait moins efficace car :
- ❌ Limité par le GIL (1 thread actif à la fois en Python)
- ❌ Bon pour I/O, pas pour calculs CPU

## 💡 Optimisation Maximale

Pour tirer le meilleur parti de vos 12 cores :

```python
# Dans run_parameter_analysis.py, vous pourriez modifier :

analyzer = GAParameterAnalyzer('data/instances/data.vrp', n_runs=12)

# Tests avec 12 runs en parallèle (1 par core)
analyzer.test_individual_parameters(
    num_runs=12,           # 12 répétitions
    max_workers=12,        # 12 processus en parallèle
    time_limit=30.0,
    generations=20000
)
```

**Résultat** : Utilisation maximale de tous vos cores ! 🔥

## 📈 Monitoring

Pour voir le multi-threading en action :

### Pendant l'exécution :
1. Ouvrez le **Gestionnaire des tâches** (Windows)
2. Regardez l'onglet **Performance** → **CPU**
3. Vous verrez **tous les cores à ~100%** pendant les tests !

### Dans le code :
```python
# Le nombre de workers s'affiche dans les logs
print(f"Utilisation de {max_workers} processus parallèles")
```

## 🎯 Résumé

| Aspect | Détail |
|--------|--------|
| **Fichier** | `src/optimization/ga_parameter_analyzer.py` |
| **Fonction Worker** | `_run_ga_single()` (ligne 56) |
| **Méthode Parallèle** | `_run_multiple_tests()` (ligne 130) |
| **Technologie** | `ProcessPoolExecutor` |
| **Workers par défaut** | 16 (auto) sur votre machine 12 cores |
| **Gain de temps** | **~12x plus rapide** sur vos 12 cores |

---

✨ **Le multi-threading est déjà actif et optimisé pour vos 12 cores !** ✨
