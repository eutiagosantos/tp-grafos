"""Implementação de grafo por lista de adjacência.

Este módulo fornece a implementação concreta `AdjacencyListGraph`
que estende `AbstractGraph` e mantém, além das estruturas
herdadas, uma lista de adjacência explícita (`adj_list`) para
operações de leitura/escrita eficientes.
"""

from AbstractGraph import AbstractGraph


class AdjacencyListGraph(AbstractGraph):
    """Grafo direcionado implementado por lista de adjacência.

    A classe preserva a API definida em `AbstractGraph` e mantém a
    estrutura `adj_list` como um mapeamento de vértice -> lista de
    vizinhos de saída. Métodos públicos documentados abaixo delegam
    parte do comportamento à classe base quando apropriado.
    """

    def __init__(self):
        """Inicializa o grafo e a lista de adjacência vazia."""
        super().__init__()
        self.adj_list = {}

    def add_node(self, node):
        """Adiciona um vértice ao grafo e à lista de adjacência.

        Args:
            node: identificador do vértice (qualquer tipo hashable).
        """
        super().add_node(node)
        self.adj_list[node] = []

    def add_edge(self, from_node, to_node):
        """Adiciona aresta dirigida `from_node -> to_node`.

        O método delega validações à classe base e atualiza a
        lista de adjacência local.

        Args:
            from_node: vértice de origem.
            to_node: vértice de destino.
        """
        super().add_edge(from_node, to_node)
        self.adj_list[from_node].append(to_node)

    def get_neighbors(self, node):
        """Retorna a lista de vizinhos de saída de `node`.

        Mantém comportamento idêntico ao método da classe base,
        mas exposto aqui para otimização futura caso a estrutura
        de `adj_list` precise ser usada diretamente.
        """
        return super().get_neighbors(node)

    def __str__(self):
        """Representação legível do grafo baseada na lista de adjacência."""
        return f"Adjacency List: {self.adj_list}"