import pickle
import json
import math
from pathlib import Path

import networkx as nx


class GraphAPI:
    def __init__(self):
        self._cache: dict[str, nx.Graph] = {}

    def _load(self, city_id: str) -> nx.Graph:
        if city_id not in self._cache:
            p = Path("outputs") / city_id / "healed_graph.gpickle"
            if not p.exists():
                raise FileNotFoundError(f"No graph for {city_id}")
            with open(p, "rb") as f:
                self._cache[city_id] = pickle.load(f)
        return self._cache[city_id]

    def reroute(self, city_id: str, src, dst, disabled_nodes: list):
        G = self._load(city_id)
        H = G.copy()
        for n in disabled_nodes:
            if H.has_node(n):
                H.remove_node(n)
        try:
            path = nx.shortest_path(H, src, dst, weight="length")
            length = nx.shortest_path_length(H, src, dst, weight="length")
            return [int(n) for n in path], float(length)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return [], None

    def disable_node(self, city_id: str, node_id):
        G = self._load(city_id)
        if not G.has_node(node_id):
            return {"error": "node not found"}
        H = G.copy()
        H.remove_node(node_id)
        comps = list(nx.connected_components(H))
        lcc = max(len(c) for c in comps) if comps else 0
        return {
            "node_id": node_id,
            "components_after": len(comps),
            "lcc_fraction": round(lcc / max(G.number_of_nodes(), 1), 4),
            "isolated_nodes": sum(1 for c in comps if len(c) == 1),
        }

    def run_scenario(self, city_id: str, scenario_type: str, params: dict):
        from src.graph.dem import flood_scenario
        from src.graph.criticality import global_efficiency

        G = self._load(city_id)

        if scenario_type == "flood":
            threshold = params.get("elevation_threshold_m", 10.0)
            G_damaged = flood_scenario(G, threshold)
        elif scenario_type == "earthquake":
            lat = params.get("lat", 0)
            lon = params.get("lon", 0)
            radius_m = params.get("radius_m", 500)
            remove = []
            for n, d in G.nodes(data=True):
                dlat = d.get("lat", 0) - lat
                dlon = d.get("lon", 0) - lon
                dist_m = math.sqrt(
                    (dlat * 111000) ** 2
                    + (dlon * 111000 * math.cos(math.radians(lat))) ** 2
                )
                if dist_m <= radius_m:
                    remove.append(n)
            G_damaged = G.copy()
            for n in remove:
                G_damaged.remove_node(n)
        elif scenario_type == "collapse":
            node_ids = params.get("node_ids", [])
            G_damaged = G.copy()
            for n in node_ids:
                if G_damaged.has_node(n):
                    G_damaged.remove_node(n)
        else:
            return {"error": f"unknown scenario type: {scenario_type}"}

        # Normalize both by the original node count so resilience stays in [0,1]:
        # removing nodes can only reduce retained efficiency, never inflate it.
        n0 = G.number_of_nodes()
        base_eff = global_efficiency(G, norm_n=n0)
        damaged_eff = global_efficiency(G_damaged, norm_n=n0)
        ri = damaged_eff / base_eff if base_eff > 0 else 0.0

        comps = list(nx.connected_components(G_damaged))
        lcc = max(len(c) for c in comps) if comps else 0
        flood_critical = (
            [
                n
                for n, d in G_damaged.nodes(data=True)
                if d.get("flood_vulnerable") and d.get("zone") == "critical"
            ]
            if scenario_type == "flood"
            else []
        )

        disabled_nodes = list(set(G.nodes()) - set(G_damaged.nodes()))

        return {
            "scenario": scenario_type,
            "nodes_disabled": len(disabled_nodes),
            "disabled_ids": disabled_nodes[:100],
            "resilience_index": round(ri, 4),
            "lcc_fraction": round(lcc / max(G.number_of_nodes(), 1), 4),
            "components": len(comps),
            "flood_critical_nodes": len(flood_critical),
        }
