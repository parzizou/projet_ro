# -*- coding: utf-8 -*-
"""
test.py
Banc d'essai pour fine-tuner l'algo génétique CVRP.
- On choisit 1 paramètre de ga.genetic_algorithm à faire varier.
- On fixe l'instance + la valeur optimale (cible) pour calculer un gap.
- On lance des essais limités en temps (par défaut 60s) pour chaque valeur.
- On sélectionne la valeur qui donne le meilleur gap moyen (ou meilleur gap).

Exemples:
  - Instance locale:
    python test.py --instance data3.vrp --target 784 --param pm --values 0.10,0.20,0.30,0.40 --time-sec 60 --repeats 3

  - Instance CVRPLIB (récup via vrplib) avec best-known auto:
    pip install vrplib
    python test.py --name A-n32-k5 --param pop_size --values 30:120:10 --time-sec 60 --repeats 2

Options utiles:
  --fixed "pc=0.6,tournament_k=3,init_mode=nn_plus_random"
  --save-csv results.csv
"""

from __future__ import annotations
import argparse
import csv
import inspect
import math
import time
from typing import Any, Callable, Dict, List, Optional, Tuple, Type

from cvrp_data import load_cvrp_instance, load_cvrp_from_vrplib, CVRPInstance
from ga import genetic_algorithm
from solution import verify_solution, solution_total_cost


# Types attendus pour chaque param du GA (pour caster proprement)
_PARAM_TYPES: Dict[str, Type] = {
    "pop_size": int,
    "generations": int,
    "tournament_k": int,
    "elitism": int,
    "pc": float,
    "pm": float,
    "seed": int,
    "use_2opt": bool,
    "verbose": bool,
    "log_interval": int,
    "two_opt_prob": float,
    "time_limit_sec": float,
    "target_optimum": int,
    "stop_on_file": str,
    "init_mode": str,
    "immigrants_frac": float,
    "duplicate_avoidance": bool,
    "stagnation_shake_gens": int,
    "stagnation_restart_gens": int,
    "adaptive_mutation": bool,
    "return_metrics": bool,
}


def _coerce_val(val: str, typ: Type) -> Any:
    if typ is bool:
        v = val.strip().lower()
        if v in ("1", "true", "t", "yes", "y", "on"):
            return True
        if v in ("0", "false", "f", "no", "n", "off"):
            return False
        raise ValueError(f"Valeur bool invalide: {val}")
    if typ is int:
        return int(float(val))  # tolère "10.0"
    if typ is float:
        return float(val)
    if val.strip().lower() == "none":
        return None
    return val


def _parse_values(spec: str, param_name: str) -> List[Any]:
    """
    Accepte:
      - liste: "0.1,0.2,0.3"
      - range: "start:end:step" (inclusif sur end, step peut être float)
    """
    typ = _PARAM_TYPES.get(param_name, float)

    def cast(x: str) -> Any:
        return _coerce_val(x, typ)

    if "," in spec:
        return [cast(x.strip()) for x in spec.split(",") if x.strip()]

    # "start:end:step"
    parts = [p.strip() for p in spec.split(":")]
    if len(parts) == 3:
        start_s, end_s, step_s = parts
        start = float(start_s)
        end = float(end_s)
        step = float(step_s)
        if step == 0:
            raise ValueError("step ne peut pas être 0")
        vals: List[float] = []
        x = start
        # gérer direction step
        if step > 0:
            while x <= end + 1e-12:
                vals.append(x)
                x += step
        else:
            while x >= end - 1e-12:
                vals.append(x)
                x += step
        # cast final
        if typ is int:
            return [int(round(v)) for v in vals]
        return [typ(v) if typ in (float,) else v for v in vals]  # type: ignore
    elif len(parts) == 1:
        # valeur unique
        return [cast(parts[0])]
    else:
        raise ValueError(f"Format de --values invalide: {spec}")


def _parse_fixed(spec: Optional[str]) -> Dict[str, Any]:
    """
    Parse "k=v,k2=v2" en dict, avec cast selon _PARAM_TYPES.
    """
    if not spec:
        return {}
    out: Dict[str, Any] = {}
    for tok in spec.split(","):
        tok = tok.strip()
        if not tok:
            continue
        if "=" not in tok:
            raise ValueError(f"Paramètre fixe invalide (attendu k=v): '{tok}'")
        k, v = tok.split("=", 1)
        k = k.strip()
        v = v.strip()
        typ = _PARAM_TYPES.get(k, str)
        out[k] = _coerce_val(v, typ)
    return out


def _get_allowed_params() -> List[str]:
    sig = inspect.signature(genetic_algorithm)
    return list(sig.parameters.keys())


