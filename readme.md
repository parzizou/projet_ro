# CVRP — Résolution par algorithme génétique, simple et clair

Ce projet résout un problème de tournées de véhicules avec capacité (chaque camion a une place limitée). L’objectif est de livrer tous les clients en partant du dépôt, sans dépasser la capacité des camions, en minimisant le temps de trajet total (on l’assimile à la distance totale).

Points importants:
- Tous les véhicules ont la même capacité.
- On respecte la capacité grâce au “découpage intelligent” des tournées.
- Limite stricte de temps de calcul: par défaut ~170 secondes (< 3 minutes).
- Fenêtres de temps (ex: livrer entre 8h et 18h): non gérées explicitement dans cette version.
  - On suppose que minimiser la distance revient à minimiser le temps de tournée.

## Ce que contient le dépôt

- `cvrp_data.py` — Lecture des fichiers CVRPLIB `.vrp`, construction de l’instance:
  - coordonnées des points (clients + dépôt)
  - demandes des clients
  - capacité des véhicules
  - matrice de distances (euclidienne arrondie à la manière TSPLIB)
  - Nouveau: `load_cvrp_from_vrplib(name)` pour charger directement une instance par son nom depuis le package Python `vrplib`, et récupérer le best-known cost si disponible.
- `split.py` — Découpe une “grande tournée” en plusieurs tournées faisables (respect de la capacité) via une programmation dynamique.
- `localsearch.py` — Amélioration locale “par inversion de segments” à l’intérieur d’une tournée (souvent appelée 2-opt).
- `solution.py` — Calcul du coût d’une solution, vérification des contraintes, lecture/écriture de solutions texte.
- `ga.py` — Le cœur de l’algorithme génétique: population, sélection, croisement, mutation, évaluation, élitisme, limite de temps.
- `plot.py` — Affichage des tournées trouvées (optionnel, nécessite `matplotlib`).
- `main.py` — Petit lanceur: charge une instance (par chemin local ou par nom CVRPLIB), exécute l’algo, vérifie et écrit la solution, et affiche le tracé.

## Nouveautés

- Arrêt propre à la demande:
  - Appuie sur Ctrl+C pendant l’exécution: l’algo s’arrête proprement et garde le meilleur individu courant.
  - Option `STOP_SENTINEL_FILE` dans `main.py`: si ce fichier existe, l’algo stoppe proprement à la fin de la génération.
- Gap vs optimal:
  - Variable `TARGET_OPTIMUM` dans `main.py`. Lors d’un chargement par nom CVRPLIB (`--name`), si une solution de référence est disponible via `vrplib`, la valeur est automatiquement mise à jour avec le best-known cost.
- Chargement direct par nom CVRPLIB:
  - Utilise le package `vrplib` pour télécharger/charger les instances et, si possible, la solution de référence.
  - Permet d’appeler: `python main.py --name A-n32-k5`

## Lancer le programme

Prérequis:
- Python 3.10 ou plus
- Optionnel pour l’affichage: `pip install matplotlib`
- Optionnel pour le chargement par nom CVRPLIB: `pip install vrplib`

Exécutions possibles:
- Avec un fichier `.vrp` local:
```
python main.py --instance /chemin/vers/mon_instance.vrp
```
- Directement par le nom d’une instance CVRPLIB (ex: A-n32-k5):
```
pip install vrplib
python main.py --name A-n32-k5
```
Dans ce second cas:
- L’instance est récupérée via `vrplib`.
- Si `vrplib` expose une solution de référence, le best-known cost est automatiquement utilisé pour calculer le gap.

Sorties:
- Affiche le coût total, le nombre de véhicules (nombre de tournées), et la validité des contraintes.
- Si une valeur optimale est connue (`TARGET_OPTIMUM` non nulle): affiche aussi `Gap vs optimal: X.YZ%`.
- Écrit un fichier solution texte: `solution_<nom_instance>.sol`
- Si `matplotlib` est dispo, sauvegarde une image: `solution_<nom_instance>.png`

## Paramètres utiles (où les changer)

Dans `ga.py`, la fonction `genetic_algorithm(...)` contient les réglages principaux:
- Taille de population, nombre de générations max
- Sélection par tournoi (taille du tournoi)
- Probabilités de croisement et de mutation
- Activation et probabilité de l’amélioration locale
- Limite de temps (par défaut 170 secondes)
- Option `target_optimum` (affichage gap), et `stop_on_file` (arrêt propre via fichier sentinelle)

Besoin d’aide pour intégrer des fenêtres de temps ou booster les perfs ? Dis-moi, on itère.