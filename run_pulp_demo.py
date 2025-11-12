"""
run_pulp_demo.py
1. loads a simplified MDVRP instance from .vrp file.
2. simulates parameters for constraints
3. builds a PuLP MIP model for MDVRP with split deliveries and compatibility constraints within a limited time.
4. solves the model with the CBC solver within a time limit.
5. prints the solution routes per vehicle with remaining load at each step.

"""

import pulp    
import re      # regex-string splitting
import math    
import sys     
import time    # timer


# Configuration
# =========================================================================
# switch dataset
# FILE_TO_SOLVE = "p01.vrp" / "p03_test.vrp"
FILE_TO_SOLVE = "p03_test.vrp" 

# Solver time limit(beta)
TIME_LIMIT_SECONDES = 36000  # secondes - 10 hours

#simulated parameters
VEHICULE_COUNT = None # number of vehicles available, will be set after loading instance
# static product types for depots and orders (for compatibility constraints)
PRODUCT_TYPES = ["Type_A", "Type_B", "Type_C"]

# Solution optimized printer
def print_results(K, home_depot, N, C, demands, capacite_Q, x):
    """
    K3: 1->4(27)->7(9)->1   (node(remaining load after serving commande))
    """
    print("\nRoutes for each vehicle (load remain) \n============")
    # collect active arcs per vehicle and incoming arcs
    arcs_by_k = {k: {} for k in K}
    incoming_by_k = {k: set() for k in K}
    for i in N:
        for j in N:
            if i == j:
                continue
            for k in K:
                try:
                    val = pulp.value(x[i][j][k])
                except Exception:
                    val = None
                if val is not None and val > 0.5:
                    arcs_by_k[k][i] = j
                    incoming_by_k[k].add(j)

    for k in K:
        outgoing = arcs_by_k.get(k, {})
        home = home_depot.get(k, None)
        if not outgoing:
            print(f"{k}: not used")
            continue

        # find start nodes (outgoing node with no incoming), fallback to home or any outgoing key
        starts = [n for n in outgoing.keys() if n not in incoming_by_k.get(k, set())]
        if not starts:
            starts = [home] if home in outgoing or home is not None else [next(iter(outgoing.keys()))]

        # if multiple disjoint paths, print each
        routes_strs = []
        for start in starts:
            cur = start
            load = capacite_Q
            visited = set([cur])
            seq = [cur]
            rem_after = []  # remaining loads after serving customers in seq order
            while True:
                nxt = outgoing.get(cur)
                if nxt is None:
                    break
                # if next is customer, reduce load
                if nxt in C:
                    d = demands.get(nxt, 0)
                    load -= d
                    rem_after.append(load)
                seq.append(nxt)
                cur = nxt
                if cur in visited:
                    break
                visited.add(cur)

            # build annotated sequence: customers annotated with remaining load
            rem_iter = iter(rem_after)
            annotated = []
            for node in seq:
                if node in C:
                    try:
                        r = next(rem_iter)
                        annotated.append(f"{node}({r})")
                    except StopIteration:
                        annotated.append(str(node))
                else:
                    annotated.append(str(node))
            routes_strs.append("->".join(annotated) if annotated else "empty")

        # join multiple routes by " | "
        print(f"{k}: " + " | ".join(routes_strs))
    print("============\nEnd")








# =========================================================================
# 1：MDVRP Loader
# =========================================================================

def nint(x):
    return int(x + 0.5) # Rounder for distances


def calc_dist_matrix(coords):
    """
    translate the coordinates dict into a distance matrix:
    treated rounded Euclidean distances between all pairs of nodes.
    return distances[i][j] = int_distance between node i and j
    zero distance for i==j
    """
    dist_matrix = {}
    node_ids = sorted(coords.keys()) # get sorted list of node ids
    for i in node_ids:
        dist_matrix[i] = {} # initialize sub-dictionary
        for j in node_ids:
            if i == j:
                dist_matrix[i][j] = 0 # zero distance to self
            else:
                (x1, y1) = coords[i] # get coordinates
                (x2, y2) = coords[j]
                # rounded Euclidean distance
                dist_matrix[i][j] = nint(math.sqrt((x1 - x2)**2 + (y1 - y2)**2))
    return dist_matrix