def _ensure_param_supported(param: str) -> None:
    allowed = _get_allowed_params()
    if param not in allowed:
        raise ValueError(f"Paramètre '{param}' inconnu. Autorisés: {', '.join(allowed)}")


def run_trial(
    inst: CVRPInstance,
    param_name: str,
    param_value: Any,
    base_kwargs: Dict[str, Any],
    time_sec: float,
    seed: int,
    target: Optional[int],
) -> Dict[str, Any]:
    """
    Lance un essai du GA avec une contrainte de temps.
    Retourne dict avec: cost, gap, elapsed_sec, generations_done, routes, value
    """
    kwargs = dict(base_kwargs)
    kwargs[param_name] = param_value
    # Sécurité: si two_opt_prob == 0 => use_2opt False
    if "two_opt_prob" in kwargs:
        kwargs["use_2opt"] = float(kwargs["two_opt_prob"]) > 0.0

    res = genetic_algorithm(
        inst,
        time_limit_sec=float(time_sec),
        seed=int(seed),
        verbose=False,
        log_interval=9999999,  # pas de logs
        return_metrics=True,   # nécessite la petite modif dans ga.py
        **kwargs,
    )
    # genetic_algorithm retourne (best, metrics) si return_metrics=True
    best, metrics = res  # type: ignore
    total = best.cost
    gap = None
    if target is not None and target > 0:
        gap = 100.0 * (total - target) / target

    return {
        "value": param_value,
        "cost": total,
        "gap": gap,
        "elapsed_sec": metrics.get("elapsed_sec"),
        "generations_done": metrics.get("generations_done"),
        "routes": len(best.routes),
        "stopped_by": metrics.get("stopped_by"),
    }


