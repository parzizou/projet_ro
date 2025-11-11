# -*- coding: utf-8 -*-
"""
plot.py
Affichage graphique d'une solution CVRP:
- Couleurs fortes (haute visibilité) pour routes et dépôts
"""

from __future__ import annotations
from typing import List, Optional, Dict, Tuple

from cvrp_data import CVRPInstance


# Palette de couleurs fortes (éviter les tons proches du blanc)
STRONG_COLORS = [
    "#1f77b4",  # blue
    "#d62728",  # red
    "#2ca02c",  # green
    "#ff7f0e",  # orange
    "#9467bd",  # purple
    "#e377c2",  # pink
    "#17becf",  # cyan
    "#000000",  # black
    "#bcbd22",  # yellow/olive
    "#8c564b",  # brown
]


def _color_cycle(k: int) -> str:
    return STRONG_COLORS[k % len(STRONG_COLORS)]


def plot_solution(
    inst: CVRPInstance,
    routes: List[List[int]],
    title: Optional[str] = None,
    save_path: Optional[str] = None,
    show: bool = True,
    annotate: bool = False,
    dpi: int = 120,
    connect_depot: bool = False,  # par défaut False, pour ne pas tracer vers le dépôt
) -> None:
    """
    Affiche la solution mono-dépôt avec couleurs fortes.
    """
    try:
        import matplotlib.pyplot as plt
        from matplotlib.lines import Line2D
    except Exception as e:
        raise ImportError(
            "matplotlib n'est pas installé. Installe-le avec: pip install matplotlib"
        ) from e

    coords = inst.coords
    depot = inst.depot_index

    fig, ax = plt.subplots(figsize=(10, 8))

    # Clients
    xs_clients = [coords[i][0] for i in range(inst.dimension) if i != depot]
    ys_clients = [coords[i][1] for i in range(inst.dimension) if i != depot]
    ax.scatter(xs_clients, ys_clients, c="#666666", s=18, label="Clients", zorder=2)

    # Dépôt
    x0, y0 = coords[depot]
    ax.scatter([x0], [y0], marker="*", c="#000000", s=220, edgecolors="white", linewidths=1.2, label="Dépôt", zorder=5)

    # Tracé des routes
    handles = []
    for k, r in enumerate(routes, start=1):
        if not r:
            continue
        col = _color_cycle(k - 1)

        # Points de la route
        rx = [coords[i][0] for i in r]
        ry = [coords[i][1] for i in r]
        ax.scatter(rx, ry, c=[col], s=28, zorder=6, edgecolors="white", linewidths=0.8)

        if connect_depot:
            seq = [depot] + r + [depot]
            xs = [coords[i][0] for i in seq]
            ys = [coords[i][1] for i in seq]
            ax.plot(xs, ys, "-", color=col, linewidth=2.6, alpha=0.95, zorder=4)
        else:
            if len(r) >= 2:
                xs = [coords[i][0] for i in r]
                ys = [coords[i][1] for i in r]
                ax.plot(xs, ys, "-", color=col, linewidth=2.6, alpha=0.95, zorder=4)

        # Label route
        x_first, y_first = coords[r[0]]
        ax.text(x_first, y_first, f"  R{k}", fontsize=9, color=col, va="center", zorder=7)

        handles.append(Line2D([0], [0], color=col, lw=3.0, label=f"Route {k}"))

        if annotate:
            for idx in r:
                xi, yi = coords[idx]
                ax.text(xi, yi, f"{idx}", fontsize=7, color="#000000", zorder=7)

    # Esthétique
    ax.set_aspect("equal", adjustable="datalim")
    ax.grid(True, linestyle="--", alpha=0.25)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")

    if title:
        ax.set_title(title)

    base_handles, _ = ax.get_legend_handles_labels()
    all_handles = base_handles + handles
    if len(handles) <= 16:
        ax.legend(handles=all_handles, loc="best", fontsize=9)
    else:
        ax.legend(handles=all_handles, bbox_to_anchor=(1.04, 1), loc="upper left", fontsize=9)

    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=dpi, bbox_inches="tight")
        print(f"[Plot] Image sauvegardée: {save_path}")

    if show:
        plt.show()
    else:
        plt.close(fig)


