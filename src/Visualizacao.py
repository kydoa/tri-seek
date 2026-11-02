# ************************************************
#   Visualizacao.py
#   Todo o codigo OpenGL de desenho fica aqui.
#   Nao calcula nada de geometria/consulta.
# ************************************************

from OpenGL.GL import *
from OpenGL.GLUT import *

from ListaDeCoresRGB import colors

# Cores das categorias (RGB)
COR_GRADE       = (0.70, 0.70, 0.70)   # linhas da subdivisao
COR_CELULA      = (1.00, 0.90, 0.30, 0.55)   # celula que contem o ponto
COR_ENVELOPE    = (0.60, 0.60, 0.60)   # envelope de todos os triangulos
COR_CAND_GRADE  = (1.00, 0.50, 0.00)   # candidatos da subdivisao
COR_CAND_ENV    = (0.00, 0.35, 1.00)   # aprovados pelo envelope
COR_DENTRO      = (0.00, 0.75, 0.20)   # contem o ponto
COR_PONTO       = (0.00, 0.00, 0.00)


def CriaLista(desenha):
    id = glGenLists(1)
    glNewList(id, GL_COMPILE)
    desenha()
    glEndList()
    return id


def _corDoTriangulo(T):
    return colors[T.cor % len(colors)]


def ContornoTriangulo(T, rgb=None):
    glColor3f(*(rgb or _corDoTriangulo(T)))
    glBegin(GL_LINE_LOOP)
    for v in T.Vertices:
        glVertex2f(v.x, v.y)
    glEnd()


def PreencheTriangulo(T, rgba):
    glColor4f(*rgba)
    glBegin(GL_TRIANGLES)
    for v in T.Vertices:
        glVertex2f(v.x, v.y)
    glEnd()


def ContornoEnvelope(T, rgb):
    glColor3f(*rgb)
    mn, mx = T.Envelope
    glBegin(GL_LINE_LOOP)
    glVertex2f(mn.x, mn.y); glVertex2f(mx.x, mn.y)
    glVertex2f(mx.x, mx.y); glVertex2f(mn.x, mx.y)
    glEnd()


def DesenhaTodosContornos(tris):
    for T in tris:
        ContornoTriangulo(T)


def DesenhaTodosEnvelopes(tris):
    for T in tris:
        ContornoEnvelope(T, COR_ENVELOPE)


def DesenhaGrade(g):
    glColor3f(*COR_GRADE)
    glBegin(GL_LINES)
    for i in range(g.nx + 1):
        x = g.minx + i * g.cw
        glVertex2f(x, g.miny); glVertex2f(x, g.maxy)
    for j in range(g.ny + 1):
        y = g.miny + j * g.ch
        glVertex2f(g.minx, y); glVertex2f(g.maxx, y)
    glEnd()


def PreencheCelula(g, celula):
    x0, y0, x1, y1 = g.Retangulo(*celula)
    glColor4f(*COR_CELULA)
    glBegin(GL_QUADS)
    glVertex2f(x0, y0); glVertex2f(x1, y0); glVertex2f(x1, y1); glVertex2f(x0, y1)
    glEnd()


def DesenhaEixos(Min, Max):
    mx = (Min.x + Max.x) / 2
    my = (Min.y + Max.y) / 2
    glColor3f(0, 0, 0)
    glLineWidth(3)
    glBegin(GL_LINES)
    glVertex2f(Min.x, my); glVertex2f(Max.x, my)
    glVertex2f(mx, Min.y); glVertex2f(mx, Max.y)
    glEnd()
    glLineWidth(1)


def DesenhaPonto(P):
    glPointSize(8)
    glColor3f(*COR_PONTO)
    glBegin(GL_POINTS)
    glVertex2f(P.x, P.y)
    glEnd()
    glPointSize(1)


# **********************************************************************
# DesenhaHUD(linhas, Min, Max, w, h)
#   linhas = lista de (texto, rgb). Texto em fonte bitmap (tamanho fixo
#   em pixels), posicionado no canto superior esquerdo.
# **********************************************************************
def DesenhaHUD(linhas, Min, Max, w, h):
    if w <= 0 or h <= 0:
        return
    ux = (Max.x - Min.x) / w            # unidades do universo por pixel
    uy = (Max.y - Min.y) / h
    alt = 15
    larg = max(len(t) for t, _ in linhas) * 8 + 12
    topo = Max.y - 4 * uy
    esq = Min.x + 4 * ux

    glColor4f(1, 1, 1, 0.80)
    glBegin(GL_QUADS)
    glVertex2f(esq, topo); glVertex2f(esq + larg * ux, topo)
    glVertex2f(esq + larg * ux, topo - (len(linhas) * alt + 8) * uy)
    glVertex2f(esq, topo - (len(linhas) * alt + 8) * uy)
    glEnd()

    for k, (texto, rgb) in enumerate(linhas):
        glColor3f(*rgb)
        glRasterPos2f(esq + 6 * ux, topo - (k + 1) * alt * uy)
        for ch in texto:
            glutBitmapCharacter(GLUT_BITMAP_8_BY_13, ord(ch))
