from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)
DB_NAME = "contratos.db"

# --- Cria o banco e tabela se não existir ---
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS contratos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente TEXT NOT NULL,
                valor REAL NOT NULL,
                data_vencimento TEXT NOT NULL,
                status TEXT NOT NULL
            )
        """)
init_db()

# --- Atualiza status (Ativo/Vencido) automaticamente ---
def atualizar_status():
    hoje = datetime.now().date()
    with sqlite3.connect(DB_NAME) as conn:
        contratos = conn.execute("SELECT id, data_vencimento FROM contratos").fetchall()
        for c in contratos:
            data_venc = datetime.strptime(c[1], "%Y-%m-%d").date()
            status = "Vencido" if data_venc < hoje else "Ativo"
            conn.execute("UPDATE contratos SET status=? WHERE id=?", (status, c[0]))
        conn.commit()

# --- Função para buscar alertas de vencimento próximos ---
def buscar_alertas():
    hoje = datetime.now().date()
    alerta_dias = 7  # dias antes do vencimento para avisar
    alertas = []
    with sqlite3.connect(DB_NAME) as conn:
        contratos = conn.execute("SELECT id, cliente, data_vencimento FROM contratos").fetchall()
        for c in contratos:
            data_venc = datetime.strptime(c[2], "%Y-%m-%d").date()
            dias_restantes = (data_venc - hoje).days
            if 0 <= dias_restantes <= alerta_dias:
                alertas.append({
                    "id": c[0],
                    "cliente": c[1],
                    "data_vencimento": c[2],
                    "dias_restantes": dias_restantes
                })
    return alertas

# --- Middleware para adicionar alertas a cada requisição ---
@app.before_request
def adicionar_alertas():
    g.alertas = buscar_alertas()

# --- Página inicial: lista os contratos ---
@app.route('/')
def index():
    atualizar_status()
    with sqlite3.connect(DB_NAME) as conn:
        contratos = conn.execute("SELECT * FROM contratos ORDER BY data_vencimento").fetchall()
    return render_template('index.html', contratos=contratos, alertas=g.alertas)

# --- Novo contrato ---
@app.route('/novo', methods=['GET', 'POST'])
def novo():
    if request.method == 'POST':
        cliente = request.form['cliente']
        valor = float(request.form['valor'])
        data_vencimento = request.form['data_vencimento']
        status = "Ativo"

        with sqlite3.connect(DB_NAME) as conn:
            conn.execute("INSERT INTO contratos (cliente, valor, data_vencimento, status) VALUES (?, ?, ?, ?)",
                         (cliente, valor, data_vencimento, status))
        return redirect(url_for('index'))
    return render_template('form.html', contrato=None)

# --- Editar contrato ---
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    with sqlite3.connect(DB_NAME) as conn:
        contrato = conn.execute("SELECT * FROM contratos WHERE id=?", (id,)).fetchone()

    if request.method == 'POST':
        cliente = request.form['cliente']
        valor = float(request.form['valor'])
        data_vencimento = request.form['data_vencimento']

        with sqlite3.connect(DB_NAME) as conn:
            conn.execute("UPDATE contratos SET cliente=?, valor=?, data_vencimento=? WHERE id=?",
                         (cliente, valor, data_vencimento, id))
        return redirect(url_for('index'))
    return render_template('form.html', contrato=contrato)

# --- Excluir contrato ---
@app.route('/excluir/<int:id>')
def excluir(id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("DELETE FROM contratos WHERE id=?", (id,))
    return redirect(url_for('index'))

# --- Executar o app ---
if __name__ == '__main__':
    app.run(debug=True)
