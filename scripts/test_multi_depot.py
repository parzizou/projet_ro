# -*- coding: utf-8 -*-
"""
test_multi_depot.py
Tests d'optimisation de paramètres pour le mode multi-dépôts.

Ce script étend test.py pour supporter les paramètres spécifiques au multi-dépôt:
- k_depots: Nombre de dépôts (2-10)
- types_alphabet: Alphabet des types de dépôts ("AB", "ABC", "ABCD", etc.)
- capacity_override: Surcharge de la capacité des véhicules
- Tous les paramètres GA standards (pop_size, pm, pc, etc.)

Usage:
    # Test nombre de dépôts
    python scripts/test_multi_depot.py --instance data/instances/data.vrp --param k_depots --values 2,3,4,5 --repeats 3

    # Test types de dépôts
    python scripts/test_multi_depot.py --instance data/instances/data.vrp --param types_alphabet --values AB,ABC,ABCD --repeats 2

    # Test paramètres GA en mode multi-dépôt
    python scripts/test_multi_depot.py --instance data/instances/data.vrp --param ga_pop_size --values 20,40,60,80 --repeats 3 --fixed "k_depots=3,types_alphabet=ABC"
"""

from __future__ import annotations
import argparse
import csv
import math
import sys
import os
import time
from typing import Any, Dict, List, Optional, Tuple

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.cvrp_data import load_cvrp_instance, CVRPInstance
from scripts.multi_depot import (
    MultiDepotConfig,
    run_multi_depot_pipeline,
    build_multi_depot_scenario
)


# Types de paramètres supportés
_PARAM_TYPES: Dict[str, type] = {
    # Paramètres multi-dépôt
    "k_depots": int,
    "types_alphabet": str,
    "seed": int,
    "capacity_override": int,
    "connect_depot_on_plot": bool,
    # Paramètres GA (préfixés ga_)
    "ga_pop_size": int,
    "ga_pm": float,
    "ga_pc": float,
    "ga_two_opt_prob": float,
    "ga_time_limit_sec": float,
    "init_mode": str,
    "verbose_ga": bool,
}


def _coerce_val(val: str, typ: type) -> Any:
    """Convertit une valeur string selon son type."""
    if typ is bool:
        v = val.strip().lower()
        if v in ("1", "true", "t", "yes", "y", "on"):
            return True
        if v in ("0", "false", "f", "no", "n", "off"):
            return False
        raise ValueError(f"Valeur bool invalide: {val}")
    if typ is int:
        return int(float(val))
    if typ is float:
        return float(val)
    if val.strip().lower() == "none":
        return None
    return val.strip()


def _parse_values(spec: str, param_name: str) -> List[Any]:
    """
    Parse une spécification de valeurs:
    - Liste: "2,3,4,5"
    - Range: "2:10:2" (start:end:step)
    """
    typ = _PARAM_TYPES.get(param_name, str)

    def cast(x: str) -> Any:
        return _coerce_val(x, typ)

    if "," in spec:
        return [cast(x.strip()) for x in spec.split(",") if x.strip()]

    # Range numérique
    parts = [p.strip() for p in spec.split(":")]
    if len(parts) == 3 and typ in (int, float):
        start = float(parts[0])
        end = float(parts[1])
        step = float(parts[2])
        if step == 0:
            raise ValueError("Step ne peut pas être 0")
        
        vals = []
        current = start
        while (current <= end if step > 0 else current >= end):
            vals.append(cast(str(current)))
            current += step
        return vals

    # Valeur unique
    return [cast(spec)]


def _parse_fixed(fixed_str: str) -> Dict[str, Any]:
    """Parse les paramètres fixes: "k_depots=3,ga_pm=0.06,types_alphabet=ABC" """
    result = {}
    if not fixed_str.strip():
        return result
    
    for pair in fixed_str.split(","):
        pair = pair.strip()
        if not pair or "=" not in pair:
            continue
        key, val = pair.split("=", 1)
        key = key.strip()
        val = val.strip()
        
        typ = _PARAM_TYPES.get(key, str)
        result[key] = _coerce_val(val, typ)
    
    return result


def build_original_id_mapping(inst: CVRPInstance) -> List[int]:
    """Construit le mapping index -> ID original (pour les fichiers .sol)."""
    return list(range(inst.dimension))


