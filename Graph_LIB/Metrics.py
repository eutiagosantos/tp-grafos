from typing import Any, Dict, List, Tuple, Optional

import networkx as nx


class CentralityMetrics:
    """
    Calcula métricas de centralidade para um grafo de colaboração.

    Pensado para a Etapa 3 – Relatórios:
      1) Grau (degree centrality)
      2) Betweenness centrality
      3) Closeness centrality
      4) PageRank (implementado manualmente, sem SciPy)
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
            - True: usa degree_centrality normalizado
            - False: usa apenas o grau (ponderado) bruto
        :param mode:
            - 'total': grau total (in + out em dígrafos)
            - 'in'   : grau de entrada (apenas para DiGraph)
            - 'out'  : grau de saída (apenas para DiGraph)
        """
        G = self.G

        # Grafo não direcionado
        if not isinstance(G, nx.DiGraph):
            if normalized:
                # degree_centrality: deg(v) / (n - 1)
                n = len(G)
                if n <= 1:
                    values = {node: 0.0 for node in G.nodes()}
                else:
                    values = {}
                    for node in G.nodes():
                        deg = G.degree(node, weight="weight")
                        values[node] = deg / (n - 1)
            else:
                values = dict(G.degree(weight="weight"))
            return self._translate_ids(values)

        # Dígrafo: trata in/out/total
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

        Aqui usamos a implementação do NetworkX, que é puramente
        baseada em algoritmos de grafos (sem SciPy/pandas/etc).

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

    # ---------- 4) PageRank (implementado manualmente) ----------

    def pagerank(
        self,
        alpha: float = 0.85,
        max_iter: int = 100,
        tol: float = 1.0e-06
    ) -> Dict[str, float]:
        """
        PageRank clássico, implementado manualmente (sem SciPy).

        - Usa iteração de potência.
        - Pondera arestas pelo atributo 'weight'.
        - Trata vértices pendurados (sem saída).
        """
        G = self.G

        if G.number_of_nodes() == 0:
            return {}

        nodes = list(G.nodes())
        n = len(nodes)

        # inicializa ranks iguais
        rank: Dict[Any, float] = {v: 1.0 / n for v in nodes}

        # grau de saída ponderado (ou grau em grafo não direcionado)
        if isinstance(G, nx.DiGraph):
            out_strength = {
                v: G.out_degree(v, weight="weight") for v in nodes
            }
        else:
            out_strength = {
                v: G.degree(v, weight="weight") for v in nodes
            }

        for _ in range(max_iter):
            new_rank: Dict[Any, float] = {}

            # soma dos ranks dos vértices sem saída
            dangling_sum = sum(
                rank[v] for v in nodes if out_strength.get(v, 0.0) == 0.0
            )

            # parte base + contribuição dos vértices pendurados
            for v in nodes:
                new_rank[v] = (1.0 - alpha) / n
                new_rank[v] += alpha * dangling_sum / n

            # redistribui rank pelos vizinhos
            for u in nodes:
                out_s = out_strength.get(u, 0.0)
                if out_s == 0.0:
                    continue

                if isinstance(G, nx.DiGraph):
                    vizinhos = G.successors(u)
                else:
                    vizinhos = G.neighbors(u)

                for v in vizinhos:
                    w = G[u][v].get("weight", 1.0)
                    new_rank[v] += alpha * rank[u] * (w / out_s)

            # critério de parada
            diff = sum(abs(new_rank[v] - rank[v]) for v in nodes)
            rank = new_rank

            if diff < tol:
                break

        # traduz ids se tiver mapeamento
        return self._translate_ids(rank)

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
        }

def resumo_metricas_grafo(G: nx.Graph) -> Dict[str, Dict[str, float]]:
    """
    Calcula, para um grafo, a soma e a média de cada métrica
    (degree, betweenness, closeness, pagerank).
    """
    cm = CentralityMetrics(G)
    all_metrics = cm.compute_all()

    resumo: Dict[str, Dict[str, float]] = {}

    for nome_metrica, valores in all_metrics.items():
        # valores: dict[label -> valor_float]
        n = len(valores)
        if n == 0:
            resumo[nome_metrica] = {"soma": 0.0, "media": 0.0, "n": 0}
            continue

        soma = sum(valores.values())
        media = soma / n
        resumo[nome_metrica] = {
            "soma": soma,
            "media": media,
            "n": n
        }

    return resumo


def resumo_geral_grafos(
    grafos: List[Tuple[str, nx.Graph]]
) -> Tuple[List[Tuple[str, Dict[str, Dict[str, float]]]], Dict[str, float]]:
    """
    :param grafos: lista de tuplas (nome_grafo, grafo)
    :return:
        - lista com (nome_grafo, resumo_metricas_grafo)
        - dicionário com média geral (ponderada) entre grafos para cada métrica
    """
    individuais: List[Tuple[str, Dict[str, Dict[str, float]]]] = []
    for nome, G in grafos:
        resumo = resumo_metricas_grafo(G)
        individuais.append((nome, resumo))

    metricas = ["degree", "betweenness", "closeness", "pagerank"]
    media_geral: Dict[str, float] = {}

    for met in metricas:
        soma_total = 0.0
        n_total = 0

        for _, resumo in individuais:
            if met in resumo:
                soma_total += resumo[met]["soma"]
                n_total += resumo[met]["n"]

        if n_total > 0:
            media_geral[met] = soma_total / n_total
        else:
            media_geral[met] = 0.0

    return individuais, media_geral
