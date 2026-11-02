# ************************************************
#   Triangulo.py
#   Dados geometricos do triangulo (SEM codigo OpenGL).
#   Todo o desenho foi movido para Visualizacao.py.
#   Base: Marcio Sarroglia Pinho
# ************************************************

import math

from Ponto import Ponto, ObtemMinimo, ObtemMaximo

# Tolerancia numerica (em unidades do universo) usada para considerar que
# um ponto esta "sobre" uma aresta ou vertice.
EPS = 1e-9


class Triangulo:
    def __init__(self, *args):
        self.Vertices = [Ponto(), Ponto(), Ponto()]
        self.Envelope = [Ponto(), Ponto()]
        self.cor = 0

        if len(args) == 1:                      # somente a cor
            self.cor = args[0]
        elif len(args) == 2:                    # vetor de vertices e cor
            V, cor = args
            for i in range(3):
                self.Vertices[i] = Ponto(V[i].x, V[i].y, V[i].z)
            self.cor = cor
        elif len(args) == 4:                    # tres pontos e cor
            P1, P2, P3, cor = args
            self.Vertices[0] = Ponto(P1.x, P1.y, P1.z)
            self.Vertices[1] = Ponto(P2.x, P2.y, P2.z)
            self.Vertices[2] = Ponto(P3.x, P3.y, P3.z)
            self.cor = cor
        else:
            raise TypeError("Parametros invalidos para o construtor de Triangulo")

        self.CalculaEnvelope()

    # ******************************************************************
    # CalculaEnvelope()
    #   Calcula o envelope (AABB) e os dados pre-calculados usados no
    #   teste detalhado (comprimento das arestas, degeneracao).
    #   Deve ser chamado sempre que os vertices mudarem.
    # ******************************************************************
    def CalculaEnvelope(self):
        self.Envelope[0] = Ponto(self.Vertices[0].x, self.Vertices[0].y, self.Vertices[0].z)
        self.Envelope[1] = Ponto(self.Vertices[0].x, self.Vertices[0].y, self.Vertices[0].z)
        for i in range(1, 3):
            self.Envelope[0] = ObtemMinimo(self.Envelope[0], self.Vertices[i])
            self.Envelope[1] = ObtemMaximo(self.Envelope[1], self.Vertices[i])
        self._PreCalcula()

    def _PreCalcula(self):
        A, B, C = self.Vertices
        # comprimentos das arestas AB, BC, CA (d1, d2 e d3 usam estas arestas)
        self._L = (math.hypot(A.x - B.x, A.y - B.y),
                   math.hypot(B.x - C.x, B.y - C.y),
                   math.hypot(C.x - A.x, C.y - A.y))
        self.Area = abs((B.x - A.x) * (C.y - A.y) - (B.y - A.y) * (C.x - A.x)) / 2.0

        # Triangulo degenerado: altura <= EPS (3 pontos colineares ou coincidentes)
        maior = max(self._L)
        self.Degenerado = (2.0 * self.Area) <= EPS * maior or maior == 0.0
        if self.Degenerado:
            # o triangulo vira o segmento formado pelo par de vertices mais distante
            par = [(A, B), (B, C), (C, A)][self._L.index(maior)]
            self._Seg = (par[0].x, par[0].y, par[1].x, par[1].y)

    def getVertices(self, i=None):
        if i is None:
            return self.Vertices
        if 0 <= i < 3:
            return self.Vertices[i]
        return Ponto()

    def imprime(self):
        print("[" + " - ".join("(%g, %g)" % (v.x, v.y) for v in self.Vertices) + "]")

    # ******************************************************************
    # EnvelopeContem(P)
    #   Teste de ENVELOPE (AABB). Barato; so descarta, nunca decide.
    #   O envelope e' expandido por EPS para nao perder pontos que o teste
    #   detalhado aceitaria por tolerancia.
    # ******************************************************************
    def EnvelopeContem(self, P, eps=EPS):
        mn, mx = self.Envelope
        return (mn.x - eps <= P.x <= mx.x + eps and
                mn.y - eps <= P.y <= mx.y + eps)

    # ******************************************************************
    # PontoNoTriangulo(P)
    #   Teste DETALHADO (orientacao do ponto em relacao as 3 arestas).
    #   Mesma formula do codigo base, mas com:
    #     - tolerancia: |d| <= eps*comprimento_da_aresta conta como "zero"
    #       (d / comprimento = distancia do ponto a reta da aresta);
    #     - tratamento de triangulo degenerado (o base devolvia True para
    #       qualquer ponto da RETA que contem os vertices).
    #   Ponto sobre aresta ou vertice => pertence ao triangulo.
    # ******************************************************************
    def PontoNoTriangulo(self, P, eps=EPS):
        V = self.Vertices
        px, py = P.x, P.y

        if self.Degenerado:
            return _DistPontoSegmento(px, py, *self._Seg) <= eps

        ax, ay = V[0].x, V[0].y
        bx, by = V[1].x, V[1].y
        cx, cy = V[2].x, V[2].y
        L1, L2, L3 = self._L

        d1 = (px - bx) * (ay - by) - (ax - bx) * (py - by)
        d2 = (px - cx) * (by - cy) - (bx - cx) * (py - cy)
        d3 = (px - ax) * (cy - ay) - (cx - ax) * (py - ay)

        temNegativo = (d1 < -eps * L1) or (d2 < -eps * L2) or (d3 < -eps * L3)
        temPositivo = (d1 > eps * L1) or (d2 > eps * L2) or (d3 > eps * L3)

        return not (temNegativo and temPositivo)


def _DistPontoSegmento(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    q = dx * dx + dy * dy
    t = 0.0 if q == 0.0 else max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / q))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))