def run_trial(
    inst: CVRPInstance,
    param_name: str,
    param_value: Any,
    base_config: MultiDepotConfig,
    base_ga_kwargs: Dict[str, Any],
    seed: int,
) -> Dict[str, Any]:
    """
    Lance un essai avec une valeur de paramètre spécifique.
    """
    # Copier les configs
    config = MultiDepotConfig(
        k_depots=base_config.k_depots,
        types_alphabet=base_config.types_alphabet,
        seed=seed,
        capacity_override=base_config.capacity_override,
        connect_depot_on_plot=False,  # Pas de plot pendant les tests
    )
    
    ga_kwargs = base_ga_kwargs.copy()
    
    # Appliquer la valeur du paramètre testé
    if param_name.startswith("ga_"):
        # Paramètre GA
        ga_key = param_name[3:]  # Enlever le préfixe "ga_"
        ga_kwargs[ga_key] = param_value
    else:
        # Paramètre multi-dépôt
        setattr(config, param_name, param_value)
    
    # Construire le label
    base_label = f"test_md_{param_name}_{param_value}"
    original_ids = build_original_id_mapping(inst)
    
    # Lancer le pipeline
    start_time = time.time()
    try:
        result = run_multi_depot_pipeline(
            inst_base=inst,
            original_id_from_baseindex=original_ids,
            base_label=base_label,
            cfg=config,
            ga_pop_size=ga_kwargs.get("pop_size", 40),
            ga_pm=ga_kwargs.get("pm", 0.06),
            ga_pc=ga_kwargs.get("pc", 0.50),
            ga_two_opt_prob=ga_kwargs.get("two_opt_prob", 0.6),
            init_mode=ga_kwargs.get("init_mode", "nn_plus_random"),
            verbose_ga=False,  # Pas de verbose pendant les tests
            do_plot=False,
            ga_time_limit_sec=ga_kwargs.get("time_limit_sec", 30.0),
        )
        elapsed = time.time() - start_time
        
        return {
            "cost": result["total_cost"],
            "elapsed_sec": elapsed,
            "depots_count": len(result["per_depot"]),
            "total_routes": sum(d["routes_count"] for d in result["per_depot"]),
            "success": True,
        }
    
    except Exception as e:
        print(f"  ❌ Erreur lors du test: {e}")
        return {
            "cost": float("inf"),
            "elapsed_sec": time.time() - start_time,
            "depots_count": 0,
            "total_routes": 0,
            "success": False,
        }


