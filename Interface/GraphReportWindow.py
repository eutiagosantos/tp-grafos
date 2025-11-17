import tkinter as tk
from tkinter import ttk
import networkx as nx
from Graph_LIB.Metrics import CentralityMetrics  # importa sua classe de métricas
from typing import Dict, Any, List, Tuple



class GraphReportWindow:
    """
    Janela de relatório para um grafo NetworkX.
    Mostra resumo básico + métricas de centralidade.
    """

    def __init__(self, parent, titulo: str, graph: nx.Graph):
        self.parent = parent
        self.G = graph

        # DEBUG opcional (pode remover depois)
        print(
            f"[Relatório] {titulo}: nós={self.G.number_of_nodes()}, "
            f"arestas={self.G.number_of_edges()}"
        )

        self.win = tk.Toplevel(parent)
        self.win.title(titulo)
        self.win.geometry("800x600")

        main_frame = ttk.Frame(self.win, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ===== Resumo do grafo =====
        resumo_frame = ttk.LabelFrame(main_frame, text="Resumo do grafo")
        resumo_frame.pack(fill=tk.X)

        n = self.G.number_of_nodes()
        m = self.G.number_of_edges()
        densidade = nx.density(self.G) if n > 1 else 0.0

        # conexidade (só faz sentido pra Graph não vazio)
        conectado = False
        try:
            if n > 0 and isinstance(self.G, nx.Graph):
                conectado = nx.is_connected(self.G)
        except nx.NetworkXError:
            conectado = False

        lbl_resumo = ttk.Label(
            resumo_frame,
            text=(
                f"Vértices: {n}   "
                f"Arestas: {m}   "
                f"Densidade: {densidade:.4f}   "
                f"Conexo: {'Sim' if conectado else 'Não'}"
            )
        )
        lbl_resumo.pack(side=tk.LEFT, anchor="w", pady=5)

        # ===== Métricas de centralidade =====
        metrics_frame = ttk.LabelFrame(main_frame, text="Métricas de centralidade")
        metrics_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        colunas = ("vertice", "grau", "betweenness", "closeness", "pagerank")
        self.tree = ttk.Treeview(
            metrics_frame,
            columns=colunas,
            show="headings",
            height=15
        )

        headers = ["Vértice", "Grau", "Betweenness", "Closeness", "PageRank"]
        for col, header in zip(colunas, headers):
            self.tree.heading(col, text=header)
            self.tree.column(col, anchor="center", width=120)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(
            metrics_frame,
            orient="vertical",
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # calcula métricas e preenche tabela
        self._popular_metricas()

        # ===== Botões inferiores =====
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=(10, 0))

        btn_fechar = ttk.Button(bottom_frame, text="Fechar", command=self.win.destroy)
        btn_fechar.pack(side=tk.RIGHT)

    # ----------------- lógica das métricas -----------------

    def _popular_metricas(self):
        print(self)
        if self.G.number_of_nodes() == 0:
            return

        # usa CentralityMetrics para calcular tudo
        cm = CentralityMetrics(self.G)
        all_metrics = cm.compute_all()

        degree = all_metrics["degree"]
        betweenness = all_metrics["betweenness"]
        closeness = all_metrics["closeness"]
        pagerank = all_metrics["pagerank"]

        # vamos ordenar pela métrica de PageRank (decrescente)
        nodes_sorted = sorted(
            pagerank.items(),
            key=lambda x: x[1],
            reverse=True
        )

        for node, _ in nodes_sorted:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    node,
                    f"{degree.get(node, 0.0):.4f}",
                    f"{betweenness.get(node, 0.0):.4f}",
                    f"{closeness.get(node, 0.0):.4f}",
                    f"{pagerank.get(node, 0.0):.4f}",
                ),
            )


