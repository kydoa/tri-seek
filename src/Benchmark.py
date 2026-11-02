# ************************************************
#   Benchmark.py
#   Compara as 4 configuracoes sobre os MESMOS cenarios e MESMOS pontos.
#   Nao precisa de OpenGL.
#
#   Exemplos:
#     python Benchmark.py                       (varredura padrao -> resultados.csv)
#     python Benchmark.py --n 1000 10000 --tamanho 0.5 2 --grade 8 32 --seeds 1 2
#     python Benchmark.py --pontos uniforme dentro --consultas 300 --csv saida.csv
# ************************************************

import argparse
import csv
import random

import Cenario
from Aceleracao import GradeUniforme
from Consulta import ConsultaPonto, ReferenciaForcaBruta
from Ponto import Ponto

CONFIGS = [  # (numero, usaGrade, usaEnvelope, nome)
    (1, False, False, "Detalhado (todos)"),
    (2, False, True,  "Envelope + Detalhado"),
    (3, True,  False, "Grade + Detalhado"),
    (4, True,  True,  "Grade + Envelope + Detalhado"),
]


# Distribuicoes de posicao dos pontos consultados (sempre reprodutiveis)
def GeraPontos(tipo, n, Min, Max, semente, tris=None):
    rng = random.Random(semente)
    w, h = Max.x - Min.x, Max.y - Min.y
    pts = []
    for _ in range(n):
        if tipo == "uniforme":
            pts.append(Ponto(rng.uniform(Min.x, Max.x), rng.uniform(Min.y, Max.y)))
        elif tipo == "centro":
            x = min(max(rng.gauss(Min.x + w / 2, w / 8), Min.x), Max.x)
            y = min(max(rng.gauss(Min.y + h / 2, h / 8), Min.y), Max.y)
            pts.append(Ponto(x, y))
        elif tipo == "canto":
            pts.append(Ponto(rng.uniform(Min.x, Min.x + 0.2 * w), rng.uniform(Min.y, Min.y + 0.2 * h)))
        elif tipo == "dentro":      # ponto dentro de um triangulo sorteado (acerto garantido)
            v = tris[rng.randrange(len(tris))].Vertices
            a, b = rng.random(), rng.random()
            if a + b > 1:
                a, b = 1 - a, 1 - b
            pts.append(Ponto(v[0].x + a * (v[1].x - v[0].x) + b * (v[2].x - v[0].x),
                             v[0].y + a * (v[1].y - v[0].y) + b * (v[2].y - v[0].y)))
        else:
            raise ValueError("tipo de ponto desconhecido: " + tipo)
    return pts


# Executa as configuracoes pedidas; devolve {num: dict de medias}
def Executa(tris, grade, pontos, configs=CONFIGS):
    refs = [ReferenciaForcaBruta(P, tris) for P in pontos]
    out = {}
    for num, g, e, nome in configs:
        t = cg = ce = td = dn = div = 0
        for P, ref in zip(pontos, refs):
            r = ConsultaPonto(P, tris, grade, g, e)
            t += r.tempo; cg += len(r.candGrade); ce += len(r.candEnvelope)
            td += r.testesDetalhados; dn += len(r.dentro)
            div += (r.dentro != ref)
        m = len(pontos)
        out[num] = {"nome": nome, "tempo_ms": t / m * 1000, "cand_grade": cg / m,
                    "cand_env": ce / m, "testes": td / m, "dentro": dn / m, "divergencias": div}
    return out


def ImprimeTabela(res):
    print("%-30s %10s %11s %10s %9s %8s %5s" %
          ("Configuracao", "tempo(ms)", "cand.grade", "cand.env", "testes", "dentro", "div"))
    for num in sorted(res):
        r = res[num]
        print("%-30s %10.4f %11.1f %10.1f %9.1f %8.2f %5d" %
              (r["nome"], r["tempo_ms"], r["cand_grade"], r["cand_env"], r["testes"], r["dentro"], r["divergencias"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, nargs="+", default=[100, 1000, 10000])
    ap.add_argument("--tamanho", type=float, nargs="+", default=[0.5, 2.0])
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2])
    ap.add_argument("--grade", type=int, nargs="+", default=[4, 16, 64])
    ap.add_argument("--pontos", nargs="+", default=["uniforme", "dentro"])
    ap.add_argument("--consultas", type=int, default=200)
    ap.add_argument("--csv", default="resultados.csv")
    a = ap.parse_args()

    campos = ["n", "tamanho", "area_media", "seed", "grade_nx", "grade_ny", "pontos", "config", "nome",
              "tempo_ms", "cand_grade", "cand_env", "testes", "dentro", "divergencias",
              "build_grade_ms", "max_por_celula"]
    with open(a.csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        for n in a.n:
            for tam in a.tamanho:
                for seed in a.seeds:
                    tris = Cenario.GeraAleatorio(n, seed, tam)
                    area = Cenario.Estatisticas(tris)["area_media"]
                    for tipo in a.pontos:
                        pts = GeraPontos(tipo, a.consultas, Cenario.LIMITE_MIN, Cenario.LIMITE_MAX, 999, tris)
                        base = Executa(tris, None, pts, [c for c in CONFIGS if not c[1]])   # 1 e 2: independem da grade
                        for nx in a.grade:
                            g = GradeUniforme(tris, Cenario.LIMITE_MIN, Cenario.LIMITE_MAX, nx)
                            res = dict(base)
                            res.update(Executa(tris, g, pts, [c for c in CONFIGS if c[1]]))
                            info = g.Info()
                            print("\nN=%d tam=%g (area media %.3f) seed=%d grade=%dx%d pontos=%s" %
                                  (n, tam, area, seed, g.nx, g.ny, tipo))
                            ImprimeTabela(res)
                            for num, r in res.items():
                                w.writerow({"n": n, "tamanho": tam, "area_media": round(area, 4), "seed": seed,
                                            "grade_nx": g.nx, "grade_ny": g.ny, "pontos": tipo, "config": num,
                                            "nome": r["nome"], "tempo_ms": round(r["tempo_ms"], 5),
                                            "cand_grade": r["cand_grade"], "cand_env": r["cand_env"],
                                            "testes": r["testes"], "dentro": r["dentro"],
                                            "divergencias": r["divergencias"],
                                            "build_grade_ms": round(info["tempo_construcao_ms"], 3),
                                            "max_por_celula": info["max_por_celula"]})
    print("\nResultados gravados em", a.csv)


if __name__ == "__main__":
    main()