def main():
    parser = argparse.ArgumentParser(
        description="Test d'optimisation de paramètres pour le mode multi-dépôts"
    )
    parser.add_argument("--instance", required=True, help="Chemin vers le fichier .vrp")
    parser.add_argument(
        "--param",
        required=True,
        help="Paramètre à tester (ex: k_depots, types_alphabet, ga_pop_size, ga_pm, etc.)"
    )
    parser.add_argument(
        "--values",
        required=True,
        help="Valeurs à tester (ex: '2,3,4,5' ou '2:10:2')"
    )
    parser.add_argument(
        "--repeats",
        type=int,
        default=3,
        help="Nombre de répétitions par valeur (défaut: 3)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Seed de base pour la reproductibilité (défaut: 42)"
    )
    parser.add_argument(
        "--fixed",
        default="",
        help="Paramètres fixes (ex: 'k_depots=3,ga_pm=0.06')"
    )
    parser.add_argument(
        "--save-csv",
        help="Chemin du fichier CSV pour sauvegarder les résultats"
    )
    parser.add_argument(
        "--target",
        type=int,
        help="Coût optimal cible (pour calculer le gap - optionnel)"
    )
    
    args = parser.parse_args()
    
    # Charger l'instance
    print(f"\n📊 Chargement de l'instance: {args.instance}")
    inst = load_cvrp_instance(args.instance)
    print(f"   Instance: {inst.name}")
    print(f"   Dimension: {inst.dimension} nœuds ({inst.dimension - 1} clients)")
    print(f"   Capacité: {inst.capacity}")
    
    # Parser les valeurs à tester
    values = _parse_values(args.values, args.param)
    print(f"\n🔬 Paramètre à tester: {args.param}")
    print(f"   Valeurs: {values}")
    print(f"   Répétitions: {args.repeats}")
    
    # Parser les paramètres fixes
    fixed = _parse_fixed(args.fixed)
    if fixed:
        print(f"   Paramètres fixes: {fixed}")
    
    # Configuration de base
    base_config = MultiDepotConfig(
        k_depots=fixed.get("k_depots", 4),
        types_alphabet=fixed.get("types_alphabet", "ABCD"),
        seed=args.seed,
        capacity_override=fixed.get("capacity_override", None),
        connect_depot_on_plot=fixed.get("connect_depot_on_plot", False),
    )
    
    # Paramètres GA de base
    base_ga_kwargs = {
        "pop_size": fixed.get("ga_pop_size", 40),
        "pm": fixed.get("ga_pm", 0.06),
        "pc": fixed.get("ga_pc", 0.50),
        "two_opt_prob": fixed.get("ga_two_opt_prob", 0.6),
        "init_mode": fixed.get("init_mode", "nn_plus_random"),
        "time_limit_sec": fixed.get("ga_time_limit_sec", 30.0),
    }
    
    print(f"\n⚙️  Configuration de base:")
    print(f"   k_depots: {base_config.k_depots}")
    print(f"   types_alphabet: {base_config.types_alphabet}")
    print(f"   GA pop_size: {base_ga_kwargs['pop_size']}")
    print(f"   GA pm: {base_ga_kwargs['pm']}")
    print(f"   GA time_limit: {base_ga_kwargs['time_limit_sec']}s")
    
    # Lancer les tests
    print(f"\n🚀 Début des tests...")
    print("=" * 80)
    
    results: List[Dict[str, Any]] = []
    
    for v in values:
        print(f"\n📌 Test de {args.param}={v}")
        
        costs: List[float] = []
        times: List[float] = []
        routes_counts: List[int] = []
        successes: List[bool] = []
        
        for rep in range(args.repeats):
            seed = args.seed + rep
            
            res = run_trial(
                inst=inst,
                param_name=args.param,
                param_value=v,
                base_config=base_config,
                base_ga_kwargs=base_ga_kwargs,
                seed=seed,
            )
            
            costs.append(res["cost"])
            times.append(res["elapsed_sec"])
            routes_counts.append(res["total_routes"])
            successes.append(res["success"])
            
            status = "✅" if res["success"] else "❌"
            print(f"  {status} Répétition {rep+1}/{args.repeats} | "
                  f"Coût: {res['cost']:.0f} | "
                  f"Routes: {res['total_routes']} | "
                  f"Temps: {res['elapsed_sec']:.1f}s")
        
        # Calculer les statistiques
        valid_costs = [c for c, s in zip(costs, successes) if s and c != float("inf")]
        
        if valid_costs:
            best_cost = min(valid_costs)
            avg_cost = sum(valid_costs) / len(valid_costs)
            std_cost = (sum((c - avg_cost) ** 2 for c in valid_costs) / len(valid_costs)) ** 0.5
            
            # Calculer gap si target fourni
            gap = None
            if args.target:
                gap = ((avg_cost - args.target) / args.target) * 100
        else:
            best_cost = float("inf")
            avg_cost = float("inf")
            std_cost = 0
            gap = None
        
        avg_time = sum(times) / len(times)
        avg_routes = sum(routes_counts) / len(routes_counts)
        success_rate = sum(successes) / len(successes) * 100
        
        results.append({
            "value": v,
            "best_cost": best_cost,
            "avg_cost": avg_cost,
            "std_cost": std_cost,
            "gap": gap,
            "avg_time_sec": avg_time,
            "avg_routes": avg_routes,
            "success_rate": success_rate,
        })
    
    # Trier par meilleur coût moyen
    results.sort(key=lambda r: (r["avg_cost"], r["std_cost"]))
    
    # Afficher les résultats
    print("\n" + "=" * 80)
    print("📊 RÉSUMÉ DES RÉSULTATS")
    print("=" * 80)
    
    for r in results:
        gap_str = f"{r['gap']:+.2f}%" if r['gap'] is not None else "n/a"
        print(f"\n{args.param}={r['value']}")
        print(f"  Meilleur coût: {r['best_cost']:.0f}")
        print(f"  Coût moyen: {r['avg_cost']:.1f} ± {r['std_cost']:.1f}")
        if r['gap'] is not None:
            print(f"  Gap vs optimal: {gap_str}")
        print(f"  Routes moyennes: {r['avg_routes']:.1f}")
        print(f"  Temps moyen: {r['avg_time_sec']:.1f}s")
        print(f"  Taux de succès: {r['success_rate']:.0f}%")
    
    # Meilleure configuration
    best = results[0]
    print("\n" + "=" * 80)
    print("🏆 MEILLEURE CONFIGURATION")
    print("=" * 80)
    print(f"{args.param} = {best['value']}")
    print(f"Coût moyen: {best['avg_cost']:.1f}")
    if best['gap'] is not None:
        print(f"Gap: {best['gap']:+.2f}%")
    
    # Sauvegarder en CSV
    if args.save_csv:
        with open(args.save_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "param", "value", "best_cost", "avg_cost", "std_cost",
                "gap", "avg_time_sec", "avg_routes", "success_rate"
            ])
            for r in results:
                writer.writerow([
                    args.param, r["value"], r["best_cost"], r["avg_cost"],
                    r["std_cost"], r["gap"] if r["gap"] is not None else "",
                    r["avg_time_sec"], r["avg_routes"], r["success_rate"]
                ])
        print(f"\n💾 Résultats sauvegardés: {args.save_csv}")


if __name__ == "__main__":
    main()
