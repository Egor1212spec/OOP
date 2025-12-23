import re
from collections import defaultdict

def get_node_profile(node, adj, weighted):
    deg = len(adj[node])
    neighbor_degs = sorted([len(adj[n]) for n in adj[node]])
    
    if not weighted:
        return (deg, tuple(neighbor_degs))
    
    weights = sorted(adj[node].values())
    complex_w = sorted([(adj[node][n], len(adj[n])) for n in adj[node]])
    return (deg, tuple(neighbor_degs), tuple(weights), tuple(complex_w))

def find_mapping(g_data, t_data, is_w):
    g_nodes = sorted(g_data.keys())
    t_nodes = sorted(t_data.keys())
    
    g_sigs = {u: get_node_profile(u, g_data, is_w) for u in g_nodes}
    t_sigs = {v: get_node_profile(v, t_data, is_w) for v in t_nodes}
    
    possibilities = {}
    for u in g_nodes:
        matches = {v for v in t_nodes if t_sigs[v] == g_sigs[u]}
        if not matches:
            return []
        possibilities[u] = matches
        
    search_order = sorted(g_nodes, key=lambda n: len(possibilities[n]))
    results = []
    
    def walker(idx, current_map, used_vals):
        if idx == len(search_order):
            results.append(current_map.copy())
            return

        u = search_order[idx]
        options = sorted(list(possibilities[u] - used_vals))
        
        for v in options:
            valid = True
            for existing_u, existing_v in current_map.items():
                if existing_u in g_data[u]:
                    if existing_v not in t_data[v]:
                        valid = False
                        break
                    if is_w and g_data[u][existing_u] != t_data[v][existing_v]:
                        valid = False
                        break
                elif existing_v in t_data[v]:
                    pass 
            
            if valid:
                current_map[u] = v
                used_vals.add(v)
                walker(idx + 1, current_map, used_vals)
                used_vals.remove(v)
                del current_map[u]

    walker(0, {}, set())
    return results

def process_table(raw_data, weighted):
    lines = [l.strip() for l in raw_data.strip().split('\n') if l.strip()]
    if not lines:
        raise ValueError("Empty table data")
        
    size = len(lines)
    adj = defaultdict(dict)
    all_weights = []
    
    for r, row_str in enumerate(lines):
        vals = row_str.split()
        if len(vals) != size:
            vals = [0] * size 
            
        for c, val in enumerate(vals):
            if c <= r: continue
            
            cost = 0
            if val.isdigit():
                cost = int(val)
            
            if cost > 0:
                adj[r+1][c+1] = cost if weighted else 1
                adj[c+1][r+1] = cost if weighted else 1
                all_weights.append(cost)
                
    return adj, sorted(all_weights)

def process_graph_text(text, weighted):
    adj = defaultdict(dict)
    nodes = set()
    collected_weights = []
    seen_edges = {}
    
    for line in text.split('\n'):
        clean = re.sub(r'[^\w\d\s-]', ' ', line.upper()).strip()
        if not clean: continue
        
        tokens = re.split(r'[\s-]+', clean)
        tokens = [t for t in tokens if t]
        
        if not tokens: continue
        
        if len(tokens) == 1:
            nodes.add(tokens[0])
            continue
            
        if len(tokens) >= 2:
            u, v = tokens[0], tokens[1]
            w = 1
            if weighted and len(tokens) > 2 and tokens[-1].isdigit():
                w = int(tokens[-1])
            
            if u == v: continue
            
            pair = tuple(sorted((u, v)))
            if pair in seen_edges and seen_edges[pair] != w:
                raise ValueError(f"Conflict in edge weights for {u}-{v}")
            
            seen_edges[pair] = w
            adj[u][v] = w
            adj[v][u] = w
            nodes.add(u)
            nodes.add(v)
            if weighted:
                collected_weights.append(w)

    for n in nodes:
        if n not in adj:
            adj[n] = {}
            
    return adj, sorted(list(nodes)), sorted(collected_weights)

def solve(mat_in, graph_in, targets_in, use_weights=True):
    try:
        t_adj, t_weights = process_table(mat_in, use_weights)
        g_adj, g_nodes, g_weights = process_graph_text(graph_in, use_weights)
        
        req_nodes = [x.strip().upper() for x in re.split(r'[\s,;]+', targets_in) if x.strip()]
        
        if len(t_adj) != len(g_nodes):
            return f"Size mismatch: Table={len(t_adj)}, Graph={len(g_nodes)}"
            
        if use_weights and t_weights != g_weights:
            return f"Weights mismatch.\nTable: {t_weights}\nGraph: {g_weights}"
            
        solutions = find_mapping(g_adj, t_adj, use_weights)
        
        if not solutions:
            return "No isomorphism found."
            
        final_set = set()
        for sol in solutions:
            for r in req_nodes:
                if r in sol:
                    final_set.add(sol[r])
        
        if not final_set:
            return "Targets not found in solution."
            
        return "".join(str(x) for x in sorted(final_set))

    except Exception as e:
        return f"Error: {str(e)}"