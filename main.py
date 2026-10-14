import math
import sys
from metodos_intervalo import bisseccao, falsa_posicao
from metodos_abertos import newton_raphson, secante
from medicao import executar_comparativo
from gerador_relatorio import exportar_para_excel, gerar_graficos

# ------------------------------------------------------------------------------
# DEFINIÇÃO DOS PROBLEMAS DO PROJETO
# ------------------------------------------------------------------------------

def get_problemas_padrao():
    return [
        {
            "nome": "Exemplo de Teste: cos(x) - x = 0",
            "f": lambda x: math.cos(x) - x,
            "df": lambda x: -math.sin(x) - 1,
            "a": 0.0, "b": 1.0,
            "x0_newton": 0.5,
            "x0_sec": 0.0, "x1_sec": 1.0
        },
        {
            "nome": "Problema 1: Resfriamento de Componente Eletrônico",
            "f": lambda t: 20.0 + 90.0 * math.exp(-0.15 * t) - 50.0,
            "df": lambda t: -13.5 * math.exp(-0.15 * t),
            "a": 0.0, "b": 10.0,
            "x0_newton": 0.0,
            "x0_sec": 0.0, "x1_sec": 10.0
        },
        {
            "nome": "Problema 2: Carregamento de Capacitor em Circuito RC",
            "f": lambda t: 5.0 * (1.0 - math.exp(-t)) - 3.8,
            "df": lambda t: 5.0 * math.exp(-t),
            "a": 0.0, "b": 3.0,
            "x0_newton": 0.0,
            "x0_sec": 0.0, "x1_sec": 3.0
        }
    ]


def exibir_tabela_terminal(resultado_problema):
    nome = resultado_problema["nome"]
    dados = resultado_problema["dados"]

    print("\n" + "=" * 80)
    print(f" {nome.upper()}")
    print("=" * 80)
    print(f"| {'Método':<16} | {'Raiz Encontrada':<16} | {'Iterações':<9} | {'Tempo (ms)':<11} | {'|f(raiz)|':<11} |")
    print(f"|{'-'*18}|{'-'*18}|{'-'*11}|{'-'*13}|{'-'*13}|")

    for item in dados:
        metodo = item["metodo"]
        raiz_str = f"{item['raiz']:.8f}" if item["raiz"] is not None else "Falha"
        iter_str = f"{item['iteracoes']:^9}"
        tempo_str = f"{item['tempo_ms']:>8.4f} ms"
        res_str = f"{item['residuo']:.2e}" if item["residuo"] is not None else "-"
        print(f"| {metodo:<16} | {raiz_str:<16} | {iter_str} | {tempo_str:<11} | {res_str:<11} |")

    print("-" * 80 + "\n")


def resolver_personalizado():
    print("\n--- Resolução de Equação Personalizada ---")
    expr_f = input("Digite a função f(x) (ex: math.cos(x) - x): ").strip()
    expr_df = input("Digite a derivada f'(x) (ex: -math.sin(x) - 1): ").strip()

    try:
        f = lambda x: eval(expr_f, {"x": x, "math": math, "np": math, "exp": math.exp, "sin": math.sin, "cos": math.cos})
        df = lambda x: eval(expr_df, {"x": x, "math": math, "np": math, "exp": math.exp, "sin": math.sin, "cos": math.cos})

        a = float(input("Intervalo inferior [a]: "))
        b = float(input("Intervalo superior [b]: "))
        x0_newton = float(input("Estimativa inicial x0 para Newton-Raphson: "))
        x0_sec = float(input("Estimativa inicial x0 para Secante: "))
        x1_sec = float(input("Estimativa inicial x1 para Secante: "))
        tol = float(input("Tolerância desejada (padrão 1e-6): ") or 1e-6)

        resultado = executar_comparativo(
            f=f, df=df, a=a, b=b,
            x0_newton=x0_newton, x0_sec=x0_sec, x1_sec=x1_sec,
            tol=tol, nome="Problema Personalizado"
        )
        exibir_tabela_terminal(resultado)

    except Exception as e:
        print(f"\nErro ao processar a entrada: {e}")


def executar_todos_e_exportar():
    print("\nExecutando bateria completa de problemas e gerando relatórios...")
    problemas = get_problemas_padrao()
    bateria = []

    for p in problemas:
        res = executar_comparativo(
            f=p["f"], df=p["df"], a=p["a"], b=p["b"],
            x0_newton=p["x0_newton"], x0_sec=p["x0_sec"], x1_sec=p["x1_sec"],
            nome=p["nome"]
        )
        exibir_tabela_terminal(res)
        bateria.append(res)

    exportar_para_excel(bateria, "tabelas_comparativas.xlsx")
    gerar_graficos(bateria, "graficos")
    print("\n✓ Planilha Excel gerada: 'tabelas_comparativas.xlsx'")
    print("✓ Gráficos gerados na pasta: 'graficos/'\n")


def menu():
    problemas = get_problemas_padrao()

    while True:
        print("=" * 60)
        print(" SIMULADOR DE EQUAÇÕES ALGÉBRICAS E TRANSCENDENTES")
        print(" Cálculo Numérico - UNIVASF 2026.2")
        print("=" * 60)
        print("1. Executar Exemplo de Teste [cos(x) - x = 0]")
        print("2. Executar Problema 1 [Resfriamento de Componente]")
        print("3. Executar Problema 2 [Capacitor em Circuito RC]")
        print("4. Executar TODOS e Gerar Relatório Completo (Excel + Gráficos)")
        print("5. Resolver Função Personalizada")
        print("0. Sair")
        print("=" * 60)

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            p = problemas[0]
            res = executar_comparativo(p["f"], p["df"], p["a"], p["b"], p["x0_newton"], p["x0_sec"], p["x1_sec"], nome=p["nome"])
            exibir_tabela_terminal(res)
        elif opcao == "2":
            p = problemas[1]
            res = executar_comparativo(p["f"], p["df"], p["a"], p["b"], p["x0_newton"], p["x0_sec"], p["x1_sec"], nome=p["nome"])
            exibir_tabela_terminal(res)
        elif opcao == "3":
            p = problemas[2]
            res = executar_comparativo(p["f"], p["df"], p["a"], p["b"], p["x0_newton"], p["x0_sec"], p["x1_sec"], nome=p["nome"])
            exibir_tabela_terminal(res)
        elif opcao == "4":
            executar_todos_e_exportar()
        elif opcao == "5":
            resolver_personalizado()
        elif opcao == "0":
            print("\nEncerrando o simulador. Até logo!")
            break
        else:
            print("\nOpção inválida! Tente novamente.")


if __name__ == "__main__":
    # Inicia a Interface Web Interativa (estilo shadcn/ui) por padrão.
    # Caso passe o argumento --cli, executa no terminal.
    if "--cli" in sys.argv or "-c" in sys.argv:
        menu()
    else:
        try:
            from servidor_web import iniciar_servidor
            iniciar_servidor()
        except KeyboardInterrupt:
            print("\nSimulador encerrado.")
        except Exception as e:
            print(f"Aviso: Não foi possível iniciar a interface web ({e}).")
            print("Iniciando em modo terminal (CLI)...\n")
            menu()
