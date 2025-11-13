# 📐 Guide de Contribution à la Documentation

Ce guide explique comment maintenir la documentation du projet propre et cohérente.

---

## 🎯 Principes Directeurs

### 1. **Minimalisme**
- Garder uniquement ce qui est nécessaire
- Supprimer dès qu'une fonctionnalité disparaît
- Pas de "au cas où" → Si supprimé, vraiment supprimer

### 2. **Cohérence Code ↔ Docs**
- La documentation doit refléter le code actuel
- Mettre à jour la doc **immédiatement** après un changement de code
- Vérifier les références aux fichiers/scripts

### 3. **Navigation Facilitée**
- INDEX.md est le point d'entrée
- Chaque doc a un rôle clair et unique
- Pas de duplication d'information

---

## 📂 Structure Actuelle

```
docs/
├── INDEX.md                    ← Point d'entrée (TOUJOURS à jour)
├── README.md                   ← Vue d'ensemble projet
├── experiment_protocol.md      ← Guide complet benchmark
├── CVRP_GAP_STANDARDS.md       ← Standards techniques
├── SOLUTION_REFERENCE.md       ← Format solutions
├── VISUALIZATIONS_GAP.md       ← Guide visualisations
└── CLEANUP_REPORT.md           ← Historique nettoyage
```

**Règle** : Maximum **8 fichiers** dans docs/

---

## ✅ Checklist Avant d'Ajouter un Document

- [ ] Ce document est-il vraiment nécessaire ?
- [ ] L'information n'existe-t-elle pas déjà ailleurs ?
- [ ] Le document restera-t-il pertinent longtemps ?
- [ ] Référence-t-il du code qui existe vraiment ?
- [ ] Puis-je plutôt ajouter une section à un doc existant ?

**Si 3+ réponses "non"** → Ne pas créer le document

---

## 📝 Quand Modifier la Documentation

### Ajout de Fonctionnalité
1. Coder la fonctionnalité
2. Tester qu'elle fonctionne
3. Documenter dans experiment_protocol.md (si benchmark)
4. Mettre à jour INDEX.md (si nouveau doc)

### Suppression de Fonctionnalité
1. Supprimer le code
2. **Immédiatement** supprimer/mettre à jour la doc
3. Mettre à jour INDEX.md
4. Ajouter au .gitignore si nécessaire

### Modification de Paramètres
1. Modifier le code
2. Mettre à jour experiment_protocol.md (section "Paramètres Testés")
3. Vérifier les exemples dans tous les docs

---

## 🗑️ Quand Supprimer un Document

### Indicateurs de Suppression
- ❌ Référence un script qui n'existe plus
- ❌ Décrit une fonctionnalité supprimée
- ❌ Information obsolète (instance changée, méthode modifiée)
- ❌ Contenu redondant avec un autre doc
- ❌ Guide pour un outil temporaire

### Procédure de Suppression
1. Supprimer le fichier
2. Retirer toutes les références dans les autres docs
3. Mettre à jour INDEX.md
4. Ajouter à .gitignore (pour éviter retour)
5. Documenter dans CLEANUP_REPORT.md

---

## 📖 Rôle de Chaque Document

### INDEX.md
**Rôle** : Navigation et découverte  
**Contenu** : Liens, mots-clés, parcours apprentissage  
**Mise à jour** : À chaque ajout/suppression de doc

### README.md
**Rôle** : Vue d'ensemble projet  
**Contenu** : Installation, architecture, utilisation basique  
**Mise à jour** : Changements d'architecture uniquement

### experiment_protocol.md
**Rôle** : Guide complet du système de benchmark  
**Contenu** : Pipeline, paramètres, visualisations, interprétation  
**Mise à jour** : Changements de benchmark (paramètres, configs, visualisations)

### CVRP_GAP_STANDARDS.md
**Rôle** : Référence technique gap  
**Contenu** : Formules, standards académiques  
**Mise à jour** : Rarement (standards académiques stables)

### SOLUTION_REFERENCE.md
**Rôle** : Format des solutions  
**Contenu** : Structure .sol, validation  
**Mise à jour** : Changement de format uniquement

### VISUALIZATIONS_GAP.md
**Rôle** : Guide des visualisations  
**Contenu** : 9 types de graphiques, interprétation  
**Mise à jour** : Ajout/modification de visualisations

### CLEANUP_REPORT.md
**Rôle** : Historique des nettoyages  
**Contenu** : Rapports de suppressions/réorganisations  
**Mise à jour** : À chaque nettoyage majeur

---

## ⚠️ Erreurs Courantes à Éviter

### ❌ Créer un guide pour un script temporaire
**Mauvais** :
```
docs/guide_test_quick.md  ← Pour scripts/test_quick.py (temporaire)
```

**Bon** :
- Mettre le guide en commentaires dans le script
- Ou section dans experiment_protocol.md si pertinent

