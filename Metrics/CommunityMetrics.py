import networkx as nx
from networkx.algorithms import community


class CommunityMetrics:
    """
    Métricas de comunidade:
      1. Detecção de comunidades (Louvain-like usando greedy modularity)
      2. Modularidade
      3. Bridging ties: nós que conectam comunidades
    """

    def __init__(self, G: nx.Graph):
        self.G = G

    # --------------------------------------------------------------
    # 1) DETECÇÃO DE COMUNIDADES
    # --------------------------------------------------------------
    def detectar_comunidades(self):
        """
        Usa greedy_modularity_communities (NetworkX puro, sem SciPy)
        """
        if self.G.number_of_nodes() == 0:
            return {
                "modularidade": 0.0,
                "num_comunidades": 0,
                "tamanho_comunidades": [],
                "comunidades": []
            }

        comunidades = list(community.greedy_modularity_communities(self.G))

        modularidade = community.modularity(self.G, comunidades)

        tamanhos = [len(c) for c in comunidades]

        return {
            "modularidade": modularidade,
            "num_comunidades": len(comunidades),
            "tamanho_comunidades": tamanhos,
            "comunidades": [list(c) for c in comunidades]
        }

    # --------------------------------------------------------------
    # 2) BRIDGING TIES
    # --------------------------------------------------------------
    def bridging_ties(self):
        """
        Nós que servem de ponte entre comunidades:
        Calculado usando 'bridging centrality':
            bridging centrality = betweenness * bridging coefficient
        """
        if self.G.number_of_nodes() == 0:
            return {}

        bet = nx.betweenness_centrality(self.G, weight="weight")

        # coeficiente de ponte: 1 - clustering
        coef_ponte = {}
        for node in self.G.nodes():
            c = nx.clustering(self.G, node)
            coef_ponte[node] = 1 - c

        bridging = {}
        for n in self.G.nodes():
            bridging[n] = bet[n] * coef_ponte[n]

        return bridging
