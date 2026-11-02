# ************************************************
#   Aceleracao.py
#   Subdivisao espacial: GRADE UNIFORME (grid) 2D.
#   Guarda apenas INDICES dos triangulos (nao copia geometria).
#   Construida uma vez, quando o cenario e' criado ou carregado.
# ************************************************

import time

from Triangulo import EPS


class GradeUniforme:
    # nx = numero de celulas em x; ny e' calculado para as celulas ficarem
    # aproximadamente quadradas (a menos que seja informado).
    def __init__(self, triangulos, Min, Max, nx, ny=None):
        t0 = time.perf_counter()

        # limites da grade = area do cenario + envelope de todos os triangulos
        self.minx = min([Min.x] + [T.Envelope[0].x for T in triangulos])
        self.miny = min([Min.y] + [T.Envelope[0].y for T in triangulos])
        self.maxx = max([Max.x] + [T.Envelope[1].x for T in triangulos])
        self.maxy = max([Max.y] + [T.Envelope[1].y for T in triangulos])

        w = self.maxx - self.minx
        h = self.maxy - self.miny
        self.nx = max(1, int(nx))
        self.ny = max(1, int(ny)) if ny else max(1, round(self.nx * h / w)) if w > 0 else 1
        self.cw = w / self.nx if w > 0 else 1.0
        self.ch = h / self.ny if h > 0 else 1.0

        # celulas[j][i] = lista de indices de triangulos cujo envelope
        # (expandido por EPS) intersecta a celula
        self.celulas = [[[] for _ in range(self.nx)] for _ in range(self.ny)]
        for k, T in enumerate(triangulos):
            i0 = self._ix(T.Envelope[0].x - EPS)
            i1 = self._ix(T.Envelope[1].x + EPS)
            j0 = self._iy(T.Envelope[0].y - EPS)
            j1 = self._iy(T.Envelope[1].y + EPS)
            for j in range(j0, j1 + 1):
                linha = self.celulas[j]
                for i in range(i0, i1 + 1):
                    linha[i].append(k)

        self.tempoConstrucao = time.perf_counter() - t0

    def _ix(self, x):
        i = int((x - self.minx) / self.cw)
        return 0 if i < 0 else self.nx - 1 if i >= self.nx else i

    def _iy(self, y):
        j = int((y - self.miny) / self.ch)
        return 0 if j < 0 else self.ny - 1 if j >= self.ny else j

    # ******************************************************************
    # Candidatos(P) -> (lista_de_indices, (i, j))
    #   Candidatos = triangulos registrados na celula que contem P.
    #   Fora dos limites da grade nao ha triangulo possivel.
    # ******************************************************************
    def Candidatos(self, P):
        if (P.x < self.minx - EPS or P.x > self.maxx + EPS or
                P.y < self.miny - EPS or P.y > self.maxy + EPS):
            return [], None
        i = self._ix(P.x)
        j = self._iy(P.y)
        return self.celulas[j][i], (i, j)

    def Retangulo(self, i, j):
        x0 = self.minx + i * self.cw
        y0 = self.miny + j * self.ch
        return x0, y0, x0 + self.cw, y0 + self.ch

    def Info(self):
        tam = [len(c) for linha in self.celulas for c in linha]
        return {"celulas": len(tam), "media_por_celula": sum(tam) / len(tam),
                "max_por_celula": max(tam), "vazias": sum(1 for t in tam if t == 0),
                "tempo_construcao_ms": self.tempoConstrucao * 1000}
