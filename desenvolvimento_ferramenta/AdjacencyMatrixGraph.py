from desenvolvimento_ferramenta import AbstractGraph


class AdjacencyMatrixGraph(AbstractGraph):
    def __init__(self, num_vertices):
        super().__init__()
        self.num_vertices = num_vertices
        self.adj_matrix = [[0 for _ in range(num_vertices)] for _ in range(num_vertices)]