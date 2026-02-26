from services.resultados_atualizador import atualizar_resultados
from analysis.baseline_91_18_oficial import main as rodar_baseline

def main():
    print("Escolha uma opção:")
    print("1 - Atualizar + Rodar Baseline")
    print("2 - Rodar só Baseline")

    opcao = input("Opção: ").strip()

    jogo_id = 2

    if opcao == "1":
        print("\n=== ATUALIZANDO RESULTADOS ===")
        atualizar_resultados(jogo_id)
        print("\n=== RODANDO BASELINE 91/18 ===")
        rodar_baseline()

    elif opcao == "2":
        print("\n=== RODANDO BASELINE 91/18 ===")
        rodar_baseline()

    else:
        print("Opção inválida.")

if __name__ == "__main__":
    main()