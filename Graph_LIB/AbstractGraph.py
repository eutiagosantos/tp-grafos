"""Modos abstratos de grafo.

Este módulo fornece a classe base `AbstractGraph` com operações
comuns a diferentes representações de grafos (lista de adjacência,
matriz, etc.). As mensagens e docstrings aqui usam português para
manter consistência com o restante do projeto.
"""


class AbstractGraph:
    """Classe base para representações de grafos direcionados.

    A classe oferece operações elementares (adição/remoção de nós e
    arestas, consulta de vizinhança, graus, pesos, e propriedades
    básicas como conectividade e completude). Não impõe restrições
    sobre armazenamento — subclasses podem especializar a
    representação quando necessário.
    """

    def __init__(self):
        """Inicializa as estruturas internas do grafo.

        Estruturas:
        - `peso_vertice`: mapa de peso de vértices (vértice -> peso)
        - `rotulos`: rótulos opcionais para vértices
        - `vertices`: dicionário de vértices cadastrados
        - `edges`: dicionário de listas de adjacência (u -> [v, ...])
        - `edge_weights`: mapa de pesos de arestas ((u, v) -> peso)
        """
        self.peso_vertice = {}
        self.rotulos = {}
        self.vertices = {}
        self.edges = {}
        self.edge_weights = {}  # pesos das arestas (u, v) -> w

    def add_node(self, node):
        """Adiciona um vértice ao grafo.

        Args:
            node: identificador do vértice (qualquer tipo hashable).

        Note:
            Se o vértice já existir, o comportamento atual sobrescreve
            sua entrada interna sem lançar erro.
        """
        self.vertices[node] = {}
        self.edges[node] = []

    def add_edge(self, from_node, to_node):
        """Adiciona uma aresta dirigida de `from_node` para `to_node`.

        Args:
            from_node: vértice de origem.
            to_node: vértice de destino.

        Raises:
            ValueError: se qualquer um dos vértices não existir no grafo.
        """
        if from_node not in self.vertices or to_node not in self.vertices:
            raise ValueError("Both nodes must be in the graph.")
        self.edges[from_node].append(to_node)

    def remove_edge(self, from_node, to_node):
        """Remove a aresta dirigida `from_node` -> `to_node` se existir.

        Args:
            from_node: vértice de origem.
            to_node: vértice de destino.
        """
        if from_node in self.edges and to_node in self.edges[from_node]:
            self.edges[from_node].remove(to_node)

    def get_neighbors(self, node):
        """Retorna os vizinhos de saída (adjacência) de um vértice.

        Args:
            node: vértice cujo conjunto de vizinhos será retornado.

        Returns:
            lista de vértices alcançáveis a partir de `node`.

        Raises:
            ValueError: se o vértice não existir.
        """
        if node not in self.vertices:
            raise ValueError("Node not found in the graph.")
        return self.edges[node]

    def get_vertex_count(self):
        """Retorna o número de vértices no grafo.

        Returns:
            int: contagem de vértices.
        """
        return len(self.vertices)

    def get_edge_count(self):
        """Retorna o total de arestas dirigidas no grafo.

        Contabiliza múltiplas arestas separadamente.
        """
        return sum(len(neighbors) for neighbors in self.edges.values())

    def has_edge(self, from_node: int, to_node: int) -> bool:
        """Verifica existência de aresta dirigida `from_node` -> `to_node`.

        Returns:
            True se a aresta existir, caso contrário False.
        """
        return to_node in self.edges.get(from_node, [])

    def is_sucessor(self, u, v):
        """Indica se `v` é sucessor imediato de `u`.

        Retorna True quando existe a aresta `u -> v`.
        """
        return self.has_edge(u, v)

    def is_predessor(self, u, v):
        """Indica se `v` é predecessor imediato de `u`.

        Retorna True quando existe a aresta `v -> u`.
        """
        return self.has_edge(v, u)

    def is_divergent(self, u1, v1, u2, v2):
        """Verifica se duas arestas são divergentes.

        Duas arestas são divergentes quando possuem a mesma origem e
        destinos distintos, e ambas existem no grafo.
        """
        return (
            u1 == u2
            and v1 != v2
            and self.has_edge(u1, v1)
            and self.has_edge(u2, v2)
        )

    def is_convergent(self, u1, v1, u2, v2):
        """Verifica se duas arestas são convergentes.

        Duas arestas são convergentes quando possuem o mesmo destino e
        origens distintas, e ambas existem no grafo.
        """
        return (
            v1 == v2
            and u1 != u2
            and self.has_edge(u1, v1)
            and self.has_edge(u2, v2)
        )

    def is_incident(self, u, v, x):
        """Indica se o vértice `x` é incidente à aresta `(u, v)`.

        Retorna True se `x` for uma das extremidades da aresta e a
        aresta existir.
        """
        return self.has_edge(u, v) and (x == u or x == v)

    def get_vertex_in_degree(self, u):
        """Retorna o grau de entrada (in-degree) do vértice `u`.

        Contabiliza múltiplas arestas de entrada.

        Raises:
            ValueError: se o vértice não existir no grafo.
        """
        if u not in self.vertices:
            raise ValueError("Vertex not found in the graph.")
        count = 0
        for src, neighbors in self.edges.items():
            count += neighbors.count(u)
        return count

    def get_vertex_out_degree(self, u):
        """Retorna o grau de saída (out-degree) do vértice `u`.

        Raises:
            ValueError: se o vértice não existir no grafo.
        """
        if u not in self.vertices:
            raise ValueError("Vertex not found in the graph.")
        return len(self.edges.get(u, []))

    def set_vertex_weight(self, v, w):
        """Atribui um peso `w` ao vértice `v`.

        Raises:
            ValueError: se o vértice não existir.
        """
        if v not in self.vertices:
            raise ValueError("Vertex not found in the graph.")
        self.peso_vertice[v] = w

    def get_vertex_weight(self, v):
        """Retorna o peso associado ao vértice `v`.

        Returns:
            valor do peso ou `None` se não houver peso definido.

        Raises:
            ValueError: se o vértice não existir.
        """
        if v not in self.vertices:
            raise ValueError("Vertex not found in the graph.")
        return self.peso_vertice.get(v)

    def set_edge_weight(self, u, v, w):
        """Define peso `w` para a aresta `(u, v)`.

        Raises:
            ValueError: se a aresta não existir.
        """
        if not self.has_edge(u, v):
            raise ValueError("Edge not found in the graph.")
        self.edge_weights[(u, v)] = w

    def get_edge_weight(self, u, v):
        """Retorna o peso da aresta `(u, v)`.

        Returns:
            peso associado à aresta ou `None` se não definido.

        Raises:
            ValueError: se a aresta não existir.
        """
        if not self.has_edge(u, v):
            raise ValueError("Edge not found in the graph.")
        return self.edge_weights.get((u, v))

    def is_connected(self):
        """Verifica se o grafo é fracamente conectado.

        A conectividade fraca é verificada ignorando a direção das
        arestas (trata-se como grafo não-direcionado para alcance).

        Returns:
            True se o grafo estiver conectado (por convenção, grafo
            vazio é considerado conectado).
        """
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

            for w in self.edges.get(v, []):
                if w not in visited:
                    stack.append(w)

            for u in self.vertices:
                if v in self.edges.get(u, []) and u not in visited:
                    stack.append(u)

        return len(visited) == len(self.vertices)

    def is_empty_graph(self):
        """Indica se o grafo está vazio (sem vértices)."""
        return self.get_vertex_count() == 0

    def is_complete_graph(self):
        """Verifica se o grafo é completo (direcionado, sem laços).

        Define-se completo quando, para todo par distinto (u, v),
        existe a aresta `u -> v`.
        """
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
