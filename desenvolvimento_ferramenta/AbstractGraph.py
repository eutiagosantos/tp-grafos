

class AbstractGraph:
    def __init__(self):
        self.peso_vertice= {}
        self.rotulos= {}
        self.vertices = {}
        self.edges = {}

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


    def __str__(self):
        return f"Nodes: {self.vertices}, Edges: {self.edges}"