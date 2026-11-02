# ************************************************
#   Cenario.py
#   Geracao (aleatoria, com semente), leitura e gravacao de triangulos.
#   Nao usa OpenGL.
# ************************************************

import random

from Ponto import Ponto
from Triangulo import Triangulo

# Limites logicos padrao da area de desenho (iguais ao codigo base)
LIMITE_MIN = Ponto(-10, -5)
LIMITE_MAX = Ponto(10, 5)

# A cor e' sempre sorteada no mesmo intervalo (indices 2..92 da lista de cores,
# evitando Black e White) para que a mesma semente gere SEMPRE o mesmo cenario,
# com ou sem OpenGL (Benchmark.py).
COR_MIN, COR_MAX = 2, 92


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


# **********************************************************************
# GeraAleatorio(n, semente, tamanho)
#   tamanho = None  -> como no codigo base: 3 vertices livres na area toda
#   tamanho = t     -> centro uniforme na area; cada vertice a no maximo
#                      t unidades do centro em x e em y (triangulos "pequenos")
# **********************************************************************
def GeraAleatorio(n, semente, tamanho=None, Min=LIMITE_MIN, Max=LIMITE_MAX):
    rng = random.Random(semente)
    tris = []
    for _ in range(n):
        if tamanho is None:
            rx, ry = (Max.x - Min.x) / 2, (Max.y - Min.y) / 2
            cx, cy = (Min.x + Max.x) / 2, (Min.y + Max.y) / 2
        else:
            cx = rng.uniform(Min.x, Max.x)
            cy = rng.uniform(Min.y, Max.y)
            rx = ry = tamanho
        P = []
        for _ in range(3):
            x = _clamp(cx + rng.uniform(-rx, rx), Min.x, Max.x)
            y = _clamp(cy + rng.uniform(-ry, ry), Min.y, Max.y)
            P.append(Ponto(x, y))
        tris.append(Triangulo(P[0], P[1], P[2], rng.randint(COR_MIN, COR_MAX)))
    return tris


# **********************************************************************
# Salva / Carrega
#   Formato texto: uma linha por triangulo  "x1 y1 x2 y2 x3 y3 [cor]"
#   Linhas vazias e linhas iniciadas por '#' sao ignoradas.
# **********************************************************************
def Salva(caminho, tris, comentario=""):
    with open(caminho, "w") as f:
        if comentario:
            f.write("# " + comentario + "\n")
        for T in tris:
            v = T.Vertices
            f.write("%.9g %.9g %.9g %.9g %.9g %.9g %d\n" %
                    (v[0].x, v[0].y, v[1].x, v[1].y, v[2].x, v[2].y, T.cor))


def Carrega(caminho):
    tris = []
    with open(caminho) as f:
        for num, linha in enumerate(f, 1):
            linha = linha.strip()
            if not linha or linha.startswith("#"):
                continue
            v = linha.split()
            if len(v) not in (6, 7):
                raise ValueError("%s:%d: esperado 6 ou 7 valores" % (caminho, num))
            x = [float(s) for s in v[:6]]
            cor = int(v[6]) if len(v) == 7 else COR_MIN + len(tris) % (COR_MAX - COR_MIN + 1)
            tris.append(Triangulo(Ponto(x[0], x[1]), Ponto(x[2], x[3]), Ponto(x[4], x[5]), cor))
    return tris


# **********************************************************************
# Limites(tris, margem)  -> (Min, Max) que englobam todos os triangulos
# Estatisticas(tris)     -> tamanho medio (area e dimensoes do envelope)
# **********************************************************************
def Limites(tris, margem=0.05):
    xs0 = min(T.Envelope[0].x for T in tris); ys0 = min(T.Envelope[0].y for T in tris)
    xs1 = max(T.Envelope[1].x for T in tris); ys1 = max(T.Envelope[1].y for T in tris)
    mx, my = (xs1 - xs0) * margem or 1.0, (ys1 - ys0) * margem or 1.0
    return Ponto(xs0 - mx, ys0 - my), Ponto(xs1 + mx, ys1 + my)


def Estatisticas(tris):
    n = max(1, len(tris))
    return {
        "area_media": sum(T.Area for T in tris) / n,
        "largura_env_media": sum(T.Envelope[1].x - T.Envelope[0].x for T in tris) / n,
        "altura_env_media": sum(T.Envelope[1].y - T.Envelope[0].y for T in tris) / n,
    }
