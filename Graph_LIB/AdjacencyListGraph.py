

from AbstractGraph import AbstractGraph


class AdjacencyListGraph(AbstractGraph):
    def __init__(self):
        super().__init__()
        self.adj_list = {}

    def add_node(self, node):
        super().add_node(node)
        self.adj_list[node] = []

    def add_edge(self, from_node, to_node):
        super().add_edge(from_node, to_node)
        self.adj_list[from_node].append(to_node)

    def get_neighbors(self, node):
        return super().get_neighbors(node)

    def __str__(self):
        return f"Adjacency List: {self.adj_list}"