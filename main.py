"""Citizen Assist AI - assistente de orientação para jovens no primeiro emprego.

Inclui o módulo de Energia (Soluções em Energias Renováveis e Sustentáveis).

Execute com: python main.py
"""

import os

from assistente import Assistente, ler_opcao
from base_conhecimento import BaseConhecimento
from energia import ModuloEnergia, Premissas

# Garante que os caminhos "data/..." funcionem de qualquer pasta
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def main():
    base = BaseConhecimento("data/base_conhecimento.json")
    if not base.carregar():
        print("Não foi possível carregar a base de conhecimento. Verifique o arquivo e tente de novo.")
        return

    assistente = Assistente("Citizen Assist AI", base)

    premissas = Premissas("data/energia_premissas.json")
    energia = ModuloEnergia(premissas) if premissas.carregar() else None

    print("=" * 60)
    print(f"  {assistente.nome} - Primeiro Emprego")
    print("  Orientações sobre documentos, trabalho, benefícios e energia para jovens")
    print("  Não digite nome, CPF, telefone ou e-mail.")
    print("  Este assistente NÃO é um canal oficial.")
    print("=" * 60)

    while True:
        print("\n=== Menu principal ===")
        print("1. Fazer uma pergunta")
        print("2. Navegar por categorias")
        print("3. Ver indicadores")
        print("4. Exportar atendimentos (CSV)")
        print("5. Energia: calcular e economizar na conta de luz")
        print("0. Sair")
        opcao = ler_opcao("Escolha uma opção: ", 0, 5)

        if opcao == 1:
            assistente.perguntar()
        elif opcao == 2:
            assistente.navegar()
        elif opcao == 3:
            assistente.indicadores()
            if energia:
                energia.indicadores()
        elif opcao == 4:
            assistente.exportar_csv()
        elif opcao == 5:
            if energia:
                energia.menu()
            else:
                print("O módulo de energia está indisponível (arquivo de premissas não encontrado).")
        else:
            assistente.pedir_nota()
            print("Até logo!")
            break


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nPrograma encerrado.")
