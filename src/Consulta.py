# ************************************************
#   Consulta.py
#   Algoritmo de consulta: subdivisao -> envelopes -> teste detalhado.
#   Cada etapa pode ser ligada/desligada. Contadores e tempo sao
#   recalculados a cada consulta. Nao usa OpenGL.
# ************************************************

import time


class Resultado:
    def __init__(self):
        self.total = 0               # triangulos do cenario
        self.candGrade = []          # indices candidatos da subdivisao
        self.candEnvelope = []       # indices aprovados pelo envelope
        self.dentro = []             # indices que contem o ponto
        self.testesDetalhados = 0
        self.celula = None           # (i, j) da celula que contem o ponto
        self.tempo = 0.0             # segundos (so' a consulta)


# Etapa 1 (grade)    : usaGrade
# Etapa 2 (envelope) : usaEnvelope
# Etapa 3 (detalhado): sempre executada
def ConsultaPonto(P, tris, grade, usaGrade, usaEnvelope):
    r = Resultado()
    r.total = len(tris)

    t0 = time.perf_counter()

    if usaGrade and grade is not None:
        cand, r.celula = grade.Candidatos(P)
    else:
        cand = range(r.total)                        # etapa desligada: tudo passa
    r.candGrade = cand

    if usaEnvelope:
        cand = [k for k in cand if tris[k].EnvelopeContem(P)]
    r.candEnvelope = cand

    r.testesDetalhados = len(cand)
    r.dentro = [k for k in cand if tris[k].PontoNoTriangulo(P)]

    r.tempo = time.perf_counter() - t0
    return r


# Referencia: teste detalhado em todos os triangulos (fora da medicao de tempo)
def ReferenciaForcaBruta(P, tris):
    return [k for k in range(len(tris)) if tris[k].PontoNoTriangulo(P)]
