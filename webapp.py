from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from services.resultados_atualizador import atualizar_resultados
from analysis.baseline_91_18_oficial import executar_baseline, main as rodar_baseline
from db.db_repository import ContextoJogo

app = FastAPI()

from db.db_repository import conectar

def obter_ultimo_numero_concurso() -> int | None:
    conn = conectar()
    try:
        with conn.cursor() as cur:
            # troque "numero_concurso" e "sorteios" se no seu banco tiver nomes diferentes
            cur.execute("SELECT MAX(numero_concurso) FROM sorteios;")
            return cur.fetchone()[0]
    finally:
        conn.close()

def render_page(msg=""):
    ultimo=obter_ultimo_numero_concurso()
    info=f"Último sorteio atualizado: {ultimo}" if ultimo else "Nenhum sorteio encontrado."
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Loterias 91/18</title>
    </head>

    <script>
    function enviarAtualizacao() {{
        var el = document.getElementById("status");
        if (el) {{
            el.innerText = "Aguarde, atualizando...";
        }}
        setTimeout(function() {{
            document.forms[0].submit();
        }}, 100);

        return false;
    }}
    </script>
    
    <body>
        <h2>Loterias 91/18</h2>
        
        <!--
         <form action="/atualizar" method="post">
             <button type="submit">Atualizar Resultados</button>
         </form>
        -->
        
        <div style="display:flex; align-items:center; gap:20px;">
            <form action="/atualizar" method="post" onsubmit="return enviarAtualizacao()">
                <button type="submit">Atualizar</button>
            </form>
            
            <div id="status" style="font-weight:bold;">
                {info}
            </div>
        </div>
        

        <br>

        <form action="/baseline" method="post">
            Quantidade de apostas (3 a 10):
            <input type="number" name="qtd" min="3" max="10" value="3">
            <button type="submit">Executar Baseline</button>
        </form>

        <hr>

        <pre>{msg}</pre>

    </body>
    </html>
    """

# @app.get("/", response_class=HTMLResponse)
# def home():
#     return render_page()


@app.get("/", response_class=HTMLResponse)
def home():
    # ultimo = obter_ultimo_numero_concurso()
    #
    # if ultimo:
    #     info = f"Último sorteio atualizado: {ultimo}"
    # else:
    #     info = "Nenhum sorteio encontrado."
    #
    return render_page()

@app.post("/atualizar", response_class=HTMLResponse)
def atualizar():
    atualizar_resultados(2)
    return render_page()

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