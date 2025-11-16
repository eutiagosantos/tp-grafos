import json
import re
import networkx as nx


def slugify(s: str) -> str:
    return re.sub(r'[^a-zA-Z0-9_.-]+', '_', s)


def load_data(caminho_arquivo="dados_github.json"):
    with open(caminho_arquivo, "r") as f:
        data = json.load(f)
    return data


def build_graph(usuarios, interacoes):
    """
    Constrói e retorna um grafo não direcionado (nx.Graph)
    a partir da lista de usuários e das interações.
    """
    G = nx.Graph()
    G.add_nodes_from(usuarios)

    for interacao in interacoes:
        de = interacao["from"]
        para = interacao["to"]
        peso = interacao.get("weight", 1)

        if G.has_edge(de, para):
            G[de][para]["weight"] += peso
        else:
            G.add_edge(de, para, weight=peso)

    return G


if __name__ == "__main__":
    # quando rodar main.py, abre a interface gráfica
    from interface import GitHubGraphGUI
    import tkinter as tk

    data = load_data("dados_github.json")

    root = tk.Tk()
    app = GitHubGraphGUI(root, data, build_graph, slugify)
    root.mainloop()
