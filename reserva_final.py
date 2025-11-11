import customtkinter as ctk
from tkinter import messagebox
import sqlite3
import os

# ===============================
# CONFIGURAÇÕES INICIAIS
# ===============================
DB_FILE = "reservas.db"

# ===============================
# FUNÇÃO: CRIAR BANCO DE DADOS
# ===============================
def criar_banco():
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()

    # Tabelas
    cur.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE,
        senha TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS salas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS reservas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        sala_id INTEGER,
        data TEXT,
        horario TEXT,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id),
        FOREIGN KEY(sala_id) REFERENCES salas(id)
    )
    """)

    # Inserir usuários padrão
    usuarios = [("prof1", "123"), ("prof2", "456"), ("prof3", "789")]
    for nome, senha in usuarios:
        cur.execute("INSERT OR IGNORE INTO usuarios (nome, senha) VALUES (?, ?)", (nome, senha))

    # Inserir salas padrão
    salas = ["Robótica", "Laboratório de Ciências", "Biblioteca"]
    for sala in salas:
        cur.execute("INSERT OR IGNORE INTO salas (nome) VALUES (?)", (sala,))

    con.commit()
    con.close()


# ===============================
# CLASSE PRINCIPAL
# ===============================
class SistemaReservas(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Reservas de Salas")
        self.geometry("500x400")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        self.usuario_logado = None
        self.tela_login()

    # -------------------------------
    # TELA DE LOGIN
    # -------------------------------
    def tela_login(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.lbl_titulo = ctk.CTkLabel(self, text="Login", font=("Arial", 22))
        self.lbl_titulo.pack(pady=15)

        self.entry_usuario = ctk.CTkEntry(self, placeholder_text="Usuário")
        self.entry_usuario.pack(pady=5)

        self.entry_senha = ctk.CTkEntry(self, placeholder_text="Senha", show="*")
        self.entry_senha.pack(pady=5)

        self.btn_login = ctk.CTkButton(self, text="Entrar", command=self.verificar_login)
        self.btn_login.pack(pady=10)

    # -------------------------------
    # VERIFICAR LOGIN
    # -------------------------------
    def verificar_login(self):
        usuario = self.entry_usuario.get()
        senha = self.entry_senha.get()

        con = sqlite3.connect(DB_FILE)
        cur = con.cursor()
        cur.execute("SELECT * FROM usuarios WHERE nome = ? AND senha = ?", (usuario, senha))
        resultado = cur.fetchone()
        con.close()

        if resultado:
            self.usuario_logado = resultado
            messagebox.showinfo("Sucesso", f"Bem-vindo, {usuario}!")
            self.tela_reservas()
        else:
            messagebox.showerror("Erro", "Usuário ou senha incorretos!")

    # -------------------------------
    # TELA DE RESERVAS
    # -------------------------------
    def tela_reservas(self):
        for widget in self.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self, text=f"Olá, {self.usuario_logado[1]}", font=("Arial", 18)).pack(pady=5)
        ctk.CTkLabel(self, text="Faça sua reserva", font=("Arial", 20)).pack(pady=10)

        # Conexão para buscar salas
        con = sqlite3.connect(DB_FILE)
        cur = con.cursor()
        cur.execute("SELECT nome FROM salas")
        salas = [s[0] for s in cur.fetchall()]
        con.close()

        # SALA
        ctk.CTkLabel(self, text="Selecione a sala:").pack(pady=2)
        self.sala_var = ctk.StringVar(value=salas[0])
        self.menu_salas = ctk.CTkOptionMenu(self, values=salas, variable=self.sala_var)
        self.menu_salas.pack(pady=5)

        # DATA
        ctk.CTkLabel(self, text="Data (ex: 2025-11-10):").pack(pady=2)
        self.entry_data = ctk.CTkEntry(self, placeholder_text="YYYY-MM-DD")
        self.entry_data.pack(pady=5)

        # HORÁRIO (fixos)
        horarios = ["08:00", "09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00"]
        ctk.CTkLabel(self, text="Selecione o horário:").pack(pady=2)
        self.horario_var = ctk.StringVar(value=horarios[0])
        self.menu_horarios = ctk.CTkOptionMenu(self, values=horarios, variable=self.horario_var)
        self.menu_horarios.pack(pady=5)

        # BOTÕES
        ctk.CTkButton(self, text="Reservar Sala", command=self.fazer_reserva).pack(pady=8)
        ctk.CTkButton(self, text="Minhas Reservas", command=self.tela_minhas_reservas).pack(pady=5)
        ctk.CTkButton(self, text="Sair", command=self.tela_login).pack(pady=5)

    # -------------------------------
    # FAZER RESERVA
    # -------------------------------
    def fazer_reserva(self):
        sala = self.sala_var.get()
        data = self.entry_data.get()
        horario = self.horario_var.get()

        if not data:
            messagebox.showwarning("Atenção", "Preencha a data da reserva!")
            return

        con = sqlite3.connect(DB_FILE)
        cur = con.cursor()

        cur.execute("SELECT id FROM salas WHERE nome = ?", (sala,))
        sala_id = cur.fetchone()[0]

        cur.execute("""
        SELECT * FROM reservas
        WHERE sala_id = ? AND data = ? AND horario = ?
        """, (sala_id, data, horario))
        conflito = cur.fetchone()

        if conflito:
            messagebox.showerror("Erro", "Esta sala já está reservada neste horário!")
        else:
            cur.execute("INSERT INTO reservas (usuario_id, sala_id, data, horario) VALUES (?, ?, ?, ?)",
                        (self.usuario_logado[0], sala_id, data, horario))
            con.commit()
            messagebox.showinfo("Sucesso", f"Sala '{sala}' reservada com sucesso!")
        con.close()

    # -------------------------------
    # TELA: MINHAS RESERVAS
    # -------------------------------
    def tela_minhas_reservas(self):
        for widget in self.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self, text="Minhas Reservas", font=("Arial", 20)).pack(pady=10)

        con = sqlite3.connect(DB_FILE)
        cur = con.cursor()
        cur.execute("""
            SELECT reservas.id, salas.nome, data, horario
            FROM reservas
            JOIN salas ON reservas.sala_id = salas.id
            WHERE usuario_id = ?
            ORDER BY data, horario
        """, (self.usuario_logado[0],))
        reservas = cur.fetchall()
        con.close()

        if not reservas:
            ctk.CTkLabel(self, text="Nenhuma reserva encontrada.").pack(pady=10)
        else:
            for res in reservas:
                texto = f"{res[1]} - {res[2]} às {res[3]}"
                frame = ctk.CTkFrame(self)
                frame.pack(pady=5, padx=10, fill="x")
                ctk.CTkLabel(frame, text=texto).pack(side="left", padx=10)
                ctk.CTkButton(frame, text="Cancelar", width=80,
                              command=lambda r=res[0]: self.cancelar_reserva(r)).pack(side="right", padx=10)

        ctk.CTkButton(self, text="Voltar", command=self.tela_reservas).pack(pady=10)

    # -------------------------------
    # CANCELAR RESERVA
    # -------------------------------
    def cancelar_reserva(self, reserva_id):
        con = sqlite3.connect(DB_FILE)
        cur = con.cursor()
        cur.execute("DELETE FROM reservas WHERE id = ?", (reserva_id,))
        con.commit()
        con.close()
        messagebox.showinfo("Sucesso", "Reserva cancelada com sucesso!")
        self.tela_minhas_reservas()


# ===============================
# EXECUÇÃO
# ===============================
if __name__ == "__main__":
    criar_banco()
    app = SistemaReservas()
    app.mainloop()
