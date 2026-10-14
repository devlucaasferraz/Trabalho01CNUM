import math
import time

def newton_raphson(f, df, x0, tol=1e-6, max_iter=100):
    x0_val = float(x0)
    for i in range(1, max_iter + 1):
        derivada = df(x0_val)
        if abs(derivada) < 1e-15:
            return None, i, None

        xn = x0_val - f(x0_val) / derivada
        if abs(f(xn)) < tol:
            return xn, i, f(xn)

        x0_val = xn

    return x0_val, max_iter, f(x0_val)

def secante(f, x0, x1, tol=1e-6, max_iter=100):
    xe, xd = float(x0), float(x1)
    for i in range(1, max_iter + 1):
        denominador = f(xd) - f(xe)
        if abs(denominador) < 1e-15:
            return None, i, None

        xm = (xe * f(xd) - xd * f(xe)) / denominador
        if abs(f(xm)) < tol:
            return xm, i, f(xm)

        xe, xd = xd, xm

    return xd, max_iter, f(xd)

# 2. A função a ser analisada
def f_teste(x):
    return math.cos(x) - x

def df_teste(x):
    return -math.sin(x) - 1

# 3. Execução e medição de resultados
def testar_meu_codigo():
    print("--- Resultados do Membro 2 ---")

    # Teste de Newton-Raphson
    inicio_n = time.perf_counter()
    raiz_n, iter_n, res_n = newton_raphson(f_teste, df_teste, 0.5)
    tempo_n = (time.perf_counter() - inicio_n) * 1000
    print(f"Newton-Raphson | Raiz: {raiz_n:.6f} | Iterações: {iter_n:2} | Tempo: {tempo_n:.4f} ms")

    # Teste da Secante
    inicio_s = time.perf_counter()
    raiz_s, iter_s, res_s = secante(f_teste, 0, 1)
    tempo_s = (time.perf_counter() - inicio_s) * 1000
    print(f"Secante        | Raiz: {raiz_s:.6f} | Iterações: {iter_s:2} | Tempo: {tempo_s:.4f} ms")

if __name__ == "__main__":
    testar_meu_codigo()
