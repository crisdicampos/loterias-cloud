import psycopg

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "loterias",
    "user": "postgres",
    "password": "Dados8641"
}


# =========================
# CONEXÃO
# =========================

def conectar():
    import os

    database_url = os.environ.get("DATABASE_URL")

    if database_url:
        return psycopg.connect(database_url)
    else:
        return psycopg.connect(**DB_CONFIG)

    #return psycopg.connect(**DB_CONFIG)


# =========================
# MODELO
# =========================

class JogoInfo:
    def __init__(self, dezenas_total, dezenas_sorteadas):
        self.dezenas_total = dezenas_total
        self.dezenas_sorteadas = dezenas_sorteadas


# =========================
# FUNÇÕES INTERNAS
# =========================

def carregar_jogo_info(jogo_id):
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT dezenas_total, dezenas_sorteadas
                FROM jogos
                WHERE id = %s
            """, (jogo_id,))
            row = cur.fetchone()
            return JogoInfo(row[0], row[1])


def carregar_sorteios(jogo_id):
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT s.numero_concurso, r.numero
                FROM sorteios s
                JOIN resultados r ON r.sorteio_id = s.id
                WHERE s.jogo_id = %s
                ORDER BY s.numero_concurso, r.bola
            """, (jogo_id,))
            dados = cur.fetchall()

    sorteios = []
    atual = None
    dezenas = []

    for concurso, numero in dados:
        if atual is None:
            atual = concurso

        if concurso != atual:
            sorteios.append({"numero": atual, "dezenas": dezenas})
            dezenas = []
            atual = concurso

        dezenas.append(numero)

    if dezenas:
        sorteios.append({"numero": atual, "dezenas": dezenas})

    return sorteios


# =========================
# CONTEXTO CENTRAL
# =========================

class ContextoJogo:
    def __init__(self, jogo_id):
        print("Carregando dados do banco...")
        self.jogo_id = jogo_id
        self.info = carregar_jogo_info(jogo_id)
        self.sorteios = carregar_sorteios(jogo_id)
        print(f"{len(self.sorteios)} sorteios carregados.")