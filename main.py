# -*- coding: utf-8 -*-
"""
main.py (avec:
 - time_limit_sec param pour mono et multi
 - mode multi-dépôts optionnel piloté par les paramètres de main())
"""

from __future__ import annotations
import argparse
import os
import sys

from src.core.cvrp_data import load_cvrp_instance, CVRPInstance, load_cvrp_from_vrplib
from src.core.ga import genetic_algorithm
from src.core.solution import verify_solution, solution_total_cost, write_solution_text

# Multi-dépôts
try:
    from multi_depot import (
        MultiDepotConfig,
        run_multi_depot_pipeline,
    )
    _MD_AVAILABLE = True
except Exception:
    _MD_AVAILABLE = False

pathfile = "data3.vrp"  # fichier par défaut s'il n'y en a pas d'autre

TARGET_OPTIMUM: int | None = 58578
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


def _clamp01(x: float | None, default: float) -> float:
    if x is None:
        return default
    return max(0.0, min(1.0, float(x)))


def main(
    pop_size: int | None = None,
    mutation_rate: float | None = None,
    crossover_rate: float | None = None,
    two_opt_chance: float | None = None,
    instance_vrplib: str | None = None,
    init_mode: str = "nn_plus_random",   # "nn_plus_random" (défaut) ou "all_random"
    instance: str | None = None,         # chemin .vrp alternatif si pas d'instance_vrplib

    # NOUVEAU: time limit commun mono/multi
    time_limit_sec: float | None = 170.0,

    # NOUVEAU: paramètres pour le mode multi-dépôts (pilotés par la fonction)
    multi: bool = False,
    md_n: int = 4,
    md_types: str = "ABCD",
    md_seed: int = 123,
    md_capacity: int | None = None,
    md_plot_connect_depot: bool = False,
):
    """
    Lance l'algo avec des paramètres passés directement à main pour faciliter les tests rapides.
    - time_limit_sec s'applique au mono et au multi (passé au GA).
    - Pour activer le multi-dépôts: passe multi=True et les md_* voulus.
    """
    parser = argparse.ArgumentParser(description="CVRP - Exécution simple de l'algorithme génétique + plot")
    parser.add_argument("--instance", type=str, default=None)
    parser.add_argument("--name", type=str, default=None)
    args = parser.parse_args()

    # Surcharges via paramètres de main()
    if instance_vrplib is not None:
        args.name = instance_vrplib
    if instance is not None:
        args.instance = instance

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

    # Préparation des paramètres GA (avec valeurs par défaut si None)
    ps = pop_size if pop_size is not None else 50
    pm = _clamp01(mutation_rate, 0.30)
    pc = _clamp01(crossover_rate, 0.50)
    two_opt_prob = _clamp01(two_opt_chance, 0.35)
    use_2opt = two_opt_prob > 0.0
    tl = float(time_limit_sec) if time_limit_sec is not None else 0.0

    print(f"[Run] Paramètres GA: pop_size={ps} | pm={pm:.2f} | pc={pc:.2f} | two_opt_prob={two_opt_prob:.2f} | init_mode={init_mode} | time_limit_sec={tl:.1f}")

    # =========================
    # MODE MULTI-DÉPÔTS (optionnel)
    # =========================
    if multi:
        if not _MD_AVAILABLE:
            print("[Err] Module multi_depot introuvable. Ajoute multi_depot.py à la racine du projet.")
            sys.exit(1)

        cfg = MultiDepotConfig(
            k_depots=max(1, int(md_n)),
            types_alphabet=md_types if md_types else "ABCD",
            seed=int(md_seed),
            capacity_override=int(md_capacity) if md_capacity else None,
            connect_depot_on_plot=bool(md_plot_connect_depot),
        )
        print(f"[MD] Mode multi-dépôts activé: K={cfg.k_depots}, types='{cfg.types_alphabet}', seed={cfg.seed}, cap={cfg.capacity_override or inst.capacity}")

        summary = run_multi_depot_pipeline(
            inst_base=inst,
            original_id_from_baseindex=original_ids_list,
            base_label=instance_label or "instance",
            cfg=cfg,
            ga_pop_size=ps,
            ga_pm=pm,
            ga_pc=pc,
            ga_two_opt_prob=two_opt_prob,
            init_mode=init_mode,
            verbose_ga=True,
            do_plot=True,
            ga_time_limit_sec=tl,
        )

        print("\n=== Résultat multi-dépôts ===")
        print(f"Coût total agrégé: {summary['total_cost']}")
        for d in summary["per_depot"]:
            print(f" - Dépôt d{d['depot_idx']} ({d['type']}): coût={d['cost']} | #routes={d['routes_count']}")
        print(f"Solution agrégée: {summary['solution_aggregate_path']}")
        return

    # =========================
    # MODE MONO-DÉPÔT — inchangé (avec time_limit_sec)
    # =========================
    best = genetic_algorithm(
        inst,
        pop_size=ps,
        pm=pm,
        pc=pc,
        two_opt_prob=two_opt_prob,
        use_2opt=use_2opt,
        target_optimum=TARGET_OPTIMUM,
        stop_on_file=STOP_SENTINEL_FILE,
        init_mode=init_mode,
        time_limit_sec=tl,
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
    # Exemples:

    main(
        instance=pathfile,
        time_limit_sec=30.0,
        multi=True,
        md_n=4,
        md_types="ABAB",
        md_seed=42,
        md_plot_connect_depot=False,
    )