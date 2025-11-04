# CVRP - Algorithme génétique (compatible CVRPLIB X-n153-k22)

Ce projet implémente un algorithme génétique (GA) pour résoudre le problème de tournées de véhicules capacitaire (CVRP), avec:
- Représentation par permutation globale ("giant tour")
- Découpage en tournées faisables par programmation dynamique (split)
- Local search 2-opt par route
- Sélection par tournoi, crossover OX, mutation swap/inversion
- Vérification des contraintes (capacité, couverture, départ/retour dépôt)

Il est conçu pour lire les fichiers CVRPLIB (`.vrp`), et a été testé avec l'instance `X-n153-k22`.

## Prérequis

- Python 3.10 ou plus
- Pas de dépendances externes obligatoires (librairie standard uniquement)

Optionnel: créer un venv:
```
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate     # Windows
```

## Installation

Aucune installation requise. Place les fichiers dans un même dossier.

## Récupérer l’instance CVRPLIB

1) Télécharge `X-n153-k22.vrp` depuis CVRPLIB (section X):
   - Page générale: https://vrp.galgos.inf.puc-rio.br/index.php/en/
   - Section Instances -> "X": https://vrp.galgos.inf.puc-rio.br/index.php/en/ (navigue jusqu’à la série X)
   - Sauvegarde le fichier `X-n153-k22.vrp` localement, par exemple dans `./data/X-n153-k22.vrp`

2) (Optionnel) Si tu as aussi un fichier solution `.sol` officiel, tu peux le passer pour valider le parsing du coût.

## Lancer l'algorithme

Exemple:
```
python main.py --instance ./data/X-n153-k22.vrp --pop 120 --gens 400 --seed 42 --elitism 4 --pc 0.9 --pm 0.2
```

Paramètres principaux:
- `--instance`: chemin vers le fichier `.vrp`
- `--pop`: taille de population (par défaut 100)
- `--gens`: nombre de générations (par défaut 200)
- `--seed`: graine aléatoire pour reproductibilité (par défaut 123)
- `--elitism`: nombre d'élites conservés (par défaut 2)
- `--pc`: probabilité de crossover (par défaut 0.9)
- `--pm`: probabilité de mutation (par défaut 0.2)
- `--no-2opt`: désactive le 2-opt local si fourni

Sortie:
- Affiche le meilleur coût trouvé, le nombre de véhicules, et vérifie les contraintes
- Écrit un fichier solution `solution_X-n153-k22.sol` dans le dossier courant (format lisible, avec routes et coût)

## Vérification avec un fichier .sol (optionnel)

Tu peux calculer le coût d’un fichier `.sol` (format "Route #i: ...") pour valider le parsing:
```
python main.py --instance ./data/X-n153-k22.vrp --validate-sol ./data/X-n153-k22.sol
```

Cela n’exécute pas le GA mais lit et calcule le coût des routes du `.sol` fourni (selon la métrique CVRPLIB EUC_2D).

## Remarques

- Distances: EUC_2D avec arrondi TSPLIB (int(sqrt(dx^2 + dy^2) + 0.5))
- Le split par DP garantit que toutes les tournées respectent la capacité. On évite ainsi les pénalités d’infaisabilité dans la fitness.
- Le 2-opt local explore seulement à l’intérieur de chaque tournée (pas de mouvements inter-routes dans cette version).
- Les meilleurs coûts officiels peuvent varier; le but ici est de fournir une base correcte et vérifiable.

## Structure

- `main.py`            : CLI, exécution GA, affichage, sauvegarde solution
- `cvrp_data.py`       : Parsing CVRPLIB `.vrp`, construction de l’instance et matrice de distances
- `solution.py`        : Coût d’une solution, vérification des contraintes, I/O solution texte
- `split.py`           : Split DP (permutation -> routes faisables)
- `localsearch.py`     : 2-opt intra-route
- `ga.py`              : Algorithme génétique (init, sélection, crossover, mutation, évaluation)
