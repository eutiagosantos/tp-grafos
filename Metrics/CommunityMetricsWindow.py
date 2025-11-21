import tkinter as tk
from tkinter import ttk
import networkx as nx
from Metrics.CommunityMetrics import CommunityMetrics


class CommunityMetricsWindow:
    def __init__(self, master, titulo, G):
        self.win = tk.Toplevel(master)
        self.win.title(titulo)
        self.win.geometry("780x750")

        # ============================
        # SCROLL (Canvas + Frame)
        # ============================
        container = ttk.Frame(self.win)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, bg="#fafafa")
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=frame, anchor="nw")

        # ==========================================================
        # TÍTULO
        # ==========================================================
        ttk.Label(
            frame,
            text="📊 Métricas de Comunidade",
            font=("Arial", 22, "bold"),
            foreground="#003366"
        ).pack(pady=(10, 20))

        # ==========================================================
        # FUNÇÃO AUXILIAR – BLOCO COLORIDO
        # ==========================================================
        def bloco(parent, titulo, texto, cor_bg, cor_borda):
            box = tk.Frame(parent, bg=cor_bg, highlightbackground=cor_borda,
                           highlightthickness=2, padx=12, pady=12)
            box.pack(fill="x", pady=10)

            tk.Label(box, text=titulo, font=("Arial", 15, "bold"),
                     bg=cor_bg, fg="#000").pack(anchor="w", pady=(0, 6))

            tk.Label(box, text=texto, font=("Arial", 11),
                     bg=cor_bg, fg="#000", justify="left",
                     wraplength=740).pack(anchor="w")

            return box

        # ==========================================================
        # 1) MÉTRICAS BÁSICAS DO GRAFO
        # ==========================================================
        num_nodes = G.number_of_nodes()
        num_edges = G.number_of_edges()
        grau_medio = sum(dict(G.degree()).values()) / num_nodes if num_nodes else 0
        densidade = nx.density(G)

        texto_basico = (
            f"• Usuários (nós): {num_nodes}\n"
            f"• Interações (arestas): {num_edges}\n"
            f"• Grau médio: {grau_medio:.2f}\n"
            f"• Densidade da rede: {densidade:.4f}\n\n"
            "➤ Grau médio indica quantas pessoas, em média, cada usuário interage.\n"
            "➤ Densidade próxima de 0 significa rede dispersa; próximos de 1 indicam rede totalmente interligada.\n"
        )

        bloco(frame, "1) Estrutura Geral da Rede", texto_basico, "#e8f1ff", "#4d88ff")

        # ==========================================================
        # 2) DETECÇÃO DE COMUNIDADES
        # ==========================================================
        cm = CommunityMetrics(G)
        info = cm.detectar_comunidades()

        modularidade = info["modularidade"]
        num_comunidades = info["num_comunidades"]
        tamanhos = info["tamanho_comunidades"]
        comunidades = info["comunidades"]

        # Cor por nível de modularidade
        if modularidade >= 0.40:
            interpret_mod = "Comunidades bem definidas e separadas."
            cor_mod = "#d5f5e3"
            borda_mod = "#28b463"
        elif modularidade >= 0.20:
            interpret_mod = "Comunidades moderadamente definidas."
            cor_mod = "#fcf3cf"
            borda_mod = "#f1c40f"
        else:
            interpret_mod = "Comunidades fracas / pouco separadas."
            cor_mod = "#f9d6d5"
            borda_mod = "#e74c3c"

        texto_mod = (
            f"• Número de comunidades: {num_comunidades}\n"
            f"• Tamanhos: {tamanhos}\n"
            f"• Modularidade: {modularidade:.4f}\n\n"
            "Interpretação automática:\n"
            f"→ {interpret_mod}\n\n"
            "Escala de referência:\n"
            "• 0.00–0.20 → Grupos fracos\n"
            "• 0.20–0.40 → Grupos moderados\n"
            "• > 0.40 → Grupos fortes e bem formados\n"
        )

        # Bloco grande das comunidades
        quadro_comunidades = bloco(
            frame, "2) Estrutura de Comunidades", texto_mod, cor_mod, borda_mod
        )

        # =======================
        # 2.1) CARDS DE COMUNIDADES
        # =======================
        titulo_cards = tk.Label(
            quadro_comunidades,
            text="Comunidades Detectadas",
            font=("Arial", 15, "bold"),
            bg=cor_mod,
            fg="#000"
        )
        titulo_cards.pack(anchor="w", pady=(15, 10))

        paleta = ["#e3f2fd", "#e8f5e9", "#fff3e0", "#f3e5f5", "#fffde7"]

        for idx, com in enumerate(comunidades):
            card = tk.Frame(
                quadro_comunidades,
                bg=paleta[idx % len(paleta)],
                highlightbackground="#999",
                highlightthickness=1,
                padx=10, pady=8
            )
            card.pack(fill="x", pady=6)

            tk.Label(
                card,
                text=f"Comunidade {idx+1}",
                font=("Arial", 12, "bold"),
                bg=paleta[idx % len(paleta)]
            ).pack(anchor="w")

            tk.Label(
                card,
                text=", ".join(str(x) for x in com),
                font=("Arial", 10),
                bg=paleta[idx % len(paleta)],
                wraplength=720,
                justify="left"
            ).pack(anchor="w")

        # ==========================================================
        # 3) BRIDGING TIES
        # ==========================================================
        bridging = cm.bridging_ties()
        bridging_ord = sorted(bridging.items(), key=lambda x: x[1], reverse=True)

        explicacao_bridge = (
            "Bridging ties indicam usuários que ligam diferentes comunidades.\n\n"
            "Interpretação:\n"
            "• < 0.01 → Não é ponte\n"
            "• 0.01–0.05 → Ponte fraca\n"
            "• 0.05–0.15 → Ponte moderada\n"
            "• > 0.15 → Ponte forte (usuário crucial)\n"
        )

        quadro_bridge = bloco(
            frame,
            "3) Usuários Ponte Entre Comunidades (Bridging Ties)",
            explicacao_bridge,
            "#e6ffe6",
            "#28b463"
        )

        paleta_bridge = {
            "nenhum": "#eeeeee",
            "fraco": "#fff7d6",
            "moderado": "#ffe0b2",
            "forte": "#ffcccc"
        }

        for user, val in bridging_ord[:10]:
            if val < 0.01:
                cor = paleta_bridge["nenhum"]
                txt = "não conecta grupos"
            elif val < 0.05:
                cor = paleta_bridge["fraco"]
                txt = "ponte fraca"
            elif val < 0.15:
                cor = paleta_bridge["moderado"]
                txt = "ponte moderada"
            else:
                cor = paleta_bridge["forte"]
                txt = "ponte forte — usuário-chave"

            bloco(
                quadro_bridge,
                f"{user}",
                f"Valor: {val:.6f}\nInterpretação: {txt}",
                cor,
                "#666666"
            )

        # ==========================================================
        # BOTÃO FECHAR
        # ==========================================================
        tk.Button(
            frame,
            text="Fechar",
            command=self.win.destroy,
            font=("Arial", 12, "bold"),
            bg="#003366",
            fg="white",
            padx=12, pady=6
        ).pack(pady=25)