def load_mdvrp_instance(file_path):
    """
    load .vrp file from CVRPLIB-like format for MDVRP demo.

    classify data into sections:
      - CAPACITY: global vehicle capacity
      - NODE_COORD_SECTION: node coordinates (id x y)
      - DEMAND_SECTION: node demands (id demand)
      - DEPOT_SECTION: depot node ids (one per line, -1 terminates)

    return:
      depots: list[int]         # depot node ids
      commandes: list[int]      # commandes node ids(only clients with demand>0)
      all_nodes: list[int]      # depots + commandes(all nodes involved)
      distances: dict           # distances[i][j] = int_distance between node i and j(returned by calc_dist_matrix)
      demands: dict             # demands[node_id] = int
      capacity: int             # vehicle capacity

    Errors will raise exceptions to exit.
    """
    print(f"Loading instance: {file_path} ...")
    coords = {}
    demands = {}
    depot_ids = []
    capacity = 0

    with open(file_path, 'r') as f: 
        section = None # section tracker
        for line in f:
            line = line.strip()

            if "CAPACITY" in line:
                capacity = int(line.split(":")[-1].strip())
            elif "NODE_COORD_SECTION" in line:
                section = "COORDS"; continue
            elif "DEMAND_SECTION" in line:
                section = "DEMANDS"; continue
            elif "DEPOT_SECTION" in line:
                section = "DEPOTS"; continue
            elif "EOF" in line:
                break

            if section == "COORDS":
                parts = re.split(r'\s+', line) # split by whitespace
                if not parts[0].isdigit():
                    continue # skip non-data lines
                node_id = int(parts[0])
                coords[node_id] = (float(parts[1]), float(parts[2]))
            elif section == "DEMANDS":
                parts = re.split(r'\s+', line)
                if not parts[0].isdigit():
                    continue
                node_id = int(parts[0])
                demands[node_id] = int(parts[1])
            elif section == "DEPOTS":
                node_id_str = line.split()[0]
                if not node_id_str.isdigit():
                    continue
                node_id = int(node_id_str)
                if node_id != -1:
                    depot_ids.append(node_id)

    if not coords or not demands or not depot_ids:
        raise ValueError("Field parsing error: missing coords/demands/depots data.")
    
    # construct depots and commandes lists
    depots = [] 
    commandes = []
    for node_id in coords:
        if node_id in depot_ids:
            depots.append(node_id)
        elif demands.get(node_id, 0) > 0:
            commandes.append(node_id)

    # construct all_nodes list and distance matrix
    all_nodes = depots + commandes
    distances = calc_dist_matrix(coords)

    print(f"Complited: {len(depots)} depots, {len(commandes)} commandes loaded.")
    return depots, commandes, all_nodes, distances, demands, capacity


# Step A：Pre-processing & Parameter Simulation
# =========================================================================

# 1. Load data/ Exit if file not found
try:
    ''''''
    D, C, N, distances, demands, capacite_Q = load_mdvrp_instance(FILE_TO_SOLVE) 
    # returns depots, commandes, all_nodes, distances, demands, capacity to variables
except FileNotFoundError:
    print(f"Error, failed to find '{FILE_TO_SOLVE}'。")
    sys.exit(1)

# Stimulation of parameters for constraints 2 & 3(assume that we've done the separation of commandes in C)

# a. defination of K and M
# vehicle count setting, round up x = 1.5 times of depot count
if VEHICULE_COUNT is None:
    VEHICULE_COUNT = max(1, math.ceil(1.5 * len(D)))
    print(f"Auto-set VEHICULE_COUNT = {VEHICULE_COUNT} (1.5 * num depots = {1.5 * len(D)})")

# vehicle id list K and big M for MTZ
K = [f"K{i}" for i in range(VEHICULE_COUNT)]
M = capacite_Q # Define a "big M" constant for MTZ constraints

# b. Stimulation of parameters
# Assign evenly vehicles to depots（home_depot: vehicle -> mother depot）
home_depot = {}
for i, k in enumerate(K):
    home_depot[k] = D[i % len(D)]  # assign vehicle k to depot in turn(if vehicles > depots, wrap around)

# Stimulate product types for depots and commandes
type_depot = {}
for i, d in enumerate(D):
    type_depot[d] = PRODUCT_TYPES[i % len(PRODUCT_TYPES)]

type_commande = {}
for i, j in enumerate(C):
    type_commande[j] = PRODUCT_TYPES[i % len(PRODUCT_TYPES)]

# Capability matrix for compatibility constraints (compatibilite_P[j][k] = 1 if vehicle k can serve order j, else 0)
compatibilite_P = {}
for j in C:
    compatibilite_P[j] = {}
    for k in K:
        depot_du_vehicule = home_depot[k]
        if type_commande.get(j) == type_depot.get(depot_du_vehicule):
            compatibilite_P[j][k] = 1
        else:
            compatibilite_P[j][k] = 0

print(f"Parameter Stimulation Complited：{len(K)} vehicules was assigned to {len(D)} depots.")

# Step B：PuLP MIP Model Construction for MDVRP
# =========================================================================

print(f"Consructing PuLP Model (N={len(N)}, C={len(C)}, K={len(K)}) ...")
start_build_time = time.time() # timer start

# create the PuLP instance for distance cost minimization
prob = pulp.LpProblem("MD_VRPSC_MIP_Demo", pulp.LpMinimize)

# a. decision variables
# 3d dict: x[i][j][k] = 1, if vehicle k travels from node i to j, else 0
# continuous dict: u[j][k] = cumulative load of vehicle k after serving order j, for MTZ subtour elimination
x = pulp.LpVariable.dicts("x", (N, N, K), cat=pulp.LpBinary)
u = pulp.LpVariable.dicts("u", (C, K), lowBound=0, upBound=capacite_Q, cat=pulp.LpContinuous)

