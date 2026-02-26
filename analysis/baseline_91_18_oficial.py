import math
import random
from collections import Counter
#import psycopg
#from config import DB_CONFIG
from db.db_repository import ContextoJogo


# ============================================================
# ASSINATURA E PROBABILIDADES
# ============================================================

def assinatura(dezenas):
    dezenas = sorted(dezenas)
    soma = sum(dezenas)
    amplitude = dezenas[-1] - dezenas[0]

    blocos = 1
    for i in range(1, len(dezenas)):
        if dezenas[i] != dezenas[i - 1] + 1:
            blocos += 1

    return (soma, amplitude, blocos)


def construir_P_real(sorteios):
    cont = Counter()

    for s in sorteios:
        cont[assinatura(s["dezenas"])] += 1

    total = sum(cont.values())

    return {k: v / total for k, v in cont.items()}


def construir_P_rand(info, n=200000):
    cont = Counter()

    for _ in range(n):
        aposta = random.sample(
            range(1, info.dezenas_total + 1),
            info.dezenas_sorteadas
        )
        cont[assinatura(aposta)] += 1

    total = sum(cont.values())

    return {k: v / total for k, v in cont.items()}


def LR(ass, P_real, P_rand):
    pr = P_real.get(ass, 1e-12)
    prand = P_rand.get(ass, 1e-12)
    return pr / prand


# ============================================================
# AVALIAÇÃO BASELINE
# ============================================================

def avaliar_baseline(info, sorteios, P_real, P_rand, cut=0.83, targets=300):
    scores_hist = []

    for s in sorteios:
        lr = LR(assinatura(s["dezenas"]), P_real, P_rand)
        if lr > 0:
            scores_hist.append(math.log(lr))

    scores_hist.sort()
    idx = int(len(scores_hist) * (1 - cut))
    threshold = scores_hist[idx]

    mortes = 0
    total = 0

    for s in sorteios[-targets:]:
        total += 1
        lr = LR(assinatura(s["dezenas"]), P_real, P_rand)
        if lr > 0:
            score = math.log(lr)
            if score < threshold:
                mortes += 1

    morte_real = mortes / total
    elim = cut

    return threshold, elim, morte_real


# ============================================================
# GERAR APOSTAS
# ============================================================

def gerar_apostas(info, P_real, P_rand, threshold, n=3):
    print("\n=== APOSTAS BASELINE 91/18 ===")
    geradas = []
    tentativas = 0

    while len(geradas) < n:
        tentativas += 1

        aposta = sorted(random.sample(
            range(1, info.dezenas_total + 1),
            info.dezenas_sorteadas
        ))

        lr = LR(assinatura(aposta), P_real, P_rand)

        if lr <= 0:
            continue

        score = math.log(lr)

        if score >= threshold:
            geradas.append((aposta, score))

    for i, (ap, sc) in enumerate(geradas, 1):
        print(f"Aposta {i}: {ap} | score={sc:.4f}")

    print(f"Tentativas até gerar {n}: {tentativas}")

    return geradas


# ============================================================
# EXECUÇÃO
# ============================================================

# def main():
#     print("=== INÍCIO laboratorio_estrutural ===")
#
#     #VELHO
#     #jogo_id = 2  # Lotofácil
#     #
#     #info = carregar_jogo_info(jogo_id)
#     #sorteios = carregar_sorteios(jogo_id)
#
#     #novo teste
#     contexto = ContextoJogo(2)
#
#     print(f"Jogo {contexto.jogo_id} | dezenas_total={contexto.info.dezenas_total} | dezenas_sorteadas={contexto.info.dezenas_sorteadas}")
#     print(f"Total de sorteios carregados: {len(contexto.sorteios)}")
#
#     print("\n=== CONSTRUINDO P_real ===")
#     P_real = construir_P_real(contexto.sorteios)
#
#     print("\n=== CONSTRUINDO P_rand ===")
#     P_rand = construir_P_rand(contexto.info, 200000)
#
#     print("\n=== BASELINE PURO (91/18 aproximado) ===")
#     threshold, elim, morte = avaliar_baseline(contexto.info, contexto.sorteios, P_real, P_rand)
#
#     ganho = 1 / (1 - elim)
#
#     print(f"elim={elim:.3f} | morte={morte:.3f} | ganho_proxy={ganho:.2f}x")
#
#     gerar_apostas(contexto.info, P_real, P_rand, threshold, 3)
#
#     print("\n=== FIM ===")
#
#
# if __name__ == "__main__":
#     main()

def main():
    print("=== INÍCIO baseline_91_18_oficial ===")

    contexto = ContextoJogo(2)

    info = contexto.info
    sorteios = contexto.sorteios

    print(f"Jogo 2 | dezenas_total={info.dezenas_total} | dezenas_sorteadas={info.dezenas_sorteadas}")
    print(f"Total de sorteios carregados: {len(sorteios)}")

    print("\n=== CONSTRUINDO P_real ===")
    P_real = construir_P_real(sorteios)

    print("\n=== CONSTRUINDO P_rand ===")
    P_rand = construir_P_rand(info, 200000)

    print("\n=== BASELINE PURO (91/18 oficial) ===")
    threshold, elim, morte = avaliar_baseline(info, sorteios, P_real, P_rand)

    ganho = 1 / (1 - elim) if elim < 1 else float("inf")

    print(f"elim={elim:.3f} | morte={morte:.3f} | ganho_proxy={ganho:.2f}x")

    print("\n=== APOSTAS BASELINE 91/18 ===")
    #altere o valor após "threshold' para o número de apostas que quiser gerar
    #lembrando que quanto mais apostas mais tempo demora
    gerar_apostas(info, P_real, P_rand, threshold, 3)

    print("\n=== FIM ===")

def executar_baseline(qtd):
    contexto = ContextoJogo(2)

    P_real = construir_P_real(contexto.sorteios)
    P_rand = construir_P_rand(contexto.info, 200000)

    threshold, elim, morte = avaliar_baseline(
        contexto.info,
        contexto.sorteios,
        P_real,
        P_rand
    )

    apostas = gerar_apostas(
        contexto.info,
        P_real,
        P_rand,
        threshold,
        qtd
    )

    return apostas

if __name__ == "__main__":
    main()