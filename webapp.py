from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from services.resultados_atualizador import atualizar_resultados
from analysis.baseline_91_18_oficial import executar_baseline, main as rodar_baseline
from db.db_repository import ContextoJogo

app = FastAPI()

def render_page(mensagem=""):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Loterias 91/18</title>
    </head>
    <body>
        <h2>Loterias 91/18</h2>

        <form action="/atualizar" method="post">
            <button type="submit">Atualizar Resultados</button>
        </form>

        <br>

        <form action="/baseline" method="post">
            Quantidade de apostas (3 a 10):
            <input type="number" name="qtd" min="3" max="10" value="3">
            <button type="submit">Executar Baseline</button>
        </form>

        <hr>

        <pre>{mensagem}</pre>

    </body>
    </html>
    """

@app.get("/", response_class=HTMLResponse)
def home():
    return render_page()

@app.post("/atualizar", response_class=HTMLResponse)
def atualizar():
    atualizar_resultados(2)
    contexto = ContextoJogo(2)
    ultimo = contexto.sorteios[-1]
    msg = f"Último sorteio na base:\n{ultimo}"
    return render_page(msg)

# @app.post("/baseline", response_class=HTMLResponse)
# def baseline(qtd: int = Form(...)):
#     contexto = ContextoJogo(2)
#     apostas = gerar_apostas(contexto.info, None, None, None, qtd)
#     msg = "Apostas geradas:\n\n"
#     for i, aposta in enumerate(apostas, 1):
#         msg += f"Aposta {i}: {aposta}\n"
#     return render_page(msg)

@app.post("/baseline", response_class=HTMLResponse)
def baseline(qtd: int = Form(...)):
    apostas = executar_baseline(qtd)

    msg = "Apostas geradas:\n\n"
    for i, aposta in enumerate(apostas, 1):
        msg += f"Aposta {i}: {aposta}\n"

    return render_page(msg)