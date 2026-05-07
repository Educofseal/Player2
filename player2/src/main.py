
import sys
import os


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.graph import Graph
from src.core.user import User
from src.io.file_reader import carregar_usuarios_dict
from src.services.recommendation_service import RecommendationService


DADOS_EXEMPLO = {
    "usuarios": [
        {"id": 1,  "nome": "João",    "interesses": ["anime", "jogos", "mangá", "rpg"]},
        {"id": 2,  "nome": "Maria",   "interesses": ["jogos", "filmes", "anime", "cosplay"]},
        {"id": 3,  "nome": "Lucas",   "interesses": ["rpg", "mangá", "jogos", "board games"]},
        {"id": 4,  "nome": "Ana",     "interesses": ["cosplay", "anime", "filmes", "k-pop"]},
        {"id": 5,  "nome": "Pedro",   "interesses": ["programação", "jogos", "hacking", "rpg"]},
        {"id": 6,  "nome": "Julia",   "interesses": ["k-pop", "anime", "cosplay", "mangá"]},
        {"id": 7,  "nome": "Carlos",  "interesses": ["board games", "rpg", "xadrez"]},
        {"id": 8,  "nome": "Bruna",   "interesses": ["filmes", "séries", "k-pop"]},
        {"id": 9,  "nome": "Rafael",  "interesses": ["hacking", "programação", "jogos", "anime"]},
        {"id": 10, "nome": "Camila",  "interesses": ["mangá", "anime", "cosplay", "filmes"]},
    ]
}


LINHA = "─" * 55
LINHA_D = "═" * 55


def cabecalho():
    print(f"\n{'═'*55}")
    print("   ██████╗ ██╗      █████╗ ██╗   ██╗███████╗██████╗  ██████╗ ")
    print("   ██╔══██╗██║     ██╔══██╗╚██╗ ██╔╝██╔════╝██╔══██╗╚════██╗")
    print("   ██████╔╝██║     ███████║ ╚████╔╝ █████╗  ██████╔╝ █████╔╝")
    print("   ██╔═══╝ ██║     ██╔══██║  ╚██╔╝  ██╔══╝  ██╔══██╗██╔═══╝ ")
    print("   ██║     ███████╗██║  ██║   ██║   ███████╗██║  ██║███████╗")
    print("   ╚═╝     ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚══════╝")
    print(f"{'═'*55}")
    print("   🎮  Recomendação Geek por Teoria dos Grafos")
    print(f"{'═'*55}\n")


def menu_principal():
    print(f"\n{LINHA}")
    print("  MENU PRINCIPAL")
    print(LINHA)
    print("  1 → Listar usuários")
    print("  2 → Ver recomendações (Dijkstra)")
    print("  3 → Ver conexões por nível (BFS)")
    print("  4 → Explorar grafo (DFS)")
    print("  5 → Componentes conectados")
    print("  6 → Info do grafo")
    print("  0 → Sair")
    print(LINHA)


def selecionar_usuario(servico: RecommendationService) -> int:

    usuarios = servico.grafo.get_todos_usuarios()
    print(f"\n  {'ID':<5} {'Nome':<15} Interesses")
    print(f"  {LINHA}")
    for u in usuarios:
        interesses_str = ", ".join(u.interesses[:4])
        if len(u.interesses) > 4:
            interesses_str += f" +{len(u.interesses)-4}"
        print(f"  {u.id:<5} {u.nome:<15} {interesses_str}")
    print()

    while True:
        try:
            uid = int(input("  Digite o ID do usuário: "))
            servico.grafo.get_usuario(uid)  
            return uid
        except (ValueError, KeyError):
            print("  ❌ ID inválido. Tente novamente.")

#  Ações do menu                                                      

def listar_usuarios(servico: RecommendationService):
    print(f"\n{LINHA_D}")
    print("  👥  USUÁRIOS CADASTRADOS")
    print(LINHA_D)
    for u in servico.grafo.get_todos_usuarios():
        print(f"\n  🎮 [{u.id}] {u.nome}")
        print(f"     Interesses: {', '.join(u.interesses)}")
    print(f"\n{LINHA_D}")


def ver_recomendacoes(servico: RecommendationService):
    print(f"\n{LINHA_D}")
    print("  🔍  RECOMENDAÇÕES (Dijkstra)")
    print(LINHA_D)
    uid = selecionar_usuario(servico)
    origem = servico.grafo.get_usuario(uid)

    recomendacoes = servico.recomendar(uid)

    print(f"\n  Recomendações para {origem.nome}:")
    print(f"  {LINHA}")

    if not recomendacoes:
        print("  Nenhuma conexão encontrada.")
        return

    for rank, (usuario, custo, caminho) in enumerate(recomendacoes, 1):
        afinidade = servico.afinidade_entre(uid, usuario.id)
        caminho_nomes = " → ".join(
            servico.grafo.get_usuario(i).nome for i in caminho
        )
        print(f"\n  #{rank} {usuario.nome}")
        print(f"     🤝 Interesses em comum: {afinidade}")
        print(f"     📏 Custo Dijkstra:      {custo:.4f}")
        print(f"     🗺️  Caminho:             {caminho_nomes}")

    print(f"\n{LINHA_D}")


