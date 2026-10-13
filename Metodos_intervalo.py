import math
import time

def bisseccao(f, a, b, tol=1e-6, max_iter=100):
    if f(a) * f(b) >= 0: return None, 0, None
    
    for i in range(1, max_iter + 1):
        x = (a + b) / 2
        if abs(f(x)) < tol:
            return x, i, f(x)
        if f(a) * f(x) < 0: b = x
        else: a = x
            
    return x, max_iter, f(x)

def falsa_posicao(f, a, b, tol=1e-6, max_iter=100):
    if f(a) * f(b) >= 0: return None, 0, None
    
    for i in range(1, max_iter + 1):
        x = (a * f(b) - b * f(a)) / (f(b) - f(a))
        if abs(f(x)) < tol:
            return x, i, f(x)
        if f(a) * f(x) < 0: b = x
        else: a = x
            
    return x, max_iter, f(x)

# 2. A função a ser analisada 
def f_teste(x):
    return math.cos(x) - x

# 3. Execução e medição de resultados
def testar_meu_codigo():
    print("--- Resultados do Membro 1 ---")
    
    # Teste da Bissecção
    inicio_b = time.perf_counter()
    raiz_b, iter_b, res_b = bisseccao(f_teste, 0, 1)
    tempo_b = (time.perf_counter() - inicio_b) * 1000
    print(f"Bissecção     | Raiz: {raiz_b:.6f} | Iterações: {iter_b:2} | Tempo: {tempo_b:.4f} ms")

    # Teste da Falsa Posição
    inicio_f = time.perf_counter()
    raiz_f, iter_f, res_f = falsa_posicao(f_teste, 0, 1)
    tempo_f = (time.perf_counter() - inicio_f) * 1000
    print(f"Falsa Posição | Raiz: {raiz_f:.6f} | Iterações: {iter_f:2} | Tempo: {tempo_f:.4f} ms")

if __name__ == "__main__":
    testar_meu_codigo()