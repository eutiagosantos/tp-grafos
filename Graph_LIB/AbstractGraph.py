class AbstractGraph:
    def __init__(self):
        self.peso_vertice = {}
        self.rotulos = {}
        self.vertices = {}
        self.edges = {}
        self.edge_weights = {}  # pesos das arestas (u, v) -> w

    def add_node(self, node):
        self.vertices[node] = {}
        self.edges[node] = []

    def add_edge(self, from_node, to_node):
        if from_node not in self.vertices or to_node not in self.vertices:
            raise ValueError("Both nodes must be in the graph.")
        self.edges[from_node].append(to_node)

    def remove_edge(self, from_node, to_node):
        if from_node in self.edges and to_node in self.edges[from_node]:
            self.edges[from_node].remove(to_node)

    def get_neighbors(self, node):
        if node not in self.vertices:
            raise ValueError("Node not found in the graph.")
        return self.edges[node]

    def get_vertex_count(self):
        return len(self.vertices)

    def get_edge_count(self):
        return sum(len(neighbors) for neighbors in self.edges.values())

    def has_edge(self, from_node: int, to_node: int) -> bool:
        return to_node in self.edges.get(from_node, [])

    # --------- FUNÇÕES NOVAS DA API OBRIGATÓRIA ---------

    # boolean isSucessor(int u, int v);
    def is_sucessor(self, u, v):
        # v é sucessor de u se existir aresta u -> v
        return self.has_edge(u, v)

    # boolean isPredessor(int u, int v);
    def is_predessor(self, u, v):
        # v é predecessor de u se existir aresta v -> u
        return self.has_edge(v, u)

    # boolean isDivergent(int u1, int v1, int u2, int v2);
    def is_divergent(self, u1, v1, u2, v2):
        # Duas arestas são divergentes se saem do mesmo vértice e chegam em vértices diferentes
        return (
            u1 == u2
            and v1 != v2
            and self.has_edge(u1, v1)
            and self.has_edge(u2, v2)
        )

    # boolean isConvergent(int u1, int v1, int u2, int v2);
    def is_convergent(self, u1, v1, u2, v2):
        # Duas arestas são convergentes se chegam no mesmo vértice e saem de vértices diferentes
        return (
            v1 == v2
            and u1 != u2
            and self.has_edge(u1, v1)
            and self.has_edge(u2, v2)
        )

    # boolean isIncident(int u, int v, int x);
    def is_incident(self, u, v, x):
        # x é incidente à aresta (u, v) se for uma das extremidades
        return self.has_edge(u, v) and (x == u or x == v)

    # int getVertexInDegree(int u);
    def get_vertex_in_degree(self, u):
        if u not in self.vertices:
            raise ValueError("Vertex not found in the graph.")
        count = 0
        for src, neighbors in self.edges.items():
            # conta inclusive múltiplas arestas se tiver
            count += neighbors.count(u)
        return count

    # int getVertexOutDegree(int u);
    def get_vertex_out_degree(self, u):
        if u not in self.vertices:
            raise ValueError("Vertex not found in the graph.")
        return len(self.edges.get(u, []))

    # void setVertexWeight(int v, double w);
    def set_vertex_weight(self, v, w):
        if v not in self.vertices:
            raise ValueError("Vertex not found in the graph.")
        self.peso_vertice[v] = w

    # double getVertexWeight(int v);
    def get_vertex_weight(self, v):
        if v not in self.vertices:
            raise ValueError("Vertex not found in the graph.")
        return self.peso_vertice.get(v)

    # void setEdgeWeight(int u, int v, double w);
    def set_edge_weight(self, u, v, w):
        if not self.has_edge(u, v):
            raise ValueError("Edge not found in the graph.")
        self.edge_weights[(u, v)] = w

    # double getEdgeWeight(int u, int v);
    def get_edge_weight(self, u, v):
        if not self.has_edge(u, v):
            raise ValueError("Edge not found in the graph.")
        return self.edge_weights.get((u, v))

    # boolean isConnected();
    def is_connected(self):
        # conectado (fracamente): ignorando direção, todo mundo alcança todo mundo
        if not self.vertices:
            return True  # por convenção

        start = next(iter(self.vertices))
        visited = set()
        stack = [start]

        while stack:
            v = stack.pop()
            if v in visited:
                continue
            visited.add(v)

            # vizinhos de saída
            for w in self.edges.get(v, []):
                if w not in visited:
                    stack.append(w)

            # vizinhos de entrada (tratando como não-direcionado)
            for u in self.vertices:
                if v in self.edges.get(u, []) and u not in visited:
                    stack.append(u)

        return len(visited) == len(self.vertices)

    # boolean isEmptyGraph();
    def is_empty_graph(self):
        return self.get_vertex_count() == 0

    # boolean isCompleteGraph();
    def is_complete_graph(self):
        # completo direcionado sem laços: para todo par (u != v), existe aresta u -> v
        n = self.get_vertex_count()
        if n <= 1:
            return True
        for u in self.vertices:
            for v in self.vertices:
                if u != v and not self.has_edge(u, v):
                    return False
        return True

    def __str__(self):
        return (
            f"Nodes: {self.vertices}, "
            f"Edges: {self.edges}, "
            f"VertexWeights: {self.peso_vertice}, "
            f"EdgeWeights: {self.edge_weights}"
        )
