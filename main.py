# -*- coding: utf-8 -*-
"""
main.py (version simplifiée)
- Charge un fichier .vrp
- Exécute l'algo génétique avec ses paramètres par défaut
- Affiche et sauvegarde la solution (.sol) avec les IDs originaux
- Affiche aussi le graphe de la solution (plot.py) et sauvegarde un .png
"""

from __future__ import annotations
import argparse
import os
import sys

from src.core.cvrp_data import load_cvrp_instance, CVRPInstance
from src.core.ga import genetic_algorithm
from src.core.solution import verify_solution, solution_total_cost, write_solution_text

# Chemin par défaut du fichier .vrp  
pathfile = "data/instances/data.vrp"

# NOUVELLES OPTIONS (sans argparse): à éditer ici
# - valeur optimale cible pour afficher le gap (%) dans les logs et le résumé
TARGET_OPTIMUM: int | None = 21220
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
        help="Chemin vers le fichier .vrp. Si absent, essaie 'data.vrp' à côté de ce script puis dans le CWD.",
    )
    args = parser.parse_args()

    instance_path = resolve_instance_path(args.instance)
    if instance_path is None:
        print("Aucun fichier .vrp trouvé.")
        print("Passe un chemin avec --instance, ou place 'data.vrp' à côté de main.py (ou dans le répertoire courant).")
        sys.exit(1)

    print(f"[Run] Chargement: {instance_path}")
    inst: CVRPInstance = load_cvrp_instance(instance_path)
    print(f"[Run] Instance: {inst.name} | N={inst.dimension} | Capacité={inst.capacity}")
    if TARGET_OPTIMUM is not None and TARGET_OPTIMUM <= 0:
        print("[Warn] TARGET_OPTIMUM doit être > 0 pour un calcul de gap utile.", flush=True)
    if STOP_SENTINEL_FILE:
        print(f"[Run] Arrêt possible par fichier sentinelle: crée '{STOP_SENTINEL_FILE}' pour stopper proprement.", flush=True)
    print("[Run] Astuce: Ctrl+C pour arrêter proprement et garder le meilleur courant.", flush=True)

    # Mapping IDs originaux pour écrire une solution lisible
    original_id_from_index, _ = build_original_id_mapping(inst, instance_path)

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
    base = os.path.splitext(os.path.basename(instance_path))[0]
    sol_path = f"solution_{base}.sol"
    write_solution_text(
        best.routes,
        inst,
        sol_path,
        include_depot=False,
        original_id_from_index=[original_id_from_index[i] for i in range(inst.dimension)],
    )
    print(f"[Run] Solution écrite: {sol_path}")

    # Affichage graphique + sauvegarde image
    title = f"{inst.name} | coût={total} | véhicules={nb_veh}"
    img_path = f"solution_{base}.png"
    try:
        from src.visualization.plot_solution import plot_solution
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