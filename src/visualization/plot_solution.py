# -*- coding: utf-8 -*-
"""
plot.py
Affichage graphique d'une solution CVRP:
- Les clients sont des points.
- Le dépôt est une étoile.
- Chaque tournée est tracée en couleur différente.
- Par défaut, on N'AFFICHE PAS les segments reliant au dépôt (moins de traits au même endroit).
- Possibilité d'afficher à l'écran et/ou de sauvegarder en image.

Dépendance: matplotlib
"""

from __future__ import annotations
from typing import List, Optional

from cvrp_data import CVRPInstance


def plot_solution(
    inst: CVRPInstance,
    routes: List[List[int]],
    title: Optional[str] = None,
    save_path: Optional[str] = None,
    show: bool = True,
    annotate: bool = False,
    dpi: int = 120,
    connect_depot: bool = False,  # nouveau: par défaut False, pour ne pas tracer vers le dépôt
) -> None:
    """
    Affiche la solution:
    - inst: instance CVRPInstance
    - routes: liste de routes (indices internes, sans le dépôt)
    - title: titre du graphique
    - save_path: chemin d'image (ex: 'solution.png') si tu veux sauvegarder
    - show: True pour afficher la figure (plt.show)
    - annotate: True pour ajouter des numéros de clients (peut surcharger)
    - dpi: résolution en sauvegarde
    - connect_depot: si True, trace aussi dépôt->premier et dernier->dépôt (par défaut False)

    Remarque: si matplotlib est manquant, on lève une ImportError claire.
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

    # Prépare la palette de couleurs
    cmap = plt.get_cmap("tab20")
    def route_color(k: int):
        # tab20 a 20 couleurs distinctes; si + de 20 routes, on boucle
        return cmap(k % 20)

    # Figure
    fig, ax = plt.subplots(figsize=(10, 8))

    # Scatter des clients (tous sauf dépôt) - gris clair par défaut
    xs_clients = [coords[i][0] for i in range(inst.dimension) if i != depot]
    ys_clients = [coords[i][1] for i in range(inst.dimension) if i != depot]
    ax.scatter(xs_clients, ys_clients, c="#999999", s=16, label="Clients", zorder=2)

    # Dépôt
    x0, y0 = coords[depot]
    ax.scatter([x0], [y0], marker="*", c="red", s=180, edgecolors="k", linewidths=0.8, label="Dépôt", zorder=4)

    # Tracé des routes
    handles = []
    for k, r in enumerate(routes, start=1):
        if not r:
            continue
        col = route_color(k - 1)

        # Colorer aussi les points de la route
        rx = [coords[i][0] for i in r]
        ry = [coords[i][1] for i in r]
        ax.scatter(rx, ry, c=[col], s=24, zorder=5, edgecolors="k", linewidths=0.4)

        if connect_depot:
            # Séquence complète avec dépôt
            seq = [depot] + r + [depot]
            xs = [coords[i][0] for i in seq]
            ys = [coords[i][1] for i in seq]
            ax.plot(xs, ys, "-", color=col, linewidth=2.0, alpha=0.9, zorder=3)
        else:
            # Ne tracer QUE les segments entre clients, pas ceux avec le dépôt
            if len(r) >= 2:
                xs = [coords[i][0] for i in r]
                ys = [coords[i][1] for i in r]
                ax.plot(xs, ys, "-", color=col, linewidth=2.0, alpha=0.95, zorder=3)

        # Marquer la route près de son premier client
        x_first, y_first = coords[r[0]]
        ax.text(x_first, y_first, f"  R{k}", fontsize=8, color=col, va="center", zorder=6)

        # Légende par route
        handles.append(Line2D([0], [0], color=col, lw=3, label=f"Route {k}"))

        if annotate:
            # Numérotation des clients le long de la route
            for idx in r:
                xi, yi = coords[idx]
                ax.text(xi, yi, f"{idx}", fontsize=6, color="#333333", zorder=6)

    # Esthétique
    ax.set_aspect("equal", adjustable="datalim")
    ax.grid(True, linestyle="--", alpha=0.25)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")

    if title:
        ax.set_title(title)

    # Légende globale
    base_handles, base_labels = ax.get_legend_handles_labels()
    all_handles = base_handles + handles
    if len(handles) <= 20:
        ax.legend(handles=all_handles, loc="best", fontsize=8)
    else:
        ax.legend(handles=all_handles, bbox_to_anchor=(1.04, 1), loc="upper left", fontsize=8)

    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=dpi, bbox_inches="tight")
        print(f"[Plot] Image sauvegardée: {save_path}")

    if show:
        plt.show()
    else:
        plt.close(fig)