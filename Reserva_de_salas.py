import customtkinter as ctk
from tkinter import messagebox

# Configuração do tema
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

# Usuários cadastrados (professores)
USUARIOS = {
    "prof1": "123",
    "prof2": "456",
    "prof3": "789"
}

# Horários disponíveis (07:00 às 17:00, blocos de 50 minutos)
HORARIOS = [
    "07:00 - 07:50", "07:50 - 08:40", "08:40 - 09:30",
    "09:30 - 10:20", "10:20 - 11:10", "11:10 - 12:00",
    "13:00 - 13:50", "13:50 - 14:40", "14:40 - 15:30",
    "15:30 - 16:20", "16:20 - 17:00"
]

# Dicionário para salvar reservas: { sala: {horario: professor} }
reservas = {
    "Biblioteca": {},
    "Robótica": {},
    "Laboratório de Ciências": {}
}

# Tamanho padrão dos botões
BOTAO_WIDTH = 150


class SistemaReservas(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Reservas de salas EREF Santo Inacio de Loyola")
        self.geometry("600x500")
        self.professor = None
        self.sala_selecionada = None
        self.tela_login()

    def limpar(self):
        for widget in self.winfo_children():
            widget.destroy()

    # Criar tela de login
    def tela_login(self):
        self.limpar()
        ctk.CTkLabel(self, text="Login do Professor",
                     font=("Arial", 20)).pack(pady=20)

        entry_user = ctk.CTkEntry(self, placeholder_text="Usuário")
        entry_user.pack(pady=5)

        entry_pass = ctk.CTkEntry(self, placeholder_text="Senha", show="*")
        entry_pass.pack(pady=5)

        msg = ctk.CTkLabel(self, text="")
        msg.pack(pady=5)

        def verificar_login():
            usuario = entry_user.get()
            senha = entry_pass.get()
            if usuario in USUARIOS and USUARIOS[usuario] == senha:
                self.professor = usuario
                self.tela_salas()
            else:
                msg.configure(text="Usuário ou senha incorretos",
                              text_color="red")

        ctk.CTkButton(self, text="Entrar",
                      command=verificar_login, fg_color="green", width=BOTAO_WIDTH).pack(pady=10)

    # Tela das salas
    def tela_salas(self):
        self.limpar()
        ctk.CTkLabel(self, text=f"Professor: {self.professor}",
                     text_color="lightgreen").pack(pady=5)
        ctk.CTkLabel(self, text="Escolha a Sala",
                     font=("Arial", 20)).pack(pady=20)

        def selecionar_sala(sala):
            self.sala_selecionada = sala
            self.tela_horarios()

        ctk.CTkButton(self, text="Biblioteca",
                      command=lambda: selecionar_sala("Biblioteca"), fg_color="green", width=BOTAO_WIDTH).pack(pady=5)
        ctk.CTkButton(self, text="Robótica",
                      command=lambda: selecionar_sala("Robótica"), fg_color="green", width=BOTAO_WIDTH).pack(pady=5)
        ctk.CTkButton(self, text="Laboratório de Ciências",
                      command=lambda: selecionar_sala("Laboratório de Ciências"), fg_color="green", width=BOTAO_WIDTH).pack(pady=5)

        # Botão para consultar reservas
        ctk.CTkButton(self, text="Consultar Minhas Reservas",
                      command=self.tela_consultar_reservas, fg_color="green", width=BOTAO_WIDTH).pack(pady=10)

        ctk.CTkButton(self, text="Sair",
                      command=self.tela_login, fg_color="green", width=BOTAO_WIDTH).pack(pady=10)

    # Botão para tela de reservas
    def tela_consultar_reservas(self):
        self.limpar()
        ctk.CTkLabel(self, text=f"Reservas de {self.professor}",
                     font=("Arial", 20)).pack(pady=20)

        frame = ctk.CTkScrollableFrame(self, width=500, height=300)
        frame.pack(pady=10)

        encontrou = False
        for sala, horarios in reservas.items():
            for horario, prof in horarios.items():
                if prof == self.professor:
                    ctk.CTkLabel(frame, text=f"{sala} - {horario}",
                                 font=("Arial", 14), text_color="lightgreen").pack(pady=2, anchor="w")
                    encontrou = True

        if not encontrou:
            ctk.CTkLabel(frame, text="Nenhuma reserva encontrada.",
                         text_color="gray").pack(pady=10)

        ctk.CTkButton(self, text="Voltar",
                      command=self.tela_salas, fg_color="green", width=BOTAO_WIDTH).pack(pady=20)

    # Tela de horários
    def tela_horarios(self):
        self.limpar()
        ctk.CTkLabel(
            self, text=f"Horários - {self.sala_selecionada}", font=("Arial", 20)
        ).pack(pady=20)

        ctk.CTkLabel(self, text=f"Professor: {self.professor}",
                     text_color="lightgreen").pack(pady=5)

        frame = ctk.CTkScrollableFrame(self, width=450, height=220)
        frame.pack(pady=10)

        def reservar_horario(horario):
            reservas_professor = [
                h for h, p in reservas[self.sala_selecionada].items() if p == self.professor]
            if len(reservas_professor) >= 2:
                messagebox.showwarning(
                    "Aviso", "Você já reservou 2 horários nesta sala.")
                return

            if horario in reservas[self.sala_selecionada]:
                messagebox.showerror(
                    "Erro", f"Este horário já está ocupado por {reservas[self.sala_selecionada][horario]}")
            else:
                reservas[self.sala_selecionada][horario] = self.professor
                messagebox.showinfo(
                    "Reserva", f"Horário {horario} reservado com sucesso!")
                self.tela_horarios()

        def cancelar_reserva():
            horarios_prof = [h for h, p in reservas[self.sala_selecionada].items()
                             if p == self.professor]
            if not horarios_prof:
                messagebox.showinfo(
                    "Cancelar", "Você não tem reservas nesta sala.")
                return

            for h in horarios_prof:
                del reservas[self.sala_selecionada][h]
            messagebox.showinfo("Cancelar", "Suas reservas foram canceladas.")
            self.tela_horarios()

        def alterar_reserva():
            horarios_prof = [h for h, p in reservas[self.sala_selecionada].items()
                             if p == self.professor]
            if not horarios_prof:
                messagebox.showinfo(
                    "Alterar", "Você não tem reservas nesta sala para alterar.")
                return

            antigo = horarios_prof[0]
            del reservas[self.sala_selecionada][antigo]
            messagebox.showinfo(
                "Alterar", f"Sua reserva em {antigo} foi liberada. Escolha um novo horário.")
            self.tela_horarios()

        # Listar horários
        for h in HORARIOS:
            if h in reservas[self.sala_selecionada]:
                ocupado = reservas[self.sala_selecionada][h]
                texto = f"{h}  - Ocupado por {ocupado}"
                btn = ctk.CTkButton(frame, text=texto,
                                    state="disabled", fg_color="gray", width=BOTAO_WIDTH)
            else:
                btn = ctk.CTkButton(
                    frame, text=h, command=lambda h=h: reservar_horario(h), fg_color="green", width=BOTAO_WIDTH)
            btn.pack(pady=2, fill="x")

        # Botões de ação na parte inferior
        botoes_frame = ctk.CTkFrame(self, fg_color="transparent")
        botoes_frame.pack(pady=15)

        ctk.CTkButton(botoes_frame, text="Cancelar Reserva",
                      command=cancelar_reserva, width=BOTAO_WIDTH, fg_color="green").grid(row=0, column=0, padx=5)
        ctk.CTkButton(botoes_frame, text="Alterar Reserva",
                      command=alterar_reserva, width=BOTAO_WIDTH, fg_color="green").grid(row=0, column=1, padx=5)
        ctk.CTkButton(botoes_frame, text="Voltar",
                      command=self.tela_salas, width=BOTAO_WIDTH, fg_color="green").grid(row=0, column=2, padx=5)


# Iniciar aplicação e manter a janela aberta
if __name__ == "__main__":
    app = SistemaReservas()
    app.mainloop()
