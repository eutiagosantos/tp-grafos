import tkinter as tk
from tkinter import ttk
import networkx as nx

from Graph_LIB.Metrics import CentralityMetrics, resumo_geral_grafos, resumo_metricas_grafo


class GlobalReportWindow:
    """
    Janela com resumo geral das métricas para vários grafos.
    """

    def __init__(
        self,
        parent,
        titulo: str,
        grafos: list  # lista de (nome, grafo)
    ):
        self.parent = parent
        self.grafos = grafos

        self.win = tk.Toplevel(parent)
        self.win.title(titulo)
        self.win.geometry("900x450")

        main_frame = ttk.Frame(self.win, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # calcula resumos
        self.individuais, self.media_geral = resumo_geral_grafos(self.grafos)

        # tabela principal
        frame_tab = ttk.LabelFrame(main_frame, text="Médias das métricas por grafo")
        frame_tab.pack(fill=tk.BOTH, expand=True)

        # colunas: Métrica | Grafo1 | Grafo2 | Grafo3 | Média geral
        nomes_colunas = ["metrica"] + [nome for nome, _ in self.grafos] + ["media_geral"]
        self.tree = ttk.Treeview(
            frame_tab,
            columns=nomes_colunas,
            show="headings",
            height=10
        )

        for col in nomes_colunas:
            header = col.capitalize().replace("_", " ")
            self.tree.heading(col, text=header)
            self.tree.column(col, anchor="center", width=120)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(
            frame_tab,
            orient="vertical",
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._popular_tabela()

        # explicação das métricas em linguagem simples
        desc_frame = ttk.LabelFrame(main_frame, text="O que significa cada métrica?")
        desc_frame.pack(fill=tk.X, pady=(10, 0))

        desc_text = (
            "• degree: quão conectado o usuário está (quantas pessoas ele alcança diretamente).\n"
            "• betweenness: quem serve de 'ponte' entre grupos, aparecendo no meio de muitos caminhos.\n"
            "• closeness: quem, em média, está mais perto de todo mundo (chega rápido nos outros usuários).\n"
            "• pagerank: importância do usuário levando em conta não só quantas conexões ele tem,\n"
            "            mas também se ele é conectado com outros usuários importantes."
        )

        lbl_desc = ttk.Label(
            desc_frame,
            text=desc_text,
            justify="left"
        )
        lbl_desc.pack(side=tk.LEFT, anchor="w")

        bottom = ttk.Frame(main_frame)
        bottom.pack(fill=tk.X, pady=(10, 0))

        btn_fechar = ttk.Button(bottom, text="Fechar", command=self.win.destroy)
        btn_fechar.pack(side=tk.RIGHT)

    def _popular_tabela(self):
        metricas = ["degree", "betweenness", "closeness", "pagerank"]

        # monta uma linha por métrica
        for met in metricas:
            linha = [met]  # primeira coluna: nome da métrica

            # valores médios por grafo
            for nome_grafo, resumo in self.individuais:
                valor = resumo.get(met, {}).get("media", 0.0)
                linha.append(f"{valor:.4f}")

            # média geral entre grafos para essa métrica
            valor_geral = self.media_geral.get(met, 0.0)
            linha.append(f"{valor_geral:.4f}")

            self.tree.insert("", tk.END, values=tuple(linha))
