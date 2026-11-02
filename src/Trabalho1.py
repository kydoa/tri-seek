# **********************************************************************
# PUCRS/Escola Politecnica - COMPUTACAO GRAFICA
# Trabalho I - Inclusao de ponto em triangulos com aceleracao
# Base: Marcio Sarroglia Pinho
#
# Uso:  python Trabalho1.py [--n 500] [--seed 42] [--tamanho 1.5]
#                           [--grade 16] [--arquivo cenario.txt]
#       --tamanho 0  => triangulos "livres" (como no codigo base)
# Pressione 'h' para ver a lista de teclas.
# **********************************************************************

import argparse
import os
import random
import sys

from OpenGL.GL import *
from OpenGL.GLUT import *

import Cenario
import Visualizacao as V
from Aceleracao import GradeUniforme
from Consulta import ConsultaPonto, ReferenciaForcaBruta
from Ponto import Ponto


class App:
    pass


app = App()
app.Min = Cenario.LIMITE_MIN
app.Max = Cenario.LIMITE_MAX
app.w, app.h = 1000, 500
app.tris, app.grade, app.stats = [], None, {}
app.n, app.seed, app.tamanho, app.nx, app.arquivo = 500, 0, 1.5, 16, None
app.ponto, app.res, app.ok = Ponto(0, 0), None, True
# etapas do algoritmo
app.usaGrade, app.usaEnvelope = True, True
# opcoes de visualizacao
app.vGrade, app.vCelula, app.vEnv = True, True, False
app.vCandG, app.vCandE, app.vDentro = True, True, True
app.verifica, app.seguir = True, False
app.listas = None

AJUDA = """
Teclas:
  1..4  configuracao: 1 so detalhado | 2 envelope+det. | 3 grade+det. | 4 grade+envelope+det.
  g / e liga-desliga etapa GRADE / ENVELOPE
  d grade | z celula do ponto | b envelopes de todos | c cand. da grade | v aprov. pelo envelope | f triangulos que contem
  setas move o ponto (SHIFT = passo 10x) | clique/arrasto move o ponto | m ponto segue o mouse
  [ ] diminui/aumenta resolucao da grade | + - dobra/divide N | n novo cenario (nova semente)
  k liga-desliga verificacao contra a forca bruta | s salva cenario | B benchmark das 4 configuracoes
  h ajuda | q/ESC sair
"""


# **********************************************************************
# Cenario
# **********************************************************************
def MontaCenario():
    if app.arquivo:
        app.tris = Cenario.Carrega(app.arquivo)
        app.Min, app.Max = Cenario.Limites(app.tris)
    else:
        app.Min, app.Max = Cenario.LIMITE_MIN, Cenario.LIMITE_MAX
        app.tris = Cenario.GeraAleatorio(app.n, app.seed, app.tamanho)
    app.n = len(app.tris)
    app.grade = GradeUniforme(app.tris, app.Min, app.Max, app.nx)
    app.stats = Cenario.Estatisticas(app.tris)
    app.listas = None                  # recria as display lists no proximo display()
    AplicaProjecao()
    print("Cenario: N=%d seed=%s tamanho=%s | grade %dx%d (%.1f ms)" %
          (app.n, app.seed if not app.arquivo else app.arquivo, app.tamanho,
           app.grade.nx, app.grade.ny, app.grade.tempoConstrucao * 1000))
    Recalcula()


def RecriaGrade():
    app.grade = GradeUniforme(app.tris, app.Min, app.Max, app.nx)
    app.listas = None
    print("Grade %dx%d (%.1f ms)" % (app.grade.nx, app.grade.ny, app.grade.tempoConstrucao * 1000))
    Recalcula()


# **********************************************************************
# Consulta: executada SOMENTE quando o ponto ou a configuracao mudam
# **********************************************************************
def Recalcula(imprime=False):
    app.res = ConsultaPonto(app.ponto, app.tris, app.grade, app.usaGrade, app.usaEnvelope)
    if app.verifica:
        app.ok = (app.res.dentro == ReferenciaForcaBruta(app.ponto, app.tris))
        if not app.ok:
            print("*** DIVERGENCIA em relacao a forca bruta! ponto=(%g, %g)" % (app.ponto.x, app.ponto.y))
    if imprime:
        ImprimeConsulta()
    glutPostRedisplay()