def plot_solution_multi(
    inst: CVRPInstance,
    depots: List[Tuple[int, Tuple[float, float], str]],   # (depot_idx, (x,y), type_char)
    routes_by_depot: Dict[int, List[List[int]]],          # routes en indices "base" (sans dépôt)
    title: Optional[str] = None,
    save_path: Optional[str] = None,
    show: bool = True,
    annotate: bool = False,
    dpi: int = 120,
    connect_depot: bool = False,
) -> None:
    """
    Tracé multi-dépôts avec couleurs fortes:
    - inst: instance base (coords clients)
    - depots: liste (id, coord, type) générés (incluant le dépôt A d'origine)
    - routes_by_depot: dict depot_id -> routes (indices base)
    - connect_depot: si True, trace dépôt->clients->dépôt pour chaque route du dépôt associé
    """
    try:
        import matplotlib.pyplot as plt
        from matplotlib.lines import Line2D
    except Exception as e:
        raise ImportError(
            "matplotlib n'est pas installé. Installe-le avec: pip install matplotlib"
        ) from e

    coords = inst.coords
    depot_base = inst.depot_index

    fig, ax = plt.subplots(figsize=(10, 8))

    # Clients (gris foncé pour contraste)
    xs_clients = [coords[i][0] for i in range(inst.dimension) if i != depot_base]
    ys_clients = [coords[i][1] for i in range(inst.dimension) if i != depot_base]
    ax.scatter(xs_clients, ys_clients, c="#777777", s=16, label="Clients", zorder=1)

    # Dépôt base (référence, étoile noire)
    xb, yb = coords[depot_base]
    ax.scatter([xb], [yb], marker="*", c="#000000", s=180, edgecolors="white", linewidths=1.1, label="Dépôt base", zorder=3)

    # Dépôts générés
    depot_handles = []
    for d_order, (did, (dx, dy), t) in enumerate(depots):
        col = _color_cycle(d_order)
        ax.scatter([dx], [dy], marker="P", c=[col], s=180, edgecolors="white", linewidths=1.0, zorder=4)
        ax.text(dx, dy, f" d{did}({t})", fontsize=9, color=col, va="bottom", zorder=6)
        depot_handles.append(Line2D([0], [0], color=col, lw=0, marker="P", markersize=10, label=f"d{did} ({t})"))

    # Routes par dépôt
    for d_order, (did, (dx, dy), _t) in enumerate(depots):
        routes = routes_by_depot.get(did, [])
        if not routes:
            continue
        col = _color_cycle(d_order)
        for r in routes:
            if not r:
                continue
            rx = [coords[i][0] for i in r]
            ry = [coords[i][1] for i in r]
            ax.scatter(rx, ry, c=[col], s=24, zorder=5, edgecolors="white", linewidths=0.8)

            if connect_depot:
                xs = [dx] + rx + [dx]
                ys = [dy] + ry + [dy]
                ax.plot(xs, ys, "-", color=col, linewidth=2.4, alpha=0.95, zorder=3)
            else:
                if len(r) >= 2:
                    ax.plot(rx, ry, "-", color=col, linewidth=2.4, alpha=0.95, zorder=3)

            if annotate:
                for i in r:
                    xi, yi = coords[i]
                    ax.text(xi, yi, f"{i}", fontsize=7, color=col, zorder=6)

    ax.set_aspect("equal", adjustable="datalim")
    ax.grid(True, linestyle="--", alpha=0.25)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    if title:
        ax.set_title(title)

    base_handles, _ = ax.get_legend_handles_labels()
    all_handles = base_handles + depot_handles
    ax.legend(handles=all_handles, loc="best", fontsize=9)

    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=dpi, bbox_inches="tight")
        print(f"[Plot] Image sauvegardée: {save_path}")

    if show:
        plt.show()
    else:
        plt.close(fig)