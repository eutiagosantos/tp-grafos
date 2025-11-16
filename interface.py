import tkinter as tk
from tkinter import ttk, messagebox

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import networkx as nx
from GraphReportWindow import GraphReportWindow


class GitHubGraphGUI:
    def __init__(self, root, data, build_graph_fn, slugify_fn):
        self.root = root
        self.data = data

        # funções vindas da main
        self.build_graph = build_graph_fn
        self.slugify = slugify_fn

        self.repo = data.get("repository", "repositório-desconhecido")
        self.usuarios = data["users"]

        # separa as interações por tipo
        self.interacoes_comentarios = data["interactions"].get("comentario_em_issues", [])
        self.interacoes_fechamento = data["interactions"].get("fechamento_de_issues", [])

        self.interacoes_pr = []
        for chave in ["comentario_pull_request", "revisoes_pull_request", "merge_pull_request"]:
            self.interacoes_pr += data["interactions"].get(chave, [])

        # janela principal -> "menu" menor
        self.root.title(f"Análise em Grafos do repositório {self.repo}")
        self.root.geometry("500x260")  # menor, quase um modal

        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # TÍTULO
        titulo_label = ttk.Label(
            main_frame,
            text=f"Análise em Grafos do repositório {self.repo}",
            font=("Arial", 14, "bold")
        )
        titulo_label.pack(side=tk.TOP, anchor="center", pady=(0, 10))

        # LISTA DOS GRAFOS
        lista_frame = ttk.Frame(main_frame)
        lista_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))

        # 1) Comentários em Issues
        linha1 = ttk.Frame(lista_frame)
        linha1.pack(side=tk.TOP, fill=tk.X, pady=2)

        lbl1 = ttk.Label(linha1, text="Grafo: Comentários em Issues")
        lbl1.pack(side=tk.LEFT)

        btn1_ver = ttk.Button(
            linha1,
            text="Ver grafo",
            command=self.mostrar_grafo_comentario_issues
        )
        btn1_ver.pack(side=tk.LEFT, padx=5)

        btn1_rel = ttk.Button(
            linha1,
            text="Ver relatório",
            command=lambda: self.abrir_modal_relatorio(
                "Comentários em Issues",
                self.interacoes_comentarios
            )
        )
        btn1_rel.pack(side=tk.LEFT, padx=5)

        # 2) Fechamento de Issues
        linha2 = ttk.Frame(lista_frame)
        linha2.pack(side=tk.TOP, fill=tk.X, pady=2)

        lbl2 = ttk.Label(linha2, text="Grafo: Fechamento de Issues")
        lbl2.pack(side=tk.LEFT)

        btn2_ver = ttk.Button(
            linha2,
            text="Ver grafo",
            command=self.mostrar_grafo_fechamento_issues
        )
        btn2_ver.pack(side=tk.LEFT, padx=5)

        btn2_rel = ttk.Button(
            linha2,
            text="Ver relatório",
            command=lambda: self.abrir_modal_relatorio(
                "Fechamento de Issues",
                self.interacoes_fechamento
            )
        )
        btn2_rel.pack(side=tk.LEFT, padx=5)

        # 3) Pull Requests
        linha3 = ttk.Frame(lista_frame)
        linha3.pack(side=tk.TOP, fill=tk.X, pady=2)

        lbl3 = ttk.Label(linha3, text="Grafo: Pull Requests")
        lbl3.pack(side=tk.LEFT)

        btn3_ver = ttk.Button(
            linha3,
            text="Ver grafo",
            command=self.mostrar_grafo_pull_requests
        )
        btn3_ver.pack(side=tk.LEFT, padx=5)

        btn3_rel = ttk.Button(
            linha3,
            text="Ver relatório",
            command=lambda: self.abrir_modal_relatorio(
                "Pull Requests",
                self.interacoes_pr
            )
        )
        btn3_rel.pack(side=tk.LEFT, padx=5)

        # Botão de totais (se quiser manter)
        btn_totais = ttk.Button(
            main_frame,
            text="Mostrar totais de arestas (console)",
            command=self.mostrar_totais_arestas
        )
        btn_totais.pack(side=tk.TOP, anchor="w", pady=(8, 0))

    # ---------- modal de relatório ----------

    def abrir_modal_relatorio(self, nome_grafo, interacoes):
        if not interacoes:
            messagebox.showinfo(
                "Sem dados",
                f"Não há dados disponíveis para o grafo de {nome_grafo}."
            )
            return

        # monta o grafo NetworkX a partir das interações
        G = self.build_graph(self.usuarios, interacoes)

        titulo = f"Relatório – {nome_grafo} — {self.repo}"
        GraphReportWindow(self.root, titulo, G)


    # ---------- janela separada para o grafo ----------

    def _abrir_janela_grafo(self, interacoes, titulo, cor, salvar_png=False):

        if not interacoes:
            messagebox.showinfo(
                "Sem dados",
                f"Não há dados disponíveis para: {titulo}"
            )
            return

        # constrói grafo
        G = self.build_graph(self.usuarios, interacoes)

        # nova janela
        win = tk.Toplevel(self.root)
        win.title(titulo)
        win.geometry("900x600")

        # frame para o gráfico + toolbar
        frame_canvas = ttk.Frame(win, padding=10)
        frame_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        fig, ax = plt.subplots(figsize=(7, 5))

        # canvas do matplotlib dentro do Tk
        canvas = FigureCanvasTkAgg(fig, master=frame_canvas)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # toolbar de zoom/pan do matplotlib
        toolbar = NavigationToolbar2Tk(canvas, frame_canvas)
        toolbar.update()

        # desenha o grafo
        pos = nx.spring_layout(G, seed=42)

        nx.draw(
            G,
            pos,
            ax=ax,
            with_labels=True,
            node_color=cor,
            node_size=700,
            font_size=8,
            width=1.5
        )

        edge_labels = {(u, v): G[u][v]["weight"] for u, v in G.edges()}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, ax=ax)

        ax.set_title(titulo)
        fig.tight_layout()

        if salvar_png:
            fname = self.slugify(titulo) + ".png"
            fig.savefig(fname, dpi=150, bbox_inches="tight")
            print(f"✓ Figura salva em: {fname}")

        canvas.draw()

        # info embaixo: vértices e arestas
        info_frame = ttk.Frame(win, padding=10)
        info_frame.pack(side=tk.BOTTOM, fill=tk.X)

        lbl_info = ttk.Label(
            info_frame,
            text=f"Vértices: {G.number_of_nodes()} | Arestas: {G.number_of_edges()}"
        )
        lbl_info.pack(side=tk.LEFT, anchor="w")

    # ---------- wrappers dos 3 grafos ----------

    def mostrar_grafo_comentario_issues(self):
        titulo = f"Grafo: Comentários em Issues — {self.repo}"
        self._abrir_janela_grafo(self.interacoes_comentarios, titulo, cor="skyblue", salvar_png=True)

    def mostrar_grafo_fechamento_issues(self):
        titulo = f"Grafo: Fechamento de Issues — {self.repo}"
        self._abrir_janela_grafo(self.interacoes_fechamento, titulo, cor="lightgreen", salvar_png=True)

    def mostrar_grafo_pull_requests(self):
        titulo = f"Grafo: Pull Requests — {self.repo}"
        self._abrir_janela_grafo(self.interacoes_pr, titulo, cor="lightcoral", salvar_png=True)

    # ---------- totais de arestas (sem interface grande) ----------

    def _contar_arestas(self, interacoes):
        if not interacoes:
            return 0
        G = self.build_graph(self.usuarios, interacoes)
        return G.number_of_edges()

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
        print("\n" + texto + "\n")


if __name__ == "__main__":
    from main import load_data, build_graph, slugify

    data = load_data("dados_github.json")
    root = tk.Tk()
    app = GitHubGraphGUI(root, data, build_graph, slugify)
    root.mainloop()
