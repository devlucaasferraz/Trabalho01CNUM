import math
import time


def bisseccao(f, a, b, tol=1e-6, max_iter=100):
    """Método da Bissecção: divide o intervalo [a, b] ao meio a cada iteração.
    Retorna (raiz, iterações, f(raiz)). Se [a, b] for inválido, retorna (None, 0, None)."""
    fa, fb = f(a), f(b)
    if fa == 0: return a, 0, fa           # raiz exata em a
    if fb == 0: return b, 0, fb           # raiz exata em b
    if fa * fb > 0: return None, 0, None  # se os sinais forem iguais, não há garantia de raiz

    for i in range(1, max_iter + 1):
        x = (a + b) / 2                   # ponto médio
        fx = f(x)
        if abs(fx) < tol:                 # critério de parada: |f(x)| < tol (ex 10^-6)
            break
        if fa * fx < 0: b = x             # raiz em [a, x]
        else: a, fa = x, fx               # raiz em [x, b]
    return x, i, fx


def falsa_posicao(f, a, b, tol=1e-6, max_iter=100):
    """Método da Falsa Posição: usa a reta que liga (a, f(a)) a (b, f(b)).
    Retorna (raiz, iterações, f(raiz)). Se [a, b] for inválido, retorna (None, 0, None)."""
    fa, fb = f(a), f(b)
    if fa == 0: return a, 0, fa           # raiz exata em a
    if fb == 0: return b, 0, fb           # raiz exata em b
    if fa * fb > 0: return None, 0, None  # se os sinais forem iguais, não há garantia de raiz

    for i in range(1, max_iter + 1):
        x = (a * fb - b * fa) / (fb - fa)  # onde a reta cruza o eixo x
        fx = f(x)
        if abs(fx) < tol:                  # critério de parada: |f(x)| < tol (ex 10^-6)
            break
        if fa * fx < 0: b, fb = x, fx      # raiz em [a, x]
        else: a, fa = x, fx                # raiz em [x, b]
    return x, i, fx


# --- Funções de teste ---
def f_exemplo(x):
    return math.cos(x) - x                         # raiz de referência: 0,7390851332

#def f_problema1(t):
 #   return 20 + 90 * math.exp(-0.15 * t) - 50      # resfriamento do componente

def f_problema2(t):
    return 5 * (1 - math.exp(-t)) - 3.8            # carga do capacitor RC


# Exemplos/problemas
TESTES = [
    ("Exemplo: f(x) = cos(x) - x, intervalo [0, 1]", f_exemplo, 0, 1),
   # ("Problema 1: resfriamento, intervalo [0, 10]", f_problema1, 0, 10), Caso queira o problema 1 tire o #
    ("Problema 2: capacitor RC, intervalo [0, 2]", f_problema2, 0, 2),
]


def executar(nome, metodo, f, a, b, tol=1e-6, repeticoes=1000):
    """Roda o método, mede o tempo médio (ms) e imprime uma linha de resultado."""
    inicio = time.perf_counter()
    for _ in range(repeticoes):
        raiz, iteracoes, residuo = metodo(f, a, b, tol)
    tempo = (time.perf_counter() - inicio) * 1000 / repeticoes

    if raiz is None:
        print(f"{nome:<14}| Intervalo inválido: f(a) e f(b) precisam ter sinais opostos")
        return
    aviso = "" if abs(residuo) < tol else "  (não convergiu)"
    print(f"{nome:<14}| Raiz: {raiz:.6f} | Iterações: {iteracoes:2} | |f(x)|: {abs(residuo):.2e} | Tempo: {tempo:.4f} ms{aviso}")


if __name__ == "__main__":
    for titulo, f, a, b in TESTES:
        print(f"\n{titulo}")
        executar("Bissecção", bisseccao, f, a, b)
        executar("Falsa Posição", falsa_posicao, f, a, b)