def ver_bfs(servico: RecommendationService):
    print(f"\n{LINHA_D}")
    print("  🌐  CONEXÕES POR NÍVEL (BFS)")
    print(LINHA_D)
    uid = selecionar_usuario(servico)
    origem = servico.grafo.get_usuario(uid)

    grupos = servico.proximos_por_nivel(uid)

    print(f"\n  Níveis de separação a partir de {origem.nome}:")
    print(f"  {LINHA}")

    for nivel in sorted(grupos.keys()):
        usuarios = grupos[nivel]
        emoji = "🔵" if nivel == 0 else "🟢" if nivel == 1 else "🟡" if nivel == 2 else "🔴"
        label = "(você)" if nivel == 0 else f"grau {nivel}"
        nomes = ", ".join(u.nome for u in usuarios)
        print(f"\n  {emoji} Nível {nivel} {label}:")
        print(f"     {nomes}")

    print(f"\n{LINHA_D}")


def ver_dfs(servico: RecommendationService):
    print(f"\n{LINHA_D}")
    print("  🔎  EXPLORAÇÃO DFS")
    print(LINHA_D)
    uid = selecionar_usuario(servico)
    origem = servico.grafo.get_usuario(uid)

    ordem = servico.explorar_dfs(uid)

    print(f"\n  Ordem de exploração DFS a partir de {origem.nome}:")
    print(f"  {LINHA}")
    for i, u in enumerate(ordem, 1):
        marcador = "◉" if u.id == uid else "○"
        print(f"  {i:>2}. {marcador} {u.nome}")

    print(f"\n{LINHA_D}")


def ver_componentes(servico: RecommendationService):
    print(f"\n{LINHA_D}")
    print("  🧩  COMPONENTES CONECTADOS")
    print(LINHA_D)

    componentes = servico.componentes_conectados()

    print(f"\n  Total de componentes: {len(componentes)}")
    for i, comp in enumerate(componentes, 1):
        nomes = ", ".join(u.nome for u in comp)
        print(f"\n  Componente {i} ({len(comp)} usuário(s)):")
        print(f"     {nomes}")

    print(f"\n{LINHA_D}")


def ver_info_grafo(servico: RecommendationService):
    g = servico.grafo
    print(f"\n{LINHA_D}")
    print("  📊  INFORMAÇÕES DO GRAFO")
    print(LINHA_D)
    print(f"\n  Nós (usuários):   {g.total_usuarios()}")
    print(f"  Arestas:          {g.total_arestas()}")
    print(f"\n  Arestas (peso):")
    print(f"  {'De':<12} {'Para':<12} {'Em comum':>8} {'Peso':>8}")
    print(f"  {LINHA}")
    for aresta in sorted(g.get_arestas(), key=lambda e: e.peso):
        nome_a = g.get_usuario(aresta.usuario_id_a).nome
        nome_b = g.get_usuario(aresta.usuario_id_b).nome
        print(f"  {nome_a:<12} {nome_b:<12} {aresta.interesses_em_comum:>8} {aresta.peso:>8.4f}")
    print(f"\n{LINHA_D}")


def main():
    cabecalho()
    print("  Carregando usuários e construindo grafo...")

    usuarios = carregar_usuarios_dict(DADOS_EXEMPLO)

    grafo = Graph()
    for u in usuarios:
        grafo.adicionar_usuario(u)
    grafo.construir_arestas()

    print(f"  ✅ Grafo construído: {grafo}")

    servico = RecommendationService(grafo)

    acoes = {
        "1": listar_usuarios,
        "2": ver_recomendacoes,
        "3": ver_bfs,
        "4": ver_dfs,
        "5": ver_componentes,
        "6": ver_info_grafo,
    }

    while True:
        menu_principal()
        opcao = input("  Escolha uma opção: ").strip()

        if opcao == "0":
            print("\n  👋 Até logo! Boas conexões!\n")
            break
        elif opcao in acoes:
            try:
                acoes[opcao](servico)
            except Exception as e:
                print(f"\n  ❌ Erro: {e}")
        else:
            print("  ❌ Opção inválida. Tente novamente.")


if __name__ == "__main__":
    main()
