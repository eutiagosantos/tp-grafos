import tkinter as tk
from tkinter import ttk
import networkx as nx
from Metrics.CommunityMetrics import CommunityMetrics


class CommunityMetricsWindow:
    def __init__(self, master, titulo, G):
        self.win = tk.Toplevel(master)
        self.win.title(titulo)
        self.win.geometry("780x780")

        # ============================ SCROLL ============================
        container = ttk.Frame(self.win)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, bg="#f7f7f7")
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=frame, anchor="nw")

        # ========== TÍTULO ==========
        ttk.Label(
            frame,
            text="📊 Métricas de Comunidade",
            font=("Arial", 22, "bold"),
            foreground="#003366"
        ).pack(pady=(15, 20))

        # ======== Função auxiliar para blocos ========
        def bloco(parent, titulo, texto, bg="#f0f0f0"):
            box = tk.Frame(parent, bg=bg, padx=12, pady=12, highlightthickness=1,
                           highlightbackground="#d0d0d0")
            box.pack(fill="x", pady=10)

            tk.Label(box, text=titulo, font=("Arial", 15, "bold"),
                     bg=bg, fg="#000").pack(anchor="w", pady=(0, 6))

            tk.Label(box, text=texto, font=("Arial", 11),
                     bg=bg, fg="#000", justify="left",
                     wraplength=740).pack(anchor="w")

            return box

        # ====================== 1) MÉTRICAS BÁSICAS ======================
        num_nodes = G.number_of_nodes()
        num_edges = G.number_of_edges()
        grau_medio = sum(dict(G.degree()).values()) / num_nodes if num_nodes else 0
        densidade = nx.density(G)

        texto_basico = (
            f"• Usuários (nós): {num_nodes}\n"
            f"• Interações (arestas): {num_edges}\n"
            f"• Grau médio: {grau_medio:.2f}\n"
            f"• Densidade da rede: {densidade:.4f}\n\n"
            "➤ Grau médio indica quantas pessoas cada usuário conecta diretamente.\n"
            "➤ Densidade próxima de 0 significa rede dispersa; próxima de 1 indica forte interconexão.\n"
        )

        bloco(frame, "1) Estrutura Geral da Rede", texto_basico)

        # ====================== 2) COMUNIDADES ======================
        cm = CommunityMetrics(G)
        info = cm.detectar_comunidades()

        modularidade = info["modularidade"]
        num_comunidades = info["num_comunidades"]
        tamanhos = info["tamanho_comunidades"]
        comunidades = info["comunidades"]

        # interpretação automática
        if modularidade >= 0.40:
            interpret_mod = "Comunidades bem definidas e separadas."
        elif modularidade >= 0.20:
            interpret_mod = "Comunidades moderadamente definidas."
        else:
            interpret_mod = "Comunidades fracas ou pouco separadas."

        texto_mod = (
            f"• Número de comunidades: {num_comunidades}\n"
            f"• Tamanhos (nós por comunidade): {tamanhos}\n"
            f"• Modularidade: {modularidade:.4f}\n\n"
            f"Interpretação automática:\n→ {interpret_mod}\n\n"
            "Escala de referência para modularidade:\n"
            "• 0.00–0.20 → Grupos fracos\n"
            "• 0.20–0.40 → Grupos moderados\n"
            "• > 0.40 → Grupos fortes e bem formados\n"
        )

        quadro_com = bloco(frame, "2) Estrutura de Comunidades", texto_mod)

        # ----------------------- LISTA DE COMUNIDADES -----------------------
        tk.Label(
            quadro_com,
            text="Comunidades Detectadas",
            font=("Arial", 15, "bold"),
            bg="#f0f0f0"
        ).pack(anchor="w", pady=(15, 5))

        paleta = ["#fafafa", "#f5f5f5"]  # alternância leve de fundo

        for idx, com in enumerate(comunidades):

            # determinar força da comunidade baseada em seu tamanho
            size = len(com)
            if size >= 10:
                nivel = "Comunidade grande (bem estabelecida)"
            elif size >= 3:
                nivel = "Comunidade média (atividade moderada)"
            else:
                nivel = "Comunidade pequena / isolada"

            card = tk.Frame(
                quadro_com,
                bg=paleta[idx % 2],
                padx=10, pady=8,
                highlightbackground="#cccccc",
                highlightthickness=1
            )
            card.pack(fill="x", pady=6)

            tk.Label(
                card,
                text=f"Comunidade {idx+1} — {size} usuários",
                font=("Arial", 12, "bold"),
                bg=paleta[idx % 2]
            ).pack(anchor="w")

            # legenda individual por comunidade
            legenda_texto = (
                "Escala de tamanho:\n"
                "• 1–2 usuários → comunidade extremamente pequena / isolada\n"
                "• 3–9 usuários → comunidade moderada\n"
                "• ≥10 usuários → comunidade importante / núcleo forte\n"
                f"\nClassificação automática: {nivel}\n"
            )

            tk.Label(
                card,
                text=legenda_texto,
                font=("Arial", 10),
                bg=paleta[idx % 2],
                justify="left",
                wraplength=720
            ).pack(anchor="w")

            # membros da comunidade
            tk.Label(
                card,
                text=", ".join(str(x) for x in com),
                font=("Arial", 10),
                bg=paleta[idx % 2],
                wraplength=720,
                justify="left"
            ).pack(anchor="w")

        # ====================== 3) BRIDGING TIES ======================
        bridging = cm.bridging_ties()
        bridge_sorted = sorted(bridging.items(), key=lambda x: x[1], reverse=True)

        explic_bridge = (
            "Bridging ties medem quem conecta comunidades diferentes.\n\n"
            "Escala:\n"
            "• < 0.01 → Não é ponte\n"
            "• 0.01–0.05 → Ponte fraca\n"
            "• 0.05–0.15 → Ponte moderada\n"
            "• > 0.15 → Ponte forte (usuário crucial)\n"
        )

        quadro_bridge = bloco(frame, "3) Usuários Ponte Entre Comunidades", explic_bridge)

        for user, score in bridge_sorted[:10]:

            if score < 0.01:
                nivel = "Não conecta grupos"
            elif score < 0.05:
                nivel = "Ponte fraca"
            elif score < 0.15:
                nivel = "Ponte moderada"
            else:
                nivel = "Ponte forte — usuário-chave"

            bloco(
                quadro_bridge,
                user,
                f"Bridging score: {score:.6f}\nClassificação: {nivel}",
                bg="#f9f9f9"
            )

        # ====================== BOTÃO FECHAR ======================
        tk.Button(
            frame,
            text="Fechar",
            command=self.win.destroy,
            font=("Arial", 12, "bold"),
            bg="#003366",
            fg="white",
            padx=12,
            pady=6
        ).pack(pady=25)