def ImprimeConsulta():
    r = app.res
    print("Ponto (%.4f, %.4f) | total=%d candGrade=%d candEnv=%d testesDet=%d dentro=%d | %.4f ms" %
          (app.ponto.x, app.ponto.y, r.total, len(r.candGrade), len(r.candEnvelope),
           r.testesDetalhados, len(r.dentro), r.tempo * 1000))


def MovePonto(P, imprime=False):
    app.ponto = P
    Recalcula(imprime)


# **********************************************************************
# OpenGL
# **********************************************************************
def AplicaProjecao():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glViewport(0, 0, app.w, app.h)
    glOrtho(app.Min.x, app.Max.x, app.Min.y, app.Max.y, 0, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def reshape(w, h):
    app.w, app.h = max(1, w), max(1, h)
    AplicaProjecao()


def init():
    glClearColor(1, 1, 1, 1)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)


def CriaListas():
    if app.listas:
        for l in app.listas:
            glDeleteLists(l, 1)
    app.listas = (
        V.CriaLista(lambda: V.DesenhaTodosContornos(app.tris)),
        V.CriaLista(lambda: V.DesenhaTodosEnvelopes(app.tris)),
        V.CriaLista(lambda: V.DesenhaGrade(app.grade)),
    )


def Linhas():
    r = app.res
    cfg = "%s%s" % ("GRADE+" if app.usaGrade else "", "ENVELOPE+" if app.usaEnvelope else "") + "DETALHADO"
    off = lambda ligada, n: str(n) if ligada else "%d (etapa desligada)" % n
    pf = (0, 0, 0)
    return [
        ("Config: %s   (1-4, g/e)" % cfg, pf),
        ("N=%d  grade %dx%d  area media=%.3f  (h = ajuda)" %
         (app.n, app.grade.nx, app.grade.ny, app.stats["area_media"]), pf),
        ("Ponto: (%.3f, %.3f)  celula: %s" % (app.ponto.x, app.ponto.y, r.celula), pf),
        ("Total de triangulos ......... %d" % r.total, pf),
        ("Candidatos da subdivisao .... " + off(app.usaGrade, len(r.candGrade)), V.COR_CAND_GRADE),
        ("Aprovados pelo envelope ..... " + off(app.usaEnvelope, len(r.candEnvelope)), V.COR_CAND_ENV),
        ("Testes detalhados ........... %d" % r.testesDetalhados, pf),
        ("Triangulos que contem ....... %d" % len(r.dentro), V.COR_DENTRO),
        ("Tempo da consulta ........... %.4f ms" % (r.tempo * 1000), pf),
        ("Verificacao vs forca bruta .. " +
         (("OK" if app.ok else "DIVERGENTE!") if app.verifica else "desligada"),
         pf if app.ok else (1, 0, 0)),
    ]


