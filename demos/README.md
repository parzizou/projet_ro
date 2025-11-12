# Scripts de Démonstration

Ce dossier contient des scripts de démonstration et de test pour illustrer les fonctionnalités du système d'analyse de paramètres.

## 📄 Fichiers disponibles

### 1. `demo_gap_calculation.py`
**Description** : Démonstration du calcul de gap par rapport à la solution optimale.

**Contenu** :
- Calcul du gap : `((coût - optimal) / optimal) × 100`
- Exemples avec différents coûts
- Interprétation selon les standards CVRP

**Utilisation** :
```powershell
python demos\demo_gap_calculation.py
```

---

### 2. `demo_gap_vs_improvement.py`
**Description** : Comparaison entre le gap (vs optimal) et l'amélioration (vs baseline).

**Contenu** :
- Différence entre les deux métriques
- Pourquoi le gap est préféré pour CVRP
- Exemples avec tableau comparatif
- Standards CVRP (<5% = bon, <10% = acceptable)

**Utilisation** :
```powershell
python demos\demo_gap_vs_improvement.py
```

---

### 3. `demo_multithreading.py`
**Description** : Démonstration du système de multi-threading utilisé dans l'analyse de paramètres.

**Contenu** :
- Utilisation de `ProcessPoolExecutor`
- Parallélisation des exécutions GA
- Comparaison temps séquentiel vs parallèle
- Gestion des workers et performances

**Utilisation** :
```powershell
python demos\demo_multithreading.py
```

---

### 4. `test_visualizations_with_gap.py`
**Description** : Test du système de visualisation avec données de démonstration.

**Contenu** :
- Génération de données fictives
- Création de graphiques avec gaps
- Test des 3 types de visualisations :
  - Paramètres individuels
  - Comparaison globale
  - Meilleures combinaisons
- Code couleur basé sur les seuils CVRP

**Utilisation** :
```powershell
python demos\test_visualizations_with_gap.py
```

**Sortie** : Crée des graphiques PNG dans le répertoire courant pour validation visuelle.

---

### 5. `demo_test_multi_depot.py` 🆕
**Description** : Démonstration interactive de l'optimisation de paramètres multi-dépôts.

**Contenu** :
- 4 scénarios de test prédéfinis :
  1. Optimisation du nombre de dépôts (k_depots)
  2. Optimisation des types de dépôts (types_alphabet)
  3. Optimisation de la taille de population GA
  4. Optimisation du taux de mutation avec export CSV
- Menu interactif pour choisir les tests
- Explications détaillées de chaque test

**Utilisation** :
```powershell
python demos\demo_test_multi_depot.py
```

**Interface** : Menu interactif avec options :
- Choix du test spécifique (1-4)
- Lancer tous les tests ('all')
- Quitter ('q')

**Exemples de tests** :
```powershell
# Optimiser le nombre de dépôts
python scripts\test_multi_depot.py --instance data/instances/data.vrp --param k_depots --values 2,3,4 --repeats 2

# Optimiser les types de dépôts
python scripts\test_multi_depot.py --instance data/instances/data.vrp --param types_alphabet --values AB,ABC,ABCD --repeats 2

# Optimiser les paramètres GA
python scripts\test_multi_depot.py --instance data/instances/data.vrp --param ga_pop_size --values 20,40,60 --repeats 2 --fixed "k_depots=3"
```

---

## 🎯 Objectif des Démos

Ces scripts servent à :
1. **Éducation** : Comprendre les concepts clés (gap, multi-threading, visualisations)
2. **Validation** : Tester le système sans lancer d'analyses complètes
3. **Documentation** : Exemples de code réutilisables
4. **Débogage** : Vérifier le bon fonctionnement des modules

## 📊 Standards CVRP Utilisés

Tous les scripts de démonstration utilisent les standards scientifiques CVRP :
- **Gap < 5%** : ✅ Bon résultat (couleur verte)
- **Gap 5-10%** : 🟡 Acceptable (couleur orange)
- **Gap > 10%** : ❌ À améliorer (couleur rouge)

Voir `docs/CVRP_GAP_STANDARDS.md` pour plus de détails sur les références scientifiques.

---

## 🔗 Liens Utiles

- **Documentation complète** : `docs/`
- **Protocole d'expérimentation** : `docs/experiment_protocol.md`
- **Code source principal** : `src/`
- **Script d'analyse** : `run_parameter_analysis.py`