### ❌ Dupliquer l'information
**Mauvais** :
```
docs/parametres.md           ← Liste des paramètres
docs/experiment_protocol.md  ← Aussi liste des paramètres
```

**Bon** :
- Une seule source de vérité (experiment_protocol.md)
- Les autres docs référencent cette source

### ❌ Garder des références cassées
**Mauvais** :
```markdown
Exécuter: `python scripts/fast_exploration.py`
```
(Alors que scripts/ a été supprimé)

**Bon** :
- Supprimer ou mettre à jour immédiatement

### ❌ Fichiers de code dans docs/
**Mauvais** :
```
docs/exemple_multithreading.py  ← Code Python
```

**Bon** :
- Code dans src/ ou benchmarks/
- Doc dans docs/ (peut inclure extraits code)

---

## 🔍 Vérifications Régulières

### Checklist Mensuelle
- [ ] Tous les fichiers référencés existent-ils ?
- [ ] Les paramètres correspondent-ils au code ?
- [ ] Les exemples fonctionnent-ils ?
- [ ] INDEX.md est-il à jour ?
- [ ] Moins de 8 fichiers dans docs/ ?

### Avant un Commit Important
- [ ] Doc cohérente avec les changements ?
- [ ] Références mises à jour ?
- [ ] INDEX.md modifié si nécessaire ?
- [ ] .gitignore à jour ?

---

## 📐 Standards de Rédaction

### Format Markdown
- Utiliser des headers clairs (##, ###)
- Tableaux pour comparaisons
- Blocs de code avec langage (```python, ```bash)
- Emojis pour navigation visuelle (🎯, ✅, ❌)

### Ton
- Clair et concis
- Impératif pour les instructions
- Exemples concrets
- Pas de jargon inutile

### Structure
```markdown
# Titre Principal

**Métadonnées** (version, date, instance)

---

## Section 1
Contenu...

## Section 2
Contenu...

---

**Dernière mise à jour** : Date
```

---

## 🔄 Workflow Recommandé

### Ajout de Fonctionnalité
```bash
# 1. Développement
git checkout -b feature/nouvelle-fonctionnalite
# Coder...

# 2. Tests
python benchmarks/benchmark.py
# Vérifier que ça marche

# 3. Documentation
# Modifier experiment_protocol.md
# Mettre à jour INDEX.md si nécessaire

# 4. Commit
git add .
git commit -m "feat: Nouvelle fonctionnalité + doc"
```

### Nettoyage de Documentation
```bash
# 1. Identifier les docs obsolètes
# Lister les fichiers qui référencent du code supprimé

# 2. Supprimer
Remove-Item docs/fichier_obsolete.md

# 3. Mettre à jour
# - INDEX.md (retirer référence)
# - .gitignore (ajouter à la liste obsolète)
# - CLEANUP_REPORT.md (documenter)

# 4. Commit
git commit -m "docs: Nettoyage fichiers obsolètes"
```

---

## 🆘 En Cas de Doute

### Question : "Dois-je créer un nouveau document ?"
**Réponse** : Probablement non. Essayer d'abord d'ajouter à un doc existant.

### Question : "Puis-je garder ce doc 'au cas où' ?"
**Réponse** : Non. Si supprimé, vraiment supprimer. Git conserve l'historique.

### Question : "Comment documenter un script temporaire ?"
**Réponse** : Commentaires dans le script. Pas de doc séparée.

### Question : "Combien de docs maximum ?"
**Réponse** : Objectif < 8 fichiers dans docs/

---

## 📚 Exemples

### ✅ Bon Exemple : Mise à Jour Cohérente
```
Changement : Instance X-n153-k22 → X-n101-k25

Fichiers modifiés :
1. src/core/cvrp_data.py (charge nouvelle instance)
2. data/instances/data.vrp (nouveau fichier)
3. docs/experiment_protocol.md (mise à jour métadonnées)
4. docs/README.md (mise à jour exemple)

Résultat : Code et docs synchronisés ✅
```

### ❌ Mauvais Exemple : Documentation Désynchronisée
```
Changement : Suppression de scripts/fast_exploration.py

Fichiers modifiés :
1. Suppression du script

Oubli : Mise à jour de docs/fast_exploration_guide.md

Résultat : Doc référence un script qui n'existe plus ❌
```

---

## 🎯 Objectif Final

**Documentation** :
- ✅ Minimale (< 8 fichiers)
- ✅ Cohérente (reflète le code actuel)
- ✅ Accessible (INDEX.md comme point d'entrée)
- ✅ Maintenable (facile à mettre à jour)
- ✅ Utile (guide vraiment les utilisateurs)

---

**Rappel** : La meilleure documentation est celle qui reste synchronisée avec le code. En cas de doute, privilégier la **suppression** plutôt que la **conservation**.

---

**Dernière mise à jour** : 13 novembre 2025  
**Version** : 1.0
