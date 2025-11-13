# 📚 Index de la Documentation

Guide complet de la documentation du projet CVRP-GA

---

## 🚀 Démarrage Rapide

### Pour commencer
1. **[README.md](README.md)** - Vue d'ensemble du projet
   - Présentation générale
   - Installation et utilisation
   - Architecture du code

### Pour benchmarker (NOUVEAU ⚡)
2. **[QUICKSTART.md](QUICKSTART.md)** - Guide express (5 minutes)
   - ⚡ Version ultra-rapide
   - 🎯 Essentiel uniquement
   - 📊 Lire les résultats
   - 🔧 Utiliser les paramètres optimaux

3. **[experiment_protocol.md](experiment_protocol.md)** - Protocole complet (20 minutes)
   - 📚 Documentation exhaustive
   - 📊 Pipeline détaillé (5 phases)
   - 🎯 144 configurations expliquées
   - 📈 9 visualisations détaillées
   - 🌟 Configuration optimale combinée
   - 🔍 Interprétation approfondie

---

## 📖 Documentation Technique

### Standards et Métriques
4. **[CVRP_GAP_STANDARDS.md](CVRP_GAP_STANDARDS.md)** - Standards de calcul du gap
   - Formules de calcul
   - Standards académiques
   - Interprétation des résultats

### Solutions de Référence
5. **[SOLUTION_REFERENCE.md](SOLUTION_REFERENCE.md)** - Solutions optimales connues
   - Format des fichiers .sol
   - Solutions CVRPLIB
   - Vérification des résultats

### Visualisations
6. **[VISUALIZATIONS_GAP.md](VISUALIZATIONS_GAP.md)** - Guide des visualisations
   - 9 types de graphiques
   - Interprétation visuelle
   - Analyse des tendances

---

## 🎯 Par Cas d'Usage

### Je veux...

#### Comprendre le projet
→ Lire **[README.md](README.md)**

#### Lancer un benchmark
→ Suivre **[experiment_protocol.md](experiment_protocol.md)**
```bash
python benchmarks/benchmark.py
```

#### Interpréter les résultats
→ Consulter **[CVRP_GAP_STANDARDS.md](CVRP_GAP_STANDARDS.md)**
- Gap < 1% = Excellent 🏆
- Gap < 5% = Bon ✅
- Gap < 10% = Acceptable 🟡

#### Analyser les graphiques
→ Référence **[VISUALIZATIONS_GAP.md](VISUALIZATIONS_GAP.md)**
- 9 visualisations expliquées
- Lecture des tendances
- Identification des optimums

#### Vérifier une solution
→ Format dans **[SOLUTION_REFERENCE.md](SOLUTION_REFERENCE.md)**

---

## 📊 Structure des Documents

```
docs/
├── INDEX.md                    ← Vous êtes ici
├── README.md                   ← Démarrage (5 min)
├── experiment_protocol.md      ← Guide complet (10 min)
├── CVRP_GAP_STANDARDS.md       ← Référence technique (3 min)
├── SOLUTION_REFERENCE.md       ← Format solutions (2 min)
└── VISUALIZATIONS_GAP.md       ← Guide visuel (5 min)
```

---

## 🔍 Recherche Rapide

### Mots-clés → Document

| Mot-clé | Document | Section |
|---------|----------|---------|
| **Benchmark** | experiment_protocol.md | Système de Benchmark |
| **Gap** | CVRP_GAP_STANDARDS.md | Calcul et Standards |
| **Paramètres** | experiment_protocol.md | Paramètres Testés |
| **Visualisations** | VISUALIZATIONS_GAP.md | 9 Types de Graphiques |
| **Optimum** | SOLUTION_REFERENCE.md | Solutions Connues |
| **Configuration** | experiment_protocol.md | Configuration Optimale |
| **Installation** | README.md | Démarrage |
| **Temps** | experiment_protocol.md | Exécution (~25 min) |
| **Résultats** | experiment_protocol.md | Interprétation |
| **Standards** | CVRP_GAP_STANDARDS.md | Références Scientifiques |

---

## 🎓 Parcours Apprentissage

### Niveau Débutant (15 min)
1. README.md (5 min)
2. experiment_protocol.md - Sections 1-3 (10 min)

### Niveau Intermédiaire (30 min)
1. README.md (5 min)
2. experiment_protocol.md complet (15 min)
3. CVRP_GAP_STANDARDS.md (5 min)
4. VISUALIZATIONS_GAP.md (5 min)

### Niveau Avancé (45 min)
1. Tous les documents
2. Expérimentation pratique
3. Analyse des résultats

---

## 📝 Checklist Utilisation

### Avant le benchmark
- [ ] Lu README.md
- [ ] Compris experiment_protocol.md (sections 1-6)
- [ ] Instance data.vrp présente et correcte
- [ ] Optimum connu (27591 pour X-n101-k25)

### Pendant le benchmark
- [ ] Lancement : `python benchmarks/benchmark.py`
- [ ] Temps estimé : ~25 minutes
- [ ] Suivi terminal des progrès

### Après le benchmark
- [ ] Consulter résumé terminal
- [ ] Ouvrir gaps_comparison.png
- [ ] Lire CVRP_GAP_STANDARDS.md pour interpréter
- [ ] Analyser avec VISUALIZATIONS_GAP.md
- [ ] Noter configuration optimale

---

## 🔗 Liens Externes

### Références Académiques
- **CVRPLIB** : http://vrp.atd-lab.inf.puc-rio.br/
- **Uchoa et al. (2017)** : Benchmarks CVRP
- **Vidal et al. (2012)** : Hybrid GA

### Outils
- **Python** : https://www.python.org/
- **Matplotlib** : https://matplotlib.org/
- **NumPy** : https://numpy.org/

---

## 💡 Conseils

### Pour gagner du temps
1. **Test rapide d'abord** : `python benchmarks/test_visualizations.py` (~10s)
2. **Benchmark complet ensuite** : `python benchmarks/benchmark.py` (~25min)
3. **Analyser les gaps** : Commencer par `gaps_comparison.png`

### Pour approfondir
1. Lire les 3 MD de référence (CVRP_GAP_STANDARDS, SOLUTION_REFERENCE, VISUALIZATIONS_GAP)
2. Comparer plusieurs runs
3. Ajuster les paramètres selon les résultats

### Pour publier
1. Documenter la configuration optimale trouvée
2. Capturer les 9 visualisations
3. Citer les standards CVRP (voir CVRP_GAP_STANDARDS.md)

---

## 📅 Dernière Mise à Jour

**Date** : 13 novembre 2025  
**Version** : 4.0  
**Changements** :
- ✨ Nouveau système de configuration optimale combinée
- 📊 9 visualisations (+ init_modes et gaps_comparison)
- 🎯 144 configurations testées
- 📝 Documentation complète et nettoyée

---

**Navigation** : [↑ Retour en haut](#-index-de-la-documentation)
