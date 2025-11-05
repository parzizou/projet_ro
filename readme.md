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
- `split.py` — Découpe une “grande tournée” en plusieurs tournées faisables (respect de la capacité) via une programmation dynamique.
- `localsearch.py` — Amélioration locale “par inversion de segments” à l’intérieur d’une tournée (souvent appelée 2-opt).
- `solution.py` — Calcul du coût d’une solution, vérification des contraintes, lecture/écriture de solutions texte.
- `ga.py` — Le cœur de l’algorithme génétique: population, sélection, croisement, mutation, évaluation, élitisme, limite de temps.
- `plot.py` — Affichage des tournées trouvées (optionnel, nécessite `matplotlib`).
- `main.py` — Petit lanceur: charge une instance, exécute l’algo, vérifie et écrit la solution, et affiche le tracé.

## Comment l’algo fonctionne 

L’algorithme génétique est une méthode inspirée de l’évolution:
on manipule une population de solutions, on “reproduit” les meilleures, on mélange, on mute, et on garde ce qui marche le mieux.

Voici les étapes concrètes dans ce projet:

1) Représentation d’une solution
- On ne construit pas directement des tournées.
- On garde une seule grande liste ordonnée de tous les clients (on appelle ça une “grande tournée”).
- Exemple: [5, 12, 3, 8, 1, ...] signifie juste “l’ordre dans lequel on visitera les clients” (le dépôt n’est pas dedans).

2) Transformer cette liste en vraies tournées faisables
- En partant de cette grande liste, on coupe au bon endroit pour fabriquer des tournées qui respectent la capacité camion.
- On utilise une programmation dynamique: parmi toutes les manières de couper, on choisit celles qui donnent le coût total (distance) le plus faible.
- Résultat: un ensemble de tournées, chacune part du dépôt et y revient, sans dépasser la capacité.

3) Calcul du coût d’une solution
- Pour chaque tournée: dépôt -> clients dans l’ordre -> dépôt.
- On additionne toutes les distances pour obtenir le coût total.

4) Petite amélioration dans chaque tournée
- Pour chaque tournée, on essaie d’inverser certains morceaux (des sous-séquences) si ça raccourcit le trajet.
- Intuition: si deux segments se croisent ou sont mal ordonnés, inverser un bout améliore souvent la distance.

5) Construire la population de départ
- 1 solution “pas bête”: on part du dépôt et on ajoute toujours le client le plus proche (sans penser à la capacité, le découpage s’en occupera).
- Les autres solutions sont aléatoires (différents ordres de clients).
- On évalue chacune (découpage + coût + petite amélioration possible).

6) Faire “évoluer” la population
- Sélection des parents: on prend quelques candidats au hasard et on choisit le meilleur du petit groupe (tournoi).
- Croisement (mélange de deux parents):
  - On copie un segment du premier parent tel quel.
  - On complète avec les clients manquants dans l’ordre du deuxième parent.
  - Ça garde la variété tout en respectant l’ordre relatif de beaucoup de clients.
- Mutation (petites perturbations):
  - Soit on échange deux positions,
  - Soit on inverse un petit morceau.
  - Le but est d’explorer de nouvelles possibilités.
- On réévalue les enfants (découpage + coût).
- On garde aussi quelques meilleurs de la génération précédente (élitisme) pour ne pas perdre les bons plans.
- On recommence plusieurs générations, mais on s’arrête avant 3 minutes.

7) Respect des contraintes
- Capacité: garantie par l’étape de découpage.
- Couverture: chaque client apparaît une seule fois.
- Dépôt: chaque tournée part et revient au dépôt (implicite dans le calcul du coût).
- Fenêtres de temps: pas gérées explicitement (à ajouter si nécessaire plus tard).

## Lancer le programme

Prérequis:
- Python 3.10 ou plus
- Optionnel pour l’affichage: `pip install matplotlib`

Exécution:
- Place un fichier `.vrp` (format CVRPLIB) quelque part.
- Lance:
```
python main.py --instance /chemin/vers/mon_instance.vrp
```
- Si tu ne donnes pas `--instance`, le script essaiera de charger `data3.vrp` dans le dossier du projet ou dans le répertoire courant.

Sorties:
- Affiche le coût total, le nombre de véhicules (nombre de tournées), et la validité des contraintes.
- Écrit un fichier solution texte: `solution_<nom_instance>.sol`
  - Exemple de ligne: `Route #1: 0 14 53 ... 0` si tu actives l’option d’inclure le dépôt (dans ce projet on écrit par défaut sans répéter le dépôt).
- Si `matplotlib` est dispo, en plus d’afficher, sauvegarde une image: `solution_<nom_instance>.png`

## Paramètres utiles (où les changer)

Dans `ga.py`, la fonction `genetic_algorithm(...)` contient les réglages principaux:
- Taille de population, nombre de générations max
- Sélection par tournoi (taille du tournoi)
- Probabilités de croisement et de mutation
- Activation et probabilité de l’amélioration locale par inversion de segments
- Limite de temps (par défaut 170 secondes)
- Graine aléatoire (pour reproduire des résultats)

Tu peux les ajuster en appelant `genetic_algorithm(inst, ...)` avec tes valeurs depuis `main.py`.

## Format des instances et distances

- On lit des `.vrp` du style CVRPLIB.
- Distances calculées à partir des coordonnées (euclidiennes), avec l’arrondi standard de TSPLIB.
- Le dépôt est mis à l’index 0 en interne (on remappe pour écrire des solutions avec les identifiants d’origine si besoin).

## Limites actuelles et idées d’évolution

- Pas de fenêtres de temps (8h–18h) ni de vitesses ou durées de service: à ajouter si nécessaire (il faudrait suivre le temps accumulé et vérifier les bornes).
- Pas de mouvements “inter-tournées” en amélioration locale (du type “prendre un client d’une tournée pour le mettre dans une autre”) — facile à ajouter plus tard (relocate, swap entre tournées).
- Distances supposées symétriques et basées sur les coordonnées (pas de routes asymétriques ou “vraies” durées de circulation).

## Structure du code (rappel)

- `main.py` — Lance l’algo et gère l’I/O
- `cvrp_data.py` — Lecture de l’instance et distances
- `split.py` — Découpage de la grande liste en tournées faisables
- `localsearch.py` — Amélioration locale par inversion de segments
- `ga.py` — Boucle d’évolution (sélection, croisement, mutation, élitisme, limite de temps)
- `solution.py` — Coût, vérification, lecture/écriture de solutions
- `plot.py` — Tracé des tournées (optionnel)

Besoin d’aide pour brancher des fenêtres de temps ou pour tuner les paramètres à ton instance ? Dis-moi ce que tu veux, on ajuste ensemble.