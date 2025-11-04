# -*- coding: utf-8 -*-
"""
main.py
Point d'entrée: lance le GA sur une instance CVRPLIB .vrp.
Affiche le meilleur coût, nombre de véhicules, vérification des contraintes, écrit et trace la solution.
Chemin par défaut robuste (data.vrp à côté de ce fichier), logs et plotting.
"""

from __future__ import annotations
import argparse
import os
import traceback

from cvrp_data import load_cvrp_instance, CVRPInstance
from ga import genetic_algorithm
from solution import verify_solution, solution_total_cost, write_solution_text, read_simple_sol_and_cost


def build_original_id_mapping(inst: CVRPInstance, instance_path: str):
    """
    Construit un mapping index_interne -> id_original et inverse, à partir du fichier .vrp.
    Utile pour afficher les routes avec les IDs originaux.
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
                if u == "DEMAND_SECTION":
                    break
                if not line or u == "EOF":
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
        depot_id = 1  # fallback

    other_ids = [i for i in ids if i != depot_id]
    ordered_ids = [depot_id] + other_ids
    index_from_original_id = {oid: idx for idx, oid in enumerate(ordered_ids)}
    original_id_from_index = {idx: oid for oid, idx in index_from_original_id.items()}
    return original_id_from_index, index_from_original_id


def resolve_instance_path(cli_value: str | None) -> tuple[str | None, list[str]]:
    """
    Résout le chemin de l'instance:
    - Si cli_value est donné: teste tel quel, puis relatif au dossier du script.
    - Sinon: teste data.vrp à côté de main.py, puis ./data.vrp (cwd).
    Retourne (chemin_trouvé_ou_None, liste_des_chemins_testés).
    """
    tried = []
    script_dir = os.path.dirname(os.path.abspath(__file__))

    candidates = []
    if cli_value:
        candidates.append(cli_value)
        candidates.append(os.path.join(script_dir, cli_value))
    else:
        candidates.append(os.path.join(script_dir, "data.vrp"))
        candidates.append("data.vrp")

    for cand in candidates:
        tried.append(os.path.abspath(cand))
        if os.path.isfile(cand):
            return os.path.abspath(cand), tried
    return None, tried


def run():
    parser = argparse.ArgumentParser(description="CVRP - Algorithme génétique (compat. CVRPLIB, ex: X-n153-k22)")
    # Instance: None = on essaie data.vrp à côté du script
    parser.add_argument(
        "--instance",
        type=str,
        default=None,
        help="Chemin vers le fichier .vrp (par défaut, on cherche 'data.vrp' à côté de ce script)"
    )
    # Defaults ajustés pour bons résultats ~<3 minutes (time limit prime sur --gens)
    parser.add_argument("--pop", type=int, default=110, help="Taille de population (défaut 110)")
    parser.add_argument("--gens", type=int, default=5000, help="Nombre max de générations (défaut 1000, s'arrête plus tôt par time-limit)")
    parser.add_argument("--elitism", type=int, default=4, help="Nombre d'individus élites conservés (défaut 4)")
    parser.add_argument("--tk", type=int, default=4, help="Taille du tournoi de sélection (défaut 4)")
    parser.add_argument("--pc", type=float, default=0.95, help="Probabilité de crossover (défaut 0.95)")
    parser.add_argument("--pm", type=float, default=0.25, help="Probabilité de mutation (défaut 0.25)")
    parser.add_argument("--seed", type=int, default=4, help="Graine aléatoire")
    parser.add_argument("--no-2opt", action="store_true", help="Désactiver le 2-opt intra-route")
    parser.add_argument("--two-opt-prob", type=float, default=0.35, help="Probabilité d'appliquer 2-opt par individu (défaut 0.35)")
    parser.add_argument("--time-limit", type=float, default=170.0, help="Limite de temps en secondes (défaut 170s)")

    # IMPORTANT: argument de validation .sol (corrige l'attribut manquant)
    parser.add_argument("--validate-sol", type=str, default=None, help="Chemin vers un fichier .sol à évaluer (ne lance pas le GA)")

    # Logs d'exécution
    parser.add_argument("--verbose", action="store_true", help="Afficher des logs de progression détaillés")
    parser.add_argument("--log-interval", type=int, default=10, help="Afficher un log toutes les N générations (défaut 10)")

    # Plotting
    parser.add_argument("--plot", action="store_true", help="Afficher/produire un graphique de la solution")
    parser.add_argument("--save-plot", type=str, default=None, help="Chemin d'image pour sauvegarder le graphique (ex: solution.png)")
    parser.add_argument("--no-show", action="store_true", help="Ne pas afficher la fenêtre interactive du graphique (utile en headless)")

    # Pause en fin d'exécution (utile si lancé par double-clic)
    parser.add_argument("--pause-on-exit", action="store_true", help="Attendre Entrée avant de fermer le programme")

    args = parser.parse_args()

    # Résoudre le chemin de l'instance
    instance_path, tried = resolve_instance_path(args.instance)
    if instance_path is None:
        print("Fichier instance introuvable. Chemins testés:", flush=True)
        for p in tried:
            print(f" - {p}", flush=True)
        print("Place 'data.vrp' dans le même dossier que main.py, ou passe un chemin avec --instance.", flush=True)
        if args.pause_on_exit:
            input("\nAppuie sur Entrée pour fermer...")
        return

    print(f"[Run] Chargement de l'instance: {instance_path}", flush=True)
    inst: CVRPInstance = load_cvrp_instance(instance_path)
    print(f"[Run] Instance: {inst.name} | N={inst.dimension} | Capacité={inst.capacity}", flush=True)

    # Mapping IDs originaux <-> index internes pour les sorties lisibles
    original_id_from_index, index_from_original_id = build_original_id_mapping(inst, instance_path)

    # Mode validation d'un .sol: pas de GA, on calcule juste le coût (robuste si l'attribut n'existe pas)
    validate_sol = getattr(args, "validate_sol", None)
    if validate_sol:
        print(f"[Run] Validation du fichier solution: {validate_sol}", flush=True)
        cost = read_simple_sol_and_cost(
            validate_sol,
            inst,
            assume_includes_depot=False,
            index_from_original_id=index_from_original_id
        )
        print(f"Coût du fichier solution '{validate_sol}' selon l'instance: {cost}")
        if args.pause_on_exit:
            input("\nAppuie sur Entrée pour fermer...")
        return

    use_2opt = not args.no_2opt
    if args.verbose:
        print(
            f"[Run] Lancement GA | pop={args.pop} | gens={args.gens} | elitism={args.elitism} | tk={args.tk} | "
            f"pc={args.pc} | pm={args.pm} | seed={args.seed} | 2opt={'on' if use_2opt else 'off'} | "
            f"2opt_prob={args.two_opt_prob} | time_limit={args.time_limit}s | log_interval={args.log_interval}",
            flush=True,
        )

    best = genetic_algorithm(
        inst,
        pop_size=args.pop,
        generations=args.gens,
        tournament_k=args.tk,
        elitism=args.elitism,
        pc=args.pc,
        pm=args.pm,
        seed=args.seed,
        use_2opt=use_2opt,
        verbose=args.verbose,
        log_interval=args.log_interval,
        two_opt_prob=args.two_opt_prob,
        time_limit_sec=args.time_limit,
    )

    is_ok, msgs = verify_solution(best.routes, inst)
    total = solution_total_cost(best.routes, inst)
    nb_veh = len(best.routes)

    print("\n=== Résultat GA ===")
    print(f"Coût total: {total}")
    print(f"Nombre de véhicules: {nb_veh}")
    print(f"Contraintes OK: {is_ok}")
    if not is_ok:
        print("Détails:")
        for m in msgs:
            print(" -", m)

    # Sauvegarde solution texte
    base = os.path.splitext(os.path.basename(instance_path))[0]
    sol_path = f"solution_{base}.sol"
    print(f"[Run] Écriture de la solution dans: {sol_path}", flush=True)
    write_solution_text(
        best.routes,
        inst,
        sol_path,
        include_depot=False,
        original_id_from_index=[original_id_from_index[i] for i in range(inst.dimension)]
    )
    print(f"Solution écrite: {sol_path}")

    # Plot de la solution si demandé
    if args.plot:
        img_path = args.save_plot or f"solution_{base}.png"
        title = f"{inst.name} | coût={total} | véhicules={nb_veh}"
        try:
            from plot import plot_solution
            print(f"[Run] Génération du graphique de la solution...", flush=True)
            plot_solution(
                inst,
                best.routes,
                title=title,
                save_path=img_path,
                show=not args.no_show,
                annotate=False,
                dpi=140,
                connect_depot=False,  # pas de segments vers le dépôt
            )
            print(f"[Run] Graphique prêt. Fichier: {img_path}")
        except ImportError as e:
            print(str(e))
            print("Astuce: installe matplotlib avec 'pip install matplotlib' puis relance avec --plot.")

    if args.pause_on_exit:
        input("\nAppuie sur Entrée pour fermer...")


if __name__ == "__main__":
    try:
        run()
    except Exception:
        print("\n[Erreur] Une exception est survenue:", flush=True)
        traceback.print_exc()
        try:
            input("\nAppuie sur Entrée pour fermer...")
        except Exception:
            pass