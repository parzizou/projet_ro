# CVRP — Résolution par algorithme génétique, simple et clair

Ce projet résout un problème de tournées de véhicules avec capacité (chaque camion a une place limitée). L’objectif est de livrer tous les clients en partant du dépôt, sans dépasser la capacité des camions, en minimisant le temps de trajet total (on l’assimile à la distance totale).

Points importants:
- Tous les véhicules ont la même capacité.
- On respecte la capacité grâce au “découpage intelligent” des tournées.
- Limite stricte de temps de calcul: par défaut ~170 secondes (< 3 minutes).
- Fenêtres de temps (ex: livrer entre 8h et 18h): non gérées explicitement dans cette version.
  - On suppose que minimiser la distance revient à minimiser le temps de tournée.

## Modélisation Exacte (PuLP) - Analyse Théorique
En complément de l'algorithme génétique (méthode heuristique), cette section fournit une Modélisation Exacte (MIP) utilisant PuLP.

L'objectif de cette partie n'est pas de remplacer le solveur GA, mais de prouver théoriquement et pratiquement pourquoi une approche heuristique est nécessaire pour ce problème complexe (MD-VRPSC).

Le script run_pulp_demo.py modélise le problème complet avec les 3 contraintes (Capacité, Multi-Dépôts, Compatibilité/Split) en utilisant l'astuce de pré-traitement (décomposition des commandes) pour rester dans un modèle polynomial O(n^2v) et éviter l'explosion exponentielle (2^n) des contraintes DFJ.

Ce que contient cette partierun_pulp_demo.py 

- Le script de modélisation exacte (MIP) et de démonstration.p03_test.vrp — Instance (N=10, 3 dépôts) pour le Test de Succès (validation du modèle).p01.vrp — Instance (N=50, 4 dépôts) pour le Test d'Échec (validation de la complexité NP-hard).Rapport_Modelisation.html — (Ce document) L'analyse théorique complète (Modélisation, Complexité NP-Complet, Analyse O(2^n) vs O(n^2v)).

Lancer la Démonstration PuLP

Ce script démontre la faisabilité (sur petit N) et l'infaisabilité (sur grand N) de la méthode exacte.

Prérequis Python 3.10 ou plus PuLP (solveur MIP) : pip install pulp

Exécution de la Démonstration

Le script est conçu pour exécuter deux tests :

- Test de Succès (Validation du Modèle) Objectif : Prouver que notre modèle mathématique (Étape B) est logiquement correct. Action : Dans run_pulp_demo.py, régler FILE_TO_SOLVE = "p03_test.vrp". Lancer : python run_pulp_demo.py Résultat Attendu : Solver Status: Optimal. Le script trouve la solution optimale en quelques secondes.

- Test d'Échec (Validation de la Complexité) Objectif : Prouver en pratique que la méthode exacte est impossible pour des instances de taille réelle dans le temps imparti. Action : Dans run_pulp_demo.py, régler FILE_TO_SOLVE = "p01.vrp". Lancer : python run_pulp_demo.py Résultat Attendu : Solver Status: Not Solved. Le solveur s'arrêtera après la limite de temps (ex: 170s) sans avoir trouvé de solution.

L'échec du Test 2 justifie la stratégie principale de ce projet, qui est l'utilisation d'un algorithme heuristique (GA) pour obtenir des solutions de haute qualité en un temps raisonnable.

## Ce que contient le dépôt

- `cvrp_data.py` — Lecture des fichiers CVRPLIB `.vrp`, construction de l’instance:
  - coordonnées des points (clients + dépôt)
  - demandes des clients
  - capacité des véhicules
  - matrice de distances (euclidienne arrondie à la manière TSPLIB)
- `split.py` — Découpe une “grande tournée” en plusieurs tournées faisables (respect de la capacité) via une programmation dynamique.
- `localsearch.py` — Amélioration locale “par inversion de segments” à l’intérieur d’une tournée (souvent appelée 2-opt).
- `solution.py` — Calcul du coût d’une solution, vérification des contraintes, lecture/écriture de solutions texte.
- `ga.py` — Le cœur de l’algorithme génétique: population, sélection, croisement, mutation, évaluation, élitisme, limite de temps.
- `plot.py` — Affichage des tournées trouvées (optionnel, nécessite `matplotlib`).
- `main.py` — Petit lanceur: charge une instance, exécute l’algo, vérifie et écrit la solution, et affiche le tracé.

## Nouveautés

- Arrêt propre à la demande:
  - Appuie sur Ctrl+C pendant l’exécution: l’algo s’arrête proprement et garde le meilleur individu courant.
  - Option `--stop-file chemin/flag.txt`: si ce fichier existe, l’algo stoppe proprement à la fin de la génération.
- Gap vs optimal:
  - Passe `--optimum 12345` si tu connais la valeur optimale; on affiche le gap (%) dans les logs et dans le résumé final.

## Lancer le programme

Prérequis:
- Python 3.10 ou plus
- Optionnel pour l’affichage: `pip install matplotlib`

Exécution:
- Place un fichier `.vrp` (format CVRPLIB) quelque part.
- Lance:
```
python main.py --instance /chemin/vers/mon_instance.vrp --optimum 123456 --stop-file stop.flag
```
- Tu peux créer le fichier `stop.flag` quand tu veux (ex: `touch stop.flag`) pour stopper proprement.
- Appuie sur Ctrl+C à tout moment pour obtenir directement les résultats courants.

Sorties:
- Affiche le coût total, le nombre de véhicules (nombre de tournées), et la validité des contraintes.
- Si `--optimum` est fourni: affiche aussi `Gap vs optimal: X.YZ%`.
- Écrit un fichier solution texte: `solution_<nom_instance>.sol`
- Si `matplotlib` est dispo, sauvegarde une image: `solution_<nom_instance>.png`

## Paramètres utiles (où les changer)

Dans `ga.py`, la fonction `genetic_algorithm(...)` contient les réglages principaux:
- Taille de population, nombre de générations max
- Sélection par tournoi (taille du tournoi)
- Probabilités de croisement et de mutation
- Activation et probabilité de l’amélioration locale
- Limite de temps (par défaut 170 secondes)
- Nouvelle option `target_optimum` (affichage gap), et `stop_on_file` (arrêt propre via fichier sentinelle)

Besoin d’aide pour intégrer des fenêtres de temps ou booster les perfs ? Dis-moi, on itère.