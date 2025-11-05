# -*- coding: utf-8 -*-
"""
main.py (version simplifiée)
- Charge un fichier .vrp OU une instance par nom CVRPLIB (via 'vrplib' si installé)
- Exécute l'algo génétique avec ses paramètres par défaut
- Affiche et sauvegarde la solution (.sol) avec les IDs originaux
- Affiche aussi le graphe de la solution (plot.py) et sauvegarde un .png
"""

from __future__ import annotations
import argparse
import os
import sys

from cvrp_data import load_cvrp_instance, CVRPInstance, load_cvrp_from_vrplib
from ga import genetic_algorithm
from solution import verify_solution, solution_total_cost, write_solution_text

# Chemin par défaut du fichier .vrp
pathfile = "data4.vrp"

# NOUVELLES OPTIONS (sans argparse): à éditer ici
# - valeur optimale cible pour afficher le gap (%) dans les logs et le résumé
TARGET_OPTIMUM: int | None = 72355
# - fichier sentinelle: s'il existe pendant l'exécution, l'algo s'arrête proprement
STOP_SENTINEL_FILE: str | None = None  # ex: "stop.flag"


def resolve_instance_path(cli_value: str | None) -> str | None:
    """
    Renvoie un chemin d'instance valide si possible:
    - si cli_value est donné et existe, on le prend
    - sinon on cherche 'data.vrp' à côté de ce script, puis dans le cwd
    """
    if cli_value and os.path.isfile(cli_value):
        return os.path.abspath(cli_value)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(script_dir, pathfile),
        os.path.join(os.getcwd(), pathfile),
    ]
    for cand in candidates:
        if os.path.isfile(cand):
            return os.path.abspath(cand)
    return None


def build_original_id_mapping(inst: CVRPInstance, instance_path: str):
    """
    Construit le mapping index_interne -> id_original (et inverse) depuis le .vrp,
    pour écrire la solution avec les IDs originaux.
    """
    ids = []
    with open(instance_path, "r", encoding="utf-8", errors="ignore") as f:
        coords_section = False
        for raw in f:
            line = raw.strip()
            u = line.upper()
            if u.startswith("NODE_COORD_SECTION"):
                coords_section = True
                continue
            if coords_section:
                if u == "DEMAND_SECTION" or u == "EOF" or not line:
                    break
                parts = line.split()
                if len(parts) >= 3:
                    nid = int(parts[0])
                    ids.append(nid)

    depot_id = None
    with open(instance_path, "r", encoding="utf-8", errors="ignore") as f:
        dep_section = False
        for raw in f:
            line = raw.strip()
            u = line.upper()
            if u.startswith("DEPOT_SECTION"):
                dep_section = True
                continue
            if dep_section:
                if line == "-1":
                    break
                depot_id = int(line)
                break

    if depot_id is None:
        depot_id = 1

    other_ids = [i for i in ids if i != depot_id]
    ordered_ids = [depot_id] + other_ids
    index_from_original_id = {oid: idx for idx, oid in enumerate(ordered_ids)}
    original_id_from_index = {idx: oid for oid, idx in index_from_original_id.items()}
    return original_id_from_index, index_from_original_id


