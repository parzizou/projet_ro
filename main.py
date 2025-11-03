from genetic import *
import classes as vrp_classes
import matplotlib.pyplot as plt


def importer_data(filename: str):
    """
    Importe les données depuis un fichier .vrp (format VRP classique: NODE_COORD_SECTION, DEMAND_SECTION, DEPOT_SECTION)
    
    Parsing:
      - CAPACITY : capacité des camions (1D)
      - NODE_COORD_SECTION : id, x, y
      - DEMAND_SECTION : id, demande
      - DEPOT_SECTION : liste d'id de dépôt (on prend le premier)
    
    Retourne:
        commandes : list[Commande]  (une commande par client non-dépôt, avec poid = demande)
        camions   : list[Camion]    (flotte très grande: 1 camion par commande, tous même capacité)
    """
    
    capacity = None
    coords = {}   # id -> (x, y)
    demands = {}  # id -> demand
    depots = []   # list of depot ids

    section = None  # 'coords' | 'demands' | 'depot' | None

    with open(filename, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            if line.startswith("EOF"):
                break

            # En-têtes / métadonnées
            if line.upper().startswith("CAPACITY"):
                # ex: "CAPACITY : 144"
                try:
                    capacity = int(line.split(":")[1].strip())
                except Exception:
                    raise ValueError(f"Ligne CAPACITY mal formée: {line}")
                continue
            if line.upper().startswith("NODE_COORD_SECTION"):
                section = "coords"
                continue
            if line.upper().startswith("DEMAND_SECTION"):
                section = "demands"
                continue
            if line.upper().startswith("DEPOT_SECTION"):
                section = "depot"
                continue

            # Lecture selon section
            if section == "coords":
                # format: id x y
                parts = line.split()
                if len(parts) >= 3 and parts[0].lstrip("-").isdigit():
                    idx = int(parts[0])
                    x = float(parts[1])
                    y = float(parts[2])
                    coords[idx] = (x, y)
                continue

            if section == "demands":
                # format: id demand
                parts = line.split()
                if len(parts) >= 2 and parts[0].lstrip("-").isdigit():
                    idx = int(parts[0])
                    d = int(parts[1])
                    demands[idx] = d
                continue

            if section == "depot":
                # lignes: depot_id ... puis -1 pour terminer
                parts = line.split()
                if not parts:
                    continue
                try:
                    val = int(parts[0])
                except Exception:
                    continue
                if val == -1:
                    section = None
                else:
                    depots.append(val)
                continue

    if capacity is None:
        raise ValueError("CAPACITY non trouvée dans le fichier .vrp")
    if not coords:
        raise ValueError("NODE_COORD_SECTION vide ou non trouvé")
    if not demands:
        # Certains jeux peuvent avoir 0 pour le dépôt uniquement, mais on s'attend à des demandes pour les clients
        # On ne lève pas forcément une erreur dure, mais on prévient
        # raise ValueError("DEMAND_SECTION vide ou non trouvé")
        pass

    # Déterminer le dépôt (par défaut 1 si non fourni)
    depot_id = depots[0] if depots else 1
    if depot_id not in coords:
        raise ValueError(f"Le dépôt {depot_id} n'a pas de coordonnées dans NODE_COORD_SECTION")
    # Mettre à jour la position du dépôt pour le calcul des distances
    vrp_classes.DEPOT_POS = (float(coords[depot_id][0]), float(coords[depot_id][1]))

    # Construire les commandes (ignorer le dépôt et les demandes nulles)
    commandes = []
    for idx, demand in demands.items():
        if idx == depot_id or demand <= 0:
            continue
        pos = coords.get(idx)
        if pos is None:
            # Si pas de coord pour un client, on ignore cette demande
            continue
        commandes.append(
            Commande(
                client=idx,
                pos=(float(pos[0]), float(pos[1])),
                poid=float(demand),
                taille_x=0,
                taille_y=0,
                taille_z=0,
            )
        )
    # Optionnel: tri pour reproductibilité
    commandes.sort(key=lambda c: c.client)

    # Créer une "très grande" flotte de camions identiques (un par commande)
    # On n'utilise que la capacité de poids dans la validation, donc on recopie capacity pour les autres dimensions à titre informatif.
    n_camions = max(1, len(commandes))
    camions = [
        Camion(
            capacite_poid=float(capacity),
            capacite_taille_x=float(capacity),
            capacite_taille_y=float(capacity),
            capacite_taille_z=float(capacity),
        )
        for _ in range(n_camions)
    ]

    return commandes, camions



def main():
    # on importe les données depuis un fichier .vrp
    # On applique l'algorithme génétique pour trouver une solution
    # puis on affiche la solution trouvée
    # on l'affiche graphiquement grace a matplotlib
    commandes, camions = importer_data("data.vrp")
    solution = genetic_algorithm(commandes, camions,
                                 taille_population=100,
                                    generations=500,
                                    taux_mutation=0.1,
                                    taille_selection=30)
    solution.afficher_solution()
    # Affichage graphique
    # afficher chaque route avec une couleur différente
    # NE PAS tracer les segments vers/depuis le dépôt pour éviter l'amas de lignes
    plt.figure(figsize=(10, 8))
    couleurs = plt.cm.get_cmap('tab20', len(solution.routes))
    for idx, route in enumerate(solution.routes):
        camion, commandes_route = route
        if not commandes_route:
            continue
        # Tracer uniquement les segments entre clients, sans le dépôt
        xs = [cmd.pos[0] for cmd in commandes_route]
        ys = [cmd.pos[1] for cmd in commandes_route]
        # Si une seule commande, on verra juste le point (pas de segment vers le dépôt)
        plt.plot(xs, ys, marker='o', linestyle='-', color=couleurs(idx), label=f'Route #{idx+1}')
    # Afficher le dépôt uniquement comme repère
    plt.scatter([vrp_classes.DEPOT_POS[0]], [vrp_classes.DEPOT_POS[1]], color='red', s=100, label='Dépôt')
    plt.title('Routes de Livraison (sans segments vers le dépôt)')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.legend()
    plt.grid()
    plt.show()
    
if __name__ == "__main__":
    main()