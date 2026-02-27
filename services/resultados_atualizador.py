
import requests
import os
from datetime import datetime
import openpyxl
from db.db_repository import conectar


def atualizar_resultados(jogo_id: int):
    print(f"\nIniciando atualização do jogo {jogo_id}...")

    conn = conectar()
    cur = conn.cursor()

    # Agora usamos dezenas_sorteadas
    cur.execute(
        "SELECT url_resultados, dezenas_sorteadas FROM jogos WHERE id = %s",
        (jogo_id,)
    )
    dados = cur.fetchone()

    if not dados:
        print("Jogo não encontrado.")
        return

    url, dezenas_sorteadas = dados

    os.makedirs("downloads", exist_ok=True)
    caminho_arquivo = f"downloads/resultados_jogo_{jogo_id}.xlsx"

    # Download
    #resposta = requests.get(url)
    #resposta = requests.get(url, verify=False)
    #resposta = requests.get(url, verify=certifi.where())
    resposta = requests.get(url, timeout=30)
    resposta.raise_for_status()

    with open(caminho_arquivo, "wb") as f:
        f.write(resposta.content)

    print("Download realizado com sucesso.")
    print("Tamanho:", len(resposta.content))
    print("Arquivo salvo em:", caminho_arquivo)
    print("Lendo arquivo XLSX...")

    wb = openpyxl.load_workbook(caminho_arquivo, data_only=True)
    ws = wb.active

    concursos = []

    for row in ws.iter_rows(min_row=2, values_only=True):

        if not row or row[0] is None:
            continue

        numero_concurso = row[0]
        data = row[1]

        # Extrair apenas as dezenas sorteadas (a partir da coluna 2)
        dezenas = []
        for valor in row[2:]:
            if isinstance(valor, (int, float)):
                numero = int(valor)
                dezenas.append(numero)

                if len(dezenas) == dezenas_sorteadas:
                    break

        if len(dezenas) != dezenas_sorteadas:
            continue

        concursos.append({
            "numero_concurso": numero_concurso,
            "data": data.strftime("%d/%m/%Y") if isinstance(data, datetime) else data,
            "dezenas": dezenas
        })

    print(f"Total de concursos processados: {len(concursos)}")
    if concursos:
        print("Exemplo:", concursos[0])

    inserir_ou_atualizar_resultados(conn, jogo_id, concursos)

    cur.close()
    conn.close()


def inserir_ou_atualizar_resultados(conn, jogo_id, concursos):
    print("Iniciando inserção ou atualização de resultados...")
    cur = conn.cursor()

    for concurso in concursos:

        # Verifica se já existe
        cur.execute(
            "SELECT id FROM sorteios WHERE jogo_id = %s AND numero_concurso = %s",
            (jogo_id, concurso["numero_concurso"])
        )
        existente = cur.fetchone()

        if existente:
            sorteio_id = existente[0]
        else:
            cur.execute(
                """
                INSERT INTO sorteios (jogo_id, numero_concurso, data_sorteio)
                VALUES (%s, %s, %s)
                RETURNING id;
                """,
                (jogo_id, concurso["numero_concurso"], concurso["data"])
            )
            sorteio_id = cur.fetchone()[0]

        # Inserir dezenas
        for idx, numero in enumerate(concurso["dezenas"], start=1):
            cur.execute(
                """
                INSERT INTO resultados (sorteio_id, bola, numero)
                VALUES (%s, %s, %s)
                ON CONFLICT (sorteio_id, bola)
                DO UPDATE SET numero = EXCLUDED.numero;
                """,
                (sorteio_id, idx, numero)
            )

    conn.commit()
    print("Atualização concluída com sucesso.")

def main():
    # Defina o jogo_id que você deseja atualizar
    jogo_id = 2  # Substitua com o ID do jogo para o qual deseja atualizar os resultados
    atualizar_resultados(jogo_id)

if __name__ == "__main__":
        main()