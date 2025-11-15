import tkinter as tk
from tkinter import ttk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx


class GitHubGraphGUI:
    def __init__(self, root, data, build_graph_fn, slugify_fn):
        self.root = root
        self.data = data

        # funções vindas da main
        self.build_graph = build_graph_fn
        self.slugify = slugify_fn

        self.repo = data.get("repository", "repositório-desconhecido")
        self.usuarios = data["users"]

        # separa as interações por tipo (fica fácil reaproveitar)
        self.interacoes_comentarios = data["interactions"].get("comentario_em_issues", [])
        self.interacoes_fechamento = data["interactions"].get("fechamento_de_issues", [])

        self.interacoes_pr = []
        for chave in ["comentario_pull_request", "revisoes_pull_request", "merge_pull_request"]:
            self.interacoes_pr += data["interactions"].get(chave, [])

        # janela principal
        self.root.title(f"Grafos GitHub — {self.repo}")
        self.root.geometry("1000x700")

        # ====== FRAME SUPERIOR (botões) ======
        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.pack(side=tk.TOP, fill=tk.X)

        btn_fechamento = ttk.Button(
            top_frame,
            text="Grafo: Fechamento de Issues",
            command=self.mostrar_grafo_fechamento_issues
        )
        btn_fechamento.pack(side=tk.LEFT, padx=5)

        btn_comentarios = ttk.Button(
            top_frame,
            text="Grafo: Comentários em Issues",
            command=self.mostrar_grafo_comentario_issues
        )
        btn_comentarios.pack(side=tk.LEFT, padx=5)

        btn_pr = ttk.Button(
            top_frame,
            text="Grafo: Pull Requests",
            command=self.mostrar_grafo_pull_requests
        )
        btn_pr.pack(side=tk.LEFT, padx=5)

        btn_totais = ttk.Button(
            top_frame,
            text="Mostrar totais de arestas",
            command=self.mostrar_totais_arestas
        )
        btn_totais.pack(side=tk.LEFT, padx=5)

        # ====== FRAME CENTRAL (gráfico) ======
        center_frame = ttk.Frame(self.root)
        center_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # figura do matplotlib embutida no Tkinter
        self.fig, self.ax = plt.subplots(figsize=(7, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=center_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

        # ====== FRAME INFERIOR (informações) ======
        bottom_frame = ttk.Frame(self.root, padding=10)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.label_status = ttk.Label(bottom_frame, text="Nenhum grafo selecionado ainda.")
        self.label_status.pack(side=tk.TOP, anchor="w")

        self.label_totais = ttk.Label(bottom_frame, text="")
        self.label_totais.pack(side=tk.TOP, anchor="w")

        # já mostra os totais na inicialização
        self.mostrar_totais_arestas(inicial=True)

    # ---------- lógica de desenho (usa build_graph da main) ----------

    def _desenhar_grafo(self, interacoes, titulo, cor, salvar_png=False):
        if not interacoes:
            self.label_status.config(text=f"Nenhum dado disponível para: {titulo}")
            return

        # constrói grafo usando função recebida
        G = self.build_graph(self.usuarios, interacoes)

        # limpa o eixo
        self.ax.clear()

        pos = nx.spring_layout(G, seed=42)

        nx.draw(
            G,
            pos,
            ax=self.ax,
            with_labels=True,
            node_color=cor,
            node_size=700,
            font_size=8,
            width=1.5
        )

        edge_labels = {(u, v): G[u][v]["weight"] for u, v in G.edges()}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, ax=self.ax)

        self.ax.set_title(titulo)
        self.fig.tight_layout()

        if salvar_png:
            fname = self.slugify(titulo) + ".png"
            self.fig.savefig(fname, dpi=150, bbox_inches="tight")
            print(f"✓ Figura salva em: {fname}")

        # atualiza o canvas do Tkinter
        self.canvas.draw()

        # atualiza status embaixo
        self.label_status.config(
            text=f"{titulo} -> Nós: {G.number_of_nodes()} | Arestas: {G.number_of_edges()}"
        )

    def _contar_arestas(self, interacoes):
        if not interacoes:
            return 0
        G = self.build_graph(self.usuarios, interacoes)
        return G.number_of_edges()

    # ---------- ações dos botões (callbacks) ----------

    def mostrar_grafo_comentario_issues(self):
        titulo = f"Grafo: Comentários em Issues — {self.repo}"
        self._desenhar_grafo(self.interacoes_comentarios, titulo, cor="skyblue", salvar_png=True)

    def mostrar_grafo_fechamento_issues(self):
        titulo = f"Grafo: Fechamento de Issues — {self.repo}"
        self._desenhar_grafo(self.interacoes_fechamento, titulo, cor="lightgreen", salvar_png=True)

    def mostrar_grafo_pull_requests(self):
        titulo = f"Grafo: Pull Requests — {self.repo}"
        self._desenhar_grafo(self.interacoes_pr, titulo, cor="lightcoral", salvar_png=True)

    def mostrar_totais_arestas(self, inicial=False):
        total_comentarios = self._contar_arestas(self.interacoes_comentarios)
        total_fechamento = self._contar_arestas(self.interacoes_fechamento)
        total_pr = self._contar_arestas(self.interacoes_pr)

        texto = (
            "Totais de arestas por grafo:\n"
            f" - Comentários em Issues : {total_comentarios}\n"
            f" - Fechamento de Issues  : {total_fechamento}\n"
            f" - Pull Requests         : {total_pr}"
        )
        self.label_totais.config(text=texto)

        if not inicial:
            print("\n" + texto + "\n")


if __name__ == "__main__":
    # opcional: rodar interface direto
    from main import load_data, build_graph, slugify

    data = load_data("dados_github.json")
    root = tk.Tk()
    app = GitHubGraphGUI(root, data, build_graph, slugify)
    root.mainloop()