def main():
    parser = argparse.ArgumentParser(description="Fine-tuning GA CVRP: variation d'un paramètre sur essais limités en temps.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--instance", type=str, help="Chemin d'un fichier .vrp local")
    group.add_argument("--name", type=str, help="Nom d'instance CVRPLIB (ex: A-n32-k5) - nécessite vrplib")

    parser.add_argument("--target", type=int, default=None, help="Valeur optimale (best-known). Si non fournie et --name, tente de la récupérer via vrplib.")
    parser.add_argument("--param", required=True, help="Nom du paramètre du GA à faire varier (ex: pop_size, pm, pc, two_opt_prob, tournament_k, ...)")
    parser.add_argument("--values", required=True, help="Liste de valeurs (ex: '0.1,0.2,0.3') ou range 'start:end:step' (inclusif).")
    parser.add_argument("--time-sec", type=float, default=60.0, help="Durée par essai en secondes (défaut: 60)")
    parser.add_argument("--repeats", type=int, default=1, help="Répétitions par valeur pour réduire la variance (défaut: 1)")
    parser.add_argument("--seed", type=int, default=1, help="Seed de base; chaque répétition utilise seed+rep")
    parser.add_argument("--fixed", type=str, default=None, help="Autres paramètres fixes 'k=v,k2=v2' (ex: 'pc=0.6,tournament_k=3')")
    parser.add_argument("--save-csv", type=str, default=None, help="Chemin CSV pour sauvegarder les résultats")
    parser.add_argument("--warmup-sec", type=float, default=0.0, help="Warmup en secondes (pour compiler Numba si dispo). 0 pour désactiver.")

    args = parser.parse_args()

    # Validation param
    _ensure_param_supported(args.param)
    values = _parse_values(args.values, args.param)
    fixed_kwargs = _parse_fixed(args.fixed)

    # Chargement instance
    inst: CVRPInstance
    target = args.target
    if args.name:
        try:
            inst, _, best_known = load_cvrp_from_vrplib(args.name)
        except ImportError:
            print("vrplib n'est pas installé. Fais: pip install vrplib")
            return
        except Exception as e:
            print(f"Chargement via vrplib échoué: {e}")
            return
        if target is None and best_known is not None and best_known > 0:
            target = int(best_known)
            print(f"[Info] Best-known (vrplib): {target}")
        print(f"[Run] Instance CVRPLIB: {inst.name} | N={inst.dimension} | Capacité={inst.capacity}")
    else:
        inst = load_cvrp_instance(args.instance)
        print(f"[Run] Instance locale: {inst.name} | N={inst.dimension} | Capacité={inst.capacity}")

    if target is None or target <= 0:
        print("[Warn] Pas de cible optimale fournie. Le 'gap' ne sera pas calculé.")

    # Warmup (utile si split numba doit compiler)
    if args.warmup_sec and args.warmup_sec > 0:
        try:
            _ = genetic_algorithm(
                inst,
                time_limit_sec=float(args.warmup_sec),
                verbose=False,
                return_metrics=False,  # on s'en fiche des métriques au warmup
            )
            print(f"[Warmup] OK ({args.warmup_sec:.1f}s).")
        except Exception as e:
            print(f"[Warmup] Ignoré ({e}).")

    # Base kwargs: valeurs "raisonnables". L'utilisateur peut override via --fixed.
    base_kwargs: Dict[str, Any] = {
        "pop_size": 40,
        "pm": 0.06,
        "pc": 0.50,
        "two_opt_prob": 0.6,
        "use_2opt": True,
        "tournament_k": 5,
        "elitism": 3,
        "immigrants_frac": 0.15,
        "duplicate_avoidance": True,
        "stagnation_shake_gens": 60,
        "stagnation_restart_gens": 150,
        "adaptive_mutation": True,
        "init_mode": "nn_plus_random",
        "generations": 100000,   # peu importe, on coupe au temps
    }
    base_kwargs.update(fixed_kwargs)

    # Lancer les essais
    print(f"[Tuning] Paramètre: {args.param} | Valeurs: {values} | time/essai={args.time_sec:.1f}s | repeats={args.repeats}")
    if target:
        print(f"[Tuning] Cible (optimal): {target}")

    results: List[Dict[str, Any]] = []
    for v in values:
        costs: List[int] = []
        gaps: List[float] = []
        times: List[float] = []
        gens: List[int] = []
        routes_counts: List[int] = []

        for rep in range(args.repeats):
            seed = args.seed + rep
            res = run_trial(
                inst=inst,
                param_name=args.param,
                param_value=v,
                base_kwargs=base_kwargs,
                time_sec=args.time_sec,
                seed=seed,
                target=target,
            )
            costs.append(res["cost"])
            if res["gap"] is not None:
                gaps.append(res["gap"])
            times.append(res["elapsed_sec"] or float("nan"))
            gens.append(res["generations_done"] or 0)
            routes_counts.append(res["routes"])

            print(f"  - {args.param}={v} | rep {rep+1}/{args.repeats} | cost={res['cost']} | gap={res['gap'] if res['gap'] is not None else 'n/a'} | t={res['elapsed_sec']:.1f}s | gens={res['generations_done']}")

        # Agrégation
        best_cost = min(costs)
        avg_cost = sum(costs) / len(costs)
        best_gap = (min(gaps) if gaps else None)
        avg_gap = (sum(gaps) / len(gaps) if gaps else None)
        avg_time = sum(t for t in times if not math.isnan(t)) / max(1, sum(0 if math.isnan(t) else 1 for t in times))
        avg_gens = sum(gens) / len(gens)
        avg_routes = sum(routes_counts) / len(routes_counts)

        results.append({
            "value": v,
            "best_cost": best_cost,
            "avg_cost": avg_cost,
            "best_gap": best_gap,
            "avg_gap": avg_gap,
            "avg_time_sec": avg_time,
            "avg_generations": avg_gens,
            "avg_routes": avg_routes,
        })

    # Choix du gagnant
    def score_key(r: Dict[str, Any]) -> Tuple:
        # priorité: meilleur avg_gap (si dispo), sinon meilleur avg_cost
        if r["avg_gap"] is not None:
            return (r["avg_gap"], r["avg_cost"])
        return (float("inf"), r["avg_cost"])

    results.sort(key=score_key)
    best = results[0]
    print("\n=== Résumé ===")
    for r in results:
        print(f"{args.param}={r['value']} | avg_cost={r['avg_cost']:.1f} | best_cost={r['best_cost']} | avg_gap={r['avg_gap'] if r['avg_gap'] is not None else 'n/a'} | best_gap={r['best_gap'] if r['best_gap'] is not None else 'n/a'} | avg_time={r['avg_time_sec']:.1f}s | avg_gens={r['avg_generations']:.0f}")

    print("\n=== Meilleure valeur ===")
    print(f"{args.param}={best['value']} | avg_cost={best['avg_cost']:.1f} | avg_gap={best['avg_gap'] if best['avg_gap'] is not None else 'n/a'}")

    # CSV optionnel
    if args.save_csv:
        with open(args.save_csv, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["param", "value", "avg_cost", "best_cost", "avg_gap", "best_gap", "avg_time_sec", "avg_generations", "avg_routes"])
            for r in results:
                w.writerow([args.param, r["value"], r["avg_cost"], r["best_cost"], r["avg_gap"], r["best_gap"], r["avg_time_sec"], r["avg_generations"], r["avg_routes"]])
        print(f"[Save] Résultats écrits: {args.save_csv}")


if __name__ == "__main__":
    main()