def display():
    if not app.listas:
        CriaListas()
    glClear(GL_COLOR_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    r = app.res
    tris = app.tris

    if app.vCelula and app.usaGrade and r.celula is not None:
        V.PreencheCelula(app.grade, r.celula)
    if app.vGrade:
        glCallList(app.listas[2])
    if app.vEnv:
        glCallList(app.listas[1])
    V.DesenhaEixos(app.Min, app.Max)
    glLineWidth(1)
    glCallList(app.listas[0])

    glLineWidth(2)
    if app.vCandG and app.usaGrade:
        for k in r.candGrade:
            V.ContornoTriangulo(tris[k], V.COR_CAND_GRADE)
            V.ContornoEnvelope(tris[k], V.COR_CAND_GRADE)
    if app.vCandE and app.usaEnvelope:
        for k in r.candEnvelope:
            V.ContornoTriangulo(tris[k], V.COR_CAND_ENV)
            V.ContornoEnvelope(tris[k], V.COR_CAND_ENV)
    glLineWidth(1)
    if app.vDentro:
        for k in r.dentro:
            V.PreencheTriangulo(tris[k], V.COR_DENTRO + (0.65,))
            V.ContornoTriangulo(tris[k], (0.0, 0.4, 0.1))

    V.DesenhaPonto(app.ponto)
    V.DesenhaHUD(Linhas(), app.Min, app.Max, app.w, app.h)
    glutSwapBuffers()


# **********************************************************************
# Entrada
# **********************************************************************
def ConverteMouseParaUniverso(x, y):
    ux = app.Min.x + (x / app.w) * (app.Max.x - app.Min.x)
    uy = app.Max.y - (y / app.h) * (app.Max.y - app.Min.y)
    return Ponto(ux, uy, 0)


def Mouse(button, state, x, y):
    if state == GLUT_DOWN and button == GLUT_LEFT_BUTTON:
        MovePonto(ConverteMouseParaUniverso(x, y), imprime=True)


def MouseArrasto(x, y):
    MovePonto(ConverteMouseParaUniverso(x, y))


def MouseLivre(x, y):
    if app.seguir:
        MovePonto(ConverteMouseParaUniverso(x, y))


def arrow_keys(tecla, x, y):
    passo = (app.Max.x - app.Min.x) / 400
    if glutGetModifiers() & GLUT_ACTIVE_SHIFT:
        passo *= 10
    P = app.ponto
    if tecla == GLUT_KEY_UP:    MovePonto(Ponto(P.x, P.y + passo), True)
    if tecla == GLUT_KEY_DOWN:  MovePonto(Ponto(P.x, P.y - passo), True)
    if tecla == GLUT_KEY_LEFT:  MovePonto(Ponto(P.x - passo, P.y), True)
    if tecla == GLUT_KEY_RIGHT: MovePonto(Ponto(P.x + passo, P.y), True)


def Config(g, e):
    app.usaGrade, app.usaEnvelope = g, e
    Recalcula(True)


def Alterna(nome):
    setattr(app, nome, not getattr(app, nome))
    glutPostRedisplay()


def keyboard(*args):
    k = args[0].decode("latin-1")
    if k in ("q", "\x1b"):
        os._exit(0)
    elif k == "1": Config(False, False)
    elif k == "2": Config(False, True)
    elif k == "3": Config(True, False)
    elif k == "4": Config(True, True)
    elif k == "g": Config(not app.usaGrade, app.usaEnvelope)
    elif k == "e": Config(app.usaGrade, not app.usaEnvelope)
    elif k == "d": Alterna("vGrade")
    elif k == "z": Alterna("vCelula")
    elif k == "b": Alterna("vEnv")
    elif k == "c": Alterna("vCandG")
    elif k == "v": Alterna("vCandE")
    elif k == "f": Alterna("vDentro")
    elif k == "m": Alterna("seguir")
    elif k == "k":
        app.verifica = not app.verifica
        Recalcula()
    elif k == "[":
        app.nx = max(1, app.nx // 2); RecriaGrade()
    elif k == "]":
        app.nx = app.nx * 2; RecriaGrade()
    elif k in ("+", "-") and not app.arquivo:
        app.n = app.n * 2 if k == "+" else max(1, app.n // 2); MontaCenario()
    elif k == "n" and not app.arquivo:
        app.seed = random.randrange(1, 10**6); MontaCenario()
    elif k == "s":
        nome = "cenario_n%d_seed%s.txt" % (app.n, app.seed)
        Cenario.Salva(nome, app.tris, "n=%d seed=%s tamanho=%s" % (app.n, app.seed, app.tamanho))
        print("Cenario salvo em", nome)
    elif k == "B":
        import Benchmark
        pts = Benchmark.GeraPontos("uniforme", 200, app.Min, app.Max, 12345, app.tris)
        Benchmark.ImprimeTabela(Benchmark.Executa(app.tris, app.grade, pts))
    elif k == "h":
        print(AJUDA)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=500)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--tamanho", type=float, default=1.5)
    ap.add_argument("--grade", type=int, default=16)
    ap.add_argument("--arquivo", default=None)
    a, resto = ap.parse_known_args()

    app.n, app.nx, app.arquivo = a.n, a.grade, a.arquivo
    app.tamanho = a.tamanho if a.tamanho > 0 else None
    app.seed = a.seed if a.seed is not None else random.randrange(1, 10**6)

    glutInit([sys.argv[0]] + resto)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(app.w, app.h)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Trabalho 1 - Inclusao de ponto em triangulos")

    init()
    MontaCenario()
    print(AJUDA)

    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(arrow_keys)
    glutMouseFunc(Mouse)
    glutMotionFunc(MouseArrasto)
    glutPassiveMotionFunc(MouseLivre)

    try:
        glutMainLoop()
    except SystemExit:
        pass


if __name__ == "__main__":
    main()