# b. objective function
# Minimize total traveled distance over all vehicles and arcs for i != j
prob += pulp.lpSum(
    distances[i][j] * x[i][j][k]
    for i in N for j in N for k in K if i != j # exclude self-loops
), "Minimiser_Distance_Totale"

# c. constraints
'''vehicle logic'''
# 1. Every commande j is served exactly once by some vehicle k, make sure each order is served and only once
for j in C:
    prob += pulp.lpSum(x[i][j][k] for i in N for k in K if i != j) == 1, f"Service_Commande_{j}"


# 2. Make sure the continuity of flow for each commande j and vehicle k
for j in C:
    for k in K:
        prob += (pulp.lpSum(x[i][j][k] for i in N if i != j) - pulp.lpSum(x[j][l][k] for l in N if l != j)) == 0, f"Flux_{j}_{k}"

# 3. Every vehicle k departs from its home depot at most once
for k in K:
    prob += pulp.lpSum(x[home_depot[k]][j][k] for j in C) <= 1, f"Depart_{k}"

# 4. Every vehicle k returns to its home depot at most once
for k in K:
    prob += (pulp.lpSum(x[home_depot[k]][j][k] for j in C) - pulp.lpSum(x[i][home_depot[k]][k] for i in C)) == 0, f"Retour_{k}"

# 5. MTZ subtour elimination & capacity constraints
#    for i != j, each k habe: u_jk <= u_ik - demand[j] + M * (1 - x_i_j_k)
#    if vehicle k travels from i to j (x[i][j][k]==1), then: u[j][k] <= u[i][k] - demand[j]
#    if x[i][j][k]==0, the constraint is relaxed by M
#    complexity: O(|C|^2 * |K|) -- O(pow(n,2))
print("Processing MTZ...")
for i in C:
    for j in C:
        if i != j:
            for k in K:
                prob += (u[j][k] <= u[i][k] - demands[j] + M * (1 - x[i][j][k])), f"MTZ_{i}_{j}_{k}"

# 6. Capacity bound constraints with MTZ
#    if vehicle k goes directly from its home depot to order j (x[home_depot[k]][j][k]==1), then:
#    u[j][k] <= Q - demand[j] + M * (1 - x[home_depot[k]][j][k])
#    ensures that initial load after first delivery does not exceed capacity
for j in C:
    for k in K:
        prob += u[j][k] <= capacite_Q - demands[j] + M * (1 - x[home_depot[k]][j][k]), f"Borne_Initiale_{j}_{k}"

# 7. Compatibility constraints
#    for each commande j and vehicle k, if vehicle k cannot serve j (Matrix compatibilite_P[j][k]==0),
#    ∑_i x[i][j][k] <= compatibilite_P[j][k] （if compatibilite_P[j][k]==0, then ∑_i x[i][j][k] <= 0）
for j in C:
    for k in K:
        prob += (pulp.lpSum(x[i][j][k] for i in N if i != j) <= compatibilite_P[j][k]), f"Compatibilite_{j}_{k}"

# 8. Enforce u[j][k] to be zero if vehicle k does not serve commande j
for j in C:
    for k in K:
        prob += u[j][k] <= capacite_Q * pulp.lpSum(x[i][j][k] for i in N if i != j), f"Bind_u_active_{j}_{k}"

# 9. Forbid vehicles from departing from non-home depots
for k in K:
    for d in D:
        if d != home_depot[k]:
            # no outgoing arc from depot d for vehicle k
            prob += pulp.lpSum(x[d][j][k] for j in N if j != d) == 0, f"OnlyHomeDepart_{k}_{d}"

end_build_time = time.time() # timer end
print(f"Modeling success in: {end_build_time - start_build_time:.2f} seconds.")

# Step C：Solving with PuLP & Logging
# =========================================================================
print(f"Start Solving ...")

# set CBC solver with time limit(beta)
solver = pulp.PULP_CBC_CMD(msg=False, timeLimit=TIME_LIMIT_SECONDES)
start_solve_time = time.time()
prob.solve(solver)  # Solving
end_solve_time = time.time()

print(f"\nEnd of Solving.")
used_time = end_solve_time - start_solve_time
print(f"Total time consumption: {used_time:.2f} seconds.")

# Step D：Results Status extractions
# =========================================================================
status = pulp.LpStatus[prob.status]
print(f"Solver Status: {status}")

# if time limit reached and no feasible/optimal solution, print the requested message
if used_time >= TIME_LIMIT_SECONDES - 1 and status not in ("Optimal", "Feasible"):
    print(f"Failed to find the solution in: {TIME_LIMIT_SECONDES} seconds time limit.")

if status not in ("Optimal", "Feasible"):
    prob.writeLP("debug_model.lp")
    sys.exit("No feasible solution found.")
else:
    # simple, clear output
    print_results(K, home_depot, N, C, demands, capacite_Q, x)

