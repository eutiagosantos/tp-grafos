import json
import networkx as nx
import matplotlib.pyplot as plt

def criar_grafo(interacoes, usuarios, titulo, cor):
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

    print(f"{titulo} -> Nós: {G.number_of_nodes()}, Arestas: {G.number_of_edges()}")

    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(14, 10))
    weights = [G[u][v]["weight"] for u, v in G.edges()]
    
    nx.draw(
        G, pos,
        with_labels=True,
        node_color=cor,
        node_size=700,
        font_size=8,
        width=weights
    )
    plt.title(titulo)
    plt.show()


def grafo_comentario_issues(data):
    criar_grafo(
        data["interactions"]["comentario_em_issues"],
        data["users"],
        "Grafo de Comentários em Issues - BurntSushi/ripgrep",
        "skyblue"
    )


def fechamento_issues(data):
    criar_grafo(
        data["interactions"]["fechamento_de_issues"],
        data["users"],
        "Grafo de Fechamento de Issues - BurntSushi/ripgrep",
        "lightgreen"
    )


def grafo_pull_requests(data):
    interacoes = []
    for chave in ["comentario_pull_request", "revisoes_pull_request", "merge_pull_request"]:
        if chave in data["interactions"]:
            interacoes += data["interactions"][chave]

    if interacoes:
        criar_grafo(
            interacoes,
            data["users"],
            "Grafo de Pull Requests - BurntSushi/ripgrep",
            "lightcoral"
        )
    else:
        print("Nenhum dado de pull requests encontrado no JSON.")


if __name__ == "__main__":
    with open("dados_github.json", "r") as f:
        data = json.load(f)
    
    fechamento_issues(data)
    grafo_comentario_issues(data)
    grafo_pull_requests(data)
