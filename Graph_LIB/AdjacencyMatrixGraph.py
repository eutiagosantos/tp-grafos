"""Implementação de grafo por matriz de adjacência.

Este módulo contém a classe `AdjacencyMatrixGraph`, uma
implementação concreta que estende `AbstractGraph` e armazena as
arestas em uma matriz quadrada `adj_matrix`. Esta representação é
útil para grafos densos ou para operações que se beneficiam de
acesso O(1) à presença de uma aresta entre dois vértices.
"""

from AbstractGraph import AbstractGraph


class AdjacencyMatrixGraph(AbstractGraph):
    """Grafo direcionado representado por matriz de adjacência.

    A matriz é armazenada em `adj_matrix` como uma lista de listas
    de inteiros (0/1 por padrão). A classe preserva a API de
    `AbstractGraph` e pode ser estendida para suportar pesos
    armazenando números diferentes de 0/1.
    """

    def __init__(self, num_vertices):
        """Inicializa a matriz de adjacência.

        Args:
            num_vertices (int): número de vértices que a matriz irá
                acomodar. A matriz é inicializada com zeros.

        Nota:
            Esta implementação pressupõe um conjunto de vértices
            indexados implicitamente de 0 a `num_vertices - 1`.
            Integração com a API de nomes/identificadores da
            classe base pode ser feita por subclasses ou adaptadores.
        """
        super().__init__()
        self.num_vertices = num_vertices
        self.adj_matrix = [[0 for _ in range(num_vertices)] for _ in range(num_vertices)]