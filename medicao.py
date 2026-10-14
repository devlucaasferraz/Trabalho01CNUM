import time
from metodos_intervalo import bisseccao, falsa_posicao
from metodos_abertos import newton_raphson, secante

def medir_metodo(nome_metodo, funcao_metodo, *args, **kwargs):
    """
    Executa um método numérico qualquer, mensurando o tempo de execução
    com alta precisão (time.perf_counter) e coletando o número de iterações,
    raiz aproximada, resíduo e status de convergência.
    """
    tol = kwargs.get('tol', 1e-6)
    max_iter = kwargs.get('max_iter', 100)

    t_inicio = time.perf_counter()
    try:
        resultado = funcao_metodo(*args, **kwargs)
        t_fim = time.perf_counter()
        tempo_ms = (t_fim - t_inicio) * 1000.0

        raiz, iteracoes, residuo = resultado

        if raiz is None:
            if "Newton" in nome_metodo:
                status = "Falha: Derivada nula"
            elif "Secante" in nome_metodo:
                status = "Falha: Divisão por zero"
            else:
                status = "Falha: Sem troca de sinal"
            sucesso = False
        else:
            if residuo is not None and abs(residuo) < tol:
                status = "Convergido"
                sucesso = True
            elif iteracoes >= max_iter:
                status = "Limite de iterações"
                sucesso = False
            else:
                status = "Concluído"
                sucesso = True

        return {
            "metodo": nome_metodo,
            "raiz": raiz,
            "iteracoes": iteracoes,
            "tempo_ms": tempo_ms,
            "residuo": abs(residuo) if residuo is not None else None,
            "sucesso": sucesso,
            "status": status
        }

    except Exception as e:
        t_fim = time.perf_counter()
        return {
            "metodo": nome_metodo,
            "raiz": None,
            "iteracoes": 0,
            "tempo_ms": (t_fim - t_inicio) * 1000.0,
            "residuo": None,
            "sucesso": False,
            "status": f"Erro: {str(e)}"
        }

def executar_comparativo(f, df, a, b, x0_newton, x0_sec, x1_sec, tol=1e-6, max_iter=100, nome="Problema"):
    """
    Executa a comparação dos 4 métodos numéricos para uma dada função e parâmetros.
    """
    resultados = [
        medir_metodo("Bissecção", bisseccao, f, a, b, tol=tol, max_iter=max_iter),
        medir_metodo("Falsa Posição", falsa_posicao, f, a, b, tol=tol, max_iter=max_iter),
        medir_metodo("Newton-Raphson", newton_raphson, f, df, x0_newton, tol=tol, max_iter=max_iter),
        medir_metodo("Secante", secante, f, x0_sec, x1_sec, tol=tol, max_iter=max_iter)
    ]
    return {
        "nome": nome,
        "dados": resultados
    }