def main():
    parser = argparse.ArgumentParser(description="CVRP - Exécution simple de l'algorithme génétique + plot")
    parser.add_argument(
        "--instance",
        type=str,
        default=None,
        help="Chemin vers le fichier .vrp local. Si absent, essaie 'data.vrp' à côté de ce script puis dans le CWD.",
    )
    parser.add_argument(
        "--name",
        type=str,
        default=None,
        help="Nom d'une instance CVRPLIB (ex: A-n32-k5). Requiert 'pip install vrplib'.",
    )
    args = parser.parse_args()

    # Variables résultantes
    inst: CVRPInstance
    original_ids_list: list[int]
    instance_label = None

    if args.name:
        # Chargement direct depuis CVRPLIB via 'vrplib'
        try:
            inst, original_ids_list, best_known = load_cvrp_from_vrplib(args.name)
        except ImportError as e:
            print(str(e))
            sys.exit(1)
        except Exception as e:
            print(f"Échec de chargement via vrplib pour '{args.name}': {e}")
            sys.exit(1)

        instance_label = args.name
        print(f"[Run] Chargée depuis CVRPLIB (vrplib): {args.name}")
        if best_known is not None and best_known > 0:
            # On écrase la cible si connue pour afficher le gap
            # (tu peux commenter cette ligne si tu veux garder la cible codée en dur)
            global TARGET_OPTIMUM
            TARGET_OPTIMUM = best_known
            print(f"[Run] Best-known cost détecté: {best_known} (TARGET_OPTIMUM mis à jour)")
    else:
        # Fichier local
        instance_path = resolve_instance_path(args.instance)
        if instance_path is None:
            print("Aucun fichier .vrp trouvé.")
            print("Passe un chemin avec --instance, ou place 'data.vrp' à côté de main.py (ou dans le répertoire courant).")
            print("Ou bien utilise --name A-n32-k5 (nécessite 'pip install vrplib').")
            sys.exit(1)

        print(f"[Run] Chargement: {instance_path}")
        inst = load_cvrp_instance(instance_path)
        # Mapping IDs originaux pour écriture sol
        original_id_from_index, _ = build_original_id_mapping(inst, instance_path)
        original_ids_list = [original_id_from_index[i] for i in range(inst.dimension)]
        instance_label = os.path.splitext(os.path.basename(instance_path))[0]

    print(f"[Run] Instance: {inst.name} | N={inst.dimension} | Capacité={inst.capacity}")
    if TARGET_OPTIMUM is not None and TARGET_OPTIMUM <= 0:
        print("[Warn] TARGET_OPTIMUM doit être > 0 pour un calcul de gap utile.", flush=True)
    if STOP_SENTINEL_FILE:
        print(f"[Run] Arrêt possible par fichier sentinelle: crée '{STOP_SENTINEL_FILE}' pour stopper proprement.", flush=True)
    print("[Run] Astuce: Ctrl+C pour arrêter proprement et garder le meilleur courant.", flush=True)

    # Si on a chargé via nom CVRPLIB, on doit fabriquer original_ids_list
    if args.name:
        # load_cvrp_from_vrplib nous a déjà donné la liste index->id_original
        pass

    # Exécute le GA (arrêt possible par Ctrl+C ou fichier sentinelle)
    best = genetic_algorithm(
        inst,
        target_optimum=TARGET_OPTIMUM,
        stop_on_file=STOP_SENTINEL_FILE,
    )

    # Vérification + affichage
    is_ok, msgs = verify_solution(best.routes, inst)
    total = solution_total_cost(best.routes, inst)
    nb_veh = len(best.routes)

    print("\n=== Résultat ===")
    print(f"Coût total: {total}")
    if TARGET_OPTIMUM and TARGET_OPTIMUM > 0:
        gap = 100.0 * (total - TARGET_OPTIMUM) / TARGET_OPTIMUM
        print(f"Gap vs optimal ({TARGET_OPTIMUM}): {gap:.2f}%")
    print(f"Nombre de véhicules: {nb_veh}")
    print(f"Contraintes OK: {is_ok}")
    if not is_ok:
        print("Détails:")
        for m in msgs:
            print(" -", m)

    # Sauvegarde solution (.sol) avec IDs originaux
    base = instance_label or "instance"
    sol_path = f"solution_{base}.sol"
    write_solution_text(
        best.routes,
        inst,
        sol_path,
        include_depot=False,
        original_id_from_index=original_ids_list,
    )
    print(f"[Run] Solution écrite: {sol_path}")

    # Affichage graphique + sauvegarde image
    title = f"{inst.name} | coût={total} | véhicules={nb_veh}"
    img_path = f"solution_{base}.png"
    try:
        from plot import plot_solution
        print("[Run] Affichage du graphe de la solution (matplotlib requis)...")
        plot_solution(
            inst,
            best.routes,
            title=title,
            save_path=img_path,   # on sauvegarde aussi l'image
            show=True,            # on affiche la fenêtre
            annotate=False,
            dpi=140,
            connect_depot=False,  # segments entre clients uniquement (plus lisible)
        )
        print(f"[Run] Image sauvegardée: {img_path}")
    except ImportError:
        print("matplotlib n'est pas installé, pas de graphique. Installe-le avec: pip install matplotlib")


if __name__ == "__main__":
    main()