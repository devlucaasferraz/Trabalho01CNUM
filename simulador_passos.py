import math

def compilar_funcao(expressao_str):
    """
    Converte uma string matemática (ex: 'cos(x) - x', '20 + 90*exp(-0.15*t) - 50')
    em uma função Python segura e pronta para avaliação.
    """
    expr = expressao_str.replace('^', '**').replace('sen(', 'sin(').replace('ln(', 'log(')
    
    contexto_seguro = {
        'math': math,
        'sin': math.sin, 'sen': math.sin,
        'cos': math.cos,
        'tan': math.tan, 'tg': math.tan,
        'exp': math.exp,
        'log': math.log, 'ln': math.log,
        'sqrt': math.sqrt,
        'pi': math.pi, 'e': math.e,
        'abs': abs
    }

    def f(x):
        ctx = contexto_seguro.copy()
        ctx['x'] = float(x)
        ctx['t'] = float(x)
        return float(eval(expr, {"__builtins__": {}}, ctx))

    return f


def estimar_derivada(f, x, h=1e-7):
    """Calcula a derivada numérica pela diferença finita central."""
    return (f(x + h) - f(x - h)) / (2.0 * h)


def gerar_passos_bisseccao(f, a, b, tol=1e-6, max_iter=100):
    """Gera o histórico detalhado iteração a iteração para a Bissecção."""
    passos = []
    a_cur = float(a)
    b_cur = float(b)

    fa = f(a_cur)
    fb = f(b_cur)

    if fa * fb >= 0:
        return passos, "Falha: f(a) * f(b) >= 0 (sem troca de sinal no intervalo [a, b])."

    for i in range(1, max_iter + 1):
        x = (a_cur + b_cur) / 2.0
        fx = f(x)
        res = abs(fx)

        passos.append({
            'iter': i,
            'a': a_cur,
            'b': b_cur,
            'fa': fa,
            'fb': fb,
            'x': x,
            'fx': fx,
            'residuo': res,
            'detalhes': f"[{a_cur:.6f}, {b_cur:.6f}]"
        })

        if res < tol:
            return passos, "Convergência atingida"

        if fa * fx < 0:
            b_cur = x
            fb = fx
        else:
            a_cur = x
            fa = fx

    return passos, "Limite de iterações atingido"


def gerar_passos_falsa_posicao(f, a, b, tol=1e-6, max_iter=100):
    """Gera o histórico detalhado iteração a iteração para a Falsa Posição."""
    passos = []
    a_cur = float(a)
    b_cur = float(b)

    fa = f(a_cur)
    fb = f(b_cur)

    if fa * fb >= 0:
        return passos, "Falha: f(a) * f(b) >= 0 (sem troca de sinal garantida)."

    for i in range(1, max_iter + 1):
        fa = f(a_cur)
        fb = f(b_cur)
        den = fb - fa

        if abs(den) < 1e-15:
            return passos, "Falha: Divisão por zero (f(b) == f(a))."

        x = (a_cur * fb - b_cur * fa) / den
        fx = f(x)
        res = abs(fx)

        passos.append({
            'iter': i,
            'a': a_cur,
            'b': b_cur,
            'fa': fa,
            'fb': fb,
            'x': x,
            'fx': fx,
            'residuo': res,
            'detalhes': f"Secante entre [{a_cur:.4f}, {b_cur:.4f}]"
        })

        if res < tol:
            return passos, "Convergência atingida"

        if fa * fx < 0:
            b_cur = x
        else:
            a_cur = x

    return passos, "Limite de iterações atingido"


def gerar_passos_newton(f, df, x0, tol=1e-6, max_iter=100):
    """Gera o histórico detalhado iteração a iteração para Newton-Raphson."""
    passos = []
    x_cur = float(x0)

    for i in range(1, max_iter + 1):
        fx = f(x_cur)
        res = abs(fx)

        derivada = df(x_cur) if df is not None else estimar_derivada(f, x_cur)

        if abs(derivada) < 1e-15:
            return passos, "Falha: Derivada nula (f'(x) == 0)."

        x_prox = x_cur - fx / derivada
        fx_prox = f(x_prox)
        res_prox = abs(fx_prox)

        passos.append({
            'iter': i,
            'x': x_cur,
            'fx': fx,
            'dfx': derivada,
            'x_prox': x_prox,
            'fx_prox': fx_prox,
            'residuo': res_prox,
            'detalhes': f"f'(x) = {derivada:.6f}"
        })

        if res_prox < tol:
            return passos, "Convergência atingida"

        x_cur = x_prox

    return passos, "Limite de iterações atingido"


def gerar_passos_secante(f, x0, x1, tol=1e-6, max_iter=100):
    """Gera o histórico detalhado iteração a iteração para a Secante."""
    passos = []
    xe = float(x0)
    xd = float(x1)

    for i in range(1, max_iter + 1):
        fxe = f(xe)
        fxd = f(xd)
        den = fxd - fxe

        if abs(den) < 1e-15:
            return passos, "Falha: Divisão por zero (f(xd) == f(xe))."

        xm = (xe * fxd - xd * fxe) / den
        fxm = f(xm)
        res = abs(fxm)

        passos.append({
            'iter': i,
            'xe': xe,
            'xd': xd,
            'fxe': fxe,
            'fxd': fxd,
            'x': xm,
            'fx': fxm,
            'residuo': res,
            'detalhes': f"xe={xe:.4f}, xd={xd:.4f}"
        })

        if res < tol:
            return passos, "Convergência atingida"

        xe = xd
        xd = xm

    return passos, "Limite de iterações atingido"
