from typing import Any, Dict, List, Tuple, Optional

import networkx as nx


class CentralityMetrics:
    """
    Calcula métricas de centralidade para um grafo de colaboração.

    Pensado para a Etapa 3 – Relatórios:
      1) Grau (degree centrality)
      2) Betweenness centrality
      3) Closeness centrality
      4) PageRank / Eigenvector centrality
    """

    def __init__(
        self,
        graph: nx.Graph,
        id_to_label: Optional[Dict[Any, str]] = None
    ) -> None:
        """
        :param graph: Grafo do NetworkX (pode ser Graph ou DiGraph), ponderado em 'weight'.
        :param id_to_label: Mapeamento opcional de id de vértice -> rótulo (ex.: login do GitHub).
        """
        self.G = graph
        self.id_to_label = id_to_label or {}

    # ---------- helpers internos ----------

    def _translate_ids(self, values: Dict[Any, float]) -> Dict[str, float]:
        """
        Se existir mapeamento de id -> label, devolve resultados com label.
        Caso contrário, devolve os ids originais como string.
        """
        if not self.id_to_label:
            return {str(node): value for node, value in values.items()}
        return {
            self.id_to_label.get(node, str(node)): value
            for node, value in values.items()
        }

    @staticmethod
    def top_k(metric: Dict[str, float], k: int = 10) -> List[Tuple[str, float]]:
        """
        Retorna os k vértices com maior valor na métrica.
        """
        return sorted(metric.items(), key=lambda x: x[1], reverse=True)[:k]

    # ---------- 1) Grau (degree centrality) ----------

    def degree_centrality(
        self,
        normalized: bool = True,
        mode: str = "total"
    ) -> Dict[str, float]:
        """
        Centralidade de grau.

        :param normalized:
            - True: usa degree_centrality normalizado do NetworkX
            - False: usa apenas o grau (ponderado) bruto
        :param mode:
            - 'total': grau total (in + out em dígrafos)
            - 'in'   : grau de entrada (apenas para DiGraph)
            - 'out'  : grau de saída (apenas para DiGraph)
        """
        G = self.G

        # Para grafo não direcionado, usa direto o NetworkX
        if not isinstance(G, nx.DiGraph):
            if normalized:
                values = nx.degree_centrality(G)
            else:
                values = dict(G.degree(weight="weight"))
            return self._translate_ids(values)

        # Para dígrafo, tratamos in/out/total
        if mode == "in":
            raw = dict(G.in_degree(weight="weight"))
        elif mode == "out":
            raw = dict(G.out_degree(weight="weight"))
        else:
            raw = dict(G.degree(weight="weight"))

        if not normalized:
            return self._translate_ids(raw)

        # normaliza manualmente: divide por (n - 1)
        n = len(G) - 1
        if n <= 0:
            values = {node: 0.0 for node in G.nodes()}
        else:
            values = {node: deg / n for node, deg in raw.items()}

        return self._translate_ids(values)

    # ---------- 2) Betweenness centrality ----------

    def betweenness_centrality(
        self,
        normalized: bool = True,
        k: Optional[int] = None
    ) -> Dict[str, float]:
        """
        Centralidade de intermediação (betweenness).

        :param normalized: se True, normaliza os valores.
        :param k: se definido, usa amostragem de k vértices para acelerar (grafos grandes).
        """
        values = nx.betweenness_centrality(
            self.G,
            normalized=normalized,
            k=k,
            weight="weight"
        )
        return self._translate_ids(values)

    # ---------- 3) Closeness centrality ----------

    def closeness_centrality(self, use_weights: bool = False) -> Dict[str, float]:
        """
        Centralidade de proximidade (closeness).

        :param use_weights:
            - False: distância = número de arestas
            - True : usa o peso como 'distance'
        """
        distance_attr = "weight" if use_weights else None
        values = nx.closeness_centrality(self.G, distance=distance_attr)
        return self._translate_ids(values)

    # ---------- 4) PageRank / Eigenvector centrality ----------

    def pagerank(
        self,
        alpha: float = 0.85,
        max_iter: int = 100,
        tol: float = 1.0e-06
    ) -> Dict[str, float]:
        """
        PageRank clássico, ponderando arestas pelo atributo 'weight'.
        """
        values = nx.pagerank(
            self.G,
            alpha=alpha,
            max_iter=max_iter,
            tol=tol,
            weight="weight"
        )
        return self._translate_ids(values)

    def eigenvector_centrality(
        self,
        max_iter: int = 1000,
        tol: float = 1.0e-06
    ) -> Dict[str, float]:
        """
        Centralidade de autovetor (eigenvector centrality).
        """
        values = nx.eigenvector_centrality(
            self.G,
            max_iter=max_iter,
            tol=tol,
            weight="weight"
        )
        return self._translate_ids(values)

    # ---------- pacote completo ----------

    def compute_all(
        self,
        degree_mode: str = "total"
    ) -> Dict[str, Dict[str, float]]:
        """
        Devolve todas as métricas principais em um dicionário,
        pronto pra ser usado na etapa de relatório/interface.
        """
        return {
            "degree": self.degree_centrality(mode=degree_mode),
            "betweenness": self.betweenness_centrality(),
            "closeness": self.closeness_centrality(),
            "pagerank": self.pagerank()
            # "eigenvector": self.eigenvector_centrality()  # se quiser incluir também
        }
