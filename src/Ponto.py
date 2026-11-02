# ************************************************
#   Ponto.py
#   Define a classe Ponto
#   Autor: Márcio Sarroglia Pinho
#       pinho@pucrs.br
# ************************************************

import math

""" Classe Ponto """
class Ponto:   
    def __init__(self, x=0,y=0,z=0):
        self.x = x
        self.y = y
        self.z = z
    
    """ Imprime os valores de cada eixo do ponto """
    # Faz a impressao usando sobrecarga de funcao
    # https://www.educative.io/edpresso/what-is-method-overloading-in-python
    def imprime(self, msg=None):
        if msg is not None:
            print (msg, self.x, self.y, self.z)
        else:
            print (self.x, self.y, self.z)

    """ Define os valores dos eixos do ponto """
    def set(self, x, y, z=0):
        self.x = x
        self.y = y
        self.z = z
    
# Definicao de operadores
# https://www.programiz.com/python-programming/operator-overloading
    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        z = self.z + other.z
        return Ponto(x, y, z)

    def __sub__(self, other):
        #self.imprime("P1:")
        #other.imprime("P2:")
        x = self.x - other.x
        y = self.y - other.y
        z = self.z - other.z
        return Ponto(x, y, z)

    def __mul__(self, other: int):
        x = self.x * other.x
        y = self.y * other.x
        z = self.z * other.z
        return Ponto(x, y, z)

    def rotacionaZ(self, angulo):
        anguloRad = angulo * 3.14159265359/180.0
        xr = self.x*math.cos(anguloRad) - self.y*math.sin(anguloRad)
        yr = self.x*math.sin(anguloRad) + self.y*math.cos(anguloRad)
        self.x = xr
        self.y = yr

    def rotacionaY(self, angulo):
        anguloRad = angulo* 3.14159265359/180.0
        xr =  self.x*math.cos(anguloRad) + self.z*math.sin(anguloRad)
        zr = -self.x*math.sin(anguloRad) + self.z*math.cos(anguloRad)
        self.x = xr
        self.z = zr
   
    def rotacionaX(self, angulo):
        anguloRad = angulo* 3.14159265359/180.0
        yr =  self.y*math.cos(anguloRad) - self.z*math.sin(anguloRad)
        zr =  self.y*math.sin(anguloRad) + self.z*math.cos(anguloRad)
        self.y = yr
        self.z = zr

    def modulo(self):
        quad = self.x**2+self.y**2+self.z**2
        #print ("Quadrado :", quad)
        m = math.sqrt(quad)
        #print ("Modulo 1 :", m)
        return m

    def versor(self):
        #self.imprime("Vetor ANTES:")
        m = self.modulo()
        self.x = self.x/m
        self.y = self.y/m
        self.z = self.z/m
         
         

# ********************************************************************** */
#                                                                        */
#  Calcula a interseccao entre 2 retas (no plano "XY" Z = 0)             */
#                                                                        */
# k : ponto inicial da reta 1                                            */
# l : ponto final da reta 1                                              */
# m : ponto inicial da reta 2                                            */
# n : ponto final da reta 2                                              */
# 
# Retorna:
# 0, se não houver interseccao ou 1, caso haja                                                                       */
# int, valor do parâmetro no ponto de interseção (sobre a reta KL)       */
# int, valor do parâmetro no ponto de interseção (sobre a reta MN)       */
#                                                                        */
# ********************************************************************** */
def intersec2d(k: Ponto, l: Ponto, m: Ponto, n: Ponto):
    det = (n.x - m.x) * (l.y - k.y)  -  (n.y - m.y) * (l.x - k.x)

    if (det == 0.0):
        return 0, None, None # não há intersecção

    s = ((n.x - m.x) * (m.y - k.y) - (n.y - m.y) * (m.x - k.x))/ det
    t = ((l.x - k.x) * (m.y - k.y) - (l.y - k.y) * (m.x - k.x))/ det

    return 1, s, t # há intersecção

# **********************************************************************
# HaInterseccao(k: Ponto, l: Ponto, m: Ponto, n: Ponto)
# Detecta interseccao entre os pontos
#
# **********************************************************************
def HaInterseccao(k: Ponto, l: Ponto, m: Ponto, n: Ponto) -> bool:
    ret, s, t = intersec2d( k,  l,  m,  n)

    if not ret: return False

    return s>=0.0 and s <=1.0 and t>=0.0 and t<=1.0

# **********************************************************************
# ObtemMinimo(P1, P2)
#      Retorna um ponto contendo as menores coordenadas de P1 e P2.
# **********************************************************************
def ObtemMinimo(P1: Ponto, P2: Ponto) -> Ponto:
    x = min(P1.x, P2.x)
    y = min(P1.y, P2.y)
    z = min(P1.z, P2.z)

    return Ponto(x, y, z)

# **********************************************************************
# ObtemMaximo(P1, P2)
#      Retorna um ponto contendo as maiores coordenadas de P1 e P2.
# **********************************************************************
def ObtemMaximo(P1: Ponto, P2: Ponto) -> Ponto:
    return Ponto(max(P1.x, P2.x),
                 max(P1.y, P2.y),
                 max(P1.z, P2.